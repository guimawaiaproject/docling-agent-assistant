#!/usr/bin/env bash
# Audit dépendances — Docling (pip-audit + pnpm audit)
# Usage: ./scripts/audit-deps.sh

set -uo pipefail
IFS=$'\n\t'

cd "$(dirname "$0")/.."

echo ""
echo "=== DOCLING — AUDIT DÉPENDANCES ==="
echo ""

failed=0

# 1. Python (pip-audit)
echo "[1] Python (pip-audit)..."
if command -v pip-audit &>/dev/null; then
  reqfile="${TMPDIR:-/tmp}/docling-req.txt"
  (cd apps/api && uv export --no-dev -o "$reqfile" 2>/dev/null) || reqfile=""
  if [[ -n "${reqfile}" && -f "$reqfile" ]]; then
    pip-audit -r "$reqfile" || failed=1
  else
    pip-audit || failed=1
  fi
else
  echo "  pip-audit non installé. pip install pip-audit"
fi

echo ""

# 2. Node (pnpm audit)
echo "[2] Node (pnpm audit)..."
if [[ -f apps/pwa/package.json ]]; then
  (cd apps/pwa && pnpm audit 2>/dev/null) || (cd apps/pwa && npm audit 2>/dev/null) || failed=1
fi

echo ""
echo "=== AUDIT TERMINÉ ==="
[[ $failed -eq 1 ]] && echo "Vulnérabilités détectées. Voir ci-dessus."
echo ""
exit $failed
