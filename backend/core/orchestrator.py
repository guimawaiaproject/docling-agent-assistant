"""
Extraction pipeline orchestrator.
Hash → Cache → Gemini → Validate → Upsert DB.
"""
import logging
from pathlib import Path
from typing import Optional, Callable

from backend.core.config import AppConfig, get_config
from backend.core.db_manager import DBManager
from backend.services.gemini_service import GeminiService
import hashlib
from backend.services.gemini_service import GeminiService
from backend.schemas.invoice import ProcessingResult, InvoiceResult

logger = logging.getLogger(__name__)

MIME_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".heic": "image/heic",
}


class ExtractionOrchestrator:
    """Orchestrates the invoice extraction pipeline."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or get_config()
        self.gemini = GeminiService(self.config)

    async def process_file(
        self,
        file_bytes: bytes,
        filename: str,
        on_status: Optional[Callable[[str], None]] = None,
    ) -> ProcessingResult:
        """
        Full pipeline: hash → cache check → Gemini extract → upsert DB.
        """
        def _status(msg: str):
            logger.info(msg)
            if on_status:
                on_status(msg)

        # 1. Hash
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # 2. Cache check
        pool = await DBManager.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT 1 FROM factures WHERE filename = $1", file_hash)
            if row:
                _status(f"⏩ {filename} — déjà traité")
                return ProcessingResult(
                    invoice=InvoiceResult(), file_hash=file_hash, was_cached=True
                )

        # 3. Determine MIME type
        suffix = Path(filename).suffix.lower()
        mime_type = MIME_TYPES.get(suffix, "application/pdf")

        # 4. Gemini extraction
        _status(f"🧠 Extraction IA de {filename}...")
        result = self.gemini.extract_invoice(file_bytes, mime_type)

        if not result or not result.products:
            _status(f"⚠️ Aucun produit extrait de {filename}")
            return ProcessingResult(
                invoice=result or InvoiceResult(),
                file_hash=file_hash,
            )

        # 5. Upsert products
        updated = 0
        for product in result.products:
            p_dict = product.model_dump()
            p_dict['numero_facture'] = result.numero_facture
            p_dict['date_facture'] = result.date_facture

            action = await DBManager.upsert_product(p_dict)
            if action:
                updated += 1  # Simplified since original upsert_product didn't distinguish

        # 6. Save invoice record
        await DBManager.save_invoice(
            file_hash, filename, len(result.products),
        )

        _status(
            f"✅ {filename}: {updated} produits traités "
            f"(facture {result.numero_facture})"
        )

        return ProcessingResult(
            invoice=result,
            file_hash=file_hash,
            products_added=0,
            products_updated=updated,
        )
