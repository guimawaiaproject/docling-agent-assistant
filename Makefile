# Docling Agent v3 — Developer commands
# Usage: make <target>

.PHONY: install dev test lint docker-up docker-down migrate migrate-down validate-skills skills-to-prompt validate-env health-check validate-all review

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

# Validate Agent Skills (SKILL.md format)
validate-skills:
	python scripts/validate_skills.py

# Generate <available_skills> XML for agent prompts
skills-to-prompt:
	python scripts/skills_to_prompt.py

# Validate .env variables
validate-env:
	python scripts/validate_env.py

# Health check (API + DB)
health-check:
	python scripts/health_check.py

# Validation complète (lint + tests + skills) — après toute modification
validate-all:
	@bash scripts/validate_all.sh

# Review code (ruff + gito si installé)
review:
	@bash scripts/review.sh

# Routine DevOps senior — health-check + validate-all (début/fin session)
routine:
	python scripts/health_check.py 2>/dev/null || true
	@bash scripts/validate_all.sh
