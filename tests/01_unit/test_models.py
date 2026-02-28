"""
Tests unitaires des modèles Pydantic — zéro mock.
Données Faker pour cas réalistes.
"""

import pytest
from faker import Faker
from pydantic import ValidationError

from backend.schemas.invoice import (
    FAMILLES_VALIDES,
    BatchSaveRequest,
    InvoiceExtractionResult,
    Product,
)

fake = Faker("fr_FR")


class TestProduct:
    def test_basic_product_with_discount(self):
        p = Product(
            fournisseur="BigMat",
            designation_raw="CIMENT PORTLAND 42.5R",
            designation_fr="Ciment Portland 42.5R",
            prix_brut_ht=10.0,
            remise_pct=10.0,
        )
        assert p.fournisseur == "BigMat"
        assert p.prix_remise_ht == 9.0
        assert p.prix_ttc_iva21 == pytest.approx(10.89, rel=1e-2)
        assert p.confidence == "high"

    def test_product_with_faker_data(self):
        """Données dynamiques Faker — jamais hardcodées."""
        fournisseur = fake.company()[:50]
        designation_raw = fake.catch_phrase()[:80]
        designation_fr = fake.catch_phrase()[:80]
        prix = round(fake.random.uniform(1.0, 200.0), 2)
        p = Product(
            fournisseur=fournisseur,
            designation_raw=designation_raw,
            designation_fr=designation_fr,
            prix_brut_ht=prix,
            prix_remise_ht=prix,
        )
        assert p.fournisseur == fournisseur
        assert p.designation_raw == designation_raw
        assert p.prix_remise_ht == prix
        assert p.prix_ttc_iva21 == pytest.approx(prix * 1.21, rel=1e-3)
        assert p.famille == "Autre"

    def test_zero_price_is_low_confidence(self):
        p = Product(
            fournisseur="T", designation_raw="T", designation_fr="T", prix_brut_ht=0
        )
        assert p.confidence == "low"
        assert p.prix_remise_ht == 0.0

    def test_invalid_famille_falls_back_to_autre(self):
        p = Product(
            fournisseur="F",
            designation_raw="R",
            designation_fr="F",
            famille="Bidule",
        )
        assert p.famille == "Autre"

    def test_all_valid_familles_accepted(self):
        for fam in FAMILLES_VALIDES:
            p = Product(
                fournisseur="F",
                designation_raw="R",
                designation_fr="F",
                famille=fam,
                prix_remise_ht=1,
            )
            assert p.famille == fam

    def test_arithmetic_mismatch_sets_low_confidence(self):
        p = Product(
            fournisseur="F",
            designation_raw="R",
            designation_fr="F",
            prix_brut_ht=100.0,
            remise_pct=10.0,
            prix_remise_ht=50.0,
        )
        assert p.confidence == "low"

    def test_arithmetic_match_keeps_high_confidence(self):
        p = Product(
            fournisseur="F",
            designation_raw="R",
            designation_fr="F",
            prix_brut_ht=100.0,
            remise_pct=10.0,
            prix_remise_ht=90.0,
        )
        assert p.confidence == "high"

    def test_auto_ttc_calculation(self):
        p = Product(
            fournisseur="F",
            designation_raw="R",
            designation_fr="F",
            prix_remise_ht=100.0,
        )
        assert p.prix_ttc_iva21 == pytest.approx(121.0, rel=1e-3)

    def test_auto_calcul_remise_when_zero(self):
        p = Product(
            fournisseur="F",
            designation_raw="R",
            designation_fr="F",
            prix_brut_ht=200.0,
            remise_pct=25.0,
        )
        assert p.prix_remise_ht == 150.0
        assert p.prix_ttc_iva21 == pytest.approx(181.5, rel=1e-3)

    def test_default_values(self):
        p = Product(fournisseur="F", designation_raw="R", designation_fr="F")
        assert p.famille == "Autre"
        assert p.unite == "unité"
        assert p.numero_facture is None
        assert p.date_facture is None

    def test_empty_fournisseur_rejected(self):
        with pytest.raises(ValidationError):
            Product(fournisseur="", designation_raw="R", designation_fr="F")

    def test_negative_prix_rejected(self):
        with pytest.raises(ValidationError):
            Product(
                fournisseur="F",
                designation_raw="R",
                designation_fr="F",
                prix_brut_ht=-5,
            )

    def test_remise_over_100_rejected(self):
        with pytest.raises(ValidationError):
            Product(
                fournisseur="F",
                designation_raw="R",
                designation_fr="F",
                remise_pct=150,
            )

    def test_small_ecart_within_tolerance(self):
        p = Product(
            fournisseur="F",
            designation_raw="R",
            designation_fr="F",
            prix_brut_ht=100.0,
            remise_pct=10.0,
            prix_remise_ht=89.9,
        )
        assert p.confidence == "high"

    def test_edge_case_special_chars(self):
        """Caractères spéciaux dans les champs."""
        p = Product(
            fournisseur="Société & Cie",
            designation_raw="Produit é à ü ñ 中文",
            designation_fr="Produit é à ü ñ",
            prix_remise_ht=10.0,
        )
        assert "é" in p.designation_fr
        assert p.prix_ttc_iva21 == pytest.approx(12.1, rel=1e-3)


class TestInvoiceExtractionResult:
    def test_empty_products(self):
        r = InvoiceExtractionResult(produits=[])
        assert len(r.produits) == 0
        assert r.tokens_used == 0
        assert r.langue_detectee == "es"

    def test_with_multiple_products(self):
        products = [
            Product(
                fournisseur="A",
                designation_raw="X",
                designation_fr="Y",
                prix_remise_ht=10,
            ),
            Product(
                fournisseur="B",
                designation_raw="Z",
                designation_fr="W",
                prix_remise_ht=20,
            ),
        ]
        r = InvoiceExtractionResult(
            produits=products,
            fournisseur_detecte="A",
            tokens_used=500,
        )
        assert len(r.produits) == 2
        assert r.fournisseur_detecte == "A"

    def test_defaults(self):
        r = InvoiceExtractionResult(produits=[])
        assert r.fournisseur_detecte is None
        assert r.numero_facture is None
        assert r.date_facture is None
        assert r.nb_lignes_brutes == 0


class TestBatchSaveRequest:
    def test_basic(self):
        req = BatchSaveRequest(produits=[{"a": 1}], source="mobile")
        assert req.source == "mobile"

    def test_default_source(self):
        req = BatchSaveRequest(produits=[])
        assert req.source == "pc"

    def test_empty_produits(self):
        req = BatchSaveRequest(produits=[])
        assert len(req.produits) == 0
