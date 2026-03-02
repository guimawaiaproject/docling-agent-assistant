"""
CommunityService — Base prix communautaire anonyme
Collecte et agrégation des prix avec k-anonymité.
"""

import hashlib
import logging
import re
import unicodedata
from typing import Any

import asyncpg

from core.config import Config
from core.db_manager import _escape_like

logger = logging.getLogger(__name__)

K_ANONYMITY_MIN = 5


def _normalize(s: str) -> str:
    """Normalise pour regroupement : minuscules, trim, suppression accents."""
    if not s:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s)
    return s


def _hash_produit(designation: str, fournisseur: str) -> str:
    """Hash irréversible pour regroupement anonyme."""
    salt = Config.COMMUNITY_SALT or "docling-default-salt"
    norm = _normalize(designation or "") + "|" + _normalize(fournisseur or "")
    return hashlib.sha256((salt + norm).encode()).hexdigest()


class CommunityService:
    @classmethod
    async def insert_anonymous_price(
        cls,
        conn: asyncpg.Connection,
        designation: str,
        fournisseur: str,
        zone_geo: str,
        pays: str,
        prix_ht: float,
        date_facture: str | None,
    ) -> bool:
        """Insère un prix anonyme si COMMUNITY_SALT configuré."""
        if not Config.COMMUNITY_SALT:
            return False
        if not zone_geo or not pays or len(pays) != 2:
            return False
        try:
            ph = _hash_produit(designation, fournisseur)
            await conn.execute(
                """
                INSERT INTO prix_anonymes (produit_hash, fournisseur, zone_geo, pays, prix_ht, date_facture)
                VALUES ($1, $2, $3, $4, $5, $6::date)
                """,
                ph,
                (fournisseur or "")[:200],
                zone_geo[:10],
                pays[:2],
                prix_ht,
                date_facture,
            )
            return True
        except Exception as e:
            logger.warning("Community insert failed: %s", e)
            return False

    @classmethod
    async def get_stats(
        cls,
        zone: str | None = None,
        pays: str | None = None,
        fournisseur: str | None = None,
        search: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Agrégats avec k-anonymité (COUNT >= 5)."""
        pool = await cls._get_pool()
        conditions = []
        params: list[Any] = []
        idx = 1
        if zone:
            conditions.append(f"p.zone_geo = ${idx}")
            params.append(zone)
            idx += 1
        if pays:
            conditions.append(f"p.pays = ${idx}")
            params.append(pays[:2])
            idx += 1
        if fournisseur:
            conditions.append(f"p.fournisseur ILIKE ${idx} ESCAPE E'\\\\'")
            params.append(f"%{_escape_like(fournisseur)}%")
            idx += 1
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        having_idx = idx
        limit_idx = idx + 1
        params.extend([K_ANONYMITY_MIN, limit])

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                WITH agg AS (
                    SELECT
                        produit_hash,
                        fournisseur,
                        zone_geo,
                        pays,
                        AVG(prix_ht) AS prix_moyen,
                        MIN(prix_ht) AS prix_min,
                        MAX(prix_ht) AS prix_max,
                        COUNT(*) AS cnt
                    FROM prix_anonymes p
                    {where}
                    GROUP BY produit_hash, fournisseur, zone_geo, pays
                    HAVING COUNT(*) >= ${having_idx}
                )
                SELECT produit_hash, fournisseur, zone_geo, pays,
                       prix_moyen, prix_min, prix_max, cnt AS nb_contributions
                FROM agg
                ORDER BY nb_contributions DESC
                LIMIT ${limit_idx}
                """,
                *params,
            )
        return [dict(r) for r in rows]

    @classmethod
    async def _get_pool(cls):
        from core.db_manager import DBManager
        return await DBManager.get_pool()
