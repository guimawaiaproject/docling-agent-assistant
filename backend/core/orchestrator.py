"""
Orchestrator — Docling Agent v3
Coordonne : prétraitement image → Gemini → validation → BDD → historique.

Optimisations 2026 :
- asyncio.to_thread() pour les appels sync (Gemini, OpenCV, boto3) → vrai parallélisme
- Cache GeminiService par model_id
"""

import asyncio
import logging

from backend.core.db_manager import DBManager
from backend.services.facturx_extractor import extract_from_facturx_pdf
from backend.services.gemini_service import GeminiService
from backend.services.image_preprocessor import ImagePreprocessor
from backend.services.storage_service import StorageService

logger = logging.getLogger(__name__)

# Coût estimé par token selon le modèle (USD / 1M tokens) - Estimations 2026
COST_PER_MILLION = {
    "gemini-3-flash-preview": 0.10,
    "gemini-3.1-pro-preview": 2.50,
    "gemini-2.5-flash":       0.30,
}


class Orchestrator:

    @staticmethod
    async def process_file(
        file_bytes: bytes,
        filename:   str,
        model_id:   str = "gemini-3-flash-preview",
        source:     str = "pc",
        user_id:    int | None = None,
    ) -> dict:
        """
        Pipeline complet :
        1. Détecter le type MIME
        2. Prétraiter si image (OpenCV)
        3. Extraire via Gemini
        4. Sauvegarder en BDD
        5. Logger dans historique factures
        Retourne { success, products, products_added, facture_id, ... }
        """
        logger.info(f"→ Traitement: {filename} (modèle: {model_id}, source: {source})")

        # ── 1. Détection MIME ─────────────────────────────────────
        mime_type = Orchestrator._detect_mime(filename, file_bytes)
        logger.debug(f"MIME détecté: {mime_type}")

        # ── 2. Factur-X : extraction XML si PDF (sans IA) ───────────────────
        result = None
        if mime_type == "application/pdf":
            result = await asyncio.to_thread(
                extract_from_facturx_pdf, file_bytes
            )

        # ── 3. Fallback Gemini si pas Factur-X (async natif, sans to_thread) ─
        if result is None:
            processed_bytes = file_bytes
            if ImagePreprocessor.is_image(filename):
                processed_bytes = await asyncio.to_thread(
                    ImagePreprocessor.preprocess_bytes, file_bytes, filename
                )
                logger.debug(f"Prétraitement: {len(file_bytes)//1024}Ko → {len(processed_bytes)//1024}Ko")
            service = GeminiService.get_or_create(model_id=model_id)
            result = await service.extract_from_bytes_async(
                processed_bytes, mime_type, filename
            )

        if not result.produits:
            await DBManager.log_facture(
                filename=filename, statut="erreur",
                nb_produits=0, cout_usd=0.0,
                modele_ia=model_id, source=source, user_id=user_id,
            )
            return {
                "success": False,
                "error":   "Aucun produit extrait de la facture",
                "filename": filename,
            }

        # ── 4+5. BDD + S3 en parallèle ─────────────────────────────
        products_dicts = [p.model_dump() for p in result.produits]
        (nb_saved, historique_failures), pdf_url = await asyncio.gather(
            DBManager.upsert_products_batch(products_dicts, source=source, user_id=user_id),
            asyncio.to_thread(
                StorageService.upload_file,
                file_bytes, filename, content_type=mime_type,
            ),
        )
        if historique_failures > 0:
            logger.warning(
                "%s: %d insertion(s) prix_historique en échec",
                filename,
                historique_failures,
            )

        # ── 6. Historique ─────────────────────────────────────────
        cout_usd = (result.tokens_used / 1_000_000) * COST_PER_MILLION.get(model_id, 0.50)
        facture_id = await DBManager.log_facture(
            filename=filename, statut="traite",
            nb_produits=nb_saved, cout_usd=cout_usd,
            modele_ia=model_id, source=source, pdf_url=pdf_url, user_id=user_id,
        )

        logger.info(f"✅ {filename}: {nb_saved} produits sauvegardés, coût: ${cout_usd:.5f}")

        return {
            "success":          True,
            "filename":         filename,
            "products":         products_dicts,
            "products_added":   nb_saved,
            "facture_id":       facture_id,
            "fournisseur":      result.fournisseur_detecte,
            "langue":           result.langue_detectee,
            "tokens_used":      result.tokens_used,
            "cout_usd":         round(cout_usd, 6),
            "model_used":       model_id,
            "pdf_url":          pdf_url,
        }

    @staticmethod
    def _detect_mime(filename: str, file_bytes: bytes) -> str:
        """Détecte le MIME type par extension + magic bytes."""
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

        mime_map = {
            "pdf":  "application/pdf",
            "jpg":  "image/jpeg",
            "jpeg": "image/jpeg",
            "png":  "image/png",
            "webp": "image/webp",
            "heic": "image/heic",
            "heif": "image/heif",
        }

        if ext in mime_map:
            return mime_map[ext]

        # Magic bytes fallback
        if file_bytes[:4] == b"%PDF":
            return "application/pdf"
        if file_bytes[:3] in (b"\xff\xd8\xff",):
            return "image/jpeg"
        if file_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"

        return "image/jpeg"  # fallback safe
