# Intégration AI-first — Docling

Guide pour les agents IA (Cursor, Claude Code, Copilot) et les workflows automatisés.

## Vue d'ensemble

| Composant | Emplacement | Description |
|-----------|-------------|-------------|
| **Agent Skills** | `.agents/skills/` | Skills projet (docling-factures, neon-postgres) |
| **Règles Cursor** | `.cursor/rules/` | Conventions backend, frontend, tests, sécurité |
| **Agents** | `.cursor/agents/` | Migration assistant, test generator, API reviewer |
| **Commands** | `.cursor/commands/` | validate-all, setup-dev, generate-migration, run-full-tests |

## Agent Skills

Format [Agent Skills](https://agentskills.io/specification) :

- **docling-factures** : Extraction factures, API, catalogue BTP, pipeline Gemini
- **neon-postgres** : Neon PostgreSQL serverless, asyncpg, migrations

Validation : `make validate-skills`
Génération XML : `make skills-to-prompt`

## Règles Cursor

| Règle | Globs | Usage |
|-------|-------|-------|
| agent-skills | **/* | Flux Agent Skills |
| backend-conventions | api.py, backend/** | FastAPI, asyncpg |
| frontend-conventions | docling-pwa/src/** | React, Vite, Zustand |
| testing-patterns | tests/**, **/*.test.* | pytest, Vitest |
| security-guidelines | **/* | Auth, injection, secrets |

## Agents Cursor

| Agent | Description |
|-------|-------------|
| migration-assistant | Crée migrations Alembic |
| test-generator | Génère tests pytest/Vitest |
| api-reviewer | Revue endpoints FastAPI |

## Commands

| Command | Description |
|---------|-------------|
| validate-all | Lint + tests + validate-skills |
| setup-dev | Installation complète |
| generate-migration | Crée migration Alembic |
| run-full-tests | Tous les tests |

## Scripts

| Script | Usage |
|--------|-------|
| `scripts/validate_skills.py` | Validation format SKILL.md |
| `scripts/skills_to_prompt.py` | Génération XML prompts |
| `scripts/validate_env.py` | Validation .env |
| `scripts/health_check.py` | Health API + DB |

## Pre-commit

```bash
pip install pre-commit
pre-commit install
```

Hooks : ruff, validate-skills, trailing-whitespace, check-yaml, check-json, detect-private-key.

## Workflows

- **CI** : `.github/workflows/ci.yml` — tests backend + frontend, lint
- **Deploy** : `.github/workflows/deploy.yml` — Render, Netlify

## Bibliothèque IA

Référence complète d'outils IA : [docs/ai-library/README.md](ai-library/README.md)

Catégories : éditeurs, app builders, code completion, code review, coding agents, PR review, tests/QA, documentation, MCP, frameworks.

## Références

- [AGENTS.md](../AGENTS.md) — Guide agents
- [.cursor/rules/agent-skills.mdc](../.cursor/rules/agent-skills.mdc) — Règles Agent Skills
