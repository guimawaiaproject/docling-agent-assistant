"""
Tests API — reset catalogue (admin uniquement).
"""

import httpx


def test_reset_without_confirm_400(http_client: httpx.Client):
    resp = http_client.delete("/api/v1/catalogue/reset")
    assert resp.status_code in (400, 403)


def test_reset_without_admin_token_403(ensure_server_running: str, unique_user: dict):
    """Sans token admin, même avec confirm → 403."""
    client = httpx.Client(base_url=ensure_server_running, timeout=30)
    client.post(
        "/api/v1/auth/register",
        data={
            "email": unique_user["email"],
            "password": unique_user["password"],
            "name": unique_user.get("name", ""),
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        data={"email": unique_user["email"], "password": unique_user["password"]},
    )
    token = login.json().get("token")
    client.headers["Authorization"] = f"Bearer {token}"
    resp = client.delete(
        "/api/v1/catalogue/reset",
        params={"confirm": "SUPPRIMER_TOUT"},
    )
    assert resp.status_code == 403
    client.close()


def test_reset_with_confirm_but_no_token_400(ensure_server_running: str):
    """Confirm sans token → 400 (manque confirm) ou 403."""
    client = httpx.Client(base_url=ensure_server_running, timeout=30)
    resp = client.delete(
        "/api/v1/catalogue/reset",
        params={"confirm": "SUPPRIMER_TOUT"},
    )
    assert resp.status_code in (400, 403)
    client.close()
