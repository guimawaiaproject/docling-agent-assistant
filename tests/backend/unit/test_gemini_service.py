import pytest
from unittest.mock import MagicMock
from backend.services.gemini_service import GeminiService
from backend.core.config import AppConfig

@pytest.fixture
def gemini_svc():
    config = AppConfig(GEMINI_API_KEY="AIzaSyTestKey")
    return GeminiService(config=config)

def test_extract_invoice_success(gemini_svc, mocker):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"numero_facture": "F1", "date_facture": "01/01/2026", "fournisseur": "Test", "products": []}'
    mock_client.models.generate_content.return_value = mock_response
    gemini_svc._client = mock_client

    result = gemini_svc.extract_invoice(b"filedata", "application/pdf")
    assert result is not None
    assert result.numero_facture == "F1"

def test_extract_invalid_json(gemini_svc, mocker):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = 'INVALID JSON'
    mock_client.models.generate_content.return_value = mock_response
    gemini_svc._client = mock_client

    result = gemini_svc.extract_invoice(b"filedata", "application/pdf")
    assert result is None

def test_extract_api_error(gemini_svc, mocker):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("Rate limit RESOURCE_EXHAUSTED")
    gemini_svc._client = mock_client

    result = gemini_svc.extract_invoice(b"filedata", "application/pdf")
    # Due to retry loop it will exhaust and return None
    assert result is None
