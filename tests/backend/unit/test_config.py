import os
import pytest
from backend.core.config import AppConfig, get_config

def test_config_valid():
    os.environ["GEMINI_API_KEY"] = "fake_key_test"
    config = get_config()
    assert config.gemini_api_key == "fake_key_test"
    assert config.has_gemini_key is True

def test_config_missing_key(mocker):
    os.environ["GEMINI_API_KEY"] = ""
    config = get_config()
    assert config.has_gemini_key is False
