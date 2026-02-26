"""
Tests d'intégrité — cohérence API ↔ DB.
"""

import uuid

import pytest


def test_batch_then_catalogue_matches_db(
    authenticated_client,
    real_db_connection,
):
    """Création via batch → GET catalogue → données identiques à la DB."""
    client, _ = authenticated_client
    marker = f"coh_{uuid.uuid4().hex[:8]}"
    product = {
        "fournisseur": f"{marker}_Fournisseur",
        "designation_raw": f"{marker}_Produit cohérence",
        "designation_fr": "Produit test cohérence",
        "famille": "Plomberie",
        "unite": "m",
        "prix_brut_ht": 25.50,
        "remise_pct": 5.0,
        "prix_remise_ht": 24.23,
        "prix_ttc_iva21": 29.32,
        "confidence": "high",
    }

    resp = client.post("/api/v1/catalogue/batch", json={"produits": [product], "source": "pc"})
    assert resp.status_code == 200

    cat = client.get("/api/v1/catalogue", params={"fournisseur": product["fournisseur"]})
    assert cat.status_code == 200
    products = cat.json().get("products", [])
    found = [p for p in products if p.get("fournisseur") == product["fournisseur"]]
    assert len(found) >= 1
    api_product = found[0]

    assert api_product["designation_fr"] == product["designation_fr"]
    assert float(api_product["prix_remise_ht"]) == product["prix_remise_ht"]
    assert api_product["famille"] == product["famille"]

    if real_db_connection:
        cur = real_db_connection.cursor()
        cur.execute(
            "SELECT designation_fr, prix_remise_ht, famille FROM produits WHERE fournisseur = %s",
            (product["fournisseur"],),
        )
        row = cur.fetchone()
        assert row is not None
        assert row[0] == product["designation_fr"]
        assert float(row[1]) == product["prix_remise_ht"]
        assert row[2] == product["famille"]
        cur.execute("DELETE FROM produits WHERE fournisseur = %s", (product["fournisseur"],))
        real_db_connection.commit()
        cur.close()
