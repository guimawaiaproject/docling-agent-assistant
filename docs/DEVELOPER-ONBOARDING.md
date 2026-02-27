# Onboarding développeur — Docling

Guide pour les développeurs humains et agents IA qui rejoignent le projet. Objectif : être productif en 30 minutes.

---

## Prérequis (5 min)

- **Python 3.11+**
- **Node.js 20+**
- **Compte Neon** — [neon.tech](https://neon.tech)
- **Clé API Gemini** — [aistudio.google.com](https://aistudio.google.com)

---

## Installation

```bash
git clone <repo>
cd docling

# Backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt -r requirements-dev.txt

# Frontend
cd docling-pwa && npm install && cd ..

# Configuration
cp .env.example .env
# Remplir GEMINI_API_KEY, DATABASE_URL, JWT_SECRET

# Migrations
alembic upgrade head
```

---

## Validation

```bash
make validate-all   # Lint + tests + skills
```

Si échec : corriger avant de continuer. Voir [development-workflow](.cursor/rules/development-workflow.mdc).

---

## Lecture recommandée (ordre)

| Document | Durée | Pourquoi |
|----------|-------|----------|
| [01-ARCHITECTURE.md](01-ARCHITECTURE.md) | 10 min | Comprendre le pipeline |
| [02-INSTALLATION.md](02-INSTALLATION.md) | 5 min | Détails installation |
| [03-API.md](03-API.md) | 10 min | Endpoints, schémas |
| [AGENTS.md](../AGENTS.md) | 5 min | Skills, règles, commands |
| [workflow/README.md](workflow/README.md) | 5 min | Stages backlog → completed |

---

## Conventions

| Domaine | Conventions |
|---------|-------------|
| **Backend** | `.cursor/rules/backend-conventions.mdc` |
| **Frontend** | `.cursor/rules/frontend-conventions.mdc` |
| **Tests** | `.cursor/rules/testing-patterns.mdc` |
| **Sécurité** | `.cursor/rules/security-guidelines.mdc` |

---

## Workflow de travail

1. **Lire** les fichiers concernés avant de modifier
2. **Une chose à la fois** : un endpoint, un composant, une migration
3. **Valider** après chaque modification : `make validate-all`
4. **Pas de "cleanup"** en passant — uniquement ce qui est demandé

---

## Commandes utiles

| Commande | Usage |
|----------|-------|
| `make dev` | Lancer backend + frontend |
| `make validate-all` | Lint + tests + skills |
| `make routine` | Health-check + validate-all |
| `make review` | Revue code (ruff + gito) |
| `make migrate` | Migration Alembic |

---

## Références

- [docs/README.md](README.md) — Index complet
- [docs/CONTRIBUTING.md](CONTRIBUTING.md) — Workflow contribution
- [docs/PROJECT-PROFILE.md](PROJECT-PROFILE.md) — Profil projet IA
