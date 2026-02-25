"""
Configuration globale des tests — zéro mock.
Fixtures réelles : serveur, DB, utilisateur, client authentifié.
"""

import os
import time
import uuid
from typing import Generator

import httpx
import pytest
from faker import Faker

# Charger .env.test si présent
_env_test = os.path.join(os.path.dirname(__file__), "..", ".env.test")
if os.path.exists(_env_test):
    from dotenv import load_dotenv
    load_dotenv(_env_test)

# Variables d'environnement de test
TEST_BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
TEST_FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:5173")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")

fake = Faker("fr_FR")


# ─── Serveur accessible ───────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def ensure_server_running() -> str:
    """
    Vérifie que le serveur est réellement lancé avant tous les tests.
    Lance pytest.fail si inaccessible après 10 tentatives.
    """
    max_retries = 10
    for i in range(max_retries):
        try:
            resp = httpx.get(f"{TEST_BASE_URL}/health", timeout=2)
            if resp.status_code == 200:
                return TEST_BASE_URL
        except Exception:
            pass
        time.sleep(1)
    pytest.fail(
        f"Le serveur n'est pas accessible sur {TEST_BASE_URL}. "
        "Lancez-le avant les tests (ex: python api.py)."
    )
    return TEST_BASE_URL  # unreachable


# ─── Connexion DB réelle ──────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def real_db_connection() -> Generator:
    """
    Connexion réelle à la base de données de test.
    Utilise psycopg2 (sync) pour compatibilité avec les fixtures.
    """
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL ou DATABASE_URL non défini")
    try:
        import psycopg2
        conn = psycopg2.connect(TEST_DATABASE_URL)
        conn.autocommit = False
        yield conn
        conn.rollback()
    finally:
        conn.close()


# ─── Utilisateur unique (Faker) ───────────────────────────────────────────────
@pytest.fixture(scope="function")
def unique_user() -> dict:
    """Génère un utilisateur unique et réaliste pour chaque test."""
    import secrets
    import random
    pwd = f"Test@{secrets.token_hex(8)}!{random.randint(100, 999)}"
    return {
        "email": f"test_{uuid.uuid4().hex[:8]}@{fake.domain_name()}",
        "password": pwd,
        "name": fake.first_name(),
    }


# ─── Client HTTP authentifié ──────────────────────────────────────────────────
@pytest.fixture(scope="function")
def authenticated_client(
    ensure_server_running: str,
    unique_user: dict,
) -> Generator:
    """
    Client HTTP réel avec session authentifiée.
    Inscription + login réels via Form data (pas JSON).
    """
    base_url = ensure_server_running
    client = httpx.Client(base_url=base_url, timeout=30)

    # Inscription réelle (Form data)
    reg_resp = client.post(
        "/api/v1/auth/register",
        data={
            "email": unique_user["email"],
            "password": unique_user["password"],
            "name": unique_user.get("name", ""),
        },
    )
    # Peut être 200 (nouveau) ou 409 si email déjà utilisé (rare avec uuid)
    if reg_resp.status_code not in (200, 409):
        pytest.fail(f"Register échoué : {reg_resp.status_code} {reg_resp.text}")

    # Connexion réelle (Form data)
    login_resp = client.post(
        "/api/v1/auth/login",
        data={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )
    assert login_resp.status_code == 200, f"Login échoué : {login_resp.text}"
    token = login_resp.json().get("token")
    assert token, "Token manquant dans la réponse login"
    client.headers["Authorization"] = f"Bearer {token}"

    yield client, unique_user
    client.close()


# ─── Client HTTP non authentifié ──────────────────────────────────────────────
@pytest.fixture(scope="function")
def http_client(ensure_server_running: str) -> Generator:
    """Client HTTP simple sans auth."""
    client = httpx.Client(base_url=ensure_server_running, timeout=30)
    yield client
    client.close()


# ─── Produit Faker pour batch ─────────────────────────────────────────────────
@pytest.fixture(scope="function")
def sample_products() -> list[dict]:
    """Liste de produits réalistes générés par Faker."""
    products = []
    for _ in range(3):
        prix = round(fake.random.uniform(5.0, 150.0), 2)
        remise = round(fake.random.uniform(0, 15), 1)
        prix_remise = round(prix * (1 - remise / 100), 2)
        products.append({
            "fournisseur": fake.company()[:50],
            "designation_raw": fake.catch_phrase()[:100],
            "designation_fr": fake.catch_phrase()[:100],
            "famille": "Maçonnerie",
            "unite": "unité",
            "prix_brut_ht": prix,
            "remise_pct": remise,
            "prix_remise_ht": prix_remise,
            "prix_ttc_iva21": round(prix_remise * 1.21, 2),
            "confidence": "high",
        })
    return products
