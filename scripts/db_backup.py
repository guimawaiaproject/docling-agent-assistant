#!/usr/bin/env python3
"""
Backup PostgreSQL — Docling
Utilise DATABASE_URL depuis .env pour pg_dump.
Usage: python scripts/db_backup.py [--output FILE]
"""
import argparse
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
    parser = argparse.ArgumentParser(description="Backup PostgreSQL Docling")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Fichier de sortie (défaut: backups/docling_YYYYMMDD_HHMMSS.sql)",
    )
    parser.add_argument(
        "--format",
        "-F",
        choices=["p", "c", "t", "d"],
        default="p",
        help="Format: p=plain, c=custom, t=tar, d=directory (défaut: p)",
    )
    args = parser.parse_args()

    url = load_env()

    out_dir = PROJECT_ROOT / "backups"
    out_dir.mkdir(exist_ok=True)

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = PROJECT_ROOT / out_path
    else:
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "sql" if args.format == "p" else "dump"
        out_path = out_dir / f"docling_{ts}.{ext}"

    # pg_dump
    cmd = ["pg_dump", "-F", args.format, "-f", str(out_path), url]
    print(f"Backup vers {out_path}...")
    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ Backup OK: {out_path}")
    except FileNotFoundError:
        print("❌ pg_dump introuvable. Installer PostgreSQL client.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur pg_dump: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
