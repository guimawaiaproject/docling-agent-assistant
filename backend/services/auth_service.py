"""
AuthService - Docling Agent v4
JWT authentication (PyJWT) with PBKDF2 password hashing.
Progressive rehash to Argon2id planned in Phase 1.5.
"""

import hashlib
import hmac
import logging
import os
import time
from typing import Optional

import jwt

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "")
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET manquant. Définir la variable d'environnement JWT_SECRET "
        "avant de démarrer l'application."
    )
JWT_ALGORITHM = "HS256"
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY_HOURS", "24")) * 3600


def create_token(user_id: int, email: str, role: str = "user") -> str:
    """Create a JWT token signed with HS256 via PyJWT."""
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + JWT_EXPIRY,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token. Returns payload dict or None."""
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        data["sub"] = int(data["sub"])
        return data
    except jwt.ExpiredSignatureError:
        logger.debug("Token expiré")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Token invalide")
        return None


def hash_password(password: str) -> str:
    """Hash password with PBKDF2-SHA256 + random salt."""
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return f"{salt.hex()}:{hashed.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against its stored PBKDF2 hash."""
    try:
        salt_hex, hash_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False
