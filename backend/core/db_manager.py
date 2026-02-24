"""
Thread-safe SQLite database manager — product catalogue with price upsert.
"""
import sqlite3
import hashlib
import threading
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import pandas as pd

from backend.schemas.invoice import Product

logger = logging.getLogger(__name__)


class DBManager:
    """Product-oriented SQLite manager with price upsert logic."""

    def __init__(self, db_path: str = "data_cache.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_tables()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
        return self._conn

    def _ensure_tables(self):
        with self._lock:
            conn = self._get_connection()
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fournisseur TEXT NOT NULL,
                        designation_raw TEXT NOT NULL,
                        designation_fr TEXT,
                        famille TEXT,
                        unite TEXT,
                        prix_brut_ht REAL DEFAULT 0.0,
                        remise_pct REAL,
                        prix_remise_ht REAL DEFAULT 0.0,
                        prix_ttc_iva21 REAL DEFAULT 0.0,
                        numero_facture TEXT,
                        date_facture TEXT,
                        updated_at TIMESTAMP NOT NULL,
                        UNIQUE(designation_raw, fournisseur)
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS invoices (
                        file_hash TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        fournisseur TEXT,
                        numero_facture TEXT,
                        date_facture TEXT,
                        nb_products INTEGER DEFAULT 0,
                        processed_at TIMESTAMP NOT NULL
                    )
                """)
            logger.info(f"Database ready at {self.db_path}")

    @staticmethod
    def compute_file_hash(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def is_invoice_processed(self, file_hash: str) -> bool:
        with self._lock:
            conn = self._get_connection()
            cur = conn.execute(
                "SELECT 1 FROM invoices WHERE file_hash = ?", (file_hash,)
            )
            return cur.fetchone() is not None

    def upsert_product(self, product: Product, numero_facture: str, date_facture: str) -> str:
        """
        Insert or update a product. Returns 'added' or 'updated'.
        """
        with self._lock:
            conn = self._get_connection()
            cur = conn.execute(
                "SELECT id FROM products WHERE designation_raw = ? AND fournisseur = ?",
                (product.designation_raw, product.fournisseur),
            )
            existing = cur.fetchone()
            now = datetime.now().isoformat()

            if existing:
                conn.execute(
                    """UPDATE products SET
                        designation_fr=?, famille=?, unite=?,
                        prix_brut_ht=?, remise_pct=?, prix_remise_ht=?, prix_ttc_iva21=?,
                        numero_facture=?, date_facture=?, updated_at=?
                    WHERE id=?""",
                    (
                        product.designation_fr, product.famille, product.unite,
                        product.prix_brut_ht, product.remise_pct,
                        product.prix_remise_ht, product.prix_ttc_iva21,
                        numero_facture, date_facture, now, existing[0],
                    ),
                )
                conn.commit()
                return "updated"
            else:
                conn.execute(
                    """INSERT INTO products
                        (fournisseur, designation_raw, designation_fr, famille, unite,
                         prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,
                         numero_facture, date_facture, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        product.fournisseur, product.designation_raw,
                        product.designation_fr, product.famille, product.unite,
                        product.prix_brut_ht, product.remise_pct,
                        product.prix_remise_ht, product.prix_ttc_iva21,
                        numero_facture, date_facture, now,
                    ),
                )
                conn.commit()
                return "added"

    def save_invoice(self, file_hash: str, filename: str, fournisseur: str,
                     numero_facture: str, date_facture: str, nb_products: int):
        with self._lock:
            conn = self._get_connection()
            conn.execute(
                "INSERT OR REPLACE INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?)",
                (file_hash, filename, fournisseur, numero_facture,
                 date_facture, nb_products, datetime.now().isoformat()),
            )
            conn.commit()

    def get_catalogue(self) -> pd.DataFrame:
        with self._lock:
            conn = self._get_connection()
            return pd.read_sql_query(
                "SELECT * FROM products ORDER BY famille, designation_fr", conn
            )

    def get_invoices(self) -> pd.DataFrame:
        with self._lock:
            conn = self._get_connection()
            return pd.read_sql_query(
                "SELECT * FROM invoices ORDER BY processed_at DESC", conn
            )

    def get_stats(self) -> Dict:
        with self._lock:
            conn = self._get_connection()
            products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            invoices = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
            families = conn.execute("SELECT COUNT(DISTINCT famille) FROM products").fetchone()[0]
            return {"products": products, "invoices": invoices, "families": families}

    def reset_database(self):
        with self._lock:
            conn = self._get_connection()
            with conn:
                conn.execute("DELETE FROM products")
                conn.execute("DELETE FROM invoices")
            logger.warning("Database reset.")

    def close(self):
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None
