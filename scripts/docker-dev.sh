#!/usr/bin/env bash
# Docker Dev — Docling (lance docker compose pour environnement complet)
# Usage: ./scripts/docker-dev.sh [up|down|logs]
# Prérequis: .env configuré (DATABASE_URL, etc.)

set -euo pipefail
IFS=$'\n\t'

cd "$(dirname "$0")/.."

action="${1:-up}"

if [[ ! -f .env ]]; then
  echo "[WARN] .env absent. Copier .env.example vers .env"
fi

case "$action" in
  up)
    echo ""
    echo "=== DOCLING — DOCKER COMPOSE UP ==="
    docker compose up -d
    echo ""
    echo "Services:"
    echo "  API  : http://localhost:8000"
    echo "  PWA  : http://localhost:5173"
    echo "  Postgres : localhost:5432"
    echo ""
    ;;
  down)
    echo ""
    echo "=== DOCLING — DOCKER COMPOSE DOWN ==="
    docker compose down
    echo ""
    ;;
  logs)
    docker compose logs -f
    ;;
  *)
    echo "Usage: ./scripts/docker-dev.sh [up|down|logs]"
    exit 1
    ;;
esac
