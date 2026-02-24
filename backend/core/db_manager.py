"""
PostgreSQL database manager using asyncpg — product catalogue and invoices.
Aligned with original schema specifications.
"""
import asyncpg
import logging
from typing import Optional
from backend.core.config import get_config

logger = logging.getLogger(__name__)

# Use DATABASE_URL from config (loads from .env)
DATABASE_URL = get_config().database_url

class DBManager:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL is missing from environment.")
            cls._pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
        return cls._pool

    @classmethod
    async def init_db(cls):
        """Creates the necessary tables and extensions based on the original schema."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Extensions
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

                # Table fournisseurs
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS fournisseurs (
                        id SERIAL PRIMARY KEY,
                        nom VARCHAR(200) UNIQUE NOT NULL,
                        pays VARCHAR(50) DEFAULT 'ES',
                        langue VARCHAR(20) DEFAULT 'ca',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)

                # Table produits
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS produits (
                        id SERIAL PRIMARY KEY,
                        fournisseur_id INTEGER REFERENCES fournisseurs(id),
                        fournisseur VARCHAR(200) NOT NULL,
                        designation_raw TEXT NOT NULL,
                        designation_fr TEXT NOT NULL,
                        famille VARCHAR(100),
                        unite VARCHAR(50),
                        prix_brut_ht NUMERIC(10,4),
                        remise_pct NUMERIC(5,2) DEFAULT 0,
                        prix_remise_ht NUMERIC(10,4),
                        prix_ttc_iva21 NUMERIC(10,4),
                        numero_facture VARCHAR(100),
                        date_facture DATE,
                        confidence VARCHAR(10) DEFAULT 'high',
                        embedding vector(768),
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(designation_raw, fournisseur)
                    );
                """)

                # Table factures
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS factures (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(500),
                        storage_url TEXT,
                        statut VARCHAR(20) DEFAULT 'traite',
                        nb_produits_extraits INTEGER DEFAULT 0,
                        cout_api_usd NUMERIC(8,6) DEFAULT 0,
                        source VARCHAR(20) DEFAULT 'pc',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)

                # Indexes
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_produits_famille ON produits(famille);")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_produits_fournisseur ON produits(fournisseur);")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_produits_designation_trgm ON produits USING GIN (designation_fr gin_trgm_ops);")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_produits_updated ON produits(updated_at DESC);")

                logger.info("Base de données initialisée selon le schéma d'origine.")

    @classmethod
    async def upsert_product(cls, product: dict) -> bool:
        """
        Dénormalise le fournisseur et insère/met à jour le produit.
        """
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            # 1. Assurer l'existence du fournisseur
            fournisseur_id = await conn.fetchval("""
                INSERT INTO fournisseurs (nom) VALUES ($1)
                ON CONFLICT (nom) DO UPDATE SET nom = EXCLUDED.nom
                RETURNING id;
            """, product['fournisseur'])

            # Pour la clause ON CONFLICT DO UPDATE avec des variables explicites on parse une date valide ou null
            date_facture = None
            if product.get('date_facture'):
                try:
                    import datetime
                    # Essai simple de conversion pour le type DATE postgres (ISO format)
                    # Si c'est déjà propre du LLM, c'est bon. Sinon on met None pour éviter un crash.
                    d = datetime.datetime.fromisoformat(str(product['date_facture']).replace('Z',''))
                    date_facture = d.date()
                except Exception:
                    date_facture = None

            # 2. Upsert du Produit
            await conn.execute("""
                INSERT INTO produits
                    (fournisseur_id, fournisseur, designation_raw, designation_fr, famille, unite,
                     prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,
                     numero_facture, date_facture, confidence)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                ON CONFLICT (designation_raw, fournisseur)
                DO UPDATE SET
                    designation_fr = EXCLUDED.designation_fr,
                    famille = EXCLUDED.famille,
                    prix_brut_ht = EXCLUDED.prix_brut_ht,
                    remise_pct = EXCLUDED.remise_pct,
                    prix_remise_ht = EXCLUDED.prix_remise_ht,
                    prix_ttc_iva21 = EXCLUDED.prix_ttc_iva21,
                    updated_at = NOW()
            """,
            fournisseur_id,
            product['fournisseur'], product['designation_raw'],
            product['designation_fr'], product['famille'],
            product['unite'], product['prix_brut_ht'],
            product['remise_pct'], product['prix_remise_ht'],
            product['prix_ttc_iva21'], product['numero_facture'],
            date_facture, product.get('confidence', 'high'))
        return True

    @classmethod
    async def get_catalogue(cls, famille=None, fournisseur=None, search=None) -> list:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            query = """
                SELECT * FROM produits
                WHERE ($1::text IS NULL OR famille = $1)
                AND ($2::text IS NULL OR fournisseur ILIKE $2)
                AND ($3::text IS NULL OR designation_fr ILIKE $3)
                ORDER BY updated_at DESC
            """
            rows = await conn.fetch(
                query, famille,
                f"%{fournisseur}%" if fournisseur else None,
                f"%{search}%" if search else None
            )
            return [dict(r) for r in rows]

    @classmethod
    async def save_invoice(cls, file_hash: str, filename: str, nb_products: int):
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            # On stocke temporairement le hash dans la colonne filename (pour compatibilité)
            # ou on pourrait rajouter la colonne, mais on se tient au schéma fourni par l'utilisateur.
            await conn.execute("""
                INSERT INTO factures (filename, nb_produits_extraits, statut)
                VALUES ($1, $2, 'traite')
            """, filename, nb_products)

    @classmethod
    async def get_stats(cls) -> dict:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            products = await conn.fetchval("SELECT COUNT(*) FROM produits;")
            invoices = await conn.fetchval("SELECT COUNT(*) FROM factures;")
            families = await conn.fetchval("SELECT COUNT(DISTINCT famille) FROM produits;")
            return {"products": products, "invoices": invoices, "families": families}

    @classmethod
    async def get_invoices(cls) -> list:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM factures ORDER BY created_at DESC")
            return [dict(r) for r in rows]

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
