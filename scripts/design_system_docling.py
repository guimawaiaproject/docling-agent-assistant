#!/usr/bin/env python3
"""
Génère un design system pour Docling via UI/UX Pro Max.
Usage: python scripts/design_system_docling.py [--persist] [--page NAME]
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_SCRIPT = ROOT / ".cursor" / "skills" / "ui-ux-pro-max" / "scripts" / "search.py"


def main():
    parser = argparse.ArgumentParser(description="Génère design system Docling via UI/UX Pro Max")
    parser.add_argument("--persist", "-p", action="store_true", help="Sauvegarder dans design-system/MASTER.md")
    parser.add_argument("--page", type=str, help="Override page-specific (ex: dashboard)")
    parser.add_argument("--query", "-q", default="SaaS BTP catalogue factures scanner", help="Requête de recherche")
    args = parser.parse_args()

    if not SKILL_SCRIPT.exists():
        print("UI/UX Pro Max non installé. Exécuter: npx uipro-cli init --ai cursor")
        sys.exit(1)

    cmd = [
        sys.executable,
        str(SKILL_SCRIPT),
        args.query,
        "--design-system",
        "-p", "Docling",
        "-f", "markdown",
    ]
    if args.persist:
        cmd.append("--persist")
    if args.page:
        cmd.extend(["--page", args.page])

    result = subprocess.run(cmd, cwd=str(ROOT))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
