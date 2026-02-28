"""
Configuration centralisée — Docling Agent v3
Toutes les variables d'environnement validées au démarrage via pydantic-settings.
"""

import logging
import sys
from pathlib import Path
from typing import ClassVar

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GEMINI_API_KEY: str = ""
    DATABASE_URL: str = ""
    DEFAULT_AI_MODEL: str = "gemini-3-flash-preview"
    WATCHDOG_FOLDER: str = "./Docling_Factures"
    WATCHDOG_ENABLED: bool = True
    STORJ_BUCKET: str = "docling-factures"
    STORJ_ACCESS_KEY: str = ""
    STORJ_SECRET_KEY: str = ""
    STORJ_ENDPOINT: str = "https://gateway.storjshare.io"
    PWA_URL: str = ""
    JWT_SECRET: str = ""
    JWT_EXPIRY_HOURS: int = 24
    SENTRY_DSN: str = ""
    ENVIRONMENT: str = "production"
    FREE_ACCESS_MODE: bool = False  # Accès provisoire sans auth (guest partagé)

    MODELS_DISPONIBLES: ClassVar[dict[str, str]] = {
        "gemini-3-flash-preview": "models/gemini-3-flash-preview",
        "gemini-3.1-pro-preview": "models/gemini-3.1-pro-preview",
        "gemini-2.5-flash": "models/gemini-2.5-flash",
    }

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _strip_database_url(cls, v: str) -> str:
        return (v or "").strip()

    @property
    def DEFAULT_MODEL(self) -> str:
        return self.DEFAULT_AI_MODEL

    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        return [
            o for o in [
                "http://localhost:5173",
                "https://localhost:5173",
                "http://localhost:5174",
                "https://localhost:5174",
                "http://localhost:5175",
                "https://localhost:5175",
                "http://localhost:3000",
                "https://docling-agent.netlify.app",
                self.PWA_URL,
            ] if o
        ]

    def validate_startup(self) -> None:
        errors: list[str] = []

        if not self.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY manquante dans .env")
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL manquante dans .env")
        elif not self.DATABASE_URL.startswith("postgresql"):
            errors.append("DATABASE_URL doit commencer par postgresql://")
        if not self.JWT_SECRET:
            errors.append("JWT_SECRET manquant dans .env")
        elif len(self.JWT_SECRET) < 32:
            errors.append("JWT_SECRET doit faire au moins 32 caractères pour la sécurité")
        if self.DEFAULT_AI_MODEL not in self.MODELS_DISPONIBLES:
            errors.append(
                f"DEFAULT_AI_MODEL='{self.DEFAULT_AI_MODEL}' invalide. "
                f"Valeurs acceptées : {', '.join(self.MODELS_DISPONIBLES)}"
            )

        Path(self.WATCHDOG_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(self.WATCHDOG_FOLDER + "/Traitees").mkdir(parents=True, exist_ok=True)
        Path(self.WATCHDOG_FOLDER + "/Erreurs").mkdir(parents=True, exist_ok=True)

        if errors:
            for err in errors:
                logger.error(err)
            sys.exit(1)

        logger.info("Config OK — modele: %s", self.DEFAULT_MODEL)
        logger.info(
            "Watchdog: %s -> %s",
            "actif" if self.WATCHDOG_ENABLED else "desactive",
            self.WATCHDOG_FOLDER,
        )


_settings = _Settings()


class Config:
    """Facade preserving the original class-attribute API for backward compat."""

    GEMINI_API_KEY:     str       = _settings.GEMINI_API_KEY
    DATABASE_URL:       str       = _settings.DATABASE_URL
    DEFAULT_MODEL:      str       = _settings.DEFAULT_MODEL
    MODELS_DISPONIBLES: dict      = _Settings.MODELS_DISPONIBLES
    WATCHDOG_FOLDER:    str       = _settings.WATCHDOG_FOLDER
    WATCHDOG_ENABLED:   bool      = _settings.WATCHDOG_ENABLED
    STORJ_BUCKET:       str       = _settings.STORJ_BUCKET
    STORJ_ACCESS_KEY:   str       = _settings.STORJ_ACCESS_KEY
    STORJ_SECRET_KEY:   str       = _settings.STORJ_SECRET_KEY
    STORJ_ENDPOINT:     str       = _settings.STORJ_ENDPOINT
    ALLOWED_ORIGINS:    list[str] = _settings.ALLOWED_ORIGINS
    JWT_SECRET:         str       = _settings.JWT_SECRET
    JWT_EXPIRY_HOURS:   int       = _settings.JWT_EXPIRY_HOURS
    SENTRY_DSN:         str       = _settings.SENTRY_DSN
    ENVIRONMENT:        str       = _settings.ENVIRONMENT
    FREE_ACCESS_MODE:   bool      = _settings.FREE_ACCESS_MODE

    @classmethod
    def validate(cls) -> None:
        _settings.validate_startup()
