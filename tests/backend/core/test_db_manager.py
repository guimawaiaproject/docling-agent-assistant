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
