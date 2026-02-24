import pytest
from unittest.mock import MagicMock
from backend.services.gemini_service import GeminiService
from backend.core.config import AppConfig

def test_extract_invoice_success(mocker):
    config = AppConfig(GEMINI_API_KEY="test")
    svc = GeminiService(config)

    mock_response = MagicMock()
    mock_response.text = '{"numero_facture": "123", "date_facture": "01/01/2026", "fournisseur": "BigMat", "products": [{"fournisseur": "BigMat", "designation_raw": "Ciment", "designation_fr": "Ciment", "famille": "Ciment", "unite": "sac", "prix_brut_ht": 10.0, "remise_pct": 0, "prix_remise_ht": 8.50, "prix_ttc_iva21": 10.28}]}'

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    svc._client = mock_client

    res = svc.extract_invoice(b"dummy")
    assert res is not None
    assert res.numero_facture == "123"
    assert len(res.products) == 1

def test_extract_invoice_invalid_input(mocker):
    config = AppConfig(GEMINI_API_KEY="test")
    svc = GeminiService(config)

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "NOT JSON"
    mock_client.models.generate_content.return_value = mock_response
    svc._client = mock_client

    res = svc.extract_invoice(b"dummy")
    assert res is None

def test_extract_invoice_error_handling(mocker):
    config = AppConfig(GEMINI_API_KEY="test")
    svc = GeminiService(config)

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("RESOURCE_EXHAUSTED retry in 1")
    svc._client = mock_client

    res = svc.extract_invoice(b"dummy")
    assert res is None

def test_extract_from_text_success(mocker):
    config = AppConfig(GEMINI_API_KEY="test")
    svc = GeminiService(config)

    mock_response = MagicMock()
    mock_response.text = '{"numero_facture": "124", "products": []}'
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    svc._client = mock_client

    res = svc.extract_from_text("OCR Data here")
    assert res is not None
