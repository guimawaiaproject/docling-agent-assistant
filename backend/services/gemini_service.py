"""
Gemini AI service — multimodal invoice extraction.
Sends PDF/image directly to Gemini 2.5 Flash for structured extraction.
"""
import json
import logging
import time
import re
from typing import Optional

from google import genai
from google.genai import types

from backend.core.config import AppConfig
from backend.schemas.invoice import InvoiceResult, Product

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_DELAY = 5  # seconds

EXTRACTION_PROMPT = """Tu es un expert comptable spécialisé en matériaux de construction (BTP).
Analyse cette facture et extrais TOUTES les lignes d'articles.

Pour chaque article, fournis :
- "fournisseur": le nom du fournisseur (en-tête de la facture)
- "designation_raw": le nom exact tel qu'écrit sur la facture (souvent en Catalan ou Espagnol)
- "designation_fr": la traduction en Français du nom de l'article
- "famille": la catégorie (Ciment, Gros œuvre, Armature, Quincaillerie, Treillis, Maçonnerie, Ragréage, Finition, Cloison, Plâtre, Additif, Granulat, Évacuation, Colle, Logistique, Outillage, Étanchéité, Isolation, Peinture, Électricité, Plomberie, ou autre)
- "unite": l'unité de mesure (sac, kg, m², ml, m, unité, t, litre, rouleau, pièce)
- "prix_brut_ht": le prix unitaire brut HT
- "remise_pct": le pourcentage de remise (null si aucune)
- "prix_remise_ht": le prix unitaire après remise HT
- "prix_ttc_iva21": le prix unitaire TTC avec IVA 21%

Extrais aussi les métadonnées de la facture :
- "numero_facture": le numéro de facture
- "date_facture": la date de la facture (format JJ/MM/AAAA)
- "fournisseur": le nom du fournisseur

Réponds UNIQUEMENT en JSON strict avec cette structure :
{
  "numero_facture": "...",
  "date_facture": "JJ/MM/AAAA",
  "fournisseur": "...",
  "products": [
    {
      "fournisseur": "...",
      "designation_raw": "...",
      "designation_fr": "...",
      "famille": "...",
      "unite": "...",
      "prix_brut_ht": 0.0,
      "remise_pct": null,
      "prix_remise_ht": 0.0,
      "prix_ttc_iva21": 0.0
    }
  ]
}
"""


class GeminiService:
    """Multimodal invoice extraction via Gemini 2.0 Flash."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._client = None

        if config.has_gemini_key:
            self._client = genai.Client(api_key=config.gemini_api_key)
            logger.info("Gemini client initialized (gemini-2.5-flash)")
        else:
            logger.warning("Gemini API key missing — extraction disabled.")

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def _parse_retry_delay(self, error_msg: str) -> int:
        """Extract retry delay from 429 error message."""
        match = re.search(r"retry in (\d+)", str(error_msg))
        return int(match.group(1)) + 2 if match else BASE_DELAY

    def extract_invoice(
        self, file_bytes: bytes, mime_type: str = "application/pdf"
    ) -> Optional[InvoiceResult]:
        """
        Extract invoice data with automatic retry on rate limit (429).
        """
        if not self._client:
            logger.error("Cannot extract: Gemini client not initialized.")
            return None

        file_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[EXTRACTION_PROMPT, file_part],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    ),
                )

                data = json.loads(response.text)
                result = InvoiceResult(**data)
                logger.info(
                    f"Extracted {len(result.products)} products from invoice "
                    f"{result.numero_facture} ({result.fournisseur})"
                )
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Gemini returned invalid JSON: {e}")
                return None
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    delay = self._parse_retry_delay(error_str)
                    logger.warning(
                        f"Rate limited (attempt {attempt}/{MAX_RETRIES}). "
                        f"Waiting {delay}s..."
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Gemini extraction error: {e}")
                    return None

        logger.error(f"Failed after {MAX_RETRIES} retries (rate limit).")
        return None

    def extract_from_text(self, ocr_text: str) -> Optional[InvoiceResult]:
        """Extract structured data from pre-OCR'd text (fewer tokens)."""
        if not self._client:
            logger.error("Cannot extract: Gemini client not initialized.")
            return None

        prompt = EXTRACTION_PROMPT + "\n\nVoici le texte OCR de la facture :\n\n" + ocr_text

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    ),
                )
                data = json.loads(response.text)
                result = InvoiceResult(**data)
                logger.info(
                    f"[text mode] Extracted {len(result.products)} products "
                    f"from invoice {result.numero_facture}"
                )
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Gemini returned invalid JSON: {e}")
                return None
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    delay = self._parse_retry_delay(error_str)
                    logger.warning(
                        f"Rate limited (attempt {attempt}/{MAX_RETRIES}). "
                        f"Waiting {delay}s..."
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Gemini extraction error: {e}")
                    return None

        logger.error(f"Failed after {MAX_RETRIES} retries (rate limit).")
        return None
