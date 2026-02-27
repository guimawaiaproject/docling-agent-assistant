#!/usr/bin/env python3
"""
Validate .env — Docling
Vérifie que les variables d'environnement obligatoires sont présentes et valides.
Usage: python scripts/validate_env.py
"""

import os
import sys
from pathlib import Path


def load_dotenv() -> None:
    """Charge .env dans os.environ (sans dépendance python-dotenv)."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def validate() -> list[str]:
    """Retourne la liste des erreurs."""
    load_dotenv()
    errors = []

    gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini:
        errors.append("GEMINI_API_KEY manquante ou vide dans .env")
    elif gemini in ("YOUR_GEMINI_API_KEY", "dummy-key-for-tests"):
        errors.append("GEMINI_API_KEY contient une valeur placeholder — remplacer par une vraie clé")

    db = os.environ.get("DATABASE_URL", "").strip()
    if not db:
        errors.append("DATABASE_URL manquante ou vide dans .env")
    elif not db.startswith("postgresql"):
        errors.append("DATABASE_URL doit commencer par postgresql://")
    elif "neon.tech" not in db and "localhost" not in db:
        errors.append("DATABASE_URL : format Neon attendu (host.neon.tech) ou localhost pour dev")

    jwt = os.environ.get("JWT_SECRET", "").strip()
    if not jwt:
        errors.append("JWT_SECRET manquant ou vide dans .env")
    elif len(jwt) < 32:
        errors.append("JWT_SECRET doit faire au moins 32 caractères (openssl rand -hex 32)")
    elif jwt in ("change-this-to-a-long-random-string", "ci-test-secret-for-jwt-32chars-long"):
        errors.append("JWT_SECRET contient une valeur placeholder — générer avec: openssl rand -hex 32")

    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        errors.insert(0, "Fichier .env manquant — copier .env.example vers .env")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Validation .env échouée:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("Validation .env OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
