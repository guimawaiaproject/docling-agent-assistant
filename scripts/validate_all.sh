#!/usr/bin/env bash
# Validation complète — à lancer après toute modification
# Usage: ./scripts/validate_all.sh

set -e
cd "$(dirname "$0")/.."

echo "=== 1. Lint backend ==="
ruff check api.py backend/ scripts/ tests/ migrations/

echo "=== 2. Lint frontend ==="
(cd docling-pwa && npm run lint)

echo "=== 3. Validate skills ==="
python scripts/validate_skills.py

echo "=== 4. Tests backend ==="
pytest tests/01_unit -v --tb=short -q

echo "=== 5. Tests frontend ==="
(cd docling-pwa && npx vitest run --reporter=dot)

echo "=== Validation OK ==="
