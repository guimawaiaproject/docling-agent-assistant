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

    res = orch.process_file(b"pdf data", "facture.pdf")

    assert res.products_added == 1
    stats = db.get_stats()
    assert stats["products"] == 1
    assert stats["invoices"] == 1

    df = db.get_catalogue()
    assert len(df) == 1
    assert df.iloc[0]["designation_fr"] == "Ciment"
    assert df.iloc[0]["prix_remise_ht"] == 8.50
