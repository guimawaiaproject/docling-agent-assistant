#!/usr/bin/env bash
# Nettoyage — Docling (cache, build, node_modules)
# Usage: ./scripts/clean.sh [--full]
# --full : supprime aussi node_modules (réinstaller avec pnpm install)

set -euo pipefail
IFS=$'\n\t'

cd "$(dirname "$0")/.."

echo ""
echo "=== DOCLING — NETTOYAGE ==="
echo ""

FULL=false
[[ "${1:-}" == "--full" ]] && FULL=true

removed=0

remove_if_exists() {
  local path="$1"
  local label="${2:-$path}"
  if [[ -e "$path" ]]; then
    rm -rf "$path"
    echo "[OK] Supprimé: $label"
    ((removed++)) || true
  fi
}

# Cache Python (evite node_modules = blocage)
remove_if_exists "apps/api/.pytest_cache" ".pytest_cache"
remove_if_exists "apps/api/.ruff_cache" ".ruff_cache"
find apps/api scripts -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Build frontend
remove_if_exists "apps/pwa/dist" "dist"
remove_if_exists "apps/pwa/coverage" "coverage"

# MkDocs
remove_if_exists "site" "site (MkDocs)"

# Cache divers (evite node_modules)
remove_if_exists ".turbo" ".turbo"
find apps/api scripts -name "*.tsbuildinfo" -delete 2>/dev/null || true
find apps/pwa -maxdepth 1 -name "*.tsbuildinfo" -delete 2>/dev/null || true

if [[ "$FULL" == true ]]; then
  echo ""
  echo "[FULL] Suppression node_modules..."
  remove_if_exists "apps/pwa/node_modules" "node_modules"
fi

echo ""
echo "=== NETTOYAGE TERMINÉ ==="
if [[ "$FULL" == true ]]; then
  echo "Réinstaller: cd apps/pwa && pnpm install"
fi
echo ""
