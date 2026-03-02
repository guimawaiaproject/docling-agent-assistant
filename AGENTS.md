# AGENTS.md — Docling

Guidance pour les agents IA (Cursor, Claude Code, Copilot) travaillant sur ce dépôt.

## Skills disponibles

Ce projet utilise le format [Agent Skills](https://agentskills.io/specification). Les skills sont chargés automatiquement par Cursor.

| Skill | Emplacement | Quand l'utiliser |
|-------|-------------|------------------|
| **neon-postgres** | `.agents/skills/neon-postgres/` | Questions Neon, PostgreSQL serverless, asyncpg, migrations |
| **docling-factures** | `.agents/skills/docling-factures/` | Extraction factures, API, catalogue BTP, pipeline Gemini |
| **multi-agent-workflow** | `.agents/skills/multi-agent-workflow/` | Coordination agents, quality gates, routine DevOps |
| **ui-ux-pro-max** | `.cursor/skills/ui-ux-pro-max/` | Design system, UI/UX, 67 styles, palettes, typo — [docs](docs/UI-UX-PRO-MAX-USAGE.md) |

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
| **debug-rescue** | `.cursor/rules/debug-rescue.mdc` | **Bloqué → doc projet + web search. Jamais régresser (.cursor, .agents)** |
| **dev-access-free** | `.cursor/rules/dev-access-free.mdc` | **Accès dev sans login — maintenir config, ne jamais supprimer LoginPage** |
| **agent-executes** | `.cursor/rules/agent-executes.mdc` | **L'agent exécute — ne pas déléguer à l'utilisateur** |
| **sonarqube-audit** | `.cursor/rules/sonarqube-audit.mdc` | SonarQube MCP — analyse qualité/sécurité (si configuré) |
| **emmet** | `.cursor/rules/emmet.mdc` | Abréviations HTML/CSS/JSX — [docs.emmet.io](https://docs.emmet.io/) |

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
| **Visual Design Expert** | `.cursor/agents/visual-design-expert.md` | Refonte visuelle, tendances 2026 |
| **Spline Expert** | `.cursor/agents/spline-expert.md` | Intégration 3D Spline, scènes interactives, React, Web |

## Commands

| Command | Fichier | Usage |
|---------|---------|-------|
| validate-all | `.cursor/commands/validate-all.md` | Lint + tests + skills |
| verify-project | `scripts/verify_project.ps1` | Vérification complète (Audit Bêton, déploiement) |
| setup-dev | `.cursor/commands/setup-dev.md` | Installation complète |
| generate-migration | `.cursor/commands/generate-migration.md` | Créer migration |
| run-full-tests | `.cursor/commands/run-full-tests.md` | Tous les tests |
| **plan** | `.cursor/commands/plan.md` | Décomposer objectif (System Architect) |
| **dev** | `.cursor/commands/dev.md` | Implémenter (Feature Developer) |
| **test** | `.cursor/commands/test.md` | Générer/exécuter tests |
| **review** | `.cursor/commands/review.md` | Revue code (Security Reviewer) |
| **validate** | `.cursor/commands/validate.md` | make validate-all |
| **routine** | `.cursor/commands/routine.md` | make routine (health-check + validate-all) |
| **audit-integral** | `.cursor/commands/audit-integral.md` | Audit complet projet (Expert Dev, 8 phases) |
| **audit-beton** | `.cursor/commands/audit-beton.md` | Audit Bêton v3 — 10 phases avec agents spécialisés |
| **redesign** | `.cursor/commands/redesign.md` | Moderniser visuel (Visual Design Expert, tendances 2026) |
| **spline** | `.cursor/commands/spline.md` | Analyser + intégrer Spline 3D (Spline Expert, chef domaine) |

## Flux multi-agents (générique)

Workflow applicable à tout projet. Voir [.cursor/WORKFLOW.md](.cursor/WORKFLOW.md) et [docs/workflow/MULTI-AGENT-WORKFLOW.md](docs/workflow/MULTI-AGENT-WORKFLOW.md).

## Validation et outils

```bash
make setup             # Setup initial (première installation)
make clean            # Nettoyage cache/build (clean-full = + node_modules)
make audit-deps       # Audit sécurité (pip-audit + pnpm audit)
make db-backup        # Backup PostgreSQL (backups/)
make release BUMP=patch   # Release (patch|minor|major)
make docker-dev       # Docker Compose up
make validate-skills  # Valider le format SKILL.md
make skills-to-prompt   # Générer <available_skills> XML
make validate-env      # Valider variables .env
make health-check      # Health API + DB
make verify-project    # Vérification complète (Audit Bêton, déploiement)
make emmet-analyze     # Opportunités Emmet — docs/workflow/EMMET-OPPORTUNITIES.md
make design-system     # Design system Docling (UI/UX Pro Max) — design-system/docling/MASTER.md
make spline-analyze    # Opportunités Spline 3D — docs/workflow/SPLINE-OPPORTUNITIES.md
# Commande @spline — lance le workflow Spline Expert (analyse + intégration)
```

**verify-project** : aligné sur `AUDIT_BETON/10_RAPPORT_FINAL.md`. Vérifie render.yaml, deploy.yml, pip-audit.

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
