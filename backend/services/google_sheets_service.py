"""
Google Sheets service — sync product catalogue to a cloud spreadsheet.
"""
import logging
from typing import List, Dict

import pandas as pd

logger = logging.getLogger(__name__)

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsService:
    """Sync catalogue data to Google Sheets."""

    CATALOGUE_HEADERS = [
        "Fournisseur", "Désignation (Català)", "Désignation (FR)",
        "Famille", "Unité", "P.U. Brut HT", "Remise %",
        "P.U. Remisé HT", "P.U. IVA 21%", "N° Facture", "Date Facture"
    ]

    def __init__(self, credentials_path: str, sheet_id: str):
        if not HAS_GOOGLE:
            logger.warning("google-api-python-client not installed")
            self._service = None
            return

        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        self._service = build("sheets", "v4", credentials=creds)
        self._sheet_id = sheet_id
        logger.info("Google Sheets service initialized")

    @property
    def is_available(self) -> bool:
        return self._service is not None

    def sync_catalogue(self, df: pd.DataFrame) -> bool:
        """
        Replace the 'Catalogue' sheet content with current product data.
        """
        if not self.is_available or df.empty:
            return False

        try:
            # Map DB columns to display headers
            rows = []
            for _, row in df.iterrows():
                rows.append([
                    str(row.get("fournisseur", "")),
                    str(row.get("designation_raw", "")),
                    str(row.get("designation_fr", "")),
                    str(row.get("famille", "")),
                    str(row.get("unite", "")),
                    float(row.get("prix_brut_ht", 0)),
                    float(row.get("remise_pct", 0) or 0),
                    float(row.get("prix_remise_ht", 0)),
                    float(row.get("prix_ttc_iva21", 0)),
                    str(row.get("numero_facture", "")),
                    str(row.get("date_facture", "")),
                ])

            values = [self.CATALOGUE_HEADERS] + rows

            # Clear then write
            self._service.spreadsheets().values().clear(
                spreadsheetId=self._sheet_id, range="Catalogue!A:K"
            ).execute()

            self._service.spreadsheets().values().update(
                spreadsheetId=self._sheet_id,
                range="Catalogue!A1",
                valueInputOption="USER_ENTERED",
                body={"values": values},
            ).execute()

            logger.info(f"Synced {len(rows)} products to Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Sheets sync failed: {e}")
            return False
