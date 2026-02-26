# Docling Agent v3 — Developer commands
# Usage: make <target>

.PHONY: install dev test lint docker-up docker-down migrate migrate-down

# Install all dependencies (Python + Node)
install:
	python -m venv venv 2>/dev/null || true
	@if [ -f venv/bin/pip ]; then venv/bin/pip install -r requirements.txt -r requirements-dev.txt; \
	else venv/Scripts/pip install -r requirements.txt -r requirements-dev.txt; fi
	cd docling-pwa && npm install

# Start backend + frontend locally (Linux/Mac; use run_local.bat on Windows)
dev:
	@bash run_local.sh

# Run backend tests
test:
	python -m pytest tests/01_unit -v -k "not test_large_image"

# Lint backend and frontend
lint:
	python -m ruff check backend api.py 2>/dev/null || true
	cd docling-pwa && npm run lint

# Docker Compose: start services
docker-up:
	docker compose up -d

# Docker Compose: stop services
docker-down:
	docker compose down

# Run Alembic migrations (upgrade to head)
migrate:
	python -m alembic upgrade head

# Rollback last Alembic migration
migrate-down:
	python -m alembic downgrade -1
