"""
BytezService — API unifiée 100k+ modèles (docs.bytez.com)
- Document Question Answering : extraction factures
- Image-to-Text / Chat multimodal : fallback Gemini
- Feature Extraction : embeddings pour similarité catalogue
"""

import base64
import json
import logging
import re

import httpx

from core.config import Config
from schemas.invoice import InvoiceExtractionResult, Product

logger = logging.getLogger(__name__)

BYTEZ_BASE = "https://api.bytez.com/models/v2"

# Modèles document-QA / image-text adaptés factures BTP
DOC_QA_MODELS = [
    "cloudqi/CQI_Visual_Question_Awnser_PT_v0",  # Document QA
    "google/gemma-3-4b-it",  # Multimodal (nécessite provider-key Gemini)
]

# Modèle embeddings pour similarité catalogue (recherche sémantique)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


async def _bytez_request(
    model_id: str,
    payload: dict,
    *,
    provider_key: str | None = None,
    timeout: float = 120.0,
) -> dict:
    """Appel HTTP POST vers Bytez API."""
    key = Config.BYTEZ_API_KEY
    if not key:
        raise RuntimeError("BYTEZ_API_KEY manquante dans .env")
    url = f"{BYTEZ_BASE}/{model_id}"
    headers = {
        "Authorization": key,
        "Content-Type": "application/json",
    }
    if provider_key and "google/" in model_id:
        headers["provider-key"] = provider_key
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def document_qa_extract(
    image_base64: str,
    question: str,
    model_id: str = "cloudqi/CQI_Visual_Question_Awnser_PT_v0",
) -> str | None:
    """
    Document Question Answering — pose une question sur une image de document.
    Retourne la réponse texte ou None en cas d'erreur.
    """
    payload = {
        "question": question,
        "base64": f"data:image/jpeg;base64,{image_base64}",
    }
    try:
        data = await _bytez_request(model_id, payload)
        if data.get("error"):
            logger.warning("Bytez doc-QA error: %s", data["error"])
            return None
        out = data.get("output")
        return str(out) if out is not None else None
    except Exception as e:
        logger.warning("Bytez doc-QA failed: %s", e)
        return None


async def image_chat_extract(
    image_base64: str,
    prompt: str,
    model_id: str = "google/gemma-3-4b-it",
) -> str | None:
    """
    Chat multimodal image+texte — pour extraction structurée.
    Utilise provider-key (GEMINI_API_KEY) si modèle Google.
    """
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "base64": image_base64},
                ],
            }
        ],
        "params": {"temperature": 0.1, "max_new_tokens": 4096},
    }
    try:
        provider_key = Config.GEMINI_API_KEY if "google/" in model_id else None
        data = await _bytez_request(model_id, payload, provider_key=provider_key)
        if data.get("error"):
            logger.warning("Bytez image-chat error: %s", data["error"])
            return None
        out = data.get("output")
        if isinstance(out, list) and out:
            msg = out[0]
            out = msg.get("content", msg) if isinstance(msg, dict) else msg
        return str(out) if out is not None else None
    except Exception as e:
        logger.warning("Bytez image-chat failed: %s", e)
        return None


async def feature_extraction(
    text: str,
    model_id: str = EMBEDDING_MODEL,
) -> list[float] | None:
    """
    Feature Extraction — convertit un texte en vecteur (embedding).
    Usage : similarité catalogue, recherche sémantique "ciment 42.5" ≈ "Ciment Portland 42.5R".
    """
    if not Config.BYTEZ_API_KEY or not text:
        return None
    payload = {"text": str(text)[:8192]}
    try:
        data = await _bytez_request(model_id, payload, timeout=30.0)
        if data.get("error"):
            logger.warning("Bytez feature-extraction error: %s", data["error"])
            return None
        out = data.get("output")
        if isinstance(out, list) and out:
            return [float(x) for x in out]
        return None
    except Exception as e:
        logger.warning("Bytez feature-extraction failed: %s", e)
        return None


def _parse_json_from_response(text: str) -> dict | None:
    """Extrait un objet JSON de la réponse texte."""
    if not text:
        return None
    json_match = re.search(r"\{[\s\S]*\}", text)
    if not json_match:
        return None
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        return None


async def extract_invoice_fallback(
    image_bytes: bytes,
    filename: str,
) -> InvoiceExtractionResult | None:
    """
    Fallback Bytez quand Gemini échoue (rate limit, indisponible).
    Utilise document-QA avec questions ciblées ou chat multimodal.
    """
    if not Config.BYTEZ_API_KEY:
        return None
    b64 = base64.b64encode(image_bytes).decode("ascii")
    prompt = """Extraie TOUTES les lignes produit de cette facture BTP.
Retourne UNIQUEMENT un JSON valide avec cette structure exacte:
{"produits":[{"fournisseur":"","designation_raw":"","designation_fr":"","famille":"","unite":"","prix_brut_ht":0,"remise_pct":0,"prix_remise_ht":0,"prix_ttc_iva21":0,"confidence":"high"}],"fournisseur_detecte":"","numero_facture":"","date_facture":"","langue_detectee":"fr"}
Familles BTP: Armature, Cloison, Plomberie, Électricité, Menuiserie, Carrelage, Isolation, Peinture, Outillage, Maçonnerie, Terrassement, Autre."""
    raw = await image_chat_extract(b64, prompt)
    if not raw:
        raw = await document_qa_extract(
            b64,
            "Liste toutes les lignes produit avec désignation, quantité, prix unitaire HT et prix total. Format JSON.",
        )
    if not raw:
        return None
    data = _parse_json_from_response(raw)
    if not data or "produits" not in data:
        return None
    fournisseur_default = data.get("fournisseur_detecte") or "Inconnu"
    produits = []
    for p in data.get("produits", []):
        try:
            p.setdefault("fournisseur", fournisseur_default)
            p.setdefault("designation_raw", p.get("designation_fr", ""))
            p.setdefault("designation_fr", p.get("designation_raw", ""))
            produits.append(Product(**p))
        except Exception:
            continue
    if not produits:
        return None
    return InvoiceExtractionResult(
        produits=produits,
        fournisseur_detecte=data.get("fournisseur_detecte", ""),
        numero_facture=data.get("numero_facture", ""),
        date_facture=data.get("date_facture", ""),
        langue_detectee=data.get("langue_detectee", "fr"),
        nb_lignes_brutes=len(produits),
        tokens_used=0,
    )
