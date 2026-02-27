"""
AuthService - Docling Agent v4
JWT authentication (PyJWT) with Argon2id password hashing.
Backward-compatible: PBKDF2 hashes are verified and silently rehashed to Argon2id on login.
"""

import hashlib
import hmac
import logging
import os
import time
from typing import Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

logger = logging.getLogger(__name__)

def _get_jwt_secret() -> str:
    """Lazy accessor — validated at startup by Config.validate(), not at import."""
    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET manquant. Définir la variable d'environnement JWT_SECRET "
            "avant de démarrer l'application."
        )
    return secret

JWT_ALGORITHM = "HS256"
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY_HOURS", "24")) * 3600

_ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)


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
    return jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token. Returns payload dict or None."""
    try:
        data = jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        data["sub"] = int(data["sub"])
        return data
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError, KeyError):
        logger.debug("Token invalide ou payload malformé")
        return None


def validate_password(password: str) -> tuple[bool, str]:
    """
    Valide le mot de passe : min 8 chars, au moins 1 majuscule, au moins 1 chiffre.
    Retourne (True, "") si valide, (False, message_erreur) sinon.
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    if not any(c.isupper() for c in password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    if not any(c.isdigit() for c in password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    return True, ""


def hash_password(password: str) -> str:
    """Hash password with Argon2id (default for all new accounts)."""
    return _ph.hash(password)


def _verify_pbkdf2(password: str, stored: str) -> bool:
    """Verify a legacy PBKDF2-SHA256 hash (format: salt_hex:hash_hex)."""
    try:
        salt_hex, hash_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def verify_password(password: str, stored: str) -> bool:
    """
    Verify password against stored hash.
    Supports both Argon2id ($argon2...) and legacy PBKDF2 (hex:hex) formats.
    """
    if stored.startswith("$argon2"):
        try:
            return _ph.verify(stored, password)
        except VerifyMismatchError:
            return False
    return _verify_pbkdf2(password, stored)


def needs_rehash(stored: str) -> bool:
    """Returns True if the stored hash should be upgraded to Argon2id."""
    if stored.startswith("$argon2"):
        return _ph.check_needs_rehash(stored)
    return True
