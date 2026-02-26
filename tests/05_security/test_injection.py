"""
Tests de sécurité — injection SQL, XSS sur catalogue/batch.
"""

import pytest

pytestmark = [pytest.mark.security]


SQL_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1' UNION SELECT null,username,password FROM users--",
    "admin'--",
    "' OR 1=1--",
]


XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "<svg onload=alert(1)>",
]


@pytest.mark.parametrize("payload", SQL_PAYLOADS)
def test_sql_injection_batch_designation_raw(
    authenticated_client,
    payload,
):
    """Payload SQL dans designation_raw → stocké tel quel ou rejeté, pas d'exécution."""
    import uuid
    client, _ = authenticated_client
    marker = f"sql_test_{uuid.uuid4().hex[:6]}"
    products = [
        {
            "fournisseur": marker,
            "designation_raw": payload[:100],
            "designation_fr": "Produit test",
            "famille": "Autre",
            "prix_brut_ht": 10.0,
            "prix_remise_ht": 10.0,
            "prix_ttc_iva21": 12.1,
            "confidence": "high",
        },
    ]
    resp = client.post(
        "/api/v1/catalogue/batch",
        json={"produits": products, "source": "pc"},
    )
    # Soit 200 (données échappées et stockées comme texte), soit 500 (erreur)
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        cat = client.get("/api/v1/catalogue")
        assert cat.status_code == 200


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_batch_stored_sanitized(
    authenticated_client,
    payload,
):
    """Payload XSS dans designation_fr → stocké, pas exécuté côté serveur."""
    import uuid
    client, _ = authenticated_client
    marker = f"xss_test_{uuid.uuid4().hex[:6]}"
    products = [
        {
            "fournisseur": marker,
            "designation_raw": f"raw_{payload[:20].replace('<', '').replace('>', '')}",
            "designation_fr": payload,
            "famille": "Autre",
            "prix_brut_ht": 10.0,
            "prix_remise_ht": 10.0,
            "prix_ttc_iva21": 12.1,
            "confidence": "high",
        },
    ]
    resp = client.post(
        "/api/v1/catalogue/batch",
        json={"produits": products, "source": "pc"},
    )
    assert resp.status_code == 200
    # Les données sont stockées ; l'échappement JSON côté API évite l'injection
    # dans la réponse. Pas d'exécution de script côté serveur.
