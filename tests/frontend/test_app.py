import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, MagicMock

@patch("requests.get")
def test_app_loads_correctly(mock_get):
    # Mock /api/v1/catalogue response
    mock_resp_cat = MagicMock()
    mock_resp_cat.status_code = 200
    mock_resp_cat.json.return_value = {"products": [{"fournisseur": "BigMat", "designation_fr": "Sable"}], "total": 1}

    # Mock /health response
    mock_resp_health = MagicMock()
    mock_resp_health.status_code = 200
    mock_resp_health.json.return_value = {"status": "healthy", "db": {"products": 1, "invoices": 1, "families": 1}}

    def side_effect(url, *args, **kwargs):
        if "catalogue" in url:
            return mock_resp_cat
        if "health" in url:
            return mock_resp_health
        return MagicMock(status_code=404)

    mock_get.side_effect = side_effect

    # Initialize Streamlit Test App
    at = AppTest.from_file("app.py").run(timeout=15)

    # Assert no exceptions occurred during render
    assert not at.exception

    # Check if the Main Title is rendered correctly
    assert len(at.markdown) > 0
    assert any("Traitement Rapide" in m.value for m in at.markdown)
