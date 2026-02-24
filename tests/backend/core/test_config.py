import pytest
from backend.core.config import AppConfig, get_config

def test_get_config_success():
    config = get_config(GEMINI_API_KEY="AIzaSyTest", GOOGLE_CREDENTIALS_PATH="creds.json")
    assert config.gemini_api_key == "AIzaSyTest"
    assert config.has_gemini_key is True

def test_get_config_invalid_input():
    config = get_config(GEMINI_API_KEY="")
    assert config.has_gemini_key is False

def test_get_config_edge_case():
    config = get_config(GEMINI_API_KEY="YOUR_API_KEY_HERE")
    assert config.has_gemini_key is False
