#!/usr/bin/env bash
# Pre-launch check — Vérification 100% avant de lancer l'app
# Usage: ./scripts/pre_launch_check.sh
# Exit 0 = OK, Exit 1 = Échec (ne pas lancer)

set -e
cd "$(dirname "$0")/.."

failed=0

run_step() {
    echo ""
    echo "=== $1 ==="
    if "$2"; then
        echo "[OK] $1"
        return 0
    else
        echo "[FAIL] $1"
        return 1
    fi
}

echo ""
echo "========================================"
echo "  DOCLING — PRE-LAUNCH CHECK (100%)"
echo "========================================"

# 1. VENV
[ -f venv/bin/python ] || { echo "[FAIL] venv manquant. python -m venv venv"; exit 1; }
source venv/bin/activate 2>/dev/null || true

# 2. .env
[ -f .env ] || { echo "[FAIL] .env manquant"; exit 1; }
grep -q "JWT_SECRET=." .env || { echo "[FAIL] JWT_SECRET manquant"; exit 1; }
grep -q "DATABASE_URL=." .env || { echo "[FAIL] DATABASE_URL manquant"; exit 1; }

# 3. Lint backend
run_step "Lint backend" "ruff check api.py backend/ scripts/ tests/ migrations/" || failed=1

# 4. Lint frontend
run_step "Lint frontend" "cd docling-pwa && npm run lint" || failed=1

# 5. BUILD frontend (CRITIQUE)
run_step "Build frontend (PostCSS/Tailwind)" "cd docling-pwa && VITE_API_URL=http://localhost:8000 npm run build" || failed=1

# 6. Tests backend
run_step "Tests backend" "pytest tests/01_unit -v --tb=short -q -x" || failed=1

# 7. Tests frontend
run_step "Tests frontend" "cd docling-pwa && npx vitest run --reporter=dot" || failed=1

# 8. Validate skills
run_step "Validate skills" "python scripts/validate_skills.py" || failed=1

echo ""
echo "========================================"
if [ $failed -eq 1 ]; then
    echo "  PRE-LAUNCH CHECK : ECHEC"
    echo "  Corriger les erreurs avant de lancer."
    echo "========================================"
    exit 1
else
    echo "  PRE-LAUNCH CHECK : OK (100%)"
    echo "  L'app peut etre lancee."
    echo "========================================"
    exit 0
fi
