"""
Tests d'intégrité — contrainte UNIQUE(designation_raw, fournisseur).
"""

import uuid


def test_upsert_same_product_no_duplicate(
    authenticated_client,
    real_db_connection,
):
    """Deux batchs avec même (designation_raw, fournisseur) → upsert, pas de doublon."""
    client, _ = authenticated_client
    marker = f"uniq_{uuid.uuid4().hex[:8]}"
    product = {
        "fournisseur": f"{marker}_Fournisseur",
        "designation_raw": f"{marker}_CIMENT 42.5R",
        "designation_fr": "Ciment 42.5R",
        "famille": "Maçonnerie",
        "prix_brut_ht": 12.50,
        "remise_pct": 10.0,
        "prix_remise_ht": 11.25,
        "prix_ttc_iva21": 13.61,
        "confidence": "high",
    }

    resp1 = client.post("/api/v1/catalogue/batch", json={"produits": [product], "source": "pc"})
    assert resp1.status_code == 200
    assert resp1.json().get("saved", 0) >= 1

    product["prix_remise_ht"] = 11.50
    product["prix_ttc_iva21"] = 13.92
    resp2 = client.post("/api/v1/catalogue/batch", json={"produits": [product], "source": "pc"})
    assert resp2.status_code == 200

    if real_db_connection:
        cur = real_db_connection.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM produits WHERE fournisseur = %s AND designation_raw = %s",
            (product["fournisseur"], product["designation_raw"]),
        )
        count = cur.fetchone()[0]
        assert count == 1, f"Doublon détecté : {count} enregistrements"
        cur.execute("DELETE FROM produits WHERE fournisseur = %s", (product["fournisseur"],))
        real_db_connection.commit()
        cur.close()
