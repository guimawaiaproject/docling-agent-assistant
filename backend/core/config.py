"""
Configuration centralisée — Docling Agent v3
Validation des variables d'environnement au démarrage.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    # ─── API Keys ─────────────────────────────────────────────────
    GEMINI_API_KEY: str  = os.getenv("GEMINI_API_KEY", "")

    # ─── Base de données ──────────────────────────────────────────
    # Neon : préférer l'URL pooler (host -pooler) pour PgBouncer
    DATABASE_URL: str    = os.getenv("DATABASE_URL", "")

    # ─── Modèle IA par défaut ─────────────────────────────────────
    DEFAULT_MODEL: str   = os.getenv("DEFAULT_AI_MODEL", "gemini-3-flash-preview")

    MODELS_DISPONIBLES = {
        "gemini-3-flash-preview": "models/gemini-3-flash-preview",
        "gemini-3.1-pro-preview": "models/gemini-3.1-pro-preview",
        "gemini-2.5-flash":       "models/gemini-2.5-flash",
    }

    # ─── Dossier Magique (Watchdog) ───────────────────────────────
    WATCHDOG_FOLDER: str   = os.getenv("WATCHDOG_FOLDER", "./Docling_Factures")
    WATCHDOG_ENABLED: bool = os.getenv("WATCHDOG_ENABLED", "true").lower() == "true"

    # ─── Stockage Cloud PDFs ──────────────────────────────────────
    STORJ_BUCKET:     str = os.getenv("STORJ_BUCKET", "docling-factures")
    STORJ_ACCESS_KEY: str = os.getenv("STORJ_ACCESS_KEY", "")
    STORJ_SECRET_KEY: str = os.getenv("STORJ_SECRET_KEY", "")
    STORJ_ENDPOINT:   str = os.getenv("STORJ_ENDPOINT", "https://gateway.storjshare.io")

    # ─── CORS ─────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        o for o in [
            "http://localhost:5173",
            "https://localhost:5173",
            "http://localhost:5174",
            "https://localhost:5174",
            "http://localhost:5175",
            "https://localhost:5175",
            "http://localhost:3000",
            "https://docling-agent.netlify.app",
            os.getenv("PWA_URL", ""),
        ] if o
    ]

    # ─── Validation au démarrage ──────────────────────────────────
    @classmethod
    def validate(cls) -> None:
        errors = []

        if not cls.GEMINI_API_KEY:
            errors.append("❌ GEMINI_API_KEY manquante dans .env")

        if not cls.DATABASE_URL:
            errors.append("❌ DATABASE_URL manquante dans .env")
        elif not cls.DATABASE_URL.startswith("postgresql"):
            errors.append("❌ DATABASE_URL doit commencer par postgresql://")

        # Créer le dossier watchdog s'il n'existe pas
        Path(cls.WATCHDOG_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(cls.WATCHDOG_FOLDER + "/Traitees").mkdir(parents=True, exist_ok=True)
        Path(cls.WATCHDOG_FOLDER + "/Erreurs").mkdir(parents=True, exist_ok=True)

        if errors:
            for err in errors:
                logger.error(err)
            sys.exit(1)

        logger.info(f"✅ Config OK — modèle: {cls.DEFAULT_MODEL}")
        logger.info(f"✅ Watchdog: {'actif' if cls.WATCHDOG_ENABLED else 'désactivé'} → {cls.WATCHDOG_FOLDER}")
