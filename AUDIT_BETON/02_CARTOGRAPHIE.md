# 🗺️ 02 — CARTOGRAPHIE EXHAUSTIVE
# Référence de 100% des fichiers du projet
# Exécuté le 28 février 2026 — Phase 02 Audit Bêton Docling
# Agent : context-specialist

---

## PRINCIPE

```
Cette cartographie est LA référence absolue du projet.
Chaque fichier listé ici sera analysé dans les audits suivants.
Si un fichier n'est pas ici → il n'est pas audité → il n'existe pas.

FORMAT DE CHAQUE ENTRÉE :
  [chemin/fichier]
  ├── LIGNES       : N
  ├── TAILLE       : X Ko
  ├── RÔLE         : Ce que ce fichier fait en 1 phrase
  ├── DÉPEND DE    : Fichiers qu'il importe/utilise
  ├── UTILISÉ PAR  : Fichiers qui l'importent/utilisent
  ├── DERNIER MAJ  : git log -1 --format="%ar" -- [fichier]
  └── ÉTAT         : ✅ Normal / ⚠️ À surveiller / ❌ Problème détecté
```

---

## COMMANDES EXÉCUTÉES (Windows/PowerShell)

```powershell
# 1. Arborescence complète (excl. .git, node_modules, __pycache__, dist)
Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\.git|node_modules|__pycache__|\.pyc|\\dist\\' }

# 2. Comptage lignes (Python)
python -c "from pathlib import Path; ..."

# 3. Fichiers non trackés
git status --porcelain | findstr "^??"
```

### Fichiers non trackés (git status ??)

| Fichier | Action |
|---------|--------|
| AUDIT_BETON/ | Dossier audit en cours — GARDER |
| docling-pwa/.npmrc | Config npm — à committer si pertinent |
| docling-pwa/pnpm-lock.yaml | Lockfile pnpm — à committer si utilisé |
| docs/FIX-NPM-TAR-ENTRY-WINDOWS.md | Doc fix Windows — à committer |
| scripts/fix-npm-windows.ps1 | Script fix — à committer |
| scripts/pre_launch_check.ps1 | Pre-launch — à committer |
| scripts/pre_launch_check.sh | Pre-launch Linux — à committer |
| scripts/run-audit-beton.ps1 | Script audit — GARDER |

---

## SECTION C1 — RACINE DU PROJET

### Tableau C1 — Racine

| Fichier | Lignes | Rôle | État | Anomalies |
|---------|--------|------|------|-----------|
| api.py | 778 | Routeur FastAPI principal — endpoints extraction, catalogue, auth, sync, health | ✅ Normal | Fichier le plus long du projet — à surveiller pour découpage |
| requirements.txt | 45 | Dépendances Python prod (FastAPI, asyncpg, google-genai, boto3, etc.) | ✅ Normal | |
| requirements-dev.txt | 12 | Dépendances dev (pytest, httpx, faker, pre-commit) | ✅ Normal | |
| .env.example | 39 | Template variables d'environnement (GEMINI, DB, JWT, Storj, etc.) | ✅ Normal | |
| .gitignore | 58 | Exclusions git (venv, node_modules, .env, dist, credentials) | ✅ Normal | .cursor/ exclu — règle projet : ne pas supprimer |
| Makefile | 70 | Commandes projet (install, dev, test, lint, migrate, validate-all, routine) | ✅ Normal | |
| docker-compose.yml | 59 | Services Docker : postgres, api, pwa | ✅ Normal | |
| Dockerfile | 22 | Build multi-stage Python 3.11 pour API | ✅ Normal | |
| README.md | 204 | Documentation projet — installation, variables, déploiement | ✅ Normal | |
| alembic.ini | 39 | Config Alembic — script_location=migrations, pas d'URL hardcodée | ✅ Normal | |
| pyproject.toml | 51 | Config projet (pytest, ruff) — version 2.0.0, dépendances optionnelles | ✅ Normal | pyproject.toml déclare streamlit/pandas non dans requirements.txt — incohérence mineure |
| render.yaml | 15 | Config Render.com — service web Docker | ✅ Normal | |
| run_local.bat | 59 | Lanceur Windows — pre-launch check, backend + frontend | ✅ Normal | |
| AGENTS.md | ~100 | Guidance agents IA — skills, règles, commandes | ✅ Normal | |

---

## SECTION C2 — BACKEND/

### Sous-section C2.1 — backend/core/

| Fichier | Lignes | Rôle | Importe | Importé par | État |
|---------|--------|------|---------|-------------|------|
| config.py | 130 | Variables env + validation pydantic-settings au démarrage | pydantic, pydantic-settings | api.py, db_manager, orchestrator, services | ✅ Normal |
| db_manager.py | 646 | Pool asyncpg, CRUD produits, pagination cursor, recherche pg_trgm | asyncpg, config | api.py, orchestrator | ✅ Normal | Fichier long — logique métier dense |
| orchestrator.py | 152 | Pipeline extraction : Factur-X → Gemini → BDD → historique | db_manager, facturx, gemini, image_preprocessor, storage | api.py | ✅ Normal |

### Sous-section C2.2 — backend/services/

| Fichier | Lignes | Rôle | Service externe | État |
|---------|--------|------|-----------------|------|
| auth_service.py | 107 | JWT (PyJWT) + Argon2id, rehash PBKDF2→Argon2 | — | ✅ Normal |
| gemini_service.py | 187 | Extraction IA multilingue CA/ES/FR | Google Gemini API | ✅ Normal |
| watchdog_service.py | 153 | Surveillance dossier magique (watchdog) | filesystem (watchdog) | ✅ Normal |
| storage_service.py | 116 | Upload PDF vers S3/Storj | boto3 (S3-compatible) | ✅ Normal |
| facturx_extractor.py | 185 | Extraction Factur-X/ZUGFeRD (XML PDF) sans IA | lxml (XXE-hardened) | ✅ Normal |
| image_preprocessor.py | 74 | Prétraitement images OpenCV avant Gemini | OpenCV | ✅ Normal |

### Sous-section C2.3 — backend/schemas/

| Fichier | Lignes | Schémas définis | Utilisé par | État |
|---------|--------|-----------------|-------------|------|
| invoice.py | 84 | Product, InvoiceExtractionResult, BatchSaveRequest, FAMILLES_VALIDES | api.py, orchestrator, gemini, facturx | ✅ Normal |

### Sous-section C2.4 — backend/utils/

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| serializers.py | 24 | asyncpg Record → dict (date, Decimal, datetime) | ✅ Normal |

### Sous-section C2.5 — backend/tests/

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| conftest.py | 2 | Init minimal | ✅ Normal |
| test_security.py | 144 | Tests sécurité (injection, _escape_like, _safe_float) | ✅ Normal |

---

## SECTION C3 — MIGRATIONS/

| Fichier | Lignes | Migration | Ordre | downgrade() | État |
|---------|--------|-----------|-------|-------------|------|
| env.py | 98 | Config Alembic — asyncpg, DATABASE_URL, SSL | — | — | ✅ Normal |
| versions/a001_baseline_schema.py | 163 | Tables fournisseurs, produits, jobs, factures, users | 1 | Oui | ✅ Normal |
| versions/a002_add_check_constraints.py | 53 | CHECK status, role, confidence, source | 2 | Oui | ✅ Normal |
| versions/a003_add_fk_fournisseur.py | 54 | FK fournisseur → fournisseurs | 3 | Oui | ✅ Normal |
| versions/a004_add_jobs_user_id.py | 28 | user_id sur jobs | 4 | Oui | ✅ Normal |
| versions/a005_add_user_id_and_perf_indexes.py | 66 | user_id produits, index perf | 5 | Oui | ✅ Normal |
| versions/a006_unique_produits_user_id.py | 36 | UNIQUE (designation_raw, fournisseur, user_id) | 6 | Oui | ✅ Normal |

---

## SECTION C4 — TESTS/

| Fichier | Lignes | Ce qui est testé | Nb tests estimé | Couverture | État |
|---------|--------|-----------------|-----------------|------------|------|
| conftest.py | 158 | Fixtures globales (serveur, DB, utilisateur, client auth) | — | — | ✅ Normal |
| 01_unit/test_auth_service.py | 100 | Auth JWT, Argon2, rehash | ~8 | — | ✅ Normal |
| 01_unit/test_config.py | 24 | Config validation | ~3 | — | ✅ Normal |
| 01_unit/test_gemini_service.py | 113 | GeminiService (mock) | ~5 | — | ✅ Normal |
| 01_unit/test_image_preprocessor.py | 58 | ImagePreprocessor | ~4 | — | ✅ Normal |
| 01_unit/test_models.py | 223 | Schémas Pydantic (Product, validators) | ~15 | — | ✅ Normal |
| 01_unit/test_orchestrator.py | 55 | Orchestrator process_file | ~3 | — | ✅ Normal |
| 01_unit/test_validators.py | 87 | Validateurs invoice | ~8 | — | ✅ Normal |
| 02_integration/test_database.py | 85 | Connexion DB, CRUD | ~5 | — | ✅ Normal |
| 02_integration/test_storage.py | 38 | StorageService (mock S3) | ~3 | — | ✅ Normal |
| 03_api/test_auth.py | 102 | Login, register, token | ~8 | — | ✅ Normal |
| 03_api/test_catalogue.py | 127 | Endpoints catalogue, batch | ~10 | — | ✅ Normal |
| 03_api/test_health.py | 23 | /health | ~2 | — | ✅ Normal |
| 03_api/test_invoices.py | 56 | Process, status | ~5 | — | ✅ Normal |
| 03_api/test_reset_admin.py | 46 | DELETE /catalogue/reset | ~3 | — | ✅ Normal |
| 03_api/test_stats_history.py | 35 | Stats, history | ~3 | — | ✅ Normal |
| 03_api/test_sync.py | 12 | Sync status | ~1 | — | ✅ Normal |
| 04_e2e/test_catalogue_browse.py | 34 | E2E catalogue | ~2 | — | ✅ Normal |
| 04_e2e/test_scan_flow.py | 63 | E2E scan | ~4 | — | ✅ Normal |
| 04_e2e/test_settings_sync.py | 25 | E2E settings | ~2 | — | ✅ Normal |
| 05_security/test_auth_bypass.py | 64 | Bypass auth (FREE_ACCESS_MODE) | ~5 | — | ✅ Normal |
| 05_security/test_headers.py | 22 | Headers sécurité | ~2 | — | ✅ Normal |
| 05_security/test_injection.py | 86 | Injection SQL, XSS | ~6 | — | ✅ Normal |
| 06_performance/test_response_times.py | 51 | Temps réponse | ~3 | — | ✅ Normal |
| 06_performance/locustfile.py | 63 | Locust load test | — | — | ✅ Normal |
| 07_data_integrity/test_api_db_coherence.py | 55 | Cohérence API↔DB | ~4 | — | ✅ Normal |
| 07_data_integrity/test_constraints.py | 46 | Contraintes DB | ~3 | — | ✅ Normal |
| 07_data_integrity/test_transactions.py | 56 | Transactions | ~4 | — | ✅ Normal |
| 08_external_services/test_extraction_reelle.py | 38 | Extraction réelle (Gemini) | ~2 | — | ⚠️ Marqué external | ✅ Normal |

---

## SECTION C5 — DOCLING-PWA/

### Sous-section C5.1 — docling-pwa/src/pages/

| Fichier | Lignes | Page | Routes | Imports principaux | État |
|---------|--------|------|--------|--------------------|------|
| App.jsx | 80 | Router principal | /, /scan, /validation, /catalogue, /history, /settings, /devis, /login, /register | react-router, zustand, CommandPalette, Navbar, ProtectedRoute | ✅ Normal |
| ScanPage.jsx | 770 | Scan + upload | /scan | dropzone, apiClient, imageService, useStore | ⚠️ Très long | Fichier le plus long frontend |
| ValidationPage.jsx | 279 | Validation produits extraits | /validation | apiClient, useStore, categories | ✅ Normal |
| CataloguePage.jsx | 535 | Catalogue paginé, export Excel | /catalogue | apiClient, CompareModal, recharts, exceljs | ✅ Normal |
| DevisPage.jsx | 366 | Génération devis PDF | /devis | devisGenerator, apiClient | ✅ Normal |
| HistoryPage.jsx | 277 | Historique factures | /history | apiClient | ✅ Normal |
| SettingsPage.jsx | 409 | Paramètres, sync | /settings | apiClient, useStore, features | ✅ Normal |
| LoginPage.jsx | 116 | Connexion | /login | apiClient | ✅ Normal |
| RegisterPage.jsx | 136 | Inscription | /register | apiClient | ✅ Normal |

### Sous-section C5.2 — docling-pwa/src/components/

| Fichier | Lignes | Composant | Props | Utilisé par | État |
|---------|--------|-----------|-------|-------------|------|
| Navbar.jsx | 68 | Navigation bottom bar | — | App.jsx | ✅ Normal |
| CommandPalette.jsx | 111 | Raccourcis clavier (Ctrl+K) | — | App.jsx | ✅ Normal |
| ProtectedRoute.jsx | 14 | Redirection /login si non auth | — | App.jsx | ✅ Normal |
| CompareModal.jsx | 272 | Modal comparaison prix | products, onClose | CataloguePage | ✅ Normal |
| ErrorBoundary.jsx | 69 | Capture erreurs React | — | main.jsx | ✅ Normal |

### Sous-section C5.3 — docling-pwa/src/services/

| Fichier | Lignes | Service | API externe | État |
|---------|--------|---------|-------------|------|
| apiClient.js | 52 | Client Axios, retry, cookie httpOnly | Backend API | ✅ Normal |
| offlineQueue.js | 70 | IndexedDB queue uploads offline | — | ✅ Normal |
| devisGenerator.js | 170 | Génération PDF devis (jspdf) | — | ✅ Normal |
| imageService.js | 49 | Compression WebP (compressToWebP) | — | ✅ Normal |

### Sous-section C5.4 — docling-pwa/src/store/

| Fichier | Lignes | State géré | Persisté | État |
|---------|--------|-----------|----------|------|
| useStore.js | 126 | Produits, batchQueue, modèle IA, job | Oui (selectedModel, batchQueue partiel) | ✅ Normal |

### Sous-section C5.5 — docling-pwa/src/config/

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| api.js | 29 | URLs endpoints (ENDPOINTS, API_BASE_URL) | ✅ Normal |
| features.js | 3 | Feature flags (AUTH_REQUIRED) | ✅ Normal |

### Sous-section C5.6 — docling-pwa/src/constants/

| Fichier | Lignes | Constantes | Utilisé par | État |
|---------|--------|-----------|-------------|------|
| categories.js | 8 | FAMILLES, FAMILLES_AVEC_TOUTES | ValidationPage, CataloguePage | ✅ Normal |

### Sous-section C5.7 — docling-pwa/src/utils/

| Fichier | Lignes | Utilitaires | Utilisé par | État |
|---------|--------|------------|-------------|------|
| reportWebVitals.js | 43 | Métriques Web Vitals (CLS, LCP, etc.) | main.jsx | ✅ Normal |

### Sous-section C5.7b — docling-pwa/src/ (racine src)

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| main.jsx | 31 | Point d'entrée React — Sentry, BrowserRouter, App, ErrorBoundary | ✅ Normal |
| index.css | 31 | Styles Tailwind + base (slate-950, safe-area) | ✅ Normal |

### Sous-section C5.8 — docling-pwa/src/hooks/

| Fichier | Lignes | Hook | Utilisé par | État |
|---------|--------|------|-------------|------|
| — | — | Aucun hook custom | — | Absent |

### Sous-section C5.9 — docling-pwa/src/__tests__/

| Fichier | Lignes | Ce qui est testé | Nb tests | État |
|---------|--------|-----------------|----------|------|
| setup.js | ~10 | jest-dom, config Vitest | — | ✅ Normal |
| apiClient.test.js | ~50 | apiClient retry, interceptors | ~5 | ✅ Normal |
| useStore.test.js | ~80 | useStore actions | ~6 | ✅ Normal |
| CompareModal.test.jsx | ~100 | CompareModal | ~5 | ✅ Normal |
| pages/__tests__/CataloguePage.test.jsx | ~80 | CataloguePage | ~4 | ✅ Normal |

---

## SECTION C6 — CONFIGURATION ROOT (docling-pwa)

| Fichier | Rôle | État | Problèmes |
|---------|------|------|-----------|
| package.json | Dépendances + scripts (dev, build, lint, test) | ✅ Normal | 24 prod + 12 dev deps |
| package-lock.json | Lockfile npm déterministe | ✅ Normal | |
| vite.config.js | Build Vite + PWA (Workbox), HTTPS dev, chunks | ✅ Normal | |
| tailwind.config.js | Config Tailwind (content, theme) | ✅ Normal | |
| postcss.config.cjs | PostCSS (tailwindcss, autoprefixer) | ✅ Normal | |
| eslint.config.js | ESLint flat config (react-hooks, react-refresh) | ✅ Normal | |
| index.html | Entrée HTML, CSP, PWA meta | ✅ Normal | |
| .npmrc | Config npm (si présent) | ✅ Normal | Non tracké |
| pnpm-lock.yaml | Lockfile pnpm (si utilisé) | ✅ Normal | Non tracké |

---

## SECTION C7 — CI/CD & DÉPLOIEMENT

| Fichier | Rôle | Triggers | État |
|---------|------|----------|------|
| .github/workflows/ci.yml | CI : backend-test, frontend-build, backend-lint, frontend-lint | push, PR (main) | ✅ Normal |
| .github/workflows/ci-cd.yml | CI/CD alternatif | — | À vérifier |
| .github/workflows/deploy.yml | Déploiement | — | À vérifier |
| .github/workflows/tests.yml | Tests dédiés | — | À vérifier |
| render.yaml | Config Render.com (Docker) | — | ✅ Normal |

---

## SECTION C8 — FICHIERS SPÉCIAUX & CACHÉS

| Fichier | Rôle | Commité ? | Devrait l'être ? | Action |
|---------|------|-----------|-----------------|--------|
| .env.example | Template envs | Oui | Oui | — |
| .env | Valeurs réelles | Non (.gitignore) | NON | — |
| .editorconfig | Style éditeur | — | Oui (optionnel) | — |
| .prettierrc | Format code | — | Oui (optionnel) | — |
| .cursor/ | Config Cursor, règles, agents | Non (.gitignore) | Non (règle projet) | Ne pas supprimer |
| .agents/ | Skills Agent Skills | — | Oui (si partagés) | — |

---

## MATRICE DE DÉPENDANCES

### BACKEND

```
api.py
  → backend.core.config, db_manager, orchestrator
  → backend.schemas.invoice (BatchSaveRequest)
  → backend.services.auth_service, storage_service, watchdog_service
  → backend.utils.serializers
  → fastapi, slowapi, sentry_sdk

db_manager.py
  → backend.core.config
  → asyncpg

orchestrator.py
  → backend.core.db_manager
  → backend.services.facturx_extractor, gemini_service, image_preprocessor, storage_service

gemini_service.py
  → backend.core.config, backend.schemas.invoice
  → google.genai

facturx_extractor.py
  → backend.schemas.invoice
  → lxml

watchdog_service.py
  → backend.core.config, orchestrator
  → watchdog

storage_service.py
  → backend.core.config
  → boto3

auth_service.py
  → jwt, argon2 (pas de backend.*)
```

### FRONTEND

```
App.jsx
  → react-router-dom, sonner
  → CommandPalette, Navbar, ProtectedRoute
  → config/features
  → pages (lazy)

ScanPage.jsx
  → apiClient, ENDPOINTS, imageService, useStore
  → react-dropzone, framer-motion, lucide-react

CataloguePage.jsx
  → apiClient, ENDPOINTS, CompareModal, categories
  → recharts, exceljs

ValidationPage.jsx
  → apiClient, ENDPOINTS, useStore, categories

DevisPage.jsx
  → apiClient, ENDPOINTS, devisGenerator

SettingsPage.jsx
  → apiClient, ENDPOINTS, features, useStore

apiClient.js
  → axios, config/api (API_BASE_URL)
```

### DÉPENDANCES CIRCULAIRES DÉTECTÉES

**Aucune** — graphe acyclique.

### MODULES LES PLUS IMPORTÉS (hubs critiques)

| Module | Importé par |
|--------|-------------|
| backend.core.config | api.py, db_manager, orchestrator, gemini, storage, watchdog |
| backend.schemas.invoice | api.py, orchestrator, gemini, facturx |
| apiClient (frontend) | ScanPage, ValidationPage, CataloguePage, DevisPage, HistoryPage, SettingsPage, LoginPage, RegisterPage, CompareModal |
| config/api (ENDPOINTS) | Toutes les pages, apiClient, reportWebVitals |
| useStore | ScanPage, ValidationPage, SettingsPage |

---

## STATISTIQUES FINALES

### BACKEND

| Métrique | Valeur |
|---------|--------|
| Fichiers Python | 48 (api + backend + migrations + tests) |
| Lignes totales | ~4 200 |
| Fichier le plus long | api.py (778 lignes) |
| Fichier le 2e plus long | db_manager.py (646 lignes) |
| Fonctions totales | ~120 (estimation) |
| Classes totales | ~15 |

### FRONTEND

| Métrique | Valeur |
|---------|--------|
| Fichiers JSX/JS | 30 (pages + components + services + config + store + tests) |
| Lignes totales | ~4 100 |
| Composants React | 10 (Navbar, CommandPalette, ProtectedRoute, CompareModal, ErrorBoundary + 8 pages) |
| Hooks customs | 0 |
| Pages | 9 |

### GLOBAL

| Métrique | Valeur |
|---------|--------|
| Fichiers source total | ~80 |
| Lignes source total | ~8 300 |
| Ratio test/code | ~35% (objectif > 30%) ✅ |
| Dépendances backend (requirements.txt) | 24 |
| Dépendances frontend prod | 24 |
| Dépendances frontend dev | 12 |

---

## TOP 10 FICHIERS LES PLUS LONGS

| Rang | Fichier | Lignes |
|------|---------|--------|
| 1 | api.py | 778 |
| 2 | docling-pwa/src/pages/ScanPage.jsx | 770 |
| 3 | backend/core/db_manager.py | 646 |
| 4 | docling-pwa/src/pages/CataloguePage.jsx | 535 |
| 5 | docling-pwa/src/pages/SettingsPage.jsx | 409 |
| 6 | docling-pwa/src/pages/DevisPage.jsx | 366 |
| 7 | docling-pwa/src/pages/ValidationPage.jsx | 279 |
| 8 | docling-pwa/src/pages/HistoryPage.jsx | 277 |
| 9 | docling-pwa/src/components/CompareModal.jsx | 272 |
| 10 | tests/01_unit/test_models.py | 223 |

---

## ✅ GATE C — CARTOGRAPHIE

```
PASS si :
  → 100% des fichiers source sont dans les tableaux ci-dessus
  → Aucun fichier d'ancien audit dans la liste
  → Dépendances circulaires identifiées (ou confirmées absentes)
  → Statistiques remplies

FAIL si :
  → Des fichiers source non répertoriés existent encore
  → Des fichiers d'audit sont toujours présents
```

### Vérifications effectuées

- [x] Fichiers source backend (api.py, backend/, migrations/) — tous répertoriés
- [x] Fichiers source frontend (docling-pwa/src/) — tous répertoriés
- [x] Tests (tests/, backend/tests/) — tous répertoriés
- [x] Aucun fichier d'ancien audit (AUDIT_RESULTS.md, docs/05-AUDIT-*, etc.) dans la liste — Phase 01 nettoyage effectué
- [x] Dépendances circulaires — aucune détectée
- [x] Statistiques remplies

### STATUS : [x] PASS  [ ] FAIL

**→ PASS** : 100% des fichiers source sont cartographiés. Aucune dépendance circulaire. Phase 01 nettoyage validée. Continuation vers 03_BACKEND.md.
