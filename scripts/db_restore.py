#!/usr/bin/env python3
"""
Restauration PostgreSQL — Docling
Utilise DATABASE_URL depuis .env pour pg_restore ou psql.
Usage: python scripts/db_restore.py <fichier.sql|fichier.dump>
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env():
    """Charge .env et retourne DATABASE_URL."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print("❌ .env absent")
        sys.exit(1)
    env = {}
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    url = env.get("DATABASE_URL")
    if not url:
        print("❌ DATABASE_URL manquant dans .env")
        sys.exit(1)
    return url


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/db_restore.py <fichier.sql|fichier.dump>")
        sys.exit(1)

    backup_path = Path(sys.argv[1])
    if not backup_path.is_absolute():
        backup_path = PROJECT_ROOT / backup_path
    if not backup_path.exists():
        print(f"❌ Fichier introuvable: {backup_path}")
        sys.exit(1)

    url = load_env()

    suffix = backup_path.suffix.lower()
    if suffix == ".sql":
        cmd = ["psql", url, "-f", str(backup_path)]
        print(f"Restauration depuis {backup_path} (psql)...")
    else:
        cmd = ["pg_restore", "-d", url, "-F", "c", str(backup_path)]
        print(f"Restauration depuis {backup_path} (pg_restore)...")

    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print("✅ Restauration OK")
    except FileNotFoundError:
        print("❌ psql/pg_restore introuvable. Installer PostgreSQL client.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
