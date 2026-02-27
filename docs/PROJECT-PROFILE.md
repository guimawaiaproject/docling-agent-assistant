# Profil projet — Docling

**Profil structuré pour IA** : onboarding rapide, contexte essentiel pour agents et développeurs.

---

## Identité

| Champ | Valeur |
|-------|--------|
| **Nom** | Docling Agent v3 |
| **Domaine** | BTP — extraction factures fournisseurs |
| **Objectif** | Base de prix matériaux réutilisable pour chiffrer des devis |

---

## Contexte métier

- **Utilisateur cible** : Chef de chantier BTP
- **Fournisseurs** : BigMat, Discor, Guerin Roses, etc. (catalan/espagnol)
- **Flux** : Factures PDF → extraction IA → catalogue → devis

---

## Stack

| Couche | Technologie |
|--------|-------------|
| Frontend | React 19, Vite 5, Tailwind 4, Zustand |
| Backend | FastAPI, Uvicorn, async |
| BDD | PostgreSQL Neon (serverless) |
| IA | Google Gemini 3 Flash |
| Prétraitement | OpenCV |
| Stockage | Storj S3-compatible |

---

## Structure clés

```
api.py                    # Routeur FastAPI
backend/core/              # config, db_manager, orchestrator
backend/services/          # gemini, auth, storage, watchdog
backend/schemas/           # Pydantic
docling-pwa/src/           # pages, components, store, services
migrations/                # Alembic
.agents/skills/            # docling-factures, neon-postgres
.cursor/rules/             # Conventions
```

---

## Conventions

- **Backend** : Python 3.11+, FastAPI, asyncpg, Pydantic
- **Frontend** : React 19, Vite, Tailwind, Zustand
- **Base** : Neon PostgreSQL (URL avec `-pooler`)
- **Tests** : pytest (backend), Vitest (frontend)

---

## Validation obligatoire

```bash
make validate-all   # Après toute modification
```

---

## Skills IA

| Skill | Quand |
|-------|-------|
| **docling-factures** | Extraction factures, API, catalogue BTP |
| **neon-postgres** | Neon, migrations, asyncpg |

---

## URLs (dev)

| Service | URL |
|---------|-----|
| PWA | https://localhost:5173 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |
| Swagger | http://localhost:8000/docs |
