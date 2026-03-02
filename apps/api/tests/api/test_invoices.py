"""
Tests API — extraction factures (process, status).
"""

import time


def test_process_returns_202_and_job_id(authenticated_client):
    """Upload minimal PDF → 202 + job_id."""
    client, _ = authenticated_client
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\nxref\n0 3\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n%%EOF"
    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    data = {"model": "gemini-3-flash-preview", "source": "pc"}
    resp = client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 202
    body = resp.json()
    assert "job_id" in body
    assert body.get("status") == "processing"


def test_process_file_too_large_413(authenticated_client):
    """Fichier > 50 Mo → 413."""
    client, _ = authenticated_client
    big_content = b"x" * (51 * 1024 * 1024)
    files = {"file": ("huge.pdf", big_content, "application/pdf")}
    data = {"model": "gemini-3-flash-preview", "source": "pc"}
    resp = client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 413


def test_status_404_for_invalid_job_id(authenticated_client):
    client, _ = authenticated_client
    resp = client.get("/api/v1/invoices/status/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_status_polling_until_complete(authenticated_client):
    """Upload PDF minimal, poll jusqu'à completed ou error."""
    client, _ = authenticated_client
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\nxref\n0 3\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n%%EOF"
    files = {"file": ("poll_test.pdf", pdf_bytes, "application/pdf")}
    data = {"model": "gemini-3-flash-preview", "source": "pc"}
    resp = client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    for _ in range(60):
        status_resp = client.get(f"/api/v1/invoices/status/{job_id}")
        assert status_resp.status_code == 200
        data = status_resp.json()
        if data["status"] in ("completed", "error"):
            assert "status" in data
            break
        time.sleep(1)
    else:
        raise AssertionError("Job non terminé après 60s")
