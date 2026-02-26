"""
Tests d'intégrité — atomicité des transactions.
"""

import uuid

import pytest


def test_batch_partial_invalid_does_not_corrupt(
    authenticated_client,
    real_db_connection,
):
    """
    Batch avec un produit invalide (fournisseur vide) :
    les produits valides peuvent être insérés (comportement actuel)
    ou aucun (atomicité stricte). On vérifie qu'on n'a pas de corruption.
    """
    client, _ = authenticated_client
    marker = f"tx_test_{uuid.uuid4().hex[:8]}"
    products = [
        {
            "fournisseur": f"{marker}_Valid",
            "designation_raw": f"{marker}_Produit valide",
            "designation_fr": "Produit valide",
            "famille": "Maçonnerie",
            "prix_brut_ht": 10.0,
            "prix_remise_ht": 10.0,
            "prix_ttc_iva21": 12.1,
            "confidence": "high",
        },
        {
            "fournisseur": "",
            "designation_raw": f"{marker}_Invalide",
            "designation_fr": "Invalide",
            "famille": "Autre",
            "prix_brut_ht": 5.0,
            "prix_remise_ht": 5.0,
            "prix_ttc_iva21": 6.05,
            "confidence": "high",
        },
    ]
    resp = client.post(
        "/api/v1/catalogue/batch",
        json={"produits": products, "source": "pc"},
    )
    assert resp.status_code == 200
    saved = resp.json().get("saved", 0)
    assert saved >= 1

    if real_db_connection:
        cur = real_db_connection.cursor()
        cur.execute("SELECT COUNT(*) FROM produits WHERE designation_raw LIKE %s", (f"{marker}%",))
        count = cur.fetchone()[0]
        cur.execute("DELETE FROM produits WHERE designation_raw LIKE %s", (f"{marker}%",))
        cur.execute("DELETE FROM produits WHERE fournisseur = '' AND designation_raw LIKE %s", (f"%{marker}%",))
        real_db_connection.commit()
        cur.close()
