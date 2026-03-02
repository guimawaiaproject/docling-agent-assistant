# Docling Agent v3 — Documentation

Application d'extraction automatisée de factures fournisseurs pour le secteur BTP. Transforme des factures PDF ou photos en un catalogue de prix structuré, consultable et exportable.

---

## Démarrage rapide

| Étape | Document |
|-------|----------|
| 1. Comprendre le flux | [Architecture — Vue d'ensemble](architecture/overview.md) |
| 2. Installer et lancer | [Installation](guides/installation.md) |
| 3. Consulter l'API | [Endpoints](api/endpoints.md) |
| 4. Contribuer | [Contribution](guides/contributing.md) |

---

## Index par rôle

| Rôle | Point d'entrée |
|------|----------------|
| **Nouveau dev / IA** | [Développement](guides/development.md) |
| **Architecture** | [Vue d'ensemble](architecture/overview.md) |
| **Déploiement** | [Déploiement](guides/deployment.md) |
| **Agents IA** | [Usage](ai-agents/usage.md) |

---

## Accès rapide

| Service | URL (dev local) |
|---------|-----------------|
| PWA | https://localhost:5173 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |
| Docs API | http://localhost:8000/docs |

---

## Stack technique

- **Frontend** : React 19 + Vite 5 + Tailwind 4 (PWA)
- **Backend** : FastAPI + Uvicorn
- **BDD** : PostgreSQL Neon
- **IA** : Google Gemini 3 Flash
- **Stockage** : Storj S3 (optionnel)
