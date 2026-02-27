#!/usr/bin/env python3
"""
Health Check — Docling
Vérifie que l'API, la base de données et les services sont opérationnels.
Usage: python scripts/health_check.py [--api-url URL]
"""

import argparse
import sys
import urllib.request
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check_api(url: str = "http://localhost:8000") -> tuple[bool, str]:
    """Vérifie que l'API répond sur /health."""
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return True, "API OK"
            return False, f"API returned {resp.status}"
    except urllib.error.URLError as e:
        return False, f"API unreachable: {e.reason}"
    except Exception as e:
        return False, str(e)


def check_db() -> tuple[bool, str]:
    """Vérifie la connexion PostgreSQL via l'API (si disponible) ou asyncpg."""
    try:
        from backend.core.config import Config
        import asyncpg

        async def _check():
            conn = await asyncpg.connect(Config.DATABASE_URL)
            try:
                await conn.fetchval("SELECT 1")
                return True
            finally:
                await conn.close()

        import asyncio
        asyncio.run(_check())
        return True, "Database OK"
    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Database: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Docling health check")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--skip-db", action="store_true", help="Skip database check")
    args = parser.parse_args()

    all_ok = True

    ok, msg = check_api(args.api_url)
    print(f"  API: {msg}")
    if not ok:
        all_ok = False

    if not args.skip_db:
        ok, msg = check_db()
        print(f"  DB:  {msg}")
        if not ok:
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
