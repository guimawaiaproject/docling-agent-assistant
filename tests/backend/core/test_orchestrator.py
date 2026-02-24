import pytest
from unittest.mock import MagicMock
from backend.core.orchestrator import ExtractionOrchestrator
from backend.schemas.invoice import ProcessingResult, InvoiceResult, Product

def test_process_file_success(mocker):
    config = MagicMock()
    db = MagicMock()
    db.is_invoice_processed.return_value = False
    db.upsert_product.return_value = "added"

    orch = ExtractionOrchestrator(config=config, db_manager=db)

    product = Product(
        fournisseur="BigMat", designation_raw="Ciment 25kg", designation_fr="Ciment",
        famille="Ciment", prix_brut_ht=10.0, prix_remise_ht=8.50
    )

    mock_invoice = InvoiceResult(
        numero_facture="123",
        products=[product]
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
    mocker.patch.object(orch.gemini, "extract_invoice", return_value=None)

    result = orch.process_file(b"data", "empty.pdf")
    assert result.products_added == 0
