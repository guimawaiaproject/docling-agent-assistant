"""
Pydantic schemas for invoice data and product catalogue.
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import datetime


class Product(BaseModel):
    """A single product line from an invoice."""

    fournisseur: str = Field(..., description="Supplier name (e.g. BigMat)")
    designation_raw: str = Field(..., description="Original designation (Catalan/Spanish)")
    designation_fr: str = Field(..., description="French translation")
    famille: str = Field(..., description="Product family (Ciment, Finition, etc.)")
    unite: str = Field(default="unité", description="Unit of measure (sac, kg, m², ml...)")
    prix_brut_ht: float = Field(default=0.0, description="Unit price before discount")
    remise_pct: Optional[float] = Field(default=None, description="Discount percentage")
    prix_remise_ht: float = Field(default=0.0, description="Discounted unit price HT")
    prix_ttc_iva21: float = Field(default=0.0, description="Price with 21% IVA")

    @model_validator(mode="after")
    def validate_prices(self) -> "Product":
        if self.prix_ttc_iva21 == 0.0 and self.prix_remise_ht > 0:
            self.prix_ttc_iva21 = round(self.prix_remise_ht * 1.21, 2)
        return self


class InvoiceResult(BaseModel):
    """Result of processing a single invoice."""
    numero_facture: str = Field(default="")
    date_facture: str = Field(default="")
    fournisseur: str = Field(default="")
    products: List[Product] = Field(default_factory=list)


class ProcessingResult(BaseModel):
    """Result summary after processing."""
    invoice: InvoiceResult
    file_hash: str
    products_added: int = 0
    products_updated: int = 0
    was_cached: bool = False
