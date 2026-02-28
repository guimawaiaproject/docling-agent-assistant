"""
Tests de sécurité — _safe_float, _escape_like, isolation utilisateur.
"""

import uuid

import pytest

from backend.core.db_manager import _escape_like, _safe_float


# ─── TestSafeFloat ───────────────────────────────────────────────────────────
class TestSafeFloat:
    """10 cas : None, N/A, "", 12,50, €45, integer, negative, default."""

    def test_none_returns_default(self):
        assert _safe_float(None) == 0.0
        assert _safe_float(None, default=99.5) == 99.5

    def test_na_string_returns_default(self):
        assert _safe_float("N/A") == 0.0
        assert _safe_float("n/a") == 0.0

    def test_empty_string_returns_default(self):
        assert _safe_float("") == 0.0

    def test_comma_decimal_returns_default(self):
        """12,50 (virgule) ou double point → invalide pour float() → default."""
        # "12,50" peut être parsé en locale FR → tester aussi une chaîne invalide
        assert _safe_float("12.50.50") == 0.0  # double point invalide

    def test_currency_prefix_returns_default(self):
        """Chaîne avec préfixe non numérique (ex: €45) → default."""
        assert _safe_float("prix45") == 0.0

    def test_valid_float(self):
        assert _safe_float(12.5) == 12.5
        assert _safe_float("12.5") == 12.5

    def test_integer(self):
        assert _safe_float(42) == 42.0
        assert _safe_float("100") == 100.0

    def test_negative(self):
        assert _safe_float(-3.14) == -3.14
        assert _safe_float("-10") == -10.0

    def test_custom_default(self):
        assert _safe_float("invalid", default=7.0) == 7.0
        assert _safe_float(None, default=-1.0) == -1.0

    def test_invalid_types_return_default(self):
        assert _safe_float({}) == 0.0
        assert _safe_float([]) == 0.0


# ─── TestEscapeIlike ─────────────────────────────────────────────────────────
class TestEscapeIlike:
    """4 cas : %, _, normal string, mixed."""

    def test_percent_escaped(self):
        assert _escape_like("50%") == "50\\%"
        assert _escape_like("%%") == "\\%\\%"

    def test_underscore_escaped(self):
        assert _escape_like("a_b") == "a\\_b"
        assert _escape_like("__") == "\\_\\_"

    def test_normal_string_unchanged(self):
        assert _escape_like("ciment") == "ciment"
        assert _escape_like("Produit 42") == "Produit 42"

    def test_mixed_special_chars(self):
        assert _escape_like("50%_off") == "50\\%\\_off"
        assert _escape_like("\\%\\_") == "\\\\\\%\\\\\\_"


# ─── test_user_isolation ──────────────────────────────────────────────────────
@pytest.mark.security
def test_user_isolation_job_invisible_to_other_user(
    ensure_server_running: str,
    unique_user: dict,
):
    """
    user1 crée un job (scan), user2 ne doit PAS le voir.
    Assertion critique : isolation multi-tenant sur jobs.
    """
    import httpx

    base_url = ensure_server_running

    # User 1 : inscription + login
    client1 = httpx.Client(base_url=base_url, timeout=30)
    reg1 = client1.post(
        "/api/v1/auth/register",
        data={"email": unique_user["email"], "password": unique_user["password"], "name": unique_user.get("name", "")},
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
    import random
    import secrets

    from faker import Faker

    fake = Faker("fr_FR")
    pwd2 = f"Test@{secrets.token_hex(8)}!{random.randint(100, 999)}"
    user2 = {
        "email": f"test_{uuid.uuid4().hex[:8]}@{fake.domain_name()}",
        "password": pwd2,
        "name": fake.first_name(),
    }
    client2 = httpx.Client(base_url=base_url, timeout=30)
    client2.post("/api/v1/auth/register", data={"email": user2["email"], "password": user2["password"], "name": user2.get("name", "")})
    login2 = client2.post("/api/v1/auth/login", data={"email": user2["email"], "password": user2["password"]})
    assert login2.status_code == 200
    token2 = login2.json().get("token")
    client2.headers["Authorization"] = f"Bearer {token2}"

    # User 1 : crée un job (upload minimal pour déclencher create_job)
    files = {"file": ("test.pdf", b"%PDF-1.4 minimal", "application/pdf")}
    resp1 = client1.post("/api/v1/invoices/process", files=files)
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
