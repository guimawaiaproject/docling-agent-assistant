# 🚀 08 — AUDIT BUILD & DÉPLOIEMENT
# Docker · CI/CD · GitHub Actions · Render · Variables ENV · Pipeline
# Phase 08 — Audit Bêton Docling Agent v3

---

## BD1 — ÉTAT DU BUILD INITIAL

### Commandes exécutées

```bash
# Build frontend
cd docling-pwa && npm run build

# Import backend
python -c "import api; import backend.core.config; ..."

# Lint frontend
cd docling-pwa && npm run lint

# Tests backend
pytest tests/01_unit -v --tb=short -q

# Tests frontend
cd docling-pwa && npm run test
```

### Résultat état initial

| Commande | Résultat | Erreurs | Warnings | Action requise |
|----------|----------|---------|----------|----------------|
| npm run build | **PASS** | 0 | 1 (chunks >500kB) | Optimiser code-split |
| npm run lint | **FAIL** | 1 | — | @eslint/js non trouvé (pnpm/npm mix) |
| python import api | **PASS** | 0 | 1 (SENTRY_DSN) | — |
| pytest tests/01_unit | **PARTIEL** | 5 | — | JWT tests échouent sans JWT_SECRET |
| npm run test | **FAIL** | 1 | — | vitest non dans PATH (script) |

### Détails

- **Build frontend** : Réussi en ~3m49s. Warning `chunkSizeWarningLimit` sur excel-gen (938 kB), pdf-gen (421 kB), charts (328 kB).
- **Lint** : `Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@eslint/js'` — conflit pnpm (.npmrc `node-linker=hoisted`) vs npm. En CI avec `npm ci` : OK.
- **pytest** : 5 tests JWT échouent sans `JWT_SECRET` en env (test_create_and_verify_token, test_expired_token_rejected, etc.). CI fournit `JWT_SECRET: ci-test-secret-for-jwt-32chars-long`.
- **npm run test** : Script `"test": "vitest run"` — vitest non trouvé en PATH. CI utilise `npx vitest run`. Corriger en `"test": "npx vitest run"` ou s'assurer que vitest est exécutable.

---

## BD2 — ANALYSE DOCKERFILE

### Dockerfile backend (présent)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY backend/ ./backend/
COPY api.py .
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Grille Dockerfile backend

| Critère | Statut | Note |
|---------|--------|------|
| Image de base | ✅ | python:3.11-slim (versionnée) |
| Multi-stage | ✅ | builder + runtime |
| Utilisateur non-root | ✅ | appuser créé et utilisé |
| COPY requirements avant COPY . | ✅ | Cache layer optimal |
| pip --no-cache-dir | ✅ | Oui |
| pip --require-hashes | ❌ | Non — à considérer pour supply chain |
| HEALTHCHECK | ✅ | curl /health |
| CMD cohérent | ✅ | uvicorn api:app |
| EXPOSE | ✅ | 8000 |
| Secrets via ENV runtime | ✅ | Pas hardcodés |
| .dockerignore | ✅ | Présent |

### Dockerfile frontend

**Absent** — Le frontend est servi en dev via `node:20-slim` dans docker-compose (vite --host). Pas d'image de production nginx pour le frontend. Render déploie uniquement le backend (Dockerfile).

### Grille Dockerfile

| Critère | Backend | Frontend | Action |
|---------|---------|----------|--------|
| Image non-root | ✅ | N/A | — |
| Multi-stage | ✅ | N/A | — |
| Layer cache optimal | ✅ | N/A | — |
| HEALTHCHECK | ✅ | N/A | — |
| .dockerignore | ✅ | N/A | — |
| Taille image | ~200 Mo estimé | N/A | — |
| Secrets hardcodés | Non | N/A | — |

---

## BD3 — ANALYSE .dockerignore

### Contenu actuel

```
# Dependencies & cache
node_modules/
**/node_modules/
__pycache__/
**/__pycache__/
*.pyc
*.pyo

# Git
.git/
.gitignore

# Tests (not needed in image)
tests/
*.pdf

# Environment (never copy secrets)
.env
.env.*
!.env.example

# Migrations bytecode
migrations/versions/*.pyc

# Frontend build (API image does not need it)
docling-pwa/dist/
docling-pwa/node_modules/
```

### Entrées manquantes dans .dockerignore

| Entrée manquante | Impact | À ajouter |
|------------------|--------|-----------|
| build/ | Artifacts build | Oui |
| coverage/ | Rapports coverage | Oui |
| .pytest_cache/ | Cache pytest | Oui |
| docs/ | Documentation | Optionnel |
| .github/ | Workflows CI | Optionnel |
| *.md | Fichiers markdown | Optionnel |
| venv/ .venv/ | Environnements Python | Oui |
| .ruff_cache/ | Cache ruff | Oui |
| .cursor/ .agents/ | Config agents | Oui |

---

## BD4 — ANALYSE CI/CD GITHUB ACTIONS

### Workflows présents

| Fichier | Rôle |
|---------|------|
| .github/workflows/ci.yml | CI principal — backend + frontend |
| .github/workflows/ci-cd.yml | Pipeline alternatif — quality, test, security, deploy |
| .github/workflows/deploy.yml | Déploiement Render/Railway + Vercel/Netlify |
| .github/workflows/tests.yml | Tests minimalistes (pytest tests/) |

### Problèmes identifiés

1. **Workflows dupliqués** : ci.yml, ci-cd.yml et tests.yml se chevauchent. Risque de confusion et de double exécution.
2. **ci-cd.yml** : Job `test` exécute `pytest tests/` sans service Postgres ni DATABASE_URL — les tests d'intégration échoueraient.
3. **deploy.yml** : `if: secrets.DEPLOY_PROVIDER == 'render'` — en GitHub Actions, `secrets.X` renvoie `***` si non défini ; la comparaison ne fonctionne pas. Utiliser `vars.DEPLOY_PROVIDER` ou un secret booléen.
4. **tests.yml** : Pas de Postgres, pas de migrations — tests incomplets.

### Grille CI/CD

| Workflow | Trigger | Lint | Tests | Security | Build | Deploy | Problèmes |
|----------|---------|------|-------|----------|-------|--------|------------|
| ci.yml | push/PR main | ✅ ruff, eslint | ✅ pytest + vitest | pip-audit, npm audit | ✅ | Non | DB de test OK |
| ci-cd.yml | push/PR main | ✅ ruff | ⚠️ pytest sans DB | pip-audit, bandit | Non | Render hook | Tests sans DB |
| deploy.yml | push main | Non | Non | Non | ✅ | Oui | Condition secrets incorrecte |
| tests.yml | push/PR main | Non | ⚠️ pytest minimal | Non | Non | Non | Redondant, pas de DB |

### Secrets utilisés

| Secret | Workflow | Usage |
|-------|----------|-------|
| RENDER_DEPLOY_HOOK | deploy.yml, ci-cd.yml | Déploiement Render |
| VITE_API_URL | ci.yml, deploy.yml | Build frontend |
| VITE_AUTH_REQUIRED | deploy.yml | Build frontend |
| VITE_SENTRY_DSN | deploy.yml | Build frontend |
| RAILWAY_TOKEN | deploy.yml | Deploy Railway |
| VERCEL_TOKEN, etc. | deploy.yml | Deploy frontend |

---

## BD5 — ANALYSE RENDER.YAML

### Contenu actuel

```yaml
# render.yaml — Render.com Infrastructure as Code (SQLite 2026)
services:
  - type: web
    name: docling-agent
    runtime: docker
    plan: free
    branch: main
    dockerfilePath: ./Dockerfile
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: WATCHDOG_FOLDER
        value: ./Docling_Factures
```

### Problèmes

| Problème | Gravité | Détail |
|----------|---------|--------|
| Commentaire "SQLite" | 🟠 | Projet utilise PostgreSQL (Neon) — commentaire obsolète |
| DATABASE_URL manquant | 🔴 | Obligatoire — doit être défini (sync: false) |
| JWT_SECRET manquant | 🔴 | Obligatoire — doit être défini (sync: false) |
| PWA_URL manquant | 🟠 | CORS — à définir pour prod |
| SENTRY_DSN manquant | 🟠 | Monitoring — recommandé |
| Health check path | ✅ | /health utilisé par Dockerfile HEALTHCHECK |
| Auto-deploy | ✅ | branch: main |
| Disk/volume | 🟠 | WATCHDOG_FOLDER=./Docling_Factures — pas de volume persistant configuré ; fichiers watchdog non persistés entre redéploiements |

---

## BD6 — VARIABLES D'ENVIRONNEMENT — ANALYSE COMPLÈTE

### Backend (config.py + api.py)

| Variable | Obligatoire | Validée | Défaut | .env.example | Problème |
|----------|-------------|---------|--------|--------------|----------|
| GEMINI_API_KEY | OUI | OUI | — | ✅ | — |
| DATABASE_URL | OUI | OUI | — | ✅ | — |
| JWT_SECRET | OUI | OUI (≥32 chars) | — | ✅ | — |
| JWT_EXPIRY_HOURS | Non | — | 24 | ✅ | — |
| WATCHDOG_FOLDER | Non | — | ./Docling_Factures | ✅ | — |
| WATCHDOG_ENABLED | Non | — | true | ✅ | — |
| DEFAULT_AI_MODEL | Non | enum | gemini-3-flash-preview | ✅ | — |
| STORJ_* | Non | — | — | ✅ | — |
| PWA_URL | Non | — | — | ✅ | — |
| SENTRY_DSN | Non | — | — | ✅ | — |
| ENVIRONMENT | Non | — | production | ❌ | Manquant |
| FREE_ACCESS_MODE | Non | — | false | ✅ | — |
| PORT | Non | — | 8000 | ❌ | Procfile utilise $PORT |

### Frontend (Vite)

| Variable | Obligatoire | Défaut | .env.example | Problème |
|----------|-------------|--------|--------------|----------|
| VITE_API_URL | Prod OUI | window.origin / localhost:8000 | ❌ | Manquant (doc dans commentaire) |
| VITE_AUTH_REQUIRED | Non | true | ✅ | — |
| VITE_TVA_RATE | Non | 0.21 | ✅ | — |
| VITE_SENTRY_DSN | Non | — | ✅ | — |

### Checklist .env.example

| Critère | Statut |
|---------|--------|
| Variables obligatoires avec description | ✅ |
| Variables optionnelles avec défaut | ✅ |
| Commentaires explicatifs | ✅ |
| Exemples réalistes (pas de vraies valeurs) | ✅ |
| Sections organisées | ✅ |
| Instructions JWT_SECRET (openssl rand -hex 32) | ✅ |
| ENVIRONMENT, PORT | ❌ Manquants |

---

## BD7 — ANALYSE DES SCRIPTS NPM

### Grille scripts npm (docling-pwa/package.json)

| Script | Commande | Fonctionnel | Manque |
|--------|----------|-------------|--------|
| dev | vite | ✅ | — |
| build | vite build | ✅ | — |
| preview | vite preview | ✅ | — |
| lint | eslint . | ⚠️ | Échoue si node_modules pnpm |
| test | vitest run | ❌ | vitest pas dans PATH → utiliser npx |
| test:watch | vitest | ❌ | Idem |
| test:coverage | vitest run --coverage | ❌ | Idem |

### Scripts manquants critiques

| Script | Commande suggérée | Pourquoi |
|--------|-------------------|----------|
| lint:fix | eslint . --fix | Fix auto des erreurs lint |
| test | npx vitest run | Garantit exécution même sans PATH |

---

## BD8 — MAKEFILE / SCRIPTS DE DEV

### Commandes Makefile

| Cible | Action | Statut |
|-------|--------|--------|
| install | venv + pip + npm install | ✅ |
| dev | run_local.sh | ✅ (Linux/Mac ; Windows : run_local.bat) |
| test | pytest tests/01_unit -k "not test_large_image" | ⚠️ Exclut test_large_image |
| lint | ruff + npm run lint | ✅ |
| docker-up / docker-down | docker compose | ✅ |
| migrate / migrate-down | alembic | ✅ |
| validate-skills | scripts/validate_skills.py | ✅ |
| validate-env | scripts/validate_env.py | ✅ |
| health-check | scripts/health_check.py | ✅ |
| validate-all | scripts/validate_all.sh | ✅ |
| review | scripts/review.sh | ✅ |
| routine | health-check + validate-all | ✅ |

### Manques

- `make test` ne lance pas les tests frontend.
- `make clean` absent (nettoyage artifacts).

---

## BD9 — ANALYSE PWA

### manifest (vite-plugin-pwa)

| Critère | Statut |
|---------|--------|
| name, short_name | ✅ Docling Agent BTP, Docling |
| display: standalone | ✅ |
| start_url: / | ✅ |
| icons 192x192, 512x512 | ✅ |
| theme_color, background_color | ✅ #0f172a |
| scope | ✅ / |

### Service Worker (Workbox)

| Critère | Statut |
|---------|--------|
| registerType: autoUpdate | ✅ |
| runtimeCaching | [] (aucun cache API) | ✅ Correct — pas de CacheFirst sur /api |
| globPatterns | **/*.{js,css,html,ico,png,svg,webp} | ✅ |

### HTTPS

PWA requiert HTTPS (sauf localhost). En prod : à garantir via Render/Vercel/Netlify.

---

## BD10 — ANALYSE LOGS & MONITORING

### Backend (api.py)

| Critère | Statut |
|---------|--------|
| Sentry initialisé si SENTRY_DSN | ✅ |
| traces_sample_rate: 0.1 | ✅ |
| environment, release | ✅ |
| Warning si prod sans SENTRY_DSN | ✅ |
| Logging format JSON | ❌ Format standard Python |
| Logging level configurable | ❌ |
| Logs démarrage (version, config) | Partiel (watchdog, modèle) |

### Frontend (main.jsx)

| Critère | Statut |
|---------|--------|
| @sentry/react + ErrorBoundary | ✅ |
| Sentry.init si VITE_SENTRY_DSN | ✅ |
| browserTracingIntegration | ✅ |
| tracesSampleRate: 0.1 | ✅ |
| captureException sur erreurs API | À vérifier dans ErrorBoundary |

---

## CORRECTIONS BUILD REQUISES

### [BD-001] npm run lint — @eslint/js non trouvé en local

- **Fichier** : docling-pwa/.npmrc
- **Erreur** : `Cannot find package '@eslint/js'` — conflit pnpm (node-linker=hoisted) vs npm
- **Fix** : Supprimer ou adapter .npmrc si utilisation exclusive de npm. Ou documenter `pnpm install` pour le frontend.
- **Vérif** : `cd docling-pwa && npm ci && npm run lint`

### [BD-002] npm run test — vitest non dans PATH

- **Fichier** : docling-pwa/package.json
- **Erreur** : `'vitest' n'est pas reconnu`
- **Fix** : Remplacer `"test": "vitest run"` par `"test": "npx vitest run"`
- **Vérif** : `cd docling-pwa && npm run test`

### [BD-003] pytest JWT — échec sans JWT_SECRET

- **Fichier** : tests/01_unit/test_auth_service.py (ou conftest)
- **Erreur** : 5 tests JWT échouent si JWT_SECRET vide
- **Fix** : Dans conftest.py ou pytest.ini, définir JWT_SECRET pour les tests unitaires (ou skip si absent)
- **Vérif** : `JWT_SECRET=test-secret-32-chars-minimum python -m pytest tests/01_unit -v`

### [BD-004] .dockerignore — entrées manquantes

- **Fichier** : .dockerignore
- **Fix** : Ajouter `build/`, `coverage/`, `.pytest_cache/`, `venv/`, `.venv/`, `.ruff_cache/`, `.cursor/`, `.agents/`
- **Vérif** : `docker build -t test .` — taille image réduite

### [BD-005] render.yaml — variables obligatoires manquantes

- **Fichier** : render.yaml
- **Fix** : Ajouter dans envVars : DATABASE_URL (sync: false), JWT_SECRET (sync: false), PWA_URL, SENTRY_DSN. Corriger commentaire "SQLite" → PostgreSQL.
- **Vérif** : Déploiement Render avec DB Neon

### [BD-006] deploy.yml — condition secrets incorrecte

- **Fichier** : .github/workflows/deploy.yml
- **Erreur** : `if: secrets.DEPLOY_PROVIDER == 'render'` — secrets.X masqué, comparaison impossible
- **Fix** : Utiliser `vars.DEPLOY_PROVIDER` ou un workflow_dispatch avec input. Ou déployer systématiquement Render si c'est le seul provider.
- **Vérif** : Push sur main déclenche le bon déploiement

### [BD-007] Workflows CI dupliqués

- **Fichiers** : ci.yml, ci-cd.yml, tests.yml
- **Fix** : Consolider en un seul workflow CI (ex. ci.yml) et supprimer ou désactiver ci-cd.yml et tests.yml.
- **Vérif** : Un seul workflow CI sur push/PR

### [BD-008] ci-cd.yml — tests sans Postgres

- **Fichier** : .github/workflows/ci-cd.yml
- **Erreur** : Job test exécute pytest sans service postgres ni DATABASE_URL
- **Fix** : Ajouter service postgres comme dans ci.yml, ou limiter aux tests/01_unit qui ne nécessitent pas DB.
- **Vérif** : Job test passe en CI

### [BD-009] .env.example — ENVIRONMENT, PORT manquants

- **Fichier** : .env.example
- **Fix** : Ajouter `# ENVIRONMENT=production` et `# PORT=8000` avec commentaires.
- **Vérif** : validate_env.py et déploiement

### [BD-010] Build frontend — chunks >500 kB

- **Fichier** : docling-pwa/vite.config.js
- **Warning** : excel-gen (938 kB), pdf-gen (421 kB), charts (328 kB)
- **Fix** : Dynamic import() pour les pages Devis/Validation (excel, pdf) ; lazy load recharts.
- **Vérif** : `npm run build` — moins de warnings chunk size

---

## SCORECARD BUILD & DÉPLOIEMENT

| Domaine | Score /100 | Problèmes 🔴 | Problèmes 🟠 | Notes |
|---------|------------|--------------|--------------|-------|
| Build frontend | 85 | 0 | 1 (chunks) | Build OK, warnings |
| Build backend | 90 | 0 | 0 | Import OK |
| Dockerfile | 90 | 0 | 1 (--require-hashes) | Solide |
| CI/CD pipeline | 65 | 2 | 3 | Duplication, conditions |
| Variables d'env | 85 | 0 | 2 | .env.example quasi complet |
| PWA config | 95 | 0 | 0 | Bien configuré |
| Monitoring | 80 | 0 | 1 | Sentry OK, logs non JSON |
| **GLOBAL** | **84** | **2** | **8** | |

---

## ✅ GATE BD — BUILD & DÉPLOIEMENT

### Critères de passage

| Critère | Statut |
|---------|--------|
| npm run build → exit code 0 | ✅ PASS |
| python import api → 0 erreur | ✅ PASS |
| 0 secret hardcodé dans le code | ✅ PASS |
| package-lock.json présent | ✅ PASS |
| npm run lint (en CI avec npm ci) | ✅ PASS |
| pytest (avec JWT_SECRET en CI) | ✅ PASS |

### Problèmes bloquants

- **BD-005** : render.yaml sans DATABASE_URL, JWT_SECRET — déploiement Render échouera au démarrage.
- **BD-006** : deploy.yml condition secrets — déploiement peut ne pas se déclencher correctement.

### Verdict

```
STATUS : [ ] PASS  [X] FAIL
```

**GATE BD : FAIL**

Les corrections [BD-005] et [BD-006] sont requises pour un déploiement fiable. Les corrections [BD-001] à [BD-004] et [BD-007] à [BD-010] sont recommandées pour la robustesse du pipeline.

---

*Audit Phase 08 — Build & Déploiement — Docling Agent v3 — 2026-02-28*
