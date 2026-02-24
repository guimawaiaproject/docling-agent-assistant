import pytest
import sqlite3
import pandas as pd
from backend.core.db_manager import DBManager
from backend.schemas.invoice import Product

@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test.db"
    return DBManager(str(db_path))

def test_db_init(test_db):
    stats = test_db.get_stats()
    assert stats["products"] == 0
    assert stats["invoices"] == 0

def test_upsert_and_catalogue(test_db):
    product = Product(
        fournisseur="BigMat", designation_raw="Ciment 25kg", designation_fr="Ciment",
        famille="Ciment", unite="sac", prix_brut_ht=10.0, remise_pct=0,
        prix_remise_ht=8.50, prix_ttc_iva21=10.28
    )
    action = test_db.upsert_product(product, "F123", "2026-01-01")
    assert action == "added"

    # Update same product
    product.prix_remise_ht = 9.0
    action2 = test_db.upsert_product(product, "F124", "2026-02-01")
    assert action2 == "updated"

    # Check catalogue
    df = test_db.get_catalogue()
    assert len(df) == 1
    assert df.iloc[0]["prix_remise_ht"] == 9.0

def test_invoice_saving(test_db):
    test_db.save_invoice("hash123", "test.pdf", "BigMat", "F123", "2026-01-01", 1)
    assert test_db.is_invoice_processed("hash123") is True
    assert test_db.is_invoice_processed("unknown") is False
