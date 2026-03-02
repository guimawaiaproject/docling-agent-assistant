#!/usr/bin/env bash
# Validation complète — à lancer après toute modification (monorepo)
# Usage: ./scripts/validate_all.sh

set -e
cd "$(dirname "$0")/.."

echo "=== 1. Lint backend (ruff) ==="
(cd apps/api && uv run ruff check . ../../scripts)

echo "=== 2. Lint frontend ==="
(cd apps/pwa && pnpm run lint)

echo "=== 3. Build frontend (PostCSS/Tailwind) ==="
(cd apps/pwa && pnpm run build)

echo "=== 4. Validate skills ==="
python scripts/validate_skills.py

echo "=== 5. Tests backend ==="
(cd apps/api && uv run pytest tests -v)

echo "=== 6. Tests frontend ==="
(cd apps/pwa && pnpm run test)

echo "=== Validation OK ==="
