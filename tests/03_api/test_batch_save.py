"""
Tests API — validation batch save (limite produits, prix négatif).
"""


def test_batch_save_too_many_products_422(authenticated_client):
    """BatchSave avec trop de produits (> 500) → 422 avec message clair."""
    client, _ = authenticated_client
    products = [
        {
            "fournisseur": f"Fournisseur_{i}",
            "designation_raw": f"Prod {i}",
            "designation_fr": f"Produit {i}",
        }
        for i in range(501)
    ]
    resp = client.post(
        "/api/v1/catalogue/batch",
        json={"produits": products, "source": "pc"},
    )
    assert resp.status_code == 422


def test_batch_save_missing_required_fields_422(authenticated_client):
    """BatchSave avec champs requis manquants → 422."""
    client, _ = authenticated_client
    products = [
        {
            "fournisseur": "TestFournisseur",
            "designation_raw": "CIMENT 42.5R",
            # designation_fr manquant
        }
    ]
    resp = client.post(
        "/api/v1/catalogue/batch",
        json={"produits": products, "source": "pc"},
    )
    assert resp.status_code == 422
