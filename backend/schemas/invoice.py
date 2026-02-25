"""
Schémas Pydantic v2 — Docling Agent v3
Validation stricte des données extraites par Gemini.
Auto-calcul TVA, confidence score, normalisation multilingue.
"""

from typing import Optional
from pydantic import BaseModel, Field, model_validator


FAMILLES_VALIDES = {
    "Armature", "Cloison", "Climatisation", "Plomberie", "Électricité",
    "Menuiserie", "Couverture", "Carrelage", "Isolation", "Peinture",
    "Outillage", "Consommable", "Maçonnerie", "Terrassement", "Autre"
}


class Product(BaseModel):
    fournisseur:      str            = Field(..., min_length=1)
    designation_raw:  str            = Field(..., min_length=1)   # Original CA/ES
    designation_fr:   str            = Field(..., min_length=1)   # Traduit FR
    famille:          str            = Field(default="Autre")
    unite:            str            = Field(default="unité")
    prix_brut_ht:     float          = Field(default=0.0, ge=0)
    remise_pct:       float          = Field(default=0.0, ge=0, le=100)
    prix_remise_ht:   float          = Field(default=0.0, ge=0)
    prix_ttc_iva21:   float          = Field(default=0.0, ge=0)
    numero_facture:   Optional[str]  = None
    date_facture:     Optional[str]  = None
    confidence:       str            = Field(default="high")      # high | low

    @model_validator(mode="after")
    def validate_and_compute(self) -> "Product":
        # ── Normaliser famille ──────────────────────────────────
        if self.famille not in FAMILLES_VALIDES:
            self.famille = "Autre"

        # ── Auto-calcul prix_remise_ht ──────────────────────────
        if self.prix_brut_ht > 0 and self.remise_pct > 0:
            computed = round(self.prix_brut_ht * (1 - self.remise_pct / 100), 4)
            if self.prix_remise_ht == 0:
                self.prix_remise_ht = computed
            elif computed > 0:
                ecart = abs(self.prix_remise_ht - computed) / computed
                if ecart > 0.02:
                    self.confidence = "low"
            else:
                self.confidence = "low"

        # ── Auto-calcul TVA IVA 21% ─────────────────────────────
        if self.prix_remise_ht > 0:
            self.prix_ttc_iva21 = round(self.prix_remise_ht * 1.21, 4)

        # ── Confidence low si prix = 0 ──────────────────────────
        if self.prix_remise_ht == 0:
            self.confidence = "low"

        return self


class InvoiceExtractionResult(BaseModel):
    produits:         list[Product]
    fournisseur_detecte: Optional[str] = None
    numero_facture:   Optional[str]    = None
    date_facture:     Optional[str]    = None
    langue_detectee:  str              = "es"   # es | ca | fr
    nb_lignes_brutes: int              = 0
    tokens_used:      int              = 0


class BatchSaveRequest(BaseModel):
    produits: list[dict]
    source:   str = "pc"
