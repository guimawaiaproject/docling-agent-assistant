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
