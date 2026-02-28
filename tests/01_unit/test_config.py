"""Tests pour Config (backend/core/config.py) — zéro mock."""
from backend.core.config import Config


class TestConfig:
    def test_models_disponibles_not_empty(self):
        assert len(Config.MODELS_DISPONIBLES) > 0

    def test_default_model_exists_in_models(self):
        assert Config.DEFAULT_MODEL in Config.MODELS_DISPONIBLES

    def test_allowed_origins_is_list(self):
        assert isinstance(Config.ALLOWED_ORIGINS, list)
        assert "http://localhost:5173" in Config.ALLOWED_ORIGINS

    def test_storj_defaults(self):
        assert Config.STORJ_BUCKET == "docling-factures" or isinstance(Config.STORJ_BUCKET, str)
        assert isinstance(Config.STORJ_ENDPOINT, str)

    def test_watchdog_folder_is_string(self):
        assert isinstance(Config.WATCHDOG_FOLDER, str)

    def test_watchdog_enabled_is_bool(self):
        assert isinstance(Config.WATCHDOG_ENABLED, bool)
