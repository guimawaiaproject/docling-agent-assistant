import os
import pytest
from fastapi.testclient import TestClient
from api import app

@pytest.fixture
def test_client():
    client = TestClient(app)
    yield client

def test_full_pipeline(test_client, mocker, tmp_path):
    """
    Simulates a User uploading a PDF -> API -> Orchestrator -> Mocked Gemini -> SQLite -> API Catalogue
    """
    from backend.schemas.invoice import Product, InvoiceResult

    mock_result = InvoiceResult(
        numero_facture="E2E-123",
        date_facture="01/01/2026",
        fournisseur="E2E Supplier",
        products=[Product(
            fournisseur="E2E Supplier", designation_raw="Placo", designation_fr="Plaque de plâtre",
            famille="Platrerie", unite="plaque", prix_brut_ht=10.0, remise_pct=0,
            prix_remise_ht=10.0, prix_ttc_iva21=12.10
        )]
    )

    # We only mock the IA call, everything else (Database, Routes, Schemas) is REAL.
    mocker.patch("backend.services.gemini_service.GeminiService.extract_invoice", return_value=mock_result)

    # Stage 0: Isolate Database and Orchestrator Dependencies
    from backend.core.db_manager import DBManager
    from api import get_db, get_orchestrator
    from backend.core.orchestrator import ExtractionOrchestrator
    from backend.core.config import AppConfig

    test_db = DBManager(str(tmp_path / "e2e_mock.db"))

    def override_get_db():
        return test_db

    def override_get_orchestrator():
        return ExtractionOrchestrator(config=AppConfig(GEMINI_API_KEY="test"), db_manager=test_db)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_orchestrator] = override_get_orchestrator

    # Stage 1: Upload Invoice
    response = test_client.post(
        "/api/v1/invoices/process",
        files={"file": ("facture.pdf", b"pdf dummy bytes", "application/pdf")}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["products_added"] == 1

    # Stage 2: Verify Catalogue State
    cat_response = test_client.get("/api/v1/catalogue")
    assert cat_response.status_code == 200

    items = cat_response.json()["products"]
    assert len(items) == 1
    assert items[0]["fournisseur"] == "E2E Supplier"
    assert items[0]["designation_fr"] == "Plaque de plâtre"
