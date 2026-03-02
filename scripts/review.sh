#!/usr/bin/env bash
# Review code — ruff + gito (si configuré)
# L'agent EXÉCUTE ce script pour reviewer, pas suggérer

set -e
cd "$(dirname "$0")/.."

echo "=== Ruff ==="
(cd apps/api && uv run ruff check . ../../scripts)

echo "=== Gito (si configuré) ==="
if command -v gito &>/dev/null; then
  gito review 2>/dev/null || echo "Gito non configuré (gito setup) — skip"
else
  echo "Gito non installé — skip"
fi
