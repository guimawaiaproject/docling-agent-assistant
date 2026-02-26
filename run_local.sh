#!/usr/bin/env bash
# Docling Agent v3 - Launcher (Linux/Mac)
# Usage: ./run_local.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Kill processes on ports 8000 and 5173 (targeted, avoids killing other projects)
kill_port() {
  local port=$1
  if command -v lsof &>/dev/null; then
    local pids
    pids=$(lsof -ti:"$port" 2>/dev/null)
    [[ -n "$pids" ]] && echo "$pids" | xargs kill -9 2>/dev/null || true
  elif command -v fuser &>/dev/null; then
    fuser -k "$port"/tcp 2>/dev/null || true
  fi
}

cleanup() {
  echo ""
  echo "[Cleanup] Arrêt des services..."
  kill_port 8000
  kill_port 5173
  [[ -n "$BACKEND_PID" ]] && kill -9 "$BACKEND_PID" 2>/dev/null || true
  [[ -n "$FRONTEND_PID" ]] && kill -9 "$FRONTEND_PID" 2>/dev/null || true
  exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "============================================================"
echo "     DOCLING AGENT v3 - LANCEMENT LOCAL (BTP EDITION)"
echo "============================================================"
echo ""

echo "[0/2] Nettoyage des processus sur ports 8000 et 5173..."
kill_port 8000
kill_port 5173

# Check venv
if [[ ! -f "venv/bin/python" && ! -f "venv/Scripts/python.exe" ]]; then
  echo "[ERROR] Environnement virtuel Python manquant."
  echo "Veuillez exécuter: python -m venv venv"
  exit 1
fi

PYTHON="venv/bin/python"
[[ -f "venv/Scripts/python.exe" ]] && PYTHON="venv/Scripts/python.exe"

# Start backend
echo "[1/2] Démarrage du Backend FastAPI (Port 8000)..."
$PYTHON api.py &
BACKEND_PID=$!

# Start frontend
echo "[2/2] Démarrage du Frontend PWA (Port 5173)..."
if [[ -f "docling-pwa/package.json" ]]; then
  (cd docling-pwa && npx vite) &
  FRONTEND_PID=$!
else
  echo "[WARNING] Dossier docling-pwa introuvable."
  FRONTEND_PID=""
fi

echo ""
echo "------------------------------------------------------------"
echo "[SUCCESS] Les deux services sont en cours de démarrage."
echo ""
echo "URL API  : http://localhost:8000"
echo "URL PWA  : http://localhost:5173"
echo "------------------------------------------------------------"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter."

wait
