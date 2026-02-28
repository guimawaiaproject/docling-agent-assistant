#!/usr/bin/env bash
# verify_project.sh — Vérification complète du projet Docling
# Aligné sur Audit Bêton (AUDIT_BETON/10_RAPPORT_FINAL.md)
# Usage: ./scripts/verify_project.sh

set -e
cd "$(dirname "$0")/.."

failed=0

run_step() {
    local id="$1" name="$2" optional="${3:-}"
    echo ""
    echo "[$id] $name"
    if eval "$name"; then
        echo "  [OK]"
        return 0
    else
        echo "  [FAIL]"
        [[ -z "$optional" ]] && failed=1
        return 1
    fi
}

echo ""
echo "========================================"
echo "  DOCLING — VÉRIFICATION PROJET COMPLÈTE"
echo "  (Audit Bêton + SonarQube-ready)"
echo "========================================"
echo ""

export JWT_SECRET="${JWT_SECRET:-test-secret-32-chars-minimum-for-pytest}"
export VITE_API_URL="http://localhost:8000"
export VITE_AUTH_REQUIRED="true"

echo "=== BACKEND ==="
run_step "B1" "python -c 'import api; print(\"OK\")'" || true
run_step "B2" "ruff check api.py backend/ scripts/ tests/ migrations/" || true
run_step "B3" "python -m pytest tests/01_unit -v --tb=short -q -x" || true

echo ""
echo "=== FRONTEND ==="
cd docling-pwa
if [[ -f pnpm-lock.yaml ]]; then
    run_step "F1" "pnpm run lint" "optional" || true
    run_step "F2" "pnpm run build" || true
    run_step "F3" "pnpm exec vitest run --reporter=dot" || true
else
    run_step "F1" "npm run lint" "optional" || true
    run_step "F2" "npm run build" || true
    run_step "F3" "npx vitest run --reporter=dot" || true
fi
cd ..

echo ""
echo "=== QUALITÉ ==="
run_step "Q1" "python scripts/validate_skills.py" "optional" || true
run_step "Q2" "python scripts/validate_env.py" "optional" || true

echo ""
echo "=== DÉPLOIEMENT (Audit Bêton) ==="
if [[ -f render.yaml ]]; then
    if grep -q DATABASE_URL render.yaml && grep -q JWT_SECRET render.yaml; then
        echo "[D1] render.yaml : OK"
    else
        echo "[D1] [WARN] render.yaml : DATABASE_URL ou JWT_SECRET manquant"
    fi
fi
if [[ -f .github/workflows/deploy.yml ]]; then
    if grep -q "secrets.DEPLOY_PROVIDER == 'render'" .github/workflows/deploy.yml; then
        echo "[D2] [WARN] deploy.yml : condition secrets invalide"
    else
        echo "[D2] deploy.yml : OK"
    fi
fi

echo ""
echo "========================================"
if [[ $failed -gt 0 ]]; then
    echo "  VERDICT : ÉCHEC"
    echo "  Référence : AUDIT_BETON/10_RAPPORT_FINAL.md"
    echo "========================================"
    exit 1
else
    echo "  VERDICT : OK"
    echo "========================================"
    exit 0
fi
