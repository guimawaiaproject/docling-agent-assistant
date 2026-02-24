"""
Google Drive service — archive invoices in Year/Quarter/Month folders.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class GoogleDriveService:
    """Upload invoices to Google Drive with automatic folder structure."""

    QUARTERS = {1: "T1", 2: "T1", 3: "T1", 4: "T2", 5: "T2", 6: "T2",
                7: "T3", 8: "T3", 9: "T3", 10: "T4", 11: "T4", 12: "T4"}
    MONTHS_FR = {1: "01-Janvier", 2: "02-Février", 3: "03-Mars",
                 4: "04-Avril", 5: "05-Mai", 6: "06-Juin",
                 7: "07-Juillet", 8: "08-Août", 9: "09-Septembre",
                 10: "10-Octobre", 11: "11-Novembre", 12: "12-Décembre"}

    def __init__(self, credentials_path: str, root_folder_id: str):
        if not HAS_GOOGLE:
            logger.warning("google-api-python-client not installed")
            self._service = None
            return

        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        self._service = build("drive", "v3", credentials=creds)
        self._root_folder_id = root_folder_id
        logger.info("Google Drive service initialized")

    @property
    def is_available(self) -> bool:
        return self._service is not None

    def _find_or_create_folder(self, name: str, parent_id: str) -> str:
        query = (
            f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
            f"and '{parent_id}' in parents and trashed=false"
        )
        results = self._service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])
        if files:
            return files[0]["id"]

        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = self._service.files().create(body=metadata, fields="id").execute()
        logger.info(f"Created Drive folder: {name}")
        return folder["id"]

    def _get_date_folder(self, date_facture: str) -> str:
        try:
            parts = date_facture.split("/")
            month, year = int(parts[1]), int(parts[2])
        except (ValueError, IndexError):
            from datetime import datetime
            now = datetime.now()
            month, year = now.month, now.year

        year_folder = self._find_or_create_folder(str(year), self._root_folder_id)
        quarter_folder = self._find_or_create_folder(self.QUARTERS[month], year_folder)
        month_folder = self._find_or_create_folder(self.MONTHS_FR[month], quarter_folder)
        return month_folder

    def upload_invoice(
        self, file_bytes: bytes, filename: str, date_facture: str,
        mime_type: str = "application/pdf"
    ) -> Optional[str]:
        if not self.is_available:
            return None
        try:
            folder_id = self._get_date_folder(date_facture)
            from googleapiclient.http import MediaInMemoryUpload
            media = MediaInMemoryUpload(file_bytes, mimetype=mime_type)
            metadata = {"name": filename, "parents": [folder_id]}
            uploaded = self._service.files().create(
                body=metadata, media_body=media, fields="id, webViewLink"
            ).execute()
            link = uploaded.get("webViewLink", "")
            logger.info(f"Uploaded to Drive: {filename} → {link}")
            return link
        except Exception as e:
            logger.error(f"Drive upload failed: {e}")
            return None
