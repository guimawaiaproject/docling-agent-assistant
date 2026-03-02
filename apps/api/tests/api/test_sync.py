"""
Tests API — statut sync watchdog.
"""

import httpx


def test_sync_status_structure(http_client: httpx.Client):
    resp = http_client.get("/api/v1/sync/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "active" in data or "folder" in data or "last_file" in data
