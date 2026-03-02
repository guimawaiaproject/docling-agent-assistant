# 🗺️ 02 — CARTOGRAPHIE EXHAUSTIVE — Docling

**Date** : 2026-03-01
**Phase** : 02 CARTOGRAPHIE (post Phase 01 NETTOYAGE)
**Référence** : 100% des fichiers source du projet

---

## VÉRIFICATIONS 2026 (exécution 1er mars)

| Critère | Statut |
|---------|--------|
| api.py lifespan() | ✅ `@asynccontextmanager` + `lifespan=lifespan` (l.182-221) |
| @app.on_event | ✅ Aucun (pattern legacy absent) |
| pyproject.toml + [tool.ruff] | ✅ Présent |
| biome.json | ❌ Absent (ESLint flat config utilisé) |
| Couverture TypeScript | ❌ 0% — 0 .ts/.tsx, 35 .js/.jsx (migration backlog) |
| React 19 | ✅ 19.2.4 |
| TanStack Router | ❌ react-router-dom v7 (acceptable) |

---

## PRINCIPE

Cette cartographie est LA référence absolue du projet. Chaque fichier listé ici sera analysé dans les audits suivants.

**Exclusions appliquées** : `.git`, `node_modules`, `venv`, `__pycache__`, `dist/`, `.ruff_cache`, `.pytest_cache`, `package-lock.json`, `pnpm-lock.yaml`

---

## SECTION C1 — RACINE DU PROJET

### Tableau C1 — Racine

| Fichier | Lignes | Taille | Rôle | État | Anomalies |
|---------|--------|--------|------|------|-----------|
| api.py | 865 | ~35 Ko | Routeur FastAPI principal — endpoints extraction, catalogue, auth, community, export | ✅ | — |
| requirements.txt | 47 | ~1 Ko | Dépendances Python prod (FastAPI, asyncpg, Gemini, boto3, etc.) | ✅ | — |
| requirements-dev.txt | 15 | ~0.5 Ko | Dépendances dev (pytest, httpx, faker, pre-commit) | ✅ | — |
| .env.example | 45 | ~2 Ko | Template variables d'env (GEMINI, DATABASE_URL, JWT, etc.) | ✅ | — |
| .gitignore | 59 | ~1 Ko | Exclusions git (venv, .env, node_modules, dist, credentials) | ✅ | — |
| Makefile | 86 | ~2 Ko | Commandes projet (install, dev, test, lint, migrate, validate-all, etc.) | ✅ | — |
| docker-compose.yml | 60 | ~2 Ko | Services Docker (postgres, api, pwa) | ✅ | — |
| Dockerfile | 21 | ~0.5 Ko | Build multi-stage Python 3.11-slim | ✅ | — |
| README.md | 203 | ~8 Ko | Documentation projet, installation, variables env | ✅ | — |
| alembic.ini | 39 | ~1 Ko | Config Alembic (script_location=migrations) | ✅ | — |
| pyproject.toml | 50 | ~2 Ko | Config projet (pytest, ruff, markers slow/security/e2e) | ✅ | Dépendances divergentes vs requirements.txt (streamlit, pandas) |
| render.yaml | 21 | ~0.5 Ko | Config Render.com (web, Docker, env vars) | ✅ | — |
| run_local.sh | 77 | ~2 Ko | Script démarrage local Linux/Mac | ✅ | — |
| run_local.bat | 58 | ~1 Ko | Script démarrage local Windows | ✅ | — |

---

## SECTION C2 — BACKEND/

### Sous-section C2.1 — backend/core/

| Fichier | Lignes | Rôle | Importe | Importé par | État |
|---------|--------|------|---------|-------------|------|
| config.py | 139 | Variables env + validation pydantic-settings | pydantic, pydantic_settings, pathlib | api.py, db_manager, orchestrator, services, migrations | ✅ |
| db_manager.py | 683 | Pool asyncpg, CRUD produits, jobs, factures, catalogue paginé, stats, export | asyncpg, config | api.py, orchestrator | ✅ |
| orchestrator.py | 180 | Pipeline extraction : Factur-X → Gemini → BDD → historique | db_manager, facturx, gemini, image_preprocessor, storage | api.py | ✅ |
| __init__.py | 1 | Package marker | — | — | ✅ |

### Sous-section C2.2 — backend/services/

| Fichier | Lignes | Rôle | Service externe | Importé par | État |
|---------|--------|------|----------------|-------------|------|
| auth_service.py | 107 | JWT + Argon2, validation mot de passe | — | api.py | ✅ |
| gemini_service.py | 190 | Extraction IA factures (Google Gemini SDK) | Google Gemini API | orchestrator | ✅ |
| bytez_service.py | 202 | Fallback extraction (Bytez API) | Bytez API | orchestrator | ✅ |
| facturx_extractor.py | 185 | Extraction Factur-X/ZUGFeRD depuis PDF | lxml | orchestrator | ✅ |
| image_preprocessor.py | 74 | Prétraitement images (OpenCV) | OpenCV, numpy | orchestrator | ✅ |
| storage_service.py | 118 | Upload S3/Storj, URLs pré-signées | boto3 | api.py, orchestrator | ✅ |
| watchdog_service.py | 153 | Surveillance dossier magique (watchdog) | watchdog (filesystem) | api.py | ✅ |
| community_service.py | 137 | Base prix communautaire (k-anonymité) | asyncpg | api.py | ✅ |
| __init__.py | 1 | Package marker | — | — | ✅ |

### Sous-section C2.3 — backend/schemas/

| Fichier | Lignes | Schémas définis | Utilisé par | État |
|---------|--------|-----------------|-------------|------|
| invoice.py | 87 | Product, InvoiceExtractionResult, BatchSaveRequest, FAMILLES_VALIDES | api.py, orchestrator, gemini, facturx, bytez | ✅ |
| __init__.py | 1 | Package marker | — | ✅ |

### Sous-section C2.4 — backend/utils/

| Fichier | Lignes | Rôle | Importé par | État |
|---------|--------|------|-------------|------|
| serializers.py | 24 | asyncpg Record → dict JSON-safe (date, Decimal) | api.py | ✅ |
| __init__.py | 0 | Package marker | — | ✅ |

### Sous-section C2.5 — backend/tests/

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| conftest.py | 2 | Fixtures minimales | ✅ |
| test_security.py | 144 | Tests sécurité (_escape_like, _safe_float) | ✅ |
| __init__.py | 1 | Package marker | ✅ |

---

## SECTION C3 — MIGRATIONS/

| Fichier | Lignes | Migration | Ordre | downgrade() | État |
|---------|--------|-----------|-------|-------------|------|
| env.py | 98 | Config Alembic async (asyncpg, SSL) | — | — | ✅ |
| versions/a001_baseline_schema.py | 163 | Baseline : pg_trgm, fournisseurs, produits, factures, jobs, users | 1 | Oui | ✅ |
| versions/a002_add_check_constraints.py | 67 | Contraintes CHECK (prix >= 0, etc.) | 2 | Oui | ✅ |
| versions/a003_add_fk_fournisseur.py | 59 | FK fournisseur → fournisseurs | 3 | Oui | ✅ |
| versions/a004_add_jobs_user_id.py | 28 | user_id sur jobs | 4 | Oui | ✅ |
| versions/a005_add_user_id_and_perf_indexes.py | 66 | user_id produits, index perf | 5 | Oui | ✅ |
| versions/a006_unique_produits_user_id.py | 36 | UNIQUE (designation_raw, fournisseur, user_id) | 6 | Oui | ✅ |
| versions/a007_idx_jobs_user_ck_factures_statut.py | 36 | Index jobs, check factures | 7 | Oui | ✅ |
| versions/a008_prix_anonymes_community.py | 42 | Table prix_anonymes_community | 8 | Oui | ✅ |

---

## SECTION C4 — TESTS/

| Fichier | Lignes | Ce qui est testé | Nb tests estimé | État |
|---------|--------|------------------|----------------|------|
| conftest.py | 161 | Fixtures globales (serveur, DB, unique_user, authenticated_client, sample_products) | — | ✅ |
| 01_unit/test_config.py | 24 | Config validation | ~3 | ✅ |
| 01_unit/test_auth_service.py | 100 | JWT, hash, verify | ~8 | ✅ |
| 01_unit/test_gemini_service.py | 113 | Schéma Gemini, parsing | ~5 | ✅ |
| 01_unit/test_image_preprocessor.py | 58 | Prétraitement images | ~4 | ✅ |
| 01_unit/test_models.py | 231 | Schémas Product, BatchSaveRequest | ~15 | ✅ |
| 01_unit/test_orchestrator.py | 55 | Coûts, process_file | ~3 | ✅ |
| 01_unit/test_validators.py | 89 | _parse_date, _upsert_params | ~8 | ✅ |
| 02_integration/test_database.py | 85 | Connexion DB, migrations | ~5 | ✅ |
| 02_integration/test_storage.py | 38 | StorageService | ~3 | ✅ |
| 03_api/test_auth.py | 102 | Register, login, logout | ~10 | ✅ |
| 03_api/test_batch_save.py | 38 | POST /catalogue/batch | ~3 | ✅ |
| 03_api/test_catalogue.py | 127 | GET catalogue, fournisseurs | ~8 | ✅ |
| 03_api/test_health.py | 23 | GET /health | ~2 | ✅ |
| 03_api/test_invoices.py | 56 | Process, status | ~5 | ✅ |
| 03_api/test_reset_admin.py | 46 | DELETE reset (admin) | ~3 | ✅ |
| 03_api/test_stats_history.py | 35 | Stats, history | ~3 | ✅ |
| 03_api/test_sync.py | 12 | GET sync/status | ~1 | ✅ |
| 03_api/test_upload_validation.py | 31 | Validation upload (MIME, taille) | ~3 | ✅ |
| 04_e2e/conftest.py | 53 | Playwright setup | — | ✅ |
| 04_e2e/test_catalogue_browse.py | 34 | Parcours catalogue E2E | ~2 | ✅ |
| 04_e2e/test_scan_flow.py | 63 | Flux scan E2E | ~3 | ✅ |
| 04_e2e/test_settings_sync.py | 25 | Settings sync E2E | ~1 | ✅ |
| 05_security/test_auth_bypass.py | 64 | Bypass auth | ~4 | ✅ |
| 05_security/test_headers.py | 22 | Headers sécurité | ~2 | ✅ |
| 05_security/test_injection.py | 86 | Injection SQL | ~5 | ✅ |
| 06_performance/locustfile.py | 63 | Load test Locust | — | ✅ |
| 06_performance/test_response_times.py | 51 | Temps réponse | ~3 | ✅ |
| 07_data_integrity/test_api_db_coherence.py | 55 | Cohérence API/DB | ~3 | ✅ |
| 07_data_integrity/test_constraints.py | 46 | Contraintes BDD | ~3 | ✅ |
| 07_data_integrity/test_transactions.py | 56 | Transactions | ~3 | ✅ |
| 08_external_services/test_extraction_reelle.py | 38 | Extraction réelle (marqué external) | ~1 | ✅ |

---

## SECTION C5 — DOCLING-PWA/

### Sous-section C5.1 — docling-pwa/src/pages/

| Fichier | Lignes | Page | Routes | Imports principaux | État |
|---------|--------|------|--------|--------------------|------|
| ScanPage.jsx | 778 | Scan factures | /scan | dropzone, apiClient, useStore, SplineScene, imageService | ✅ |
| CataloguePage.jsx | 539 | Catalogue produits | /catalogue | react-virtual, apiClient, CompareModal, recharts, exceljs | ✅ |
| SettingsPage.jsx | 502 | Paramètres | /settings | apiClient, useStore, SplineScene | ✅ |
| DevisPage.jsx | 375 | Génération devis | /devis | apiClient, devisGenerator, useStore, SplineScene | ✅ |
| ValidationPage.jsx | 288 | Validation extraits | /validation | apiClient, useStore, SplineScene, categories | ✅ |
| HistoryPage.jsx | 279 | Historique factures | /history | apiClient, SkeletonCard, EmptyStateIllustration | ✅ |
| RegisterPage.jsx | 136 | Inscription | /register | apiClient, ENDPOINTS | ✅ |
| LoginPage.jsx | 116 | Connexion | /login | apiClient, ENDPOINTS | ✅ |

### Sous-section C5.2 — docling-pwa/src/components/

| Fichier | Lignes | Composant | Props | Utilisé par | État |
|---------|--------|-----------|-------|-------------|------|
| CompareModal.jsx | 278 | Modal comparateur prix | search, onClose | CataloguePage | ✅ |
| CommandPalette.jsx | 111 | Raccourcis clavier | — | App.jsx | ✅ |
| Navbar.jsx | 74 | Navigation bottom | — | App.jsx | ✅ |
| ErrorBoundary.jsx | 73 | Gestion erreurs React | — | main.jsx | ✅ |
| EmptyStateIllustration.jsx | 64 | Illustration état vide | — | CataloguePage, HistoryPage, CompareModal | ✅ |
| OfflineBanner.jsx | 63 | Bannière hors-ligne | — | App.jsx | ✅ |
| SkeletonCard.jsx | 50 | Skeleton loading | count, variant | App, HistoryPage, CataloguePage | ✅ |
| SplineScene.jsx | 26 | Scène 3D Spline | — | ValidationPage, DevisPage, SettingsPage, ErrorBoundary, ScanPage | ✅ |
| ProtectedRoute.jsx | 14 | Guard auth | — | App.jsx | ✅ |

### Sous-section C5.3 — docling-pwa/src/services/

| Fichier | Lignes | Service | API externe | État |
|---------|--------|---------|-------------|------|
| apiClient.js | 54 | Client Axios (retry, cookie, 401 redirect) | Backend API | ✅ |
| devisGenerator.js | 170 | Génération PDF/Excel devis | jsPDF, exceljs | ✅ |
| offlineQueue.js | 80 | File d'attente IndexedDB (offline) | — | ✅ |
| imageService.js | 49 | Compression WebP | — | ✅ |

### Sous-section C5.4 — docling-pwa/src/store/

| Fichier | Lignes | State géré | Persisté | État |
|---------|--------|------------|----------|------|
| useStore.js | 133 | Produits, queue, modèle IA, préférences | Oui (Zustand persist) | ✅ |

### Sous-section C5.5 — docling-pwa/src/config/

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| api.js | 32 | URLs endpoints (API_BASE_URL, ENDPOINTS) | ✅ |
| features.js | 3 | Feature flags (AUTH_REQUIRED) | ✅ |

### Sous-section C5.6 — docling-pwa/src/constants/

| Fichier | Lignes | Constantes | Utilisé par | État |
|---------|--------|-----------|-------------|------|
| categories.js | 8 | FAMILLES, FAMILLES_AVEC_TOUTES | CataloguePage, ValidationPage | ✅ |

### Sous-section C5.7 — docling-pwa/src/utils/

| Fichier | Lignes | Utilitaires | Utilisé par | État |
|---------|--------|-------------|-------------|------|
| reportWebVitals.js | 43 | Envoi Web Vitals (sendBeacon) | main.jsx | ✅ |

### Sous-section C5.8 — docling-pwa/src/hooks/

| Statut | État |
|--------|------|
| Absent | Pas de dossier hooks/ — hooks inline dans composants | ✅ |

### Sous-section C5.9 — docling-pwa/src/__tests__/

| Fichier | Lignes | Ce qui est testé | Nb tests | État |
|---------|--------|------------------|----------|------|
| useStore.test.js | 178 | Store Zustand | ~10 | ✅ |
| apiClient.test.js | 100 | Client Axios (mock) | ~5 | ✅ |
| CompareModal.test.jsx | 230 | Modal comparateur | ~8 | ✅ |
| setup.js | 29 | Config Vitest (jest-dom, vi) | — | ✅ |
| pages/CataloguePage.test.jsx | 98 | CataloguePage | ~5 | ✅ |
| pages/ScanPage.test.jsx | 95 | ScanPage | ~5 | ✅ |
| utils/__tests__/devisCalculations.test.js | 48 | Calculs devis | ~4 | ✅ |

### Autres — docling-pwa/src/

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| App.jsx | 84 | Router principal, lazy routes, Toaster | ✅ |
| main.jsx | 31 | Point d'entrée, Sentry, ErrorBoundary | ✅ |
| index.css | 30 | Styles globaux Tailwind | ✅ |

---

## SECTION C6 — CONFIGURATION ROOT PWA

| Fichier | Lignes | Rôle | État | Problèmes |
|---------|--------|------|------|-----------|
| package.json | 60 | Dépendances + scripts npm | ✅ | — |
| vite.config.js | 71 | Build Vite, PWA, SSL, chunks manuels | ✅ | — |
| tailwind.config.js | 11 | Config Tailwind (content, theme) | ✅ | — |
| postcss.config.cjs | 6 | PostCSS (tailwindcss, autoprefixer) | ✅ | — |
| eslint.config.js | 33 | ESLint flat config (react-hooks, react-refresh) | ✅ | — |
| index.html | 30 | Entrée HTML, CSP, PWA meta | ✅ | — |

---

## SECTION C7 — CI/CD & DÉPLOIEMENT

| Fichier | Lignes | Rôle | Triggers | État |
|---------|--------|------|----------|------|
| .github/workflows/ci.yml | 149 | CI : pytest, ruff, frontend build, vitest | push, PR (main) | ✅ |
| .github/workflows/ci-cd.yml | 103 | CI/CD alternatif | push, PR | ✅ |
| .github/workflows/deploy.yml | 71 | Deploy Render/Railway + Vercel/Netlify | push main, workflow_dispatch | ✅ |
| .github/workflows/tests.yml | 25 | Tests dédiés | — | ✅ |
| render.yaml | 21 | Config Render.com | — | ✅ |

---

## SECTION C8 — FICHIERS SPÉCIAUX & SCRIPTS

| Fichier | Lignes | Rôle | Commité ? | Devrait l'être ? | Action |
|---------|--------|------|-----------|-----------------|--------|
| .env.example | 45 | Template envs | Oui | Oui | ✅ |
| .env | — | Valeurs réelles | Non (.gitignore) | NON | ✅ |
| .pre-commit-config.yaml | 30 | Hooks pre-commit | Oui | Oui | ✅ |
| .vscode/extensions.json | 5 | Extensions recommandées | Oui | Optionnel | ✅ |
| .vscode/settings.json | 5 | Paramètres workspace | Oui | Optionnel | ✅ |
| tests/requirements-test.txt | 28 | Dépendances tests (pytest, playwright, locust, psycopg2) | Oui | Oui | ✅ |

### Scripts (scripts/)

| Fichier | Lignes | Rôle | État |
|---------|--------|------|------|
| validate_all.sh | 26 | Lint + tests + skills | ✅ |
| validate_all.ps1 | 29 | Idem Windows | ✅ |
| validate_skills.py | 122 | Validation SKILL.md | ✅ |
| validate_env.py | 76 | Validation .env | ✅ |
| health_check.py | 78 | Health API + DB | ✅ |
| verify_project.ps1 | 196 | Vérification complète (Audit Bêton) | ✅ |
| verify_project.sh | 88 | Idem Linux | ✅ |
| test_api_e2e.py | 257 | Tests E2E API | ✅ |
| analyze_emmet_opportunities.py | 229 | Analyse Emmet | ✅ |
| analyze_spline_opportunities.py | 156 | Analyse Spline 3D | ✅ |
| design_system_docling.py | 44 | Génération design system | ✅ |
| run-audit-beton.ps1 | 122 | Lancement audit bêton | ✅ |
| pre_launch_check.ps1 | 91 | Vérif pré-lancement | ✅ |
| pre_launch_check.sh | 67 | Idem Linux | ✅ |
| fix-npm-windows.ps1 | 72 | Fix npm Windows | ✅ |
| review.sh | 16 | Review ruff + gito | ✅ |
| review.ps1 | 15 | Idem Windows | ✅ |
| skills_to_prompt.py | 68 | Génération XML skills | ✅ |

---

## MATRICE DE DÉPENDANCES

### BACKEND

```
api.py
  → backend.core.config, db_manager, orchestrator
  → backend.schemas.invoice (BatchSaveRequest)
  → backend.services.auth_service, community_service, storage_service, watchdog_service
  → backend.utils.serializers

db_manager.py
  → backend.core.config

orchestrator.py
  → backend.core.db_manager
  → backend.services.facturx_extractor, gemini_service, image_preprocessor, storage_service
  → backend.services.bytez_service (fallback conditionnel)

gemini_service.py
  → backend.core.config, backend.schemas.invoice

bytez_service.py
  → backend.core.config, backend.schemas.invoice

facturx_extractor.py
  → backend.schemas.invoice

community_service.py
  → backend.core.config

storage_service.py
  → backend.core.config

watchdog_service.py
  → backend.core.config, orchestrator

auth_service.py
  → (stdlib: jwt, argon2)
```

### FRONTEND

```
App.jsx
  → react-router-dom, sonner, CommandPalette, Navbar, OfflineBanner, ProtectedRoute, SkeletonCard
  → config/features, pages (lazy)

ScanPage.jsx
  → framer-motion, lucide-react, react-dropzone, apiClient, useStore, SplineScene, imageService

CataloguePage.jsx
  → @tanstack/react-virtual, recharts, exceljs, apiClient, CompareModal, EmptyStateIllustration, SkeletonCard, categories

ValidationPage.jsx
  → apiClient, useStore, SplineScene, categories

DevisPage.jsx
  → apiClient, devisGenerator, useStore, SplineScene

SettingsPage.jsx
  → apiClient, useStore, SplineScene, features

HistoryPage.jsx
  → apiClient, SkeletonCard, EmptyStateIllustration

apiClient.js
  → axios, config/api

useStore.js
  → zustand
```

### DÉPENDANCES CIRCULAIRES DÉTECTÉES

**Aucune** — Graphe acyclique. Pas de cycle backend ↔ backend ni frontend ↔ frontend critique.

### MODULES LES PLUS IMPORTÉS (hubs critiques)

| Module | Importé par |
|--------|-------------|
| backend.core.config | api, db_manager, orchestrator, gemini, bytez, community, storage, watchdog |
| backend.schemas.invoice | api, orchestrator, gemini, facturx, bytez |
| backend.core.db_manager | api, orchestrator |
| docling-pwa/config/api | apiClient, toutes les pages |
| docling-pwa/store/useStore | ScanPage, ValidationPage, DevisPage, SettingsPage |
| docling-pwa/services/apiClient | Toutes les pages, CompareModal |

---

## STATISTIQUES FINALES

### BACKEND

| Métrique | Valeur |
|----------|--------|
| Fichiers Python | 35 |
| Lignes totales | ~3 850 |
| Fichier le plus long | db_manager.py (683 lignes) |
| Services | 8 (auth, gemini, bytez, facturx, image, storage, watchdog, community) |
| Schémas | 3 (Product, InvoiceExtractionResult, BatchSaveRequest) |

### FRONTEND

| Métrique | Valeur |
|----------|--------|
| Fichiers JS/JSX | 38 |
| Lignes totales | ~5 200 |
| Composants React | 9 (Navbar, CompareModal, etc.) |
| Pages | 8 |
| Hooks customs | 0 (Zustand store) |
| Tests Vitest | 7 fichiers |

### TESTS

| Métrique | Valeur |
|----------|--------|
| Fichiers test backend | 31 |
| Lignes test backend | ~2 100 |
| Fichiers test frontend | 7 |
| Lignes test frontend | ~780 |

### GLOBAL

| Métrique | Valeur |
|----------|--------|
| Fichiers source total | ~120 |
| Lignes source total (hors docs) | ~12 000 |
| Lignes code applicatif | ~9 000 |
| Lignes tests | ~2 900 |
| **Ratio test/code** | **~32%** (objectif > 30%) ✅ |
| Dépendances backend (prod) | 25 (requirements.txt) |
| Dépendances frontend (prod) | 35 (package.json) |

---

## ✅ GATE C — CARTOGRAPHIE

### Critères PASS

| Critère | Statut |
|---------|--------|
| 100% des fichiers source dans les tableaux | ✅ Oui |
| Aucun fichier d'ancien audit dans la liste | ✅ AUDIT_BETON exclus de la cartographie source |
| Dépendances circulaires identifiées | ✅ Aucune |
| Statistiques remplies | ✅ Oui |

### Critères FAIL

| Critère | Statut |
|---------|--------|
| Fichiers source non répertoriés | — |
| Fichiers d'audit dans la liste source | — |

---

## STATUS : **PASS**

**→ Continuer vers 03_BACKEND.md**

---

*Cartographie générée le 2026-03-01 — Phase 02 Audit Bêton Docling*
