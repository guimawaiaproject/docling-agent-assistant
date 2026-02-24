"""
Centralized configuration via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class AppConfig(BaseSettings):
    """Application-wide configuration."""

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    db_path: str = Field(default="data_cache.db")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key != "YOUR_API_KEY_HERE")


def get_config(**overrides) -> AppConfig:
    return AppConfig(**overrides)
