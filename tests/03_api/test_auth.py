"""
Tests API — authentification (Form data, pas JSON).
"""

import httpx


def test_register_success(ensure_server_running: str, unique_user: dict):
    client = httpx.Client(base_url=ensure_server_running, timeout=30)
    resp = client.post(
        "/api/v1/auth/register",
        data={
            "email": unique_user["email"],
            "password": unique_user["password"],
            "name": unique_user.get("name", ""),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert "user_id" in data
    assert data["email"] == unique_user["email"]
    client.close()


def test_register_duplicate_email_409(ensure_server_running: str, unique_user: dict):
    client = httpx.Client(base_url=ensure_server_running, timeout=30)
    # Premier enregistrement
    client.post(
        "/api/v1/auth/register",
        data={
            "email": unique_user["email"],
            "password": unique_user["password"],
            "name": unique_user.get("name", ""),
        },
    )
    # Doublon
    resp = client.post(
        "/api/v1/auth/register",
        data={
            "email": unique_user["email"],
            "password": "OtherPass123!",
            "name": "Other",
        },
    )
    assert resp.status_code == 409
    detail = resp.json().get("detail", "").lower()
    assert "utilise" in detail or "deja" in detail or "already" in detail
    client.close()


def test_register_missing_fields_422(ensure_server_running: str):
    client = httpx.Client(base_url=ensure_server_running, timeout=30)
    resp = client.post("/api/v1/auth/register", data={})
    assert resp.status_code in (422, 400)
    client.close()


def test_login_success(authenticated_client):
    client, user = authenticated_client
    # Déjà authentifié, vérifier /me
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == user["email"]


def test_login_wrong_password_401(ensure_server_running: str, unique_user: dict):
    client = httpx.Client(base_url=ensure_server_running, timeout=30)
    client.post(
        "/api/v1/auth/register",
        data={
            "email": unique_user["email"],
            "password": unique_user["password"],
            "name": unique_user.get("name", ""),
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={
            "email": unique_user["email"],
            "password": "WrongPassword123!",
        },
    )
    assert resp.status_code == 401
    client.close()


def test_me_no_token_401(http_client: httpx.Client):
    resp = http_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_invalid_token_401(ensure_server_running: str):
    client = httpx.Client(
        base_url=ensure_server_running,
        timeout=30,
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    client.close()
