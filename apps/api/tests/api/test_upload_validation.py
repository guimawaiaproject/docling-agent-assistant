"""
Tests API — validation upload (taille, MIME, fichier vide).
"""


def test_upload_too_large_returns_413(authenticated_client):
    """Upload d'un fichier trop grand (> 50 Mo) → 413 Request Entity Too Large."""
    client, _ = authenticated_client
    big_content = b"x" * (51 * 1024 * 1024)
    files = {"file": ("large.pdf", big_content, "application/pdf")}
    data = {"model": "gemini-3-flash-preview", "source": "pc"}
    resp = client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code == 413


def test_upload_wrong_mime_type(authenticated_client):
    """Upload d'un fichier avec mauvais type MIME → 415 ou 422."""
    client, _ = authenticated_client
    files = {"file": ("script.exe", b"MZ\x00\x00", "application/octet-stream")}
    data = {"model": "gemini-3-flash-preview", "source": "pc"}
    resp = client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code in (415, 422, 400)


def test_upload_empty_file(authenticated_client):
    """Upload d'un fichier vide → 422 ou 400."""
    client, _ = authenticated_client
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    data = {"model": "gemini-3-flash-preview", "source": "pc"}
    resp = client.post("/api/v1/invoices/process", files=files, data=data)
    assert resp.status_code in (422, 400)
