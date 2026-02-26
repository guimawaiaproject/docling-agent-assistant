"""Tests pour GeminiService (parsing, schema) — zéro mock, pas d'appel API."""
import json
import pytest
from backend.schemas.invoice import Product, InvoiceExtractionResult
from backend.services.gemini_service import RESPONSE_SCHEMA, SYSTEM_PROMPT


class TestResponseSchema:
    def test_schema_has_produits(self):
        assert "produits" in RESPONSE_SCHEMA["properties"]
        assert "produits" in RESPONSE_SCHEMA["required"]

    def test_schema_produit_required_fields(self):
        item_schema = RESPONSE_SCHEMA["properties"]["produits"]["items"]
        required = item_schema["required"]
        assert "fournisseur" in required
        assert "designation_raw" in required
        assert "designation_fr" in required
        assert "prix_brut_ht" in required
        assert "prix_remise_ht" in required

    def test_schema_is_valid_json_schema(self):
        serialized = json.dumps(RESPONSE_SCHEMA)
        parsed = json.loads(serialized)
        assert parsed["type"] == "object"


class TestSystemPrompt:
    def test_prompt_mentions_btp(self):
        assert "BTP" in SYSTEM_PROMPT

    def test_prompt_mentions_familles(self):
        assert "Armature" in SYSTEM_PROMPT
        assert "Plomberie" in SYSTEM_PROMPT

    def test_prompt_mentions_arithmetic(self):
        assert "prix_remise_ht" in SYSTEM_PROMPT
        assert "1.21" in SYSTEM_PROMPT

    def test_prompt_mentions_confidence(self):
        assert "confidence" in SYSTEM_PROMPT
        assert "low" in SYSTEM_PROMPT


class TestGeminiJsonParsing:
    def test_parse_structured_response(self):
        raw = json.dumps({
            "fournisseur_detecte": "BigMat",
            "numero_facture": "F-2023-001",
            "date_facture": "15/10/2023",
            "langue_detectee": "ca",
            "nb_lignes_brutes": 2,
            "produits": [
                {
                    "fournisseur": "BigMat",
                    "designation_raw": "CIMENT PORTLAND 42.5R 25KG",
                    "designation_fr": "Ciment Portland 42.5R 25kg",
                    "famille": "Maçonnerie",
                    "unite": "sac",
                    "prix_brut_ht": 5.80,
                    "remise_pct": 15.0,
                    "prix_remise_ht": 4.93,
                    "prix_ttc_iva21": 5.97,
                    "confidence": "high"
                },
                {
                    "fournisseur": "BigMat",
                    "designation_raw": "ARENA FINA 0/2 25KG",
                    "designation_fr": "Sable fin 0/2 25kg",
                    "famille": "Maçonnerie",
                    "unite": "sac",
                    "prix_brut_ht": 2.40,
                    "remise_pct": 0,
                    "prix_remise_ht": 2.40,
                    "prix_ttc_iva21": 2.90,
                    "confidence": "high"
                }
            ]
        })
        data = json.loads(raw)
        produits_valides = []
        for p in data["produits"]:
            p["fournisseur"] = p.get("fournisseur") or data.get("fournisseur_detecte", "Inconnu")
            produits_valides.append(Product(**p))

        result = InvoiceExtractionResult(
            produits=produits_valides,
            fournisseur_detecte=data["fournisseur_detecte"],
            tokens_used=1500,
        )
        assert len(result.produits) == 2
        assert result.produits[0].designation_fr == "Ciment Portland 42.5R 25kg"
        assert result.fournisseur_detecte == "BigMat"

    def test_parse_empty_produits(self):
        result = InvoiceExtractionResult(produits=[], fournisseur_detecte="Unknown")
        assert len(result.produits) == 0

    def test_invalid_product_skipped(self):
        data = {
            "produits": [
                {"fournisseur": "", "designation_raw": "", "designation_fr": "", "prix_brut_ht": 0, "prix_remise_ht": 0},
                {"fournisseur": "OK", "designation_raw": "X", "designation_fr": "Y", "prix_brut_ht": 10, "prix_remise_ht": 10},
            ]
        }
        produits = []
        for p in data["produits"]:
            try:
                produits.append(Product(**p))
            except Exception:
                pass
        assert len(produits) == 1
        assert produits[0].fournisseur == "OK"
