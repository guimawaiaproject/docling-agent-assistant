"""
Tests API — catalogue, batch, fournisseurs, compare, price-history.
"""

import uuid

import httpx
from faker import Faker

fake = Faker("fr_FR")


def test_catalogue_structure(http_client: httpx.Client):
    resp = http_client.get("/api/v1/catalogue")
    assert resp.status_code == 200
    data = resp.json()
    assert "products" in data
    assert "next_cursor" in data or "has_more" in data or "total" in data
    assert isinstance(data["products"], list)


def test_catalogue_with_filters(http_client: httpx.Client):
    resp = http_client.get(
        "/api/v1/catalogue",
        params={"famille": "Maçonnerie", "limit": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "products" in data
    for p in data["products"]:
        assert p.get("famille") == "Maçonnerie"


def test_catalogue_pagination_cursor(http_client: httpx.Client):
    resp1 = http_client.get("/api/v1/catalogue", params={"limit": 2})
    assert resp1.status_code == 200
    data1 = resp1.json()
    products1 = data1.get("products", [])
    if len(products1) < 2:
        return
    cursor = data1.get("next_cursor")
    if cursor:
        resp2 = http_client.get(
            "/api/v1/catalogue",
            params={"limit": 2, "cursor": cursor},
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        ids1 = {p["id"] for p in products1}
        ids2 = {p["id"] for p in data2.get("products", [])}
        assert ids1.isdisjoint(ids2)


def test_batch_save_and_verify_in_catalogue(
    authenticated_client,
    real_db_connection,
):
    client, _ = authenticated_client
    marker = f"batch_test_{uuid.uuid4().hex[:8]}"
    products = [
        {
            "fournisseur": f"{marker}_Fournisseur",
            "designation_raw": f"{marker}_CIMENT 42.5R",
            "designation_fr": f"{marker}_Ciment 42.5R",
            "famille": "Maçonnerie",
            "unite": "sac",
            "prix_brut_ht": 12.50,
            "remise_pct": 10.0,
            "prix_remise_ht": 11.25,
            "prix_ttc_iva21": 13.61,
            "confidence": "high",
        },
    ]
    resp = client.post(
        "/api/v1/catalogue/batch",
        json={"produits": products, "source": "pc"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("saved", 0) >= 1
    assert body.get("total") == 1

    # Vérifier en DB
    if real_db_connection:
        cur = real_db_connection.cursor()
        cur.execute(
            "SELECT designation_fr, prix_remise_ht FROM produits WHERE fournisseur = %s",
            (f"{marker}_Fournisseur",),
        )
        row = cur.fetchone()
        assert row is not None
        assert marker in row[0]
        assert float(row[1]) == 11.25
        cur.execute("DELETE FROM produits WHERE fournisseur = %s", (f"{marker}_Fournisseur",))
        real_db_connection.commit()
        cur.close()


def test_fournisseurs_structure(http_client: httpx.Client):
    resp = http_client.get("/api/v1/catalogue/fournisseurs")
    assert resp.status_code == 200
    data = resp.json()
    assert "fournisseurs" in data
    assert isinstance(data["fournisseurs"], list)


def test_compare_search_too_short_400(http_client: httpx.Client):
    resp = http_client.get("/api/v1/catalogue/compare", params={"search": "a"})
    assert resp.status_code == 400


def test_compare_search_ok(http_client: httpx.Client):
    resp = http_client.get(
        "/api/v1/catalogue/compare",
        params={"search": "ciment", "with_history": "false"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert "search" in data


def test_price_history_404_for_invalid_id(http_client: httpx.Client):
    resp = http_client.get("/api/v1/catalogue/price-history/999999999")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert resp.json().get("history") == []
