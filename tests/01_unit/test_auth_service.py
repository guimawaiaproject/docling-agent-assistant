"""
Tests pour auth_service (JWT PyJWT + Argon2id password hashing) — zéro mock.
"""

import importlib
import os
import time

from backend.services.auth_service import (
    create_token,
    hash_password,
    needs_rehash,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pwd = "MonSuperMotDePasse!123"
        hashed = hash_password(pwd)
        assert hashed.startswith("$argon2")
        assert verify_password(pwd, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert not verify_password("incorrect", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("test")
        h2 = hash_password("test")
        assert h1 != h2  # salt differs

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed)
        assert not verify_password("a", hashed)

    def test_malformed_stored_hash(self):
        assert not verify_password("test", "notavalidhash")
        assert not verify_password("test", "")

    def test_needs_rehash_on_new_argon2(self):
        hashed = hash_password("test")
        assert not needs_rehash(hashed)

    def test_needs_rehash_on_legacy_pbkdf2(self):
        import hashlib
        import os as _os
        salt = _os.urandom(16)
        h = hashlib.pbkdf2_hmac("sha256", b"test", salt, 100000)
        legacy = f"{salt.hex()}:{h.hex()}"
        assert needs_rehash(legacy)
        assert verify_password("test", legacy)
        assert not verify_password("wrong", legacy)


class TestJWT:
    def test_create_and_verify_token(self):
        token = create_token(
            user_id=42, email="test@example.com", role="admin"
        )
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == 42
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"

    def test_expired_token_rejected(self):
        """Token expiré via JWT_EXPIRY=0 (sans mock, rechargement module)."""
        import backend.services.auth_service as auth_mod
        orig = os.environ.get("JWT_EXPIRY_HOURS")
        os.environ["JWT_EXPIRY_HOURS"] = "0"
        importlib.reload(auth_mod)
        token = auth_mod.create_token(user_id=1, email="a@b.com")
        time.sleep(0.1)
        assert auth_mod.verify_token(token) is None
        if orig is not None:
            os.environ["JWT_EXPIRY_HOURS"] = orig
        else:
            os.environ.pop("JWT_EXPIRY_HOURS", None)
        importlib.reload(auth_mod)

    def test_tampered_token_rejected(self):
        token = create_token(user_id=1, email="a@b.com")
        parts = token.split(".")
        parts[1] = parts[1][::-1]
        tampered = ".".join(parts)
        assert verify_token(tampered) is None

    def test_malformed_token_rejected(self):
        assert verify_token("not.a.valid.jwt.token") is None
        assert verify_token("garbage") is None
        assert verify_token("") is None
        assert verify_token("a.b") is None

    def test_default_role_is_user(self):
        token = create_token(user_id=1, email="a@b.com")
        payload = verify_token(token)
        assert payload["role"] == "user"
