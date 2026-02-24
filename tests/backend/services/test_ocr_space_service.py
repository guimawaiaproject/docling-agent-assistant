import pytest
from unittest.mock import MagicMock
from backend.services.ocr_space_service import OcrSpaceService

def test_extract_text_success(mocker):
    svc = OcrSpaceService("dummy_key")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "ParsedResults": [{"ParsedText": "BIGMAT factura 1234"}],
        "IsErroredOnProcessing": False
    }
    mocker.patch("requests.post", return_value=mock_resp)

    text = svc.extract_text(b"data", "test.pdf")
    assert text == "BIGMAT factura 1234"

def test_extract_text_invalid_input(mocker):
    svc = OcrSpaceService("dummy_key")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "IsErroredOnProcessing": True,
        "ErrorMessage": ["File parse error"]
    }
    mocker.patch("requests.post", return_value=mock_resp)

    text = svc.extract_text(b"data", "test.pdf")
    assert text is None

def test_extract_text_error_handling(mocker):
    svc = OcrSpaceService("dummy_key")
    mocker.patch("requests.post", side_effect=Exception("Timeout or fail"))

    text = svc.extract_text(b"data", "test.pdf")
    assert text is None
