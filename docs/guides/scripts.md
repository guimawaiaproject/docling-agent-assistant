# Scripts — Docling

Référence des scripts du projet.

## Setup & Dev

| Script | Usage | Description |
|--------|-------|-------------|
| `setup.ps1` / `setup.sh` | `make setup` | Setup initial (.env, uv, pnpm). Options: `-Build`, `-Migrate`, `-Launch` |
| `run_dev.sh` | `make dev` | Lance API + PWA en local |
| `docker-dev.ps1` / `docker-dev.sh` | `make docker-dev` | Docker Compose (postgres + api + pwa) |

## Validation

| Script | Usage | Description |
|--------|-------|-------------|
| `validate_all.ps1` / `validate_all.sh` | `make validate-all` | Lint + build + tests + skills |
| `validate_skills.py` | `make validate-skills` | Valide format SKILL.md |
| `validate_env.py` | `make validate-env` | Vérifie variables .env |
| `verify_project.ps1` / `verify_project.sh` | `make verify-project` | Vérification complète (Audit Bêton) |
| `health_check.py` | `make health-check` | Health API + DB |

## Nettoyage & Audit

| Script | Usage | Description |
|--------|-------|-------------|
| `clean.ps1` / `clean.sh` | `make clean` | Supprime cache, dist, .pytest_cache |
| `clean.sh --full` | `make clean-full` | + node_modules |
| `audit-deps.ps1` / `audit-deps.sh` | `make audit-deps` | pip-audit + pnpm audit |

## Base de données

| Script | Usage | Description |
|--------|-------|-------------|
| `db_backup.py` | `make db-backup` | Backup PostgreSQL (backups/) |
| `db_restore.py` | `python scripts/db_restore.py <fichier>` | Restauration depuis backup |

## Release

| Script | Usage | Description |
|--------|-------|-------------|
| `release.ps1` / `release.sh` | `make release BUMP=patch` | Bump version + tag git |

## Tests

| Script | Usage | Description |
|--------|-------|-------------|
| `test_api_e2e.py` | `uv run python scripts/test_api_e2e.py` | Test E2E API (--skip-extraction) |

## Utilitaires

| Script | Usage | Description |
|--------|-------|-------------|
| `fix-npm-windows.ps1` | manuel | Fix TAR_ENTRY sur Windows |
| `skills_to_prompt.py` | `make skills-to-prompt` | Génère XML skills |
| `analyze_emmet_opportunities.py` | `make emmet-analyze` | Opportunités Emmet |
| `analyze_spline_opportunities.py` | `make spline-analyze` | Opportunités Spline 3D |
| `design_system_docling.py` | `make design-system` | Génère design-system |
