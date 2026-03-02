"""
Tests de sécurité — isolation multi-tenant (IDOR).
User A ne doit JAMAIS accéder aux données de User B.
"""

import uuid

import httpx
import pytest
from faker import Faker

fake = Faker("fr_FR")

pytestmark = [pytest.mark.security]


def test_user_isolation_job_invisible_to_other_user(
    ensure_server_running: str,
    unique_user: dict,
):
    """
    user1 crée un job (scan), user2 ne doit PAS le voir.
    Assertion critique : isolation multi-tenant sur jobs.
    """
    import random
    import secrets

    base_url = ensure_server_running

    # User 1 : inscription + login
    client1 = httpx.Client(base_url=base_url, timeout=30)
    reg1 = client1.post(
        "/api/v1/auth/register",
        data={
            "email": unique_user["email"],
            "password": unique_user["password"],
            "name": unique_user.get("name", ""),
        },
    )
    assert reg1.status_code in (200, 409)
    login1 = client1.post(
        "/api/v1/auth/login",
        data={"email": unique_user["email"], "password": unique_user["password"]},
    )
    assert login1.status_code == 200
    token1 = login1.json().get("token")
    assert token1
    client1.headers["Authorization"] = f"Bearer {token1}"

    # User 2 : création d'un second utilisateur
    pwd2 = f"Test@{secrets.token_hex(8)}!{random.randint(100, 999)}"
    user2 = {
        "email": f"test_{uuid.uuid4().hex[:8]}@{fake.domain_name()}",
        "password": pwd2,
        "name": fake.first_name(),
    }
    client2 = httpx.Client(base_url=base_url, timeout=30)
    client2.post(
        "/api/v1/auth/register",
        data={
            "email": user2["email"],
            "password": user2["password"],
            "name": user2.get("name", ""),
        },
    )
    login2 = client2.post(
        "/api/v1/auth/login",
        data={"email": user2["email"], "password": user2["password"]},
    )
    assert login2.status_code == 200
    token2 = login2.json().get("token")
    client2.headers["Authorization"] = f"Bearer {token2}"

    # User 1 : crée un job (upload minimal pour déclencher create_job)
    files = {"file": ("test.pdf", b"%PDF-1.4 minimal", "application/pdf")}
    data = {"model": "gemini-3-flash-preview", "source": "pc"}
    resp1 = client1.post("/api/v1/invoices/process", files=files, data=data)
    assert resp1.status_code == 202
    job_id = resp1.json().get("job_id")
    assert job_id

    # User 2 : tente d'accéder au job de user1 → 404 (CRITIQUE)
    resp2 = client2.get(f"/api/v1/invoices/status/{job_id}")
    assert resp2.status_code == 404, "user2 ne doit PAS voir le job de user1"

    # User 1 : peut voir son propre job
    resp1_status = client1.get(f"/api/v1/invoices/status/{job_id}")
    assert resp1_status.status_code == 200

    client1.close()
    client2.close()
