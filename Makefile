# Docling Agent v3 — Developer commands (monorepo)
# Usage: make <target>

.PHONY: install dev test lint docker-up docker-down migrate migrate-down validate-skills skills-to-prompt validate-env health-check validate-all verify-project review emmet-analyze design-system spline-analyze docs setup clean audit-deps db-backup release docker-dev

# Setup initial (première installation)
setup:
	@bash scripts/setup.sh

# Nettoyage (cache, build). clean-full = + node_modules
clean:
	@bash scripts/clean.sh
clean-full:
	@bash scripts/clean.sh --full

# Audit sécurité dépendances (pip-audit + pnpm audit)
audit-deps:
	@bash scripts/audit-deps.sh

# Backup PostgreSQL (DATABASE_URL depuis .env)
db-backup:
	python scripts/db_backup.py

# Release (bump version + tag). make release BUMP=patch|minor|major
release:
	@bash scripts/release.sh $(or $(BUMP),patch)

# Docker Compose (environnement complet)
docker-dev:
	@bash scripts/docker-dev.sh up
docker-dev-down:
	@bash scripts/docker-dev.sh down
docker-dev-logs:
	@bash scripts/docker-dev.sh logs

# Install all dependencies (deps + dev) — mode dev
install:
	cd apps/api && uv sync --all-extras
	pnpm install

# Start backend + frontend locally (Linux/Mac; use run_local.bat on Windows)
dev:
	@bash scripts/run_dev.sh

# Run backend unit tests (sans serveur ni DB)
test:
	cd apps/api && uv run pytest tests -v

# Lint backend and frontend
lint:
	cd apps/api && uv run ruff check .
	cd apps/pwa && pnpm run lint

# Docker Compose: start services
docker-up:
	docker compose up -d

# Docker Compose: stop services
docker-down:
	docker compose down

# Run Alembic migrations (upgrade to head)
migrate:
	cd apps/api && uv run alembic upgrade head

# Rollback last Alembic migration
migrate-down:
	cd apps/api && uv run alembic downgrade -1

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

# Vérification complète projet (Audit Bêton aligné)
verify-project:
	@if command -v pwsh >/dev/null 2>&1; then pwsh -File scripts/verify_project.ps1; \
	elif command -v powershell >/dev/null 2>&1; then powershell -ExecutionPolicy Bypass -File scripts/verify_project.ps1; \
	else bash scripts/verify_project.sh; fi

# Review code (ruff + gito si installé)
review:
	@bash scripts/review.sh

# Routine DevOps senior — health-check + validate-all (début/fin session)
routine:
	python scripts/health_check.py 2>/dev/null || true
	@bash scripts/validate_all.sh

# Analyse opportunités Emmet (réduire le code JSX/HTML)
emmet-analyze:
	python scripts/analyze_emmet_opportunities.py --output docs/workflow/EMMET-OPPORTUNITIES.md

# Design system Docling (UI/UX Pro Max) — génère design-system/docling/MASTER.md
design-system:
	python scripts/design_system_docling.py --persist

# Analyse opportunités Spline 3D — docs/workflow/SPLINE-OPPORTUNITIES.md
spline-analyze:
	python scripts/analyze_spline_opportunities.py --output docs/workflow/SPLINE-OPPORTUNITIES.md

# Lancer MkDocs (documentation) — http://localhost:8100 (évite conflit API:8000)
docs:
	cd apps/api && uv run mkdocs serve -f ../../mkdocs.yml --no-livereload
