#!/usr/bin/env bash
# Setup initial — Docling (première installation)
# Usage: ./scripts/setup.sh [--build] [--migrate] [--no-launch]
#   --build     : build frontend (pnpm run build)
#   --migrate   : alembic upgrade head
#   --no-launch : ne pas lancer l'app a la fin (par defaut: lance make dev)

set -e
cd "$(dirname "$0")/.."

BUILD=false
MIGRATE=false
NO_LAUNCH=false
for arg in "$@"; do
  case "$arg" in
    --build) BUILD=true ;;
    --migrate) MIGRATE=true ;;
    --no-launch) NO_LAUNCH=true ;;
  esac
done

echo ""
echo "=== DOCLING — SETUP INITIAL ==="
echo ""

# 1. .env
if [[ ! -f .env ]]; then
  if [[ -f .env.example ]]; then
    cp .env.example .env
    echo "[OK] .env créé depuis .env.example"
    echo "     Remplir GEMINI_API_KEY, DATABASE_URL, JWT_SECRET dans .env"
  else
    echo "[WARN] .env.example absent"
  fi
else
  echo "[OK] .env existe"
fi

# 2. Backend (uv sync)
echo ""
echo "[2] Backend (apps/api)..."
command -v uv &>/dev/null || { echo "[FAIL] uv manquant. https://docs.astral.sh/uv/"; exit 1; }
unset VIRTUAL_ENV 2>/dev/null || true
(cd apps/api && uv sync --all-extras)
echo "[OK] uv sync (deps + dev)"

# 3. Frontend (pnpm install)
echo ""
echo "[3] Frontend (apps/pwa)..."
if [[ -f apps/pwa/package.json ]]; then
  if command -v pnpm &>/dev/null; then
    (cd apps/pwa && pnpm install)
    echo "[OK] pnpm install"
  else
    echo "[WARN] pnpm manquant. npm install -g pnpm"
  fi
fi

# 4. Migrations (optionnel)
if [[ "$MIGRATE" == true ]]; then
  echo ""
  echo "[4] Migrations..."
  (cd apps/api && uv run alembic upgrade head)
  echo "[OK] alembic upgrade head"
fi

# 5. Build frontend (optionnel)
if [[ "$BUILD" == true ]]; then
  echo ""
  echo "[5] Build frontend..."
  (cd apps/pwa && VITE_API_URL=http://localhost:8000 VITE_AUTH_REQUIRED=true pnpm run build)
  echo "[OK] pnpm run build"
fi

echo ""
echo "=== SETUP TERMINÉ ==="
if [[ "$NO_LAUNCH" != true ]]; then
  echo "Lancement de l'app..."
  exec bash scripts/run_dev.sh
else
  echo "Lancer: make dev"
  echo "Ou relancer setup sans --no-launch"
fi
echo ""
