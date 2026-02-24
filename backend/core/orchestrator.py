"""
Extraction pipeline orchestrator.
Hash → Cache → Gemini → Validate → Upsert DB.
"""
import hashlib
import logging
from pathlib import Path
from typing import Optional, Callable

from backend.core.config import AppConfig, get_config
from backend.core.db_manager import DBManager
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

    def __init__(self, config: Optional[AppConfig] = None, db_manager: Optional[DBManager] = None):
        self.config = config or get_config()
        self.db = db_manager or DBManager(self.config.db_path)
        self.gemini = GeminiService(self.config)

    def process_file(
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
        file_hash = DBManager.compute_file_hash(file_bytes)

        # 2. Cache check
        if self.db.is_invoice_processed(file_hash):
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
        added = 0
        updated = 0
        for product in result.products:
            action = self.db.upsert_product(
                product, result.numero_facture, result.date_facture
            )
            if action == "added":
                added += 1
            else:
                updated += 1

        # 6. Save invoice record
        self.db.save_invoice(
            file_hash, filename, result.fournisseur,
            result.numero_facture, result.date_facture, len(result.products),
        )

        _status(
            f"✅ {filename}: {added} nouveaux, {updated} mis à jour "
            f"(facture {result.numero_facture})"
        )

        return ProcessingResult(
            invoice=result,
            file_hash=file_hash,
            products_added=added,
            products_updated=updated,
        )
