"""
Tests API — stats, history.
"""

import httpx


def test_stats_structure(http_client: httpx.Client):
    resp = http_client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_produits" in data
    assert "total_fournisseurs" in data
    assert "total_familles" in data or "familles" in data


def test_history_structure(http_client: httpx.Client):
    resp = http_client.get("/api/v1/history", params={"limit": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert "history" in data
    assert "total" in data
    assert isinstance(data["history"], list)


def test_history_limit_max_200(http_client: httpx.Client):
    resp = http_client.get("/api/v1/history", params={"limit": 500})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["history"]) <= 200


def test_history_pdf_404_for_invalid_id(http_client: httpx.Client):
    resp = http_client.get("/api/v1/history/999999999/pdf")
    assert resp.status_code == 404
