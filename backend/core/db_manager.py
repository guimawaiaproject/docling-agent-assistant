"""
DBManager — Docling Agent v3
PostgreSQL Neon via asyncpg
- Cursor-based pagination (plus rapide et stable que OFFSET)
- Recherche floue pg_trgm sur designation_raw (CA/ES) + designation_fr (FR)
- Upsert anti-doublon sur (designation_raw, fournisseur)
- Thread-safe via connection pool (min 2, max 10)

Neon 2026 : utiliser l'URL avec -pooler (ex: ep-xxx-pooler.region.neon.tech)
pour PgBouncer → jusqu'à 10k connexions, meilleure résilience.
"""

import json
import logging
from datetime import date, datetime
from typing import Any, Optional

import asyncpg

from backend.core.config import Config

logger = logging.getLogger(__name__)

_UPSERT_SQL = """
    INSERT INTO produits (
        fournisseur, designation_raw, designation_fr,
        famille, unite,
        prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,
        numero_facture, date_facture, confidence, source
    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
    ON CONFLICT (designation_raw, fournisseur)
    DO UPDATE SET
        designation_fr = EXCLUDED.designation_fr,
        famille        = EXCLUDED.famille,
        prix_brut_ht   = EXCLUDED.prix_brut_ht,
        remise_pct     = EXCLUDED.remise_pct,
        prix_remise_ht = EXCLUDED.prix_remise_ht,
        prix_ttc_iva21 = EXCLUDED.prix_ttc_iva21,
        numero_facture = EXCLUDED.numero_facture,
        date_facture   = EXCLUDED.date_facture,
        confidence     = EXCLUDED.confidence,
        source         = EXCLUDED.source,
        updated_at     = NOW()
"""


def _parse_date(val) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    s = str(val).strip()
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _upsert_params(product: dict, source: str) -> tuple:
    return (
        product.get("fournisseur", ""),
        product.get("designation_raw", ""),
        product.get("designation_fr", ""),
        product.get("famille", "Autre"),
        product.get("unite", "unit\u00e9"),
        float(product.get("prix_brut_ht") or 0),
        float(product.get("remise_pct") or 0),
        float(product.get("prix_remise_ht") or 0),
        float(product.get("prix_ttc_iva21") or 0),
        product.get("numero_facture"),
        _parse_date(product.get("date_facture")),
        product.get("confidence", "high"),
        source,
    )


class DBManager:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            if not Config.DATABASE_URL:
                raise RuntimeError("DATABASE_URL non définie dans .env")
            cls._pool = await asyncpg.create_pool(
                Config.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=30,
                ssl="require",
            )
            logger.info("Pool asyncpg connect\u00e9 \u00e0 Neon")
        return cls._pool

    @classmethod
    async def close_pool(cls) -> None:
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

    @classmethod
    async def run_migrations(cls) -> None:
        """Ajoute les colonnes/tables manquantes sans casser l'existant."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                ALTER TABLE factures ADD COLUMN IF NOT EXISTS pdf_url TEXT;
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS prix_historique (
                    id          SERIAL PRIMARY KEY,
                    produit_id  INTEGER REFERENCES produits(id) ON DELETE CASCADE,
                    fournisseur VARCHAR(200) NOT NULL,
                    designation_fr TEXT NOT NULL,
                    prix_ht     NUMERIC(10,4) NOT NULL,
                    prix_brut   NUMERIC(10,4),
                    remise_pct  NUMERIC(5,2) DEFAULT 0,
                    facture_id  INTEGER REFERENCES factures(id) ON DELETE SET NULL,
                    recorded_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prixhist_produit
                    ON prix_historique(produit_id, recorded_at DESC);
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            SERIAL PRIMARY KEY,
                    email         VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    display_name  VARCHAR(200),
                    role          VARCHAR(20) DEFAULT 'user',
                    created_at    TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id     UUID PRIMARY KEY,
                    status     VARCHAR(20) DEFAULT 'processing',
                    result     JSONB,
                    error      TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);
            """)
            logger.info("Migrations auto OK")

    @classmethod
    async def upsert_product(cls, product: dict, source: str = "pc") -> bool:
        """Upsert un seul produit. D\u00e9l\u00e8gue au batch."""
        await cls.upsert_products_batch([product], source=source)
        return True

    @classmethod
    async def upsert_products_batch(
        cls, products: list[dict], source: str = "pc"
    ) -> int:
        """Ins\u00e8re/met \u00e0 jour une liste de produits dans une transaction."""
        pool = await cls.get_pool()
        count = 0
        async with pool.acquire() as conn:
            async with conn.transaction():
                for product in products:
                    try:
                        result = await conn.fetchrow(
                            _UPSERT_SQL + " RETURNING id",
                            *_upsert_params(product, source)
                        )
                        count += 1
                        if result and float(product.get("prix_remise_ht") or 0) > 0:
                            try:
                                await conn.execute("""
                                    INSERT INTO prix_historique
                                        (produit_id, fournisseur, designation_fr, prix_ht, prix_brut, remise_pct)
                                    VALUES ($1, $2, $3, $4, $5, $6)
                                """,
                                    result["id"],
                                    product.get("fournisseur", ""),
                                    product.get("designation_fr", ""),
                                    float(product.get("prix_remise_ht") or 0),
                                    float(product.get("prix_brut_ht") or 0),
                                    float(product.get("remise_pct") or 0),
                                )
                            except Exception as e:
                                logger.warning("Erreur insertion prix_historique: %s", e)
                    except Exception as e:
                        logger.warning(f"Upsert ignor\u00e9 pour {product.get('designation_raw')}: {e}")
        return count

    @classmethod
    async def get_catalogue(
        cls,
        famille:     Optional[str] = None,
        fournisseur: Optional[str] = None,
        search:      Optional[str] = None,
        limit:       int = 50,
        cursor:      Optional[str] = None,
    ) -> dict[str, Any]:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:

            conditions = []
            params: list[Any] = []
            idx = 1

            if cursor:
                conditions.append(f"updated_at < ${idx}::timestamptz")
                params.append(cursor)
                idx += 1

            if famille and famille != "Toutes":
                conditions.append(f"famille = ${idx}")
                params.append(famille)
                idx += 1

            if fournisseur:
                conditions.append(f"fournisseur ILIKE ${idx}")
                params.append(f"%{fournisseur}%")
                idx += 1

            if search and search.strip():
                s = search.strip()
                conditions.append(f"""(
                    designation_raw ILIKE ${idx}
                    OR designation_fr   ILIKE ${idx}
                    OR fournisseur      ILIKE ${idx}
                    OR similarity(designation_raw, ${idx+1}) > 0.2
                    OR similarity(designation_fr,  ${idx+1}) > 0.2
                )""")
                params.append(f"%{s}%")
                params.append(s)
                idx += 2

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            score_col = "0 AS score"
            order_clause = "updated_at DESC"
            if search and search.strip():
                s = search.strip()
                score_col = f"""GREATEST(
                    similarity(designation_raw, ${idx}),
                    similarity(designation_fr,  ${idx})
                ) AS score"""
                params.append(s)
                idx += 1
                order_clause = "score DESC, updated_at DESC"

            limit_param = idx
            params.append(limit + 1)
            idx += 1

            query = f"""
                SELECT
                    id, fournisseur, designation_raw, designation_fr,
                    famille, unite,
                    prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,
                    numero_facture, date_facture, confidence, source,
                    updated_at,
                    {score_col}
                FROM produits
                {where}
                ORDER BY {order_clause}
                LIMIT ${limit_param}
            """

            rows = await conn.fetch(query, *params)

            has_more    = len(rows) > limit
            items       = rows[:limit]
            next_cursor = items[-1]["updated_at"].isoformat() if has_more and items else None

            count_where_conditions = []
            count_params_clean: list[Any] = []
            cidx = 1
            if famille and famille != "Toutes":
                count_where_conditions.append(f"famille = ${cidx}")
                count_params_clean.append(famille)
                cidx += 1
            if fournisseur:
                count_where_conditions.append(f"fournisseur ILIKE ${cidx}")
                count_params_clean.append(f"%{fournisseur}%")
                cidx += 1
            if search and search.strip():
                count_where_conditions.append(
                    f"(designation_raw ILIKE ${cidx} OR designation_fr ILIKE ${cidx})"
                )
                count_params_clean.append(f"%{search.strip()}%")
                cidx += 1

            count_where = ("WHERE " + " AND ".join(count_where_conditions)) if count_where_conditions else ""
            total = await conn.fetchval(f"SELECT COUNT(*) FROM produits {count_where}", *count_params_clean)

            return {
                "products":    [dict(r) for r in items],
                "next_cursor": next_cursor,
                "has_more":    has_more,
                "total":       total,
            }

    @classmethod
    async def get_stats(cls) -> dict:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT
                    COUNT(*)                                    AS total_produits,
                    COUNT(DISTINCT fournisseur)                 AS total_fournisseurs,
                    COUNT(DISTINCT famille)                     AS total_familles,
                    COUNT(*) FILTER (WHERE confidence = 'low')  AS low_confidence,
                    COUNT(*) FILTER (WHERE source = 'mobile')   AS depuis_mobile,
                    COUNT(*) FILTER (WHERE updated_at > NOW() - INTERVAL '7 days') AS cette_semaine
                FROM produits
            """)

            familles = await conn.fetch("""
                SELECT famille, COUNT(*) AS nb
                FROM produits
                WHERE famille IS NOT NULL
                GROUP BY famille
                ORDER BY nb DESC
            """)

            return {
                **dict(stats),
                "familles": [dict(f) for f in familles]
            }

    @classmethod
    async def get_factures_history(cls, limit: int = 50) -> list[dict]:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, filename, statut, nb_produits_extraits,
                       cout_api_usd, modele_ia, source, pdf_url, created_at
                FROM factures
                ORDER BY created_at DESC
                LIMIT $1
            """, limit)
            return [dict(r) for r in rows]

    @classmethod
    async def log_facture(
        cls,
        filename:    str,
        statut:      str,
        nb_produits: int,
        cout_usd:    float,
        modele_ia:   str,
        source:      str = "pc",
        pdf_url:     str = None,
    ) -> int:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO factures
                    (filename, statut, nb_produits_extraits, cout_api_usd, modele_ia, source, pdf_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, filename, statut, nb_produits, cout_usd, modele_ia, source, pdf_url)
            return row["id"]

    @classmethod
    async def create_job(cls, job_id: str, status: str = "processing") -> None:
        """Crée un job en base pour persistance."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO jobs (job_id, status)
                VALUES ($1::uuid, $2)
            """, job_id, status)

    @classmethod
    async def update_job(
        cls,
        job_id: str,
        status: str,
        result: dict | None = None,
        error: str | None = None,
    ) -> None:
        """Met à jour le statut et le résultat d'un job."""
        pool = await cls.get_pool()
        result_json = json.dumps(result) if result is not None else None
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE jobs
                SET status = $2, result = $3::jsonb, error = $4, updated_at = NOW()
                WHERE job_id = $1::uuid
            """, job_id, status, result_json, error)

    @classmethod
    async def get_job(cls, job_id: str) -> dict | None:
        """Récupère un job par son id. Retourne None si introuvable."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT status, result, error, created_at, updated_at
                FROM jobs
                WHERE job_id = $1::uuid
            """, job_id)
            if not row:
                return None
            result = row["result"]
            if isinstance(result, str):
                result = json.loads(result) if result else None
            return {
                "status": row["status"],
                "result": result,
                "error": row["error"],
            }

    @classmethod
    async def truncate_products(cls) -> int:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE produits RESTART IDENTITY")
            return 0

    @classmethod
    async def get_fournisseurs(cls) -> list[str]:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT DISTINCT fournisseur FROM produits ORDER BY fournisseur"
            )
            return [r["fournisseur"] for r in rows]
    @classmethod
    async def compare_prices(cls, search: str) -> list[dict]:
        """Compare les prix d'un produit entre fournisseurs."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    id,
                    fournisseur,
                    designation_fr,
                    prix_remise_ht,
                    prix_brut_ht,
                    remise_pct,
                    unite,
                    numero_facture,
                    date_facture,
                    updated_at
                FROM produits
                WHERE designation_fr ILIKE $1
                   OR designation_raw ILIKE $1
                   OR similarity(designation_fr, $2) > 0.3
                ORDER BY prix_remise_ht ASC
                LIMIT 20
            """, f"%{search}%", search)
            return [dict(r) for r in rows]

    @classmethod
    async def get_price_history_by_product_id(cls, product_id: int) -> list[dict]:
        """Historique de prix depuis prix_historique pour un produit."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT prix_ht, prix_brut, remise_pct, recorded_at
                FROM prix_historique
                WHERE produit_id = $1
                ORDER BY recorded_at ASC
                LIMIT 20
            """, product_id)
            return [dict(r) for r in rows]

    @classmethod
    async def compare_prices_with_history(cls, search: str) -> list[dict]:
        """
        Compare prices + batch-load history in 2 queries (fixes N+1).
        Returns products with an embedded 'price_history' list.
        """
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            products = await conn.fetch("""
                SELECT
                    id, fournisseur, designation_fr,
                    prix_remise_ht, prix_brut_ht, remise_pct,
                    unite, numero_facture, date_facture, updated_at
                FROM produits
                WHERE designation_fr ILIKE $1
                   OR designation_raw ILIKE $1
                   OR similarity(designation_fr, $2) > 0.3
                ORDER BY prix_remise_ht ASC
                LIMIT 20
            """, f"%{search}%", search)

            if not products:
                return []

            product_ids = [r["id"] for r in products]

            hist_rows = await conn.fetch("""
                SELECT produit_id, prix_ht, prix_brut, remise_pct, recorded_at
                FROM prix_historique
                WHERE produit_id = ANY($1::int[])
                ORDER BY recorded_at ASC
            """, product_ids)

            hist_by_id: dict[int, list[dict]] = {}
            for h in hist_rows:
                d = dict(h)
                pid = d.pop("produit_id")
                hist_by_id.setdefault(pid, []).append(d)

            result = []
            for r in products:
                d = dict(r)
                d["price_history"] = hist_by_id.get(d["id"], [])
                result.append(d)
            return result