"""
One-shot migration script: SQLite -> PostgreSQL (Neon.tech).
Run once to transfer existing data from local SQLite to cloud PostgreSQL.

Usage:
    DATABASE_URL=postgresql://... python scripts/migrate_sqlite_to_postgres.py
"""
import os
import sys
import sqlite3

try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

SQLITE_PATH = os.getenv("SQLITE_PATH", "data_cache.db")
POSTGRES_URL = os.getenv("DATABASE_URL")


def migrate():
    if not POSTGRES_URL:
        print("DATABASE_URL environment variable is required")
        sys.exit(1)

    if not os.path.exists(SQLITE_PATH):
        print(f"SQLite database not found: {SQLITE_PATH}")
        sys.exit(1)

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(POSTGRES_URL, sslmode="require")

    try:
        pg_cur = pg_conn.cursor()

        products = sqlite_conn.execute("SELECT * FROM products").fetchall()
        for row in products:
            pg_cur.execute(
                "INSERT INTO products"
                " (fournisseur, designation_raw, designation_fr, famille, unite,"
                "  prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,"
                "  numero_facture, date_facture, updated_at)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                " ON CONFLICT (designation_raw, fournisseur) DO NOTHING",
                (
                    row["fournisseur"], row["designation_raw"],
                    row["designation_fr"], row["famille"], row["unite"],
                    row["prix_brut_ht"], row["remise_pct"],
                    row["prix_remise_ht"], row["prix_ttc_iva21"],
                    row["numero_facture"], row["date_facture"],
                    row["updated_at"],
                ),
            )

        invoices = sqlite_conn.execute("SELECT * FROM invoices").fetchall()
        for inv in invoices:
            pg_cur.execute(
                "INSERT INTO invoices"
                " (file_hash, filename, fournisseur,"
                "  numero_facture, date_facture, nb_products, processed_at)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s)"
                " ON CONFLICT (file_hash) DO NOTHING",
                (
                    inv["file_hash"], inv["filename"], inv["fournisseur"],
                    inv["numero_facture"], inv["date_facture"],
                    inv["nb_products"], inv["processed_at"],
                ),
            )

        pg_conn.commit()
        print(f"Migration complete:")
        print(f"  {len(products)} products migrated")
        print(f"  {len(invoices)} invoices migrated")

    except Exception as e:
        pg_conn.rollback()
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    migrate()
