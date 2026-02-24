"""
Centralized configuration via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class AppConfig(BaseSettings):
    """Application-wide configuration."""

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    db_path: str = Field(default="data_cache.db")

    # Google Cloud
    google_credentials_path: str = Field(default="", alias="GOOGLE_CREDENTIALS_PATH")
    google_drive_folder_id: str = Field(default="", alias="GOOGLE_DRIVE_FOLDER_ID")
    google_sheet_id: str = Field(default="", alias="GOOGLE_SHEET_ID")

    # OCR.space
    ocr_space_api_key: str = Field(default="", alias="OCR_SPACE_API_KEY")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key != "YOUR_API_KEY_HERE")

    @property
    def has_google_config(self) -> bool:
        return bool(self.google_credentials_path and self.google_sheet_id)


def get_config(**overrides) -> AppConfig:
    return AppConfig(**overrides)
