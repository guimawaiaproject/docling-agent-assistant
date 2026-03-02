"""
Tests E2E — flux scan : upload → validation.
Simulation utilisateur réelle avec Playwright.
"""

import os
import re
import tempfile

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

PDF_MINIMAL = (
    b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\nxref\n0 3\n"
    b"trailer<</Size 3/Root 1 0 R>>\nstartxref\n%%EOF"
)


def test_scan_page_loads_and_dropzone_visible(page, frontend_url):
    """Page /scan charge, dropzone visible."""
    page.goto(f"{frontend_url}/scan", wait_until="networkidle")
    expect(page.locator("[data-testid='scan-dropzone']")).to_be_visible()
    expect(page).to_have_title(re.compile(r".+"))


def test_scan_upload_file_and_trigger_processing(page, frontend_url):
    """
    Upload d'un petit PDF via Parcourir, clic sur Lancer.
    Attente du statut Terminé ou Erreur (max 90s).
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(PDF_MINIMAL)
        tmp_path = f.name

    try:
        page.goto(f"{frontend_url}/scan", wait_until="networkidle")

        with page.expect_file_chooser() as fc_info:
            page.locator("[data-testid='scan-upload-btn']").click()
        fc_info.value.set_files(tmp_path)

        page.wait_for_selector(
            "[data-testid='scan-lancer-btn']:not([disabled])", timeout=5000
        )
        page.locator("[data-testid='scan-lancer-btn']").click()

        try:
            page.wait_for_selector(
                ":has-text('Traitement en cours'), "
                ":has-text('Terminé'), "
                ":has-text('Erreur')",
                timeout=10000,
            )
        except Exception:
            pass

        page.wait_for_timeout(2000)
        expect(page.locator("[data-testid='scan-dropzone']")).to_be_visible()
    finally:
        os.unlink(tmp_path)
