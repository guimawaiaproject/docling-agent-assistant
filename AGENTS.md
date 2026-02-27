# AGENTS.md — Docling

Guidance pour les agents IA (Cursor, Claude Code, Copilot) travaillant sur ce dépôt.

## Skills disponibles

Ce projet utilise le format [Agent Skills](https://agentskills.io/specification). Les skills sont chargés automatiquement par Cursor.

| Skill | Emplacement | Quand l'utiliser |
|-------|-------------|------------------|
| **neon-postgres** | `.agents/skills/neon-postgres/` | Questions Neon, PostgreSQL serverless, asyncpg, migrations |
| **docling-factures** | `.agents/skills/docling-factures/` | Extraction factures, API, catalogue BTP, pipeline Gemini |
| **multi-agent-workflow** | `.agents/skills/multi-agent-workflow/` | Coordination agents, quality gates, routine DevOps |

## Règles Cursor

| Règle | Fichier | Usage |
|-------|---------|-------|
| Agent Skills | `.cursor/rules/agent-skills.mdc` | Flux skills |
| Backend | `.cursor/rules/backend-conventions.mdc` | FastAPI, asyncpg |
| Frontend | `.cursor/rules/frontend-conventions.mdc` | React, Vite |
| Tests | `.cursor/rules/testing-patterns.mdc` | pytest, Vitest |
| Sécurité | `.cursor/rules/security-guidelines.mdc` | Auth, injection, secrets |
| workflow-planning | `docs/workflow/1_planning/**` | Stage planning (spec, design) |
| workflow-inprogress | `docs/workflow/2_inprogress/**` | Stage implémentation |
| workflow-completed | `docs/workflow/3_completed/**` | Stage livré |
| **ai-library** | `.cursor/rules/ai-library.mdc` | Bibliothèque IA — outils à suggérer (alwaysApply) |
| **development-workflow** | `.cursor/rules/development-workflow.mdc` | **Méthode dev — ne pas casser, valider avant/après (alwaysApply)** |
| **senior-devops-workflow** | `.cursor/rules/senior-devops-workflow.mdc` | **Routine DevOps — validate, review, docs (alwaysApply)** |

## Agents Cursor

| Agent | Fichier | Usage |
|-------|---------|-------|
| Migration Assistant | `.cursor/agents/migration-assistant.md` | Créer migrations Alembic |
| Test Generator | `.cursor/agents/test-generator.md` | Générer tests |
| API Reviewer | `.cursor/agents/api-reviewer.md` | Revue endpoints |
| **System Architect** | `.cursor/agents/system-architect.md` | Planification, spec, design |
| **Feature Developer** | `.cursor/agents/feature-developer.md` | Implémentation, tests |
| **Security Reviewer** | `.cursor/agents/security-reviewer.md` | Revue sécurité |
| **Context Specialist** | `.cursor/agents/context-specialist.md` | Analyse codebase |
| **Docs Writer** | `.cursor/agents/docs-writer.md` | Mise à jour documentation |

## Commands

| Command | Fichier | Usage |
|---------|---------|-------|
| validate-all | `.cursor/commands/validate-all.md` | Lint + tests + skills |
| setup-dev | `.cursor/commands/setup-dev.md` | Installation complète |
| generate-migration | `.cursor/commands/generate-migration.md` | Créer migration |
| run-full-tests | `.cursor/commands/run-full-tests.md` | Tous les tests |
| **plan** | `.cursor/commands/plan.md` | Décomposer objectif (System Architect) |
| **dev** | `.cursor/commands/dev.md` | Implémenter (Feature Developer) |
| **test** | `.cursor/commands/test.md` | Générer/exécuter tests |
| **review** | `.cursor/commands/review.md` | Revue code (Security Reviewer) |
| **validate** | `.cursor/commands/validate.md` | make validate-all |
| **routine** | `.cursor/commands/routine.md` | make routine (health-check + validate-all) |

## Flux multi-agents (générique)

Workflow applicable à tout projet. Voir [.cursor/WORKFLOW.md](.cursor/WORKFLOW.md) et [docs/workflow/MULTI-AGENT-WORKFLOW.md](docs/workflow/MULTI-AGENT-WORKFLOW.md).

## Validation et outils

```bash
make validate-skills    # Valider le format SKILL.md
make skills-to-prompt   # Générer <available_skills> XML
make validate-env      # Valider variables .env
make health-check      # Health API + DB
```

## Structure d'un skill

```
skill-name/
├── SKILL.md              # Obligatoire — name, description, instructions
├── references/           # Documentation détaillée
└── scripts/              # Scripts exécutables (optionnel)
```

Voir [.cursor/rules/agent-skills.mdc](.cursor/rules/agent-skills.mdc) et [docs/AI-INTEGRATION.md](docs/AI-INTEGRATION.md).

## Bibliothèque IA

Règle **ai-library.mdc** (alwaysApply) : contenu intégré pour que l'agent SUGGÈRE ces outils selon le contexte. Détails : [docs/ai-library/](docs/ai-library/).

## Conventions du projet

- **Backend** : Python 3.11+, FastAPI, asyncpg, Pydantic
- **Frontend** : React 19, Vite, Tailwind, Zustand
- **Base** : Neon PostgreSQL (URL avec `-pooler`)
- **Tests** : pytest (backend), Vitest (frontend)
