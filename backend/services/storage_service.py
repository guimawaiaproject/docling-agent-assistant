"""
StorageService - Docling Agent v3
Upload/download S3-compatible (Storj, R2, MinIO).
Utilise boto3 avec endpoint configurable.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from backend.core.config import Config

logger = logging.getLogger(__name__)


class StorageService:
    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            if not Config.STORJ_ACCESS_KEY or not Config.STORJ_SECRET_KEY:
                return None
            cls._client = boto3.client(
                "s3",
                endpoint_url=Config.STORJ_ENDPOINT,
                aws_access_key_id=Config.STORJ_ACCESS_KEY,
                aws_secret_access_key=Config.STORJ_SECRET_KEY,
            )
        return cls._client

    @classmethod
    def is_configured(cls) -> bool:
        return bool(Config.STORJ_ACCESS_KEY and Config.STORJ_SECRET_KEY)

    @classmethod
    def upload_file(
        cls,
        file_bytes: bytes,
        filename: str,
        content_type: str = "application/pdf",
    ) -> Optional[str]:
        """
        Upload un fichier vers le bucket S3.
        Retourne l'URL publique ou None si le stockage n'est pas configure.
        La cle S3 est : YYYY/MM/hash8_filename
        """
        client = cls._get_client()
        if client is None:
            logger.debug("Stockage cloud non configure, upload ignore")
            return None

        file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
        now = datetime.now(timezone.utc)
        safe_name = filename.replace(" ", "_").replace("/", "_")
        key = f"{now.strftime('%Y/%m')}/{file_hash}_{safe_name}"

        try:
            client.put_object(
                Bucket=Config.STORJ_BUCKET,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )
            url = f"{Config.STORJ_ENDPOINT}/{Config.STORJ_BUCKET}/{key}"
            logger.info(f"Fichier uploade -> {url}")
            return url

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Erreur upload S3 : {e}")
            return None

    @classmethod
    def _extract_key_from_url(cls, pdf_url: str) -> Optional[str]:
        """
        Extrait la clé S3 depuis une URL au format endpoint/bucket/key.
        Retourne None si l'URL ne correspond pas au format attendu.
        """
        if not pdf_url:
            return None
        prefix = f"{Config.STORJ_ENDPOINT.rstrip('/')}/{Config.STORJ_BUCKET}/"
        if not pdf_url.startswith(prefix):
            return None
        return pdf_url[len(prefix):]

    @classmethod
    def get_presigned_url_from_pdf_url(cls, pdf_url: str, expires_in: int = 3600) -> Optional[str]:
        """
        Génère une URL pré-signée à partir de pdf_url (format endpoint/bucket/key).
        Nécessaire pour Storj où l'URL directe n'est pas accessible.
        Retourne pdf_url en fallback si Storj non configuré ou URL d'un autre format.
        """
        key = cls._extract_key_from_url(pdf_url)
        if not key:
            return pdf_url  # Fallback: retourner l'URL telle quelle (bucket public)
        presigned = cls.get_presigned_url(key, expires_in)
        return presigned if presigned else pdf_url

    @classmethod
    def get_presigned_url(cls, key: str, expires_in: int = 3600) -> Optional[str]:
        """Genere une URL pre-signee pour acces temporaire."""
        client = cls._get_client()
        if client is None:
            return None
        try:
            return client.generate_presigned_url(
                "get_object",
                Params={"Bucket": Config.STORJ_BUCKET, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Erreur presigned URL : {e}")
            return None