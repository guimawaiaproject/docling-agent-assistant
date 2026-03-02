"""
Tests services externes — extraction IA réelle (Gemini).
Coûteux en tokens, exécuter manuellement ou en CI avec GEMINI_API_KEY.
"""

import os

import pytest

pytestmark = [pytest.mark.external, pytest.mark.slow]


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY non défini — skip pour éviter coûts",
)
def test_extraction_pdf_minimal_via_api(http_client):
    """
    Upload PDF minimal → attente completed ou error.
    Vérifie que le job se termine (pas de blocage).
    """
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\nxref\n0 3\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n%%EOF"
    files = {"file": ("extraction_test.pdf", pdf_bytes, "application/pdf")}
    data = {"model": "gemini-3-flash", "source": "pc"}
    resp = http_client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    import time
    for _ in range(90):
        status_resp = http_client.get(f"/api/v1/invoices/status/{job_id}")
        assert status_resp.status_code == 200
        data = status_resp.json()
        if data["status"] in ("completed", "error"):
            assert "status" in data
            return
        time.sleep(1)
    pytest.fail("Job non terminé après 90s")
