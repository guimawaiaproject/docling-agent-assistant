# Docling Agent v3 — Catalogue BTP Intelligent

Application d'extraction automatisée de factures fournisseurs pour le secteur BTP.
Transforme des factures PDF ou photos (catalan/espagnol) en un catalogue de prix structuré, consultable et exportable en français.

## Prérequis

- **Python 3.11+**
- **Node.js 20+**
- **Compte Neon** — base PostgreSQL serverless ([neon.tech](https://neon.tech))
- **Clé API Gemini** — Google AI Studio ([aistudio.google.com](https://aistudio.google.com))
- **Compte Render** (backend) et **Netlify** (frontend) pour le déploiement

## Installation

```bash
git clone https://github.com/guimawaiaproject/docling-agent-assistant.git
cd docling-agent-assistant

# Backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt -r requirements-dev.txt

# Frontend
cd docling-pwa
npm install
cd ..

# Configurer l'environnement
cp .env.example .env
# Remplir les variables obligatoires (voir ci-dessous)

# Appliquer les migrations
alembic upgrade head
```

## Variables d'environnement (.env)

### Obligatoires

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Clé API Google Gemini |
| `DATABASE_URL` | URL PostgreSQL Neon (`postgresql://user:pass@host.neon.tech/db?sslmode=require`) |
| `JWT_SECRET` | Secret JWT — générer avec `openssl rand -hex 32` |

### Optionnelles

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DEFAULT_AI_MODEL` | Modèle IA | `gemini-3-flash-preview` |
| `WATCHDOG_FOLDER` | Dossier surveillé (dossier magique) | `./Docling_Factures` |
| `WATCHDOG_ENABLED` | Activer la surveillance du dossier | `true` |
| `STORJ_BUCKET` | Bucket S3 pour archivage PDF | `docling-factures` |
| `STORJ_ACCESS_KEY` | Clé d'accès Storj | _(vide = désactivé)_ |
| `STORJ_SECRET_KEY` | Clé secrète Storj | _(vide = désactivé)_ |
| `STORJ_ENDPOINT` | Endpoint S3 | `https://gateway.storjshare.io` |
| `PWA_URL` | URL frontend en production (CORS) | _(vide)_ |
| `JWT_EXPIRY_HOURS` | Durée de validité du token | `24` |
| `SENTRY_DSN` | DSN Sentry (monitoring erreurs) | _(vide = désactivé)_ |
| `ENVIRONMENT` | Nom de l'environnement | `production` |
| `VITE_TVA_RATE` | Taux TVA/IVA frontend | `0.21` (21%) |
| `VITE_API_URL` | URL de l'API pour le frontend | `http://localhost:8000` |
| `VITE_SENTRY_DSN` | DSN Sentry frontend | _(vide = désactivé)_ |

## Démarrage local

```bash
# Méthode rapide (Linux/Mac)
make dev

# Méthode rapide (Windows)
run_local.bat

# Méthode manuelle (2 terminaux)
# Terminal 1 — Backend :
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend :
cd docling-pwa && npm run dev
```

| Service | URL |
|---------|-----|
| PWA | https://localhost:5173 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |
| Swagger | http://localhost:8000/docs |

## Architecture

```
docling-agent-assistant/
├── api.py                         # Routeur FastAPI (async + BackgroundTasks)
├── backend/
│   ├── core/
│   │   ├── config.py              # Config pydantic-settings (.env)
│   │   ├── db_manager.py          # PostgreSQL Neon (asyncpg pool, upsert, cursor)
│   │   └── orchestrator.py        # Pipeline: prétraitement → Gemini → validation → DB
│   ├── schemas/
│   │   └── invoice.py             # Modèles Pydantic (Product, BatchSaveRequest)
│   ├── services/
│   │   ├── gemini_service.py      # Connecteur Gemini + retry rate-limit
│   │   ├── image_preprocessor.py  # OpenCV (CLAHE, débruitage, WebP)
│   │   ├── auth_service.py        # JWT (PyJWT) + hash argon2id
│   │   ├── storage_service.py     # Upload S3 Storj (boto3)
│   │   └── watchdog_service.py    # Surveillance dossier magique
│   └── utils/
│       └── serializers.py         # serialize_row (asyncpg Record → dict)
├── migrations/                    # Alembic (PostgreSQL migrations)
│   ├── env.py
│   └── versions/                  # a001_baseline, a002_constraints, a003_fk
├── docling-pwa/                   # Frontend React 19 + Vite 5 + Tailwind 4
│   ├── src/
│   │   ├── pages/                 # Scan, Validation, Catalogue, Devis, History, Settings
│   │   ├── components/            # Navbar, CompareModal, ErrorBoundary
│   │   ├── store/useStore.js      # Zustand (state management)
│   │   ├── services/              # apiClient, imageService, devisGenerator, offlineQueue
│   │   └── config/api.js          # Endpoints centralisés
│   └── vite.config.js             # Config Vite + PWA + HTTPS dev
├── tests/                         # 91 backend + 43 frontend = 134 tests
│   ├── 01_unit/                   # Tests unitaires (sans serveur)
│   ├── 02_integration/            # Tests intégration DB
│   ├── 03_api/                    # Tests endpoints API
│   ├── 04_e2e/                    # Playwright E2E
│   └── ...
├── docs/                          # Documentation technique
├── .github/workflows/ci.yml       # CI GitHub Actions
├── Dockerfile                     # Image Docker multi-stage
├── docker-compose.yml             # Stack complète (API + PostgreSQL)
├── Makefile                       # Commandes développeur
└── Procfile                       # Déploiement Render
```

## Déploiement (Render + Neon + Netlify)

### Backend (Render)

1. Connecter le repo GitHub à Render
2. Type : Web Service, Build Command : `pip install -r requirements.txt`
3. Start Command : `uvicorn api:app --host 0.0.0.0 --port $PORT`
4. Ajouter les variables d'environnement obligatoires

### Base de données (Neon)

1. Créer un projet sur [neon.tech](https://neon.tech)
2. Copier la `DATABASE_URL` (avec `-pooler` pour PgBouncer)
3. Appliquer les migrations : `alembic upgrade head`

### Frontend (Netlify)

1. Connecter le repo, répertoire : `docling-pwa`
2. Build Command : `npm run build`
3. Publish directory : `docling-pwa/dist`
4. Variable : `VITE_API_URL=https://votre-api.onrender.com`

## Commandes utiles

```bash
make install          # Installer toutes les dépendances (Python + Node)
make dev              # Lancer backend + frontend en local
make test             # Tests unitaires backend
make lint             # Lint backend (ruff) + frontend (eslint)
make docker-up        # Lancer la stack Docker
make docker-down      # Arrêter Docker
make migrate          # alembic upgrade head
make migrate-down     # alembic downgrade -1
```

## Tests

```bash
# Backend (91 tests)
pytest tests/01_unit -v --tb=short

# Frontend (43 tests)
cd docling-pwa && npx vitest run

# API (serveur requis)
pytest tests/03_api -v --tb=short

# E2E Playwright
pytest tests/04_e2e -v -m e2e

# Tous les tests (hors slow/external)
pytest tests/ -v -m "not slow and not external"
```

## Documentation

Voir [docs/README.md](docs/README.md) pour la documentation complète (architecture, API, services, audits).

## Licence

[MIT](LICENSE)
