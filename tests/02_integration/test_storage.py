"""
Tests d'intégration StorageService réel — zéro mock.
Upload S3/Storj réel si configuré, sinon skip.
"""


import pytest

from backend.services.storage_service import StorageService


@pytest.fixture
def storage_configured():
    if not StorageService.is_configured():
        pytest.skip(
            "Storj non configuré — définir STORJ_ACCESS_KEY, STORJ_SECRET_KEY, STORJ_BUCKET"
        )


class TestStorageReel:
    def test_upload_file_reel(self, storage_configured):
        """Upload réel d'un fichier test vers le bucket Storj."""
        content = b"Test PDF content for integration test"
        filename = "test_integration_facture.pdf"
        url = StorageService.upload_file(
            content,
            filename,
            content_type="application/pdf",
        )
        assert url is not None
        assert filename in url or "test" in url.lower()

    def test_presigned_url_generation(self, storage_configured):
        """Génération d'URL pré-signée pour une clé existante ou fictive."""
        key = "2025/02/test_key.pdf"
        url = StorageService.get_presigned_url(key)
        assert url is not None
        assert "http" in url
