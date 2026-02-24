import pytest
from unittest.mock import MagicMock
from backend.core.orchestrator import ExtractionOrchestrator
from backend.schemas.invoice import InvoiceResult, Product

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.is_invoice_processed.return_value = False
    db.upsert_product.return_value = "added"
    return db

@pytest.fixture
def mock_config():
    return MagicMock()

def test_orchestrator_cache_hit(mock_db, mock_config):
    mock_db.is_invoice_processed.return_value = True
    orch = ExtractionOrchestrator(config=mock_config, db_manager=mock_db)

    result = orch.process_file(b"data", "test.pdf")
    assert result.was_cached is True
    assert result.products_added == 0

def test_orchestrator_success(mock_db, mock_config, mocker):
    orch = ExtractionOrchestrator(config=mock_config, db_manager=mock_db)

    mock_invoice = InvoiceResult(
        numero_facture="123",
        date_facture="01/01/2026",
        fournisseur="BigMat",
        products=[Product(
            fournisseur="BigMat", designation_raw="Sable", designation_fr="Sable",
            famille="Granulat", unite="kg", prix_brut_ht=10.0, remise_pct=0,
            prix_remise_ht=10.0, prix_ttc_iva21=12.10
        )]
    )
    mocker.patch.object(orch.gemini, "extract_invoice", return_value=mock_invoice)

    result = orch.process_file(b"data", "test.pdf")
    assert result.was_cached is False
    assert result.products_added == 1
    mock_db.save_invoice.assert_called_once()
