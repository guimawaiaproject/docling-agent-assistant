"""
OCR.space service — extract raw text from PDF/images.
Used as a pre-processing step to reduce Gemini token usage.
API docs: https://ocr.space/OCRAPI
"""
import base64
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

API_URL = "https://api.ocr.space/parse/image"


class OcrSpaceService:
    """Extract raw text from documents via OCR.space API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._available = bool(api_key)
        if self._available:
            logger.info("OCR.space service initialized")

    @property
    def is_available(self) -> bool:
        return self._available

    def extract_text(
        self, file_bytes: bytes, filename: str, language: str = "spa"
    ) -> Optional[str]:
        """
        Send file to OCR.space and get raw text.

        Args:
            file_bytes: Raw file content.
            filename: Original filename (for extension detection).
            language: OCR language code (spa=Spanish, fre=French).

        Returns:
            Extracted text string, or None on failure.
        """
        if not self._available:
            return None

        try:
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pdf"
            mime_map = {
                "pdf": "application/pdf",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "png": "image/png",
                "webp": "image/webp",
            }
            filetype = ext.upper() if ext in mime_map else "PDF"

            b64 = base64.b64encode(file_bytes).decode("utf-8")
            mime = mime_map.get(ext, "application/pdf")
            base64_str = f"data:{mime};base64,{b64}"

            payload = {
                "apikey": self.api_key,
                "base64Image": base64_str,
                "language": language,
                "isTable": True,
                "OCREngine": 2,
                "filetype": filetype,
                "scale": True,
                "detectOrientation": True,
            }

            response = requests.post(API_URL, data=payload, timeout=60)
            result = response.json()

            if result.get("IsErroredOnProcessing"):
                error_msg = result.get("ErrorMessage", ["Unknown error"])
                logger.error(f"OCR.space error: {error_msg}")
                return None

            pages = result.get("ParsedResults", [])
            text_parts = [p.get("ParsedText", "") for p in pages]
            full_text = "\n".join(text_parts).strip()

            if full_text:
                logger.info(
                    f"OCR.space extracted {len(full_text)} chars from {filename}"
                )
                return full_text
            else:
                logger.warning(f"OCR.space returned empty text for {filename}")
                return None

        except requests.Timeout:
            logger.error("OCR.space request timed out")
            return None
        except Exception as e:
            logger.error(f"OCR.space error: {e}")
            return None
