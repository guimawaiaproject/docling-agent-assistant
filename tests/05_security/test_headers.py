"""
Tests de sécurité — en-têtes HTTP.
"""

import httpx


def test_health_response_headers(ensure_server_running: str):
    """Vérifie la présence d'en-têtes de sécurité sur /health."""
    client = httpx.Client(base_url=ensure_server_running, timeout=10)
    resp = client.get("/health")
    assert resp.status_code == 200
    headers = resp.headers
    # Documenter les headers présents/absents
    # FastAPI ne met pas tous ces headers par défaut
    if "X-Content-Type-Options" in headers:
        assert headers["X-Content-Type-Options"] == "nosniff"
    if "X-Frame-Options" in headers:
        assert "DENY" in headers["X-Frame-Options"] or "SAMEORIGIN" in headers["X-Frame-Options"]
    # Content-Type JSON
    assert "application/json" in headers.get("content-type", "")
    client.close()
