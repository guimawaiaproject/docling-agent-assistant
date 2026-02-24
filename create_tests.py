import os
import textwrap

files = {
    "pytest.ini": """
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
""",

    "tests/backend/core/test_config.py": """
import pytest
from backend.core.config import AppConfig, get_config

def test_get_config_success():
    config = get_config(GEMINI_API_KEY="AIzaSyTest", GOOGLE_CREDENTIALS_PATH="creds.json")
    assert config.gemini_api_key == "AIzaSyTest"
    assert config.has_gemini_key is True

def test_get_config_invalid_input():
    config = get_config(GEMINI_API_KEY="")
    assert config.has_gemini_key is False

def test_get_config_edge_case():
    config = get_config(GEMINI_API_KEY="YOUR_API_KEY_HERE")
    assert config.has_gemini_key is False
""",

    "tests/backend/core/test_db_manager.py": """
import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from backend.core.db_manager import DBManager
from backend.schemas.invoice import Product

@pytest.fixture
def db(tmp_path):
    return DBManager(str(tmp_path / "test.db"))

def test_ensure_tables_success(db):
    stats = db.get_stats()
    assert stats["products"] == 0
    assert stats["invoices"] == 0
    assert stats["families"] == 0

def test_upsert_product_success(db):
    product = Product(
        fournisseur="BigMat", designation_raw="Sable", designation_fr="Sable",
        famille="Granulat", unite="kg", prix_brut_ht=10.0, prix_remise_ht=9.0
    )
    res = db.upsert_product(product, "F123", "01/01/2026")
    assert res == "added"

def test_upsert_product_edge_case(db):
    product = Product(
        fournisseur="BigMat", designation_raw="Sable", designation_fr="Sable",
        famille="Granulat", unite="kg", prix_brut_ht=10.0, prix_remise_ht=9.0
    )
    db.upsert_product(product, "F123", "01/01/2026")
    res = db.upsert_product(product, "F124", "15/01/2026")
    assert res == "updated"

def test_save_invoice_success(db):
    db.save_invoice("hash123", "facture.pdf", "BigMat", "F123", "01/01/2026", 1)
    assert db.is_invoice_processed("hash123") is True

@patch("sqlite3.connect")
def test_db_manager_error_handling(mock_connect):
    mock_connect.side_effect = sqlite3.Error("Mock DB error")
    with pytest.raises(sqlite3.Error):
        DBManager("fail.db")
""",

    "tests/backend/core/test_orchestrator.py": """
import pytest
from unittest.mock import MagicMock
from backend.core.orchestrator import ExtractionOrchestrator
from backend.schemas.invoice import ProcessingResult, InvoiceResult

def test_process_file_success(mocker):
    config = MagicMock()
    db = MagicMock()
    db.is_invoice_processed.return_value = False
    db.upsert_product.return_value = "added"

    orch = ExtractionOrchestrator(config=config, db_manager=db)
    mocker.patch.object(orch.ocr, "is_available", False)

    mock_invoice = InvoiceResult(
        numero_facture="123",
        products=[MagicMock(fournisseur="BigMat", designation_raw="Ciment 25kg")]
    )
    mocker.patch.object(orch.gemini, "extract_invoice", return_value=mock_invoice)

    result = orch.process_file(b"data", "test.pdf")
    assert isinstance(result, ProcessingResult)
    assert result.products_added == 1
    assert result.was_cached is False

def test_process_file_cached_edge_case(mocker):
    config = MagicMock()
    db = MagicMock()
    db.is_invoice_processed.return_value = True

    orch = ExtractionOrchestrator(config=config, db_manager=db)
    result = orch.process_file(b"data", "test.pdf")

    assert result.was_cached is True
    assert result.products_added == 0

def test_process_file_error_handling(mocker):
    config = MagicMock()
    db = MagicMock()
    db.is_invoice_processed.return_value = False

    orch = ExtractionOrchestrator(config=config, db_manager=db)
    mocker.patch.object(orch.ocr, "is_available", False)
    mocker.patch.object(orch.gemini, "extract_invoice", return_value=None)

    result = orch.process_file(b"data", "empty.pdf")
    assert result.products_added == 0
""",

    "tests/backend/services/test_gemini_service.py": """
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
""",

    "tests/backend/services/test_google_drive_service.py": """
import pytest
from unittest.mock import MagicMock, patch
from backend.services.google_drive_service import GoogleDriveService

def test_upload_invoice_success(mocker):
    mocker.patch("backend.services.google_drive_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_drive_service.build")

    svc = GoogleDriveService("dummy.json", "root")
    svc._service = MagicMock()
    svc._service.files().create().execute.return_value = {"id": "1", "webViewLink": "http://link"}
    mocker.patch.object(svc, "_get_date_folder", return_value="fld")

    res = svc.upload_invoice(b"data", "test.pdf", "01/01/2026")
    assert res == "http://link"

def test_upload_invoice_error_handling(mocker):
    mocker.patch("backend.services.google_drive_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_drive_service.build")

    svc = GoogleDriveService("dummy.json", "root")
    svc._service = MagicMock()
    svc._service.files().create().execute.side_effect = Exception("API error")
    mocker.patch.object(svc, "_get_date_folder", return_value="fld")

    res = svc.upload_invoice(b"data", "test.pdf", "01/01/2026")
    assert res is None
""",

    "tests/backend/services/test_google_sheets_service.py": """
import pytest
from unittest.mock import MagicMock
import pandas as pd
from backend.services.google_sheets_service import GoogleSheetsService

def test_sync_catalogue_success(mocker):
    mocker.patch("backend.services.google_sheets_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_sheets_service.build")

    svc = GoogleSheetsService("dummy.json", "sheet_id")
    svc._service = MagicMock()

    df = pd.DataFrame([{
        "fournisseur": "BigMat", "designation_raw": "Sable", "designation_fr": "Sable",
        "famille": "Granulats", "unite": "T", "prix_brut_ht": 10.0, "remise_pct": 0,
        "prix_remise_ht": 10.0, "prix_ttc_iva21": 12.10, "numero_facture": "F1", "date_facture": "01/01"
    }])

    res = svc.sync_catalogue(df)
    assert res is True

def test_sync_catalogue_error_handling(mocker):
    mocker.patch("backend.services.google_sheets_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_sheets_service.build")

    svc = GoogleSheetsService("dummy.json", "sheet_id")
    svc._service = MagicMock()
    svc._service.spreadsheets().values().update().execute.side_effect = Exception("API fail")

    df = pd.DataFrame([{"fournisseur": "A", "designation_raw": "B"}])
    res = svc.sync_catalogue(df)
    assert res is False
""",

    "tests/backend/services/test_ocr_space_service.py": """
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
""",

    "tests/backend/integration/test_invoice_schemas.py": """
import pytest
from backend.schemas.invoice import Product

def test_product_validation_success():
    p = Product(
        fournisseur="BigMat", designation_raw="Sable de riviere",
        designation_fr="Sable Riviere", famille="Granulat", prix_remise_ht=10.0
    )
    assert p.prix_ttc_iva21 == 12.1

def test_product_validation_edge_case():
    p = Product(
        fournisseur="BigMat", designation_raw="Sable de riviere",
        designation_fr="Sable Riviere", famille="Granulat",
        prix_remise_ht=10.0, prix_ttc_iva21=15.0
    )
    assert p.prix_ttc_iva21 == 15.0
""",

    "tests/backend/integration/test_pipeline_complete.py": """
import pytest
from unittest.mock import MagicMock
from backend.core.orchestrator import ExtractionOrchestrator
from backend.core.db_manager import DBManager
from backend.core.config import AppConfig
from backend.schemas.invoice import InvoiceResult, Product

def test_pipeline_complete_success(tmp_path, mocker):
    db = DBManager(str(tmp_path / "test.db"))
    config = AppConfig(GEMINI_API_KEY="test")
    orch = ExtractionOrchestrator(config=config, db_manager=db)

    product = Product(
        fournisseur="BigMat", designation_raw="Ciment 25kg", designation_fr="Ciment",
        famille="Ciment", prix_brut_ht=10.0, prix_remise_ht=8.50
    )
    invoice = InvoiceResult(
        numero_facture="F123", date_facture="01/01/2026",
        fournisseur="BigMat", products=[product]
    )

    mocker.patch.object(orch.gemini, 'extract_invoice', return_value=invoice)
    mocker.patch.object(orch.ocr, 'is_available', False)

    res = orch.process_file(b"pdf data", "facture.pdf")

    assert res.products_added == 1
    stats = db.get_stats()
    assert stats["products"] == 1
    assert stats["invoices"] == 1

    df = db.get_catalogue()
    assert len(df) == 1
    assert df.iloc[0]["designation_fr"] == "Ciment"
    assert df.iloc[0]["prix_remise_ht"] == 8.50
""",

    "tests/frontend/test_streamlit_app.py": """
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, MagicMock

@patch("backend.core.orchestrator.ExtractionOrchestrator")
@patch("backend.core.db_manager.DBManager")
@patch("backend.core.config.get_config")
def test_upload_facture_success(mock_get_config, mock_db_manager, mock_orch):
    mock_config = MagicMock()
    mock_config.has_gemini_key = True
    mock_config.has_google_config = False
    mock_get_config.return_value = mock_config

    mock_db = MagicMock()
    mock_db.get_stats.return_value = {"products": 0, "invoices": 0, "families": 0}
    mock_db.get_catalogue.return_value = MagicMock(empty=True)
    mock_db_manager.return_value = mock_db

    mock_orch_inst = MagicMock()
    mock_processing_result = MagicMock()
    mock_processing_result.products_added = 1
    mock_processing_result.products_updated = 0
    mock_processing_result.was_cached = False
    mock_orch_inst.process_file.return_value = mock_processing_result
    mock_orch.return_value = mock_orch_inst

    at = AppTest.from_file("app.py").run()
    assert not at.exception
"""
}

for path, content in files.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n")
    print(f"Written {path}")
