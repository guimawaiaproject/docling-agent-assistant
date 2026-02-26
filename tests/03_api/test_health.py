"""
Tests API — endpoints racine et health.
"""

import httpx


def test_root(http_client: httpx.Client):
    resp = http_client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert "Docling" in data["message"]
    assert "docs" in data
    assert "version" in data


def test_health(http_client: httpx.Client):
    resp = http_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
