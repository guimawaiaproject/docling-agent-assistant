import pytest
from unittest.mock import MagicMock
import pandas as pd
from backend.services.google_sheets_service import GoogleSheetsService

def test_sync_catalogue_success(mocker):
    mocker.patch("backend.services.google_sheets_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_sheets_service.build")

    svc = GoogleSheetsService("dummy.json", "sheet_id")
    svc._service = MagicMock()

    df = pd.DataFrame([{
        "fournisseur": "BigMat", "designation_raw": "Sable", "designation_fr": "Sable",
        "famille": "Granulats", "unite": "T", "prix_brut_ht": 10.0, "remise_pct": 0,
        "prix_remise_ht": 10.0, "prix_ttc_iva21": 12.10, "numero_facture": "F1", "date_facture": "01/01"
    }])

    res = svc.sync_catalogue(df)
    assert res is True

def test_sync_catalogue_error_handling(mocker):
    mocker.patch("backend.services.google_sheets_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_sheets_service.build")

    svc = GoogleSheetsService("dummy.json", "sheet_id")
    svc._service = MagicMock()
    svc._service.spreadsheets().values().update().execute.side_effect = Exception("API fail")

    df = pd.DataFrame([{"fournisseur": "A", "designation_raw": "B"}])
    res = svc.sync_catalogue(df)
    assert res is False
