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
