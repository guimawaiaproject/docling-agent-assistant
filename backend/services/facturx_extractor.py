"""
Factur-X / ZUGFeRD Extractor — Docling Agent v3
Extraction des lignes produits depuis le XML embarqué dans les PDF Factur-X.
Conformité facturation électronique obligatoire sept. 2026.
"""

import logging
from io import BytesIO
from typing import Optional

from lxml import etree

from backend.schemas.invoice import InvoiceExtractionResult, Product

logger = logging.getLogger(__name__)

# Namespaces Factur-X / ZUGFeRD
NS = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}


def _extract_text(el, xpath: str, default: str = "") -> str:
    """Extrait le texte du premier élément trouvé."""
    if el is None:
        return default
    found = el.xpath(xpath, namespaces=NS)
    if found and found[0].text:
        return (found[0].text or "").strip()
    return default


def _extract_float(el, xpath: str, default: float = 0.0) -> float:
    """Extrait un float du premier élément trouvé."""
    if el is None:
        return default
    found = el.xpath(xpath, namespaces=NS)
    if found and found[0].text:
        try:
            return float(found[0].text.replace(",", "."))
        except (ValueError, TypeError):
            pass
    return default


def extract_from_facturx_pdf(pdf_bytes: bytes) -> Optional[InvoiceExtractionResult]:
    """
    Extrait les produits depuis un PDF Factur-X/ZUGFeRD.
    Retourne InvoiceExtractionResult si succès, None sinon (pas Factur-X ou erreur).
    """
    try:
        from facturx import get_xml_from_pdf
    except ImportError:
        logger.debug("factur-x non installé, extraction Factur-X désactivée")
        return None

    try:
        result = get_xml_from_pdf(BytesIO(pdf_bytes), check_xsd=False)
        if not result or not result[1]:
            return None
        xml_bytes = result[1]
        parser = etree.XMLParser(resolve_entities=False, no_network=True)
        root = etree.fromstring(xml_bytes, parser=parser)
    except Exception as e:
        logger.debug("Pas de Factur-X ou erreur extraction: %s", e)
        return None

    try:
        # Fournisseur (Seller)
        seller_name = _extract_text(
            root,
            "//ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:Name",
        )
        if not seller_name:
            seller_name = _extract_text(
                root,
                "//ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:SpecifiedLegalOrganization/ram:RegistrationName",
            )
        fournisseur = seller_name or "Fournisseur"

        # Numéro et date facture
        numero_facture = _extract_text(
            root,
            "//ram:ApplicableHeaderTradeAgreement/ram:BuyerOrderReferencedDocument/ram:IssuerAssignedID",
        )
        if not numero_facture:
            numero_facture = _extract_text(
                root,
                "//rsm:ExchangedDocument/ram:ID",
            )
        date_facture = _extract_text(
            root,
            "//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString",
        )

        # Lignes produits
        line_items = root.xpath(
            "//ram:IncludedSupplyChainTradeLineItem",
            namespaces=NS,
        )
        produits: list[Product] = []

        for line in line_items:
            # Désignation
            designation_raw = _extract_text(
                line,
                ".//ram:SpecifiedTradeProduct/ram:Name",
            )
            if not designation_raw:
                designation_raw = _extract_text(
                    line,
                    ".//ram:SpecifiedTradeProduct/ram:Description",
                )
            if not designation_raw:
                continue
            designation_fr = designation_raw[:80]  # Max 80 car.

            # Prix unitaire HT
            unit_price = _extract_float(
                line,
                ".//ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice/ram:ChargeAmount",
            )
            # Quantité
            qty = _extract_float(
                line,
                ".//ram:SpecifiedLineTradeDelivery/ram:BilledQuantity",
                1.0,
            )
            if qty <= 0:
                qty = 1.0
            # Montant ligne HT
            line_amount = _extract_float(
                line,
                ".//ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount",
            )
            if line_amount == 0 and unit_price > 0:
                line_amount = unit_price * qty
            prix_remise_ht = line_amount / qty if qty > 0 else unit_price

            # Remise ligne (AllowanceCharge)
            allowance = _extract_float(
                line,
                ".//ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeAllowanceCharge[ram:ChargeIndicator/udt:Indicator='false']/ram:ActualAmount",
            )
            prix_brut_ht = unit_price
            remise_pct = 0.0
            if allowance > 0 and (line_amount + allowance) > 0:
                remise_pct = round((allowance / (line_amount + allowance)) * 100, 2)
                prix_brut_ht = unit_price / (1 - remise_pct / 100) if remise_pct < 100 else unit_price

            produits.append(
                Product(
                    fournisseur=fournisseur,
                    designation_raw=designation_raw,
                    designation_fr=designation_fr,
                    famille="Autre",
                    unite="unité",
                    prix_brut_ht=round(prix_brut_ht, 4),
                    remise_pct=remise_pct,
                    prix_remise_ht=round(prix_remise_ht, 4),
                    prix_ttc_iva21=round(prix_remise_ht * 1.21, 4),
                    numero_facture=numero_facture or None,
                    date_facture=date_facture or None,
                    confidence="high",
                )
            )

        if not produits:
            return None

        logger.info("Factur-X: %d produits extraits du XML (sans IA)", len(produits))
        return InvoiceExtractionResult(
            produits=produits,
            fournisseur_detecte=fournisseur,
            numero_facture=numero_facture or None,
            date_facture=date_facture or None,
            langue_detectee="fr",
            nb_lignes_brutes=len(produits),
            tokens_used=0,
        )

    except Exception as e:
        logger.warning("Erreur parsing Factur-X: %s", e)
        return None
