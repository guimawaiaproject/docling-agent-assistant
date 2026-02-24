import pytest
from unittest.mock import MagicMock, patch
from backend.services.google_drive_service import GoogleDriveService

def test_upload_invoice_success(mocker):
    mocker.patch("backend.services.google_drive_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_drive_service.build")

    svc = GoogleDriveService("dummy.json", "root")
    svc._service = MagicMock()
    svc._service.files().create().execute.return_value = {"id": "1", "webViewLink": "http://link"}
    mocker.patch.object(svc, "_get_date_folder", return_value="fld")

    res = svc.upload_invoice(b"data", "test.pdf", "01/01/2026")
    assert res == "http://link"

def test_upload_invoice_error_handling(mocker):
    mocker.patch("backend.services.google_drive_service.HAS_GOOGLE", True)
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("backend.services.google_drive_service.build")

    svc = GoogleDriveService("dummy.json", "root")
    svc._service = MagicMock()
    svc._service.files().create().execute.side_effect = Exception("API error")
    mocker.patch.object(svc, "_get_date_folder", return_value="fld")

    res = svc.upload_invoice(b"data", "test.pdf", "01/01/2026")
    assert res is None
