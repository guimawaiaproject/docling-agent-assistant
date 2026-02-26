"""
Image Preprocessor — Docling Agent v3
Nettoyage et optimisation des photos mobiles avant envoi à Gemini.
Pipeline : débruitage → contraste CLAHE → redressement → WebP
"""

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ImagePreprocessor:

    @staticmethod
    def preprocess_bytes(image_bytes: bytes, filename: str = "image") -> bytes:
        """
        Prend des bytes d'image (JPG/PNG/WebP),
        applique le pipeline de nettoyage,
        retourne des bytes WebP optimisés.
        """
        try:
            # Décoder l'image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.warning(f"Impossible de décoder {filename}, retour image brute")
                return image_bytes

            # ── 1. Redimensionner si trop grand (max 2500px) ──────
            h, w = img.shape[:2]
            max_dim = 2500
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                img = cv2.resize(img, (int(w * scale), int(h * scale)),
                                interpolation=cv2.INTER_LANCZOS4)
                logger.debug(f"Resize: {w}x{h} → {img.shape[1]}x{img.shape[0]}")

            # ── 2. Débruitage léger (préserve les textes fins) ────
            img = cv2.fastNlMeansDenoisingColored(img, None, 5, 5, 7, 21)

            # ── 3. Contraste CLAHE sur canal L (Lab) ──────────────
            # Améliore la lisibilité sans saturer les couleurs
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            img = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

            # ── 4. Légère netteté (unsharp mask) ──────────────────
            gaussian = cv2.GaussianBlur(img, (0, 0), 2.0)
            img = cv2.addWeighted(img, 1.4, gaussian, -0.4, 0)

            # ── 5. Encoder en WebP qualité 90 ─────────────────────
            success, buffer = cv2.imencode(
                ".webp", img, [cv2.IMWRITE_WEBP_QUALITY, 90]
            )
            if not success:
                return image_bytes

            logger.info(f"✅ Prétraitement OK: {filename} ({len(image_bytes)//1024}Ko → {len(buffer)//1024}Ko)")
            return buffer.tobytes()

        except Exception as e:
            logger.error(f"Erreur prétraitement {filename}: {e}")
            return image_bytes   # Retour image originale si erreur

    @staticmethod
    def is_image(filename: str) -> bool:
        return Path(filename).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
