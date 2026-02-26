"""
Tests API — extraction factures (process, status).
"""

import time

import httpx


def test_process_returns_202_and_job_id(http_client: httpx.Client):
    """Upload minimal PDF → 202 + job_id."""
    # PDF minimal valide (header + body minimal)
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\nxref\n0 3\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n%%EOF"
    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    data = {"model": "gemini-3-flash", "source": "pc"}
    resp = http_client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 202
    body = resp.json()
    assert "job_id" in body
    assert body.get("status") == "processing"


def test_process_file_too_large_413(http_client: httpx.Client):
    """Fichier > 50 Mo → 413."""
    big_content = b"x" * (51 * 1024 * 1024)
    files = {"file": ("huge.pdf", big_content, "application/pdf")}
    data = {"model": "gemini-3-flash", "source": "pc"}
    resp = http_client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 413


def test_status_404_for_invalid_job_id(http_client: httpx.Client):
    resp = http_client.get("/api/v1/invoices/status/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_status_polling_until_complete(http_client: httpx.Client):
    """Upload PDF minimal, poll jusqu'à completed ou error."""
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\nxref\n0 3\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n%%EOF"
    files = {"file": ("poll_test.pdf", pdf_bytes, "application/pdf")}
    data = {"model": "gemini-3-flash", "source": "pc"}
    resp = http_client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    for _ in range(60):
        status_resp = http_client.get(f"/api/v1/invoices/status/{job_id}")
        assert status_resp.status_code == 200
        data = status_resp.json()
        if data["status"] in ("completed", "error"):
            assert "status" in data
            break
        time.sleep(1)
    else:
        raise AssertionError("Job non terminé après 60s")
