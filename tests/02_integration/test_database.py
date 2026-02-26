"""
Tests d'intégration base de données réelle — zéro mock.
Connexion PostgreSQL réelle, CRUD via DBManager.
"""

import os
import uuid

import pytest

# Utiliser la même DB que l'API pour les tests
_db_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")


@pytest.fixture
def db_url():
    if not _db_url:
        pytest.skip("TEST_DATABASE_URL ou DATABASE_URL non défini")
    return _db_url


@pytest.mark.asyncio
async def test_upsert_products_batch_real_db(
    real_db_connection,
    sample_products,
):
    """
    Connexion réelle : création de produits via DBManager.upsert_products_batch,
    vérification en DB directe.
    """
    from backend.core.db_manager import DBManager

    # Marquer les produits pour cleanup
    marker = f"test_{uuid.uuid4().hex[:8]}"
    for p in sample_products:
        p["fournisseur"] = f"{marker}_{p['fournisseur'][:30]}"
        p["designation_raw"] = f"{marker}_{p['designation_raw'][:50]}"
        p["designation_fr"] = f"{marker}_{p['designation_fr'][:50]}"

    # S'assurer que le pool utilise la bonne URL
    if not os.getenv("DATABASE_URL") and os.getenv("TEST_DATABASE_URL"):
        os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

    try:
        pool = await DBManager.get_pool()
    except RuntimeError:
        pytest.skip("DATABASE_URL non définie")

    nb_saved, _ = await DBManager.upsert_products_batch(
        sample_products,
        source="pc",
    )
    assert nb_saved == len(sample_products), f"Attendu {len(sample_products)} sauvegardés, obtenu {nb_saved}"

    # Vérification directe en DB via psycopg2
    conn = real_db_connection
    cur = conn.cursor()
    cur.execute(
        "SELECT id, fournisseur, designation_fr, prix_remise_ht FROM produits WHERE fournisseur LIKE %s",
        (f"{marker}%",),
    )
    rows = cur.fetchall()
    assert len(rows) == len(sample_products), f"Produits non trouvés en DB : {rows}"

    for row, expected in zip(rows, sample_products):
        assert row[1] == expected["fournisseur"]
        assert row[2] == expected["designation_fr"]
        assert float(row[3]) == expected["prix_remise_ht"]

    # Cleanup
    cur.execute("DELETE FROM produits WHERE fournisseur LIKE %s", (f"{marker}%",))
    conn.commit()
    cur.close()


@pytest.mark.asyncio
async def test_db_connection_and_simple_query(real_db_connection):
    """Vérifie que la connexion DB fonctionne et que les tables existent."""
    cur = real_db_connection.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('produits', 'factures', 'users')"
    )
    tables = [r[0] for r in cur.fetchall()]
    assert "produits" in tables
    cur.close()
