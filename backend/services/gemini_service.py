"""
GeminiService - Docling Agent v3 / v4
Extraction multilingue CA/ES/FR avec Gemini (Flash / Pro).
- SDK google-genai avec async natif (client.aio)
- Structured Output (response_schema) pour parsing fiable
- Fallback regex si response_schema non supporte
- Retry automatique sur rate limit 429
"""

import asyncio
import json
import logging
import re
from typing import Optional

from google import genai
from google.genai import types

from backend.core.config import Config
from backend.schemas.invoice import InvoiceExtractionResult, Product

logger = logging.getLogger(__name__)

_gemini_cache: dict[str, "GeminiService"] = {}

SYSTEM_PROMPT = """Tu es un expert-comptable BTP specialise dans les factures
fournisseurs franco-espagnoles et catalanes (BigMat, Punto Madera, Leroy Merlin ES, etc.).

MISSION : Extraire CHAQUE ligne produit de la facture et retourner un JSON strict.

LANGUES : La facture peut etre en Catalan, Espagnol ou Francais. Traduis TOUJOURS
designation_fr en Francais clair et concis (max 80 caracteres).

FAMILLES BTP autorisees (choisir la plus proche) :
Armature, Cloison, Climatisation, Plomberie, Électricité, Menuiserie,
Couverture, Carrelage, Isolation, Peinture, Outillage, Consommable,
Maçonnerie, Terrassement, Autre

VERIFICATION ARITHMETIQUE OBLIGATOIRE :
- prix_remise_ht = prix_brut_ht x (1 - remise_pct/100)
- prix_ttc_iva21  = prix_remise_ht x 1.21
- Si ecart > 2% entre valeur facturee et calcul -> confidence: "low"
- Si prix_remise_ht = 0 ou illisible -> confidence: "low"

REGLES STRICTES :
- N'invente AUCUN prix. Si illisible -> confidence: "low" et mettre 0.
- Une ligne JSON par ligne produit de la facture.
- Ignorer les totaux, sous-totaux, frais de port.
- Si la facture est floue ou incomplete -> traiter ce qui est lisible.
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "fournisseur_detecte": {"type": "string"},
        "numero_facture": {"type": "string"},
        "date_facture": {"type": "string"},
        "langue_detectee": {"type": "string", "enum": ["ca", "es", "fr"]},
        "nb_lignes_brutes": {"type": "integer"},
        "produits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fournisseur": {"type": "string"},
                    "designation_raw": {"type": "string"},
                    "designation_fr": {"type": "string"},
                    "famille": {"type": "string"},
                    "unite": {"type": "string"},
                    "prix_brut_ht": {"type": "number"},
                    "remise_pct": {"type": "number"},
                    "prix_remise_ht": {"type": "number"},
                    "prix_ttc_iva21": {"type": "number"},
                    "numero_facture": {"type": "string"},
                    "date_facture": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "low"]}
                },
                "required": [
                    "fournisseur", "designation_raw", "designation_fr",
                    "prix_brut_ht", "prix_remise_ht"
                ]
            }
        }
    },
    "required": ["produits"]
}


class GeminiService:

    @classmethod
    def get_or_create(cls, model_id: Optional[str] = None) -> "GeminiService":
        """Retourne une instance mise en cache par model_id."""
        key = model_id or Config.DEFAULT_MODEL
        if key not in _gemini_cache:
            _gemini_cache[key] = cls(model_id=key)
        return _gemini_cache[key]

    def __init__(self, model_id: Optional[str] = None):
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY non configuree")

        model_id = model_id or Config.DEFAULT_MODEL
        model_name = Config.MODELS_DISPONIBLES.get(
            model_id,
            Config.MODELS_DISPONIBLES.get("gemini-2.5-flash", "models/gemini-2.5-flash")
        )
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")

        self._client = genai.Client(api_key=api_key)
        self.model_id = model_id
        self.model_name = model_name
        logger.info("GeminiService init: %s (google-genai async)", model_name)

    async def extract_from_bytes_async(
        self,
        file_bytes: bytes,
        mime_type: str,
        filename: str = "facture",
    ) -> InvoiceExtractionResult:
        """Extraction async via client.aio (sans asyncio.to_thread)."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                contents = [
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    types.Part.from_text(text="Analyse cette facture et retourne le JSON demande."),
                ]
                config = types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    system_instruction=SYSTEM_PROMPT,
                )

                async with self._client.aio as aclient:
                    response = await aclient.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config=config,
                    )

                raw_text = response.text or ""
                usage = getattr(response, "usage_metadata", None)
                tokens = usage.total_token_count if usage else 0

                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError:
                    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                    if not json_match:
                        raise ValueError("Pas de JSON dans la reponse: %s" % raw_text[:200])
                    data = json.loads(json_match.group())

                produits_valides = []
                for p in data.get("produits", []):
                    try:
                        p["fournisseur"] = p.get("fournisseur") or data.get("fournisseur_detecte", "Inconnu")
                        produits_valides.append(Product(**p))
                    except Exception as e:
                        logger.warning("Produit ignore (validation): %s", e)

                result = InvoiceExtractionResult(
                    produits=produits_valides,
                    fournisseur_detecte=data.get("fournisseur_detecte"),
                    numero_facture=data.get("numero_facture"),
                    date_facture=data.get("date_facture"),
                    langue_detectee=data.get("langue_detectee", "es"),
                    nb_lignes_brutes=data.get("nb_lignes_brutes", len(produits_valides)),
                    tokens_used=tokens,
                )

                logger.info("OK %s: %d produits (%d tokens)", filename, len(produits_valides), tokens)
                return result

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = 2 ** (attempt + 1)
                    logger.warning("Rate limit Gemini, attente %ds (%d/%d)", wait, attempt + 1, max_retries)
                    await asyncio.sleep(wait)
                    continue
                logger.error("Erreur Gemini (%s): %s", filename, e)
                raise

        raise RuntimeError("Gemini rate limit persistant apres %d tentatives" % max_retries)
