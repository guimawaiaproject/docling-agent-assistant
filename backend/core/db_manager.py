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
import re
from datetime import date, datetime
from typing import Any, Optional

import asyncpg

from backend.core.config import Config

logger = logging.getLogger(__name__)

_UPSERT_SQL = """
    INSERT INTO produits (
        user_id, fournisseur, designation_raw, designation_fr,
        famille, unite,
        prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,
        numero_facture, date_facture, confidence, source
    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
    ON CONFLICT (designation_raw, fournisseur, user_id)
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


def _escape_like(term: str) -> str:
    """Échappe % et _ pour usage dans ILIKE (PostgreSQL). Utiliser avec ESCAPE '\\'."""
    if not term:
        return term
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Convertit en float sans lever d'exception. Gère "12,50", "€45", "N/A", etc."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.upper() in ("N/A", "NA", "-", ""):
        return default
    s = re.sub(r"[€$£\s]", "", s)
    s = s.replace(",", ".")
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    """Convertit en int sans lever d'exception. Gère "12", "N/A", "€45", etc."""
    if val is None:
        return default
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val) if val == val else default  # NaN check
    s = str(val).strip()
    if not s or s.upper() in ("N/A", "NA", "-", ""):
        return default
    s = re.sub(r"[€$£\s]", "", s)
    s = s.replace(",", ".")
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default


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


def _upsert_params(product: dict, source: str, user_id: int | None) -> tuple:
    return (
        user_id,
        product.get("fournisseur", ""),
        product.get("designation_raw", ""),
        product.get("designation_fr", ""),
        product.get("famille", "Autre"),
        product.get("unite", "unit\u00e9"),
        _safe_float(product.get("prix_brut_ht")),
        _safe_float(product.get("remise_pct")),
        _safe_float(product.get("prix_remise_ht")),
        _safe_float(product.get("prix_ttc_iva21")),
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
        """Exécute les migrations Alembic. Les schémas sont versionnés dans migrations/versions/."""
        import asyncio
        import os

        def _run_alembic_upgrade() -> None:
            from alembic import command
            from alembic.config import Config
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config = Config(os.path.join(root, "alembic.ini"))
            command.upgrade(config, "head")

        await asyncio.to_thread(_run_alembic_upgrade)
        logger.info("Migrations Alembic OK")

    @classmethod
    async def upsert_product(
        cls, product: dict, source: str = "pc", user_id: int | None = None
    ) -> bool:
        """Upsert un seul produit. Délègue au batch."""
        count, _ = await cls.upsert_products_batch([product], source=source, user_id=user_id)
        return count > 0

    @classmethod
    async def upsert_products_batch(
        cls, products: list[dict], source: str = "pc", user_id: int | None = None
    ) -> tuple[int, int]:
        """Insère/met à jour une liste de produits. Retourne (count, historique_failures)."""
        pool = await cls.get_pool()
        count = 0
        historique_failures = 0
        async with pool.acquire() as conn:
            async with conn.transaction():
                for product in products:
                    try:
                        result = await conn.fetchrow(
                            _UPSERT_SQL + " RETURNING id",
                            *_upsert_params(product, source, user_id)
                        )
                        count += 1
                        if result and _safe_float(product.get("prix_remise_ht")) > 0:
                            try:
                                await conn.execute("""
                                    INSERT INTO prix_historique
                                        (produit_id, fournisseur, designation_fr, prix_ht, prix_brut, remise_pct)
                                    VALUES ($1, $2, $3, $4, $5, $6)
                                """,
                                    result["id"],
                                    product.get("fournisseur", ""),
                                    product.get("designation_fr", ""),
                                    _safe_float(product.get("prix_remise_ht")),
                                    _safe_float(product.get("prix_brut_ht")),
                                    _safe_float(product.get("remise_pct")),
                                )
                            except Exception as e:
                                historique_failures += 1
                                logger.warning(
                                    "Erreur insertion prix_historique produit_id=%s designation=%s: %s",
                                    result["id"],
                                    product.get("designation_raw", ""),
                                    e,
                                    exc_info=True,
                                )
                    except Exception as e:
                        logger.warning(f"Upsert ignor\u00e9 pour {product.get('designation_raw')}: {e}")
        return count, historique_failures

    @classmethod
    async def get_catalogue(
        cls,
        famille:     Optional[str] = None,
        fournisseur: Optional[str] = None,
        search:      Optional[str] = None,
        limit:       int = 50,
        cursor:      Optional[str] = None,
        user_id:     int | None = None,
    ) -> dict[str, Any]:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:

            conditions = []
            params: list[Any] = []
            idx = 1

            if user_id is not None:
                conditions.append(f"user_id = ${idx}")
                params.append(user_id)
                idx += 1

            if cursor:
                conditions.append(f"updated_at < ${idx}::timestamptz")
                params.append(cursor)
                idx += 1

            if famille and famille != "Toutes":
                conditions.append(f"famille = ${idx}")
                params.append(famille)
                idx += 1

            if fournisseur:
                conditions.append(f"fournisseur ILIKE ${idx} ESCAPE E'\\\\'")
                params.append(f"%{_escape_like(fournisseur)}%")
                idx += 1

            if search and search.strip():
                s = search.strip()
                s_escaped = _escape_like(s)
                conditions.append(f"""(
                    designation_raw ILIKE ${idx} ESCAPE E'\\\\'
                    OR designation_fr   ILIKE ${idx} ESCAPE E'\\\\'
                    OR fournisseur      ILIKE ${idx} ESCAPE E'\\\\'
                    OR similarity(designation_raw, ${idx+1}) > 0.2
                    OR similarity(designation_fr,  ${idx+1}) > 0.2
                )""")
                params.append(f"%{s_escaped}%")
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
            if user_id is not None:
                count_where_conditions.append(f"user_id = ${cidx}")
                count_params_clean.append(user_id)
                cidx += 1
            if famille and famille != "Toutes":
                count_where_conditions.append(f"famille = ${cidx}")
                count_params_clean.append(famille)
                cidx += 1
            if fournisseur:
                count_where_conditions.append(f"fournisseur ILIKE ${cidx} ESCAPE E'\\\\'")
                count_params_clean.append(f"%{_escape_like(fournisseur)}%")
                cidx += 1
            if search and search.strip():
                count_where_conditions.append(
                    f"(designation_raw ILIKE ${cidx} ESCAPE E'\\\\' OR designation_fr ILIKE ${cidx} ESCAPE E'\\\\')"
                )
                count_params_clean.append(f"%{_escape_like(search.strip())}%")
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
    async def get_stats(cls, user_id: int | None = None) -> dict:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            where = "WHERE user_id = $1" if user_id is not None else ""
            params = (user_id,) if user_id is not None else ()
            stats = await conn.fetchrow(f"""
                SELECT
                    COUNT(*)                                    AS total_produits,
                    COUNT(DISTINCT fournisseur)                 AS total_fournisseurs,
                    COUNT(DISTINCT famille)                     AS total_familles,
                    COUNT(*) FILTER (WHERE confidence = 'low')  AS low_confidence,
                    COUNT(*) FILTER (WHERE source = 'mobile')   AS depuis_mobile,
                    COUNT(*) FILTER (WHERE updated_at > NOW() - INTERVAL '7 days') AS cette_semaine
                FROM produits
                {where}
            """, *params)

            fam_where = "AND user_id = $1" if user_id is not None else ""
            fam_params = (user_id,) if user_id is not None else ()
            familles = await conn.fetch(f"""
                SELECT famille, COUNT(*) AS nb
                FROM produits
                WHERE famille IS NOT NULL {fam_where}
                GROUP BY famille
                ORDER BY nb DESC
            """, *fam_params)

            return {
                **dict(stats),
                "familles": [dict(f) for f in familles]
            }

    @classmethod
    async def get_factures_history(
        cls, limit: int = 50, user_id: int | None = None
    ) -> list[dict]:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            if user_id is not None:
                rows = await conn.fetch("""
                    SELECT id, filename, statut, nb_produits_extraits,
                           cout_api_usd, modele_ia, source, pdf_url, created_at
                    FROM factures
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, user_id, limit)
            else:
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
        user_id:     int | None = None,
    ) -> int:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO factures
                    (filename, statut, nb_produits_extraits, cout_api_usd, modele_ia, source, pdf_url, user_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, filename, statut, nb_produits, cout_usd, modele_ia, source, pdf_url, user_id)
            return row["id"]

    @classmethod
    async def create_job(
        cls, job_id: str, status: str = "processing", user_id: int | None = None
    ) -> None:
        """Crée un job en base pour persistance. user_id requis pour isolation multi-tenant."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO jobs (job_id, status, user_id)
                VALUES ($1::uuid, $2, $3)
            """, job_id, status, user_id)

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
    async def get_job(cls, job_id: str, user_id: int | None = None) -> dict | None:
        """Récupère un job par son id. Filtre par user_id pour isolation multi-tenant."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT status, result, error, created_at, updated_at
                FROM jobs
                WHERE job_id = $1::uuid AND user_id = $2
            """, job_id, user_id)
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
    async def truncate_products(cls, user_id: int | None = None) -> int:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            if user_id is not None:
                result = await conn.execute(
                    "DELETE FROM produits WHERE user_id = $1", user_id
                )
                return int(result.split()[-1]) if result else 0
            await conn.execute("TRUNCATE TABLE produits RESTART IDENTITY")
            return 0

    @classmethod
    async def get_facture_pdf_url(
        cls, facture_id: int, user_id: int | None = None
    ) -> str | None:
        """Retourne pdf_url si la facture existe et appartient à l'utilisateur."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            if user_id is not None:
                row = await conn.fetchrow(
                    "SELECT pdf_url FROM factures WHERE id = $1 AND user_id = $2",
                    facture_id,
                    user_id,
                )
            else:
                row = await conn.fetchrow(
                    "SELECT pdf_url FROM factures WHERE id = $1", facture_id
                )
            return row["pdf_url"] if row and row["pdf_url"] else None

    @classmethod
    async def get_fournisseurs(cls, user_id: int | None = None) -> list[str]:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            if user_id is not None:
                rows = await conn.fetch(
                    "SELECT DISTINCT fournisseur FROM produits WHERE user_id = $1 ORDER BY fournisseur",
                    user_id,
                )
            else:
                rows = await conn.fetch(
                    "SELECT DISTINCT fournisseur FROM produits ORDER BY fournisseur"
                )
            return [r["fournisseur"] for r in rows]
    @classmethod
    async def compare_prices(
        cls, search: str, user_id: int | None = None
    ) -> list[dict]:
        """Compare les prix d'un produit entre fournisseurs."""
        pool = await cls.get_pool()
        search_escaped = f"%{_escape_like(search)}%"
        async with pool.acquire() as conn:
            user_clause = "AND user_id = $3" if user_id is not None else ""
            params: tuple = (search_escaped, search, user_id) if user_id is not None else (search_escaped, search)
            rows = await conn.fetch(f"""
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
                WHERE (designation_fr ILIKE $1 ESCAPE E'\\\\'
                   OR designation_raw ILIKE $1 ESCAPE E'\\\\'
                   OR similarity(designation_fr, $2) > 0.3) {user_clause}
                ORDER BY prix_remise_ht ASC
                LIMIT 20
            """, *params)
            return [dict(r) for r in rows]

    @classmethod
    async def get_price_history_by_product_id(
        cls, product_id: int, user_id: int | None = None
    ) -> list[dict]:
        """Historique de prix depuis prix_historique pour un produit."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            if user_id is not None:
                rows = await conn.fetch("""
                    SELECT ph.prix_ht, ph.prix_brut, ph.remise_pct, ph.recorded_at
                    FROM prix_historique ph
                    JOIN produits p ON p.id = ph.produit_id AND p.user_id = $2
                    WHERE ph.produit_id = $1
                    ORDER BY ph.recorded_at ASC
                    LIMIT 20
                """, product_id, user_id)
            else:
                rows = await conn.fetch("""
                    SELECT prix_ht, prix_brut, remise_pct, recorded_at
                    FROM prix_historique
                    WHERE produit_id = $1
                    ORDER BY recorded_at ASC
                    LIMIT 20
                """, product_id)
            return [dict(r) for r in rows]

    @classmethod
    async def compare_prices_with_history(
        cls, search: str, user_id: int | None = None
    ) -> list[dict]:
        """
        Compare prices + batch-load history in 2 queries (fixes N+1).
        Returns products with an embedded 'price_history' list.
        """
        pool = await cls.get_pool()
        search_escaped = f"%{_escape_like(search)}%"
        async with pool.acquire() as conn:
            user_clause = "AND user_id = $3" if user_id is not None else ""
            params: tuple = (search_escaped, search, user_id) if user_id is not None else (search_escaped, search)
            products = await conn.fetch(f"""
                SELECT
                    id, fournisseur, designation_fr,
                    prix_remise_ht, prix_brut_ht, remise_pct,
                    unite, numero_facture, date_facture, updated_at
                FROM produits
                WHERE (designation_fr ILIKE $1 ESCAPE E'\\\\'
                   OR designation_raw ILIKE $1 ESCAPE E'\\\\'
                   OR similarity(designation_fr, $2) > 0.3) {user_clause}
                ORDER BY prix_remise_ht ASC
                LIMIT 20
            """, *params)

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
