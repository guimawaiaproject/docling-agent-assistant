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
from backend.schemas.invoice import InvoiceResult

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_DELAY = 5  # seconds

SYSTEM_PROMPT = """Tu es un expert comptable BTP spécialisé dans les factures franco-espagnoles et catalanes.

MISSION : Extraire TOUTES les lignes produit de cette facture et retourner un JSON valide.

RÈGLES STRICTES :
1. Extraire chaque ligne produit individuellement, même si la facture en contient 50+
2. Traduire designation_raw (Català/Español) → designation_fr (Français professionnel BTP)
3. Classifier famille parmi : Armature, Cloison, Climatisation, Plomberie, Électricité,
   Menuiserie, Couverture, Carrelage, Isolation, Peinture, Outillage, Consommable, Autre
4. Vérifier : prix_remise_ht = prix_brut_ht * (1 - remise_pct/100)
5. Vérifier : prix_ttc_iva21 = prix_remise_ht * 1.21
6. Si une vérification échoue → ajouter "confidence": "low" sur la ligne concernée
7. Si un champ est illisible → mettre null, jamais inventer

FORMAT JSON OBLIGATOIRE :
{
  "fournisseur": "string",
  "numero_facture": "string",
  "date_facture": "DD/MM/YYYY",
  "products": [
    {
      "fournisseur": "string",
      "designation_raw": "string",
      "designation_fr": "string",
      "famille": "string",
      "unite": "string (sac|kg|m²|ml|unité|litre|rouleau)",
      "prix_brut_ht": float,
      "remise_pct": float,
      "prix_remise_ht": float,
      "prix_ttc_iva21": float,
      "confidence": "high|low"
    }
  ]
}

Retourne UNIQUEMENT le JSON, sans markdown, sans commentaire.
"""


class GeminiService:
    """Multimodal invoice extraction via Gemini 3 Flash."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._client = None

        if config.has_gemini_key:
            self._client = genai.Client(api_key=config.gemini_api_key)
            logger.info("Gemini client initialized (gemini-3-flash)")
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
                    model="gemini-3-flash",
                    contents=[SYSTEM_PROMPT, file_part],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                        tools=[{"code_execution": {}}],
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

        prompt = SYSTEM_PROMPT + "\n\nVoici le texte OCR de la facture :\n\n" + ocr_text

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model="gemini-3-flash",
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                        tools=[{"code_execution": {}}],
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
