# Inventaire et analyse approfondie — Docling

**Projet** : Extraction factures BTP (CA/ES/FR) — FastAPI + React PWA
**Base** : Neon PostgreSQL
**Date** : 2026-03-01

---

## 1. Arborescence complète

> **Note** : L'arborescence exhaustive (incluant `node_modules`, `__pycache__`, `.ruff_cache`, `.git`) dépasse 66 000 lignes. La commande `tree /F /A` à la racine du projet génère la liste complète. Ci-dessous : structure des sources et dossiers significatifs.

### 1.1 Arborescence exhaustive (dossiers générés indiqués)

```
docling/
├── .dockerignore
├── .env
├── .env.example
├── .env.staging
├── .env.test.example
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── alembic.ini
├── api.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── Makefile
├── nettoyer.ps1
├── Procfile
├── pyproject.toml
├── README.md
├── render.yaml
├── requirements-dev.txt
├── requirements-review.txt
├── requirements.txt
├── run_local.bat
├── run_local.sh
├── skills-lock.json
│
├── .agents/skills/
│   ├── docling-factures/ (SKILL.md, references/)
│   ├── multi-agent-workflow/ (SKILL.md)
│   └── neon-postgres/ (SKILL.md)
│
├── .cursor/
│   ├── agents/ (10 agents)
│   ├── commands/ (14 commandes)
│   ├── PROMPT AUDIT/ (11 fichiers)
│   ├── rules/ (27 règles .mdc)
│   └── skills/ui-ux-pro-max/ (data/, scripts/)
│
├── .github/workflows/ (ci.yml, ci-cd.yml, deploy.yml, tests.yml)
├── .pytest_cache/ (cache pytest)
├── .ruff_cache/ (cache ruff)
├── .vscode/ (extensions.json, settings.json)
│
├── AUDIT_BETON/ (10 rapports .md)
│
├── backend/
│   ├── schema_neon.sql
│   ├── core/ (config, db_manager, orchestrator)
│   ├── schemas/ (invoice)
│   ├── services/ (8 services)
│   ├── utils/ (serializers)
│   ├── tests/ (conftest, test_security)
│   └── __pycache__/ (fichiers .pyc)
│
├── design-system/docling/ (MASTER.md)
│
├── docling-pwa/
│   ├── .env, .npmrc, package.json, vite.config.js, etc.
│   ├── dist/ (build production)
│   ├── node_modules/ (~500+ packages — npm/pnpm)
│   ├── public/ (icons, manifest)
│   └── src/ (main, App, pages, components, services, store)
│
├── docs/ (documentation)
│
├── migrations/
│   ├── env.py
│   └── versions/ (a001 à a008)
│
├── scripts/ (validate_all, health_check, etc.)
│
├── tests/
│   ├── conftest.py
│   ├── 01_unit/ à 08_external_services/
│   └── __pycache__/
│
└── [.git/ — non listé, dépôt versionné]
```

### 1.2 Arborescence détaillée (sources significatives)

```
docling/
├── .dockerignore
├── .env
├── .env.example
├── .env.staging
├── .env.test.example
├── .pre-commit-config.yaml
├── AGENTS.md
├── alembic.ini
├── api.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── Makefile
├── nettoyer.ps1
├── Procfile
├── pyproject.toml
├── README.md
├── render.yaml
├── requirements-dev.txt
├── requirements-review.txt
├── requirements.txt
├── run_local.bat
├── run_local.sh
├── skills-lock.json
│
├── .agents/skills/
│   ├── docling-factures/SKILL.md
│   ├── docling-factures/references/api.md, architecture.md
│   ├── multi-agent-workflow/SKILL.md
│   └── neon-postgres/SKILL.md
│
├── .cursor/
│   ├── agents/ (api-reviewer, context-specialist, docs-writer, etc.)
│   ├── commands/ (audit-beton, dev, plan, validate-all, etc.)
│   ├── PROMPT AUDIT/ (00-10 phases audit)
│   ├── rules/ (backend-conventions, frontend-conventions, etc.)
│   └── skills/ui-ux-pro-max/
│
├── backend/
│   ├── __init__.py
│   ├── schema_neon.sql
│   ├── core/
│   │   ├── config.py
│   │   ├── db_manager.py
│   │   └── orchestrator.py
│   ├── schemas/
│   │   ├── invoice.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── bytez_service.py
│   │   ├── community_service.py
│   │   ├── facturx_extractor.py
│   │   ├── gemini_service.py
│   │   ├── image_preprocessor.py
│   │   ├── storage_service.py
│   │   └── watchdog_service.py
│   ├── utils/
│   │   ├── serializers.py
│   │   └── __init__.py
│   └── tests/
│       ├── conftest.py
│       └── test_security.py
│
├── docling-pwa/
│   ├── .env
│   ├── .npmrc
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.cjs
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── config/
│       │   ├── api.js
│       │   └── features.js
│       ├── components/
│       │   ├── CommandPalette.jsx
│       │   ├── CompareModal.jsx
│       │   ├── EmptyStateIllustration.jsx
│       │   ├── ErrorBoundary.jsx
│       │   ├── Navbar.jsx
│       │   ├── OfflineBanner.jsx
│       │   ├── ProtectedRoute.jsx
│       │   ├── SkeletonCard.jsx
│       │   └── SplineScene.jsx
│       ├── constants/
│       │   └── categories.js
│       ├── pages/
│       │   ├── CataloguePage.jsx
│       │   ├── DevisPage.jsx
│       │   ├── HistoryPage.jsx
│       │   ├── LoginPage.jsx
│       │   ├── RegisterPage.jsx
│       │   ├── ScanPage.jsx
│       │   ├── SettingsPage.jsx
│       │   └── ValidationPage.jsx
│       ├── services/
│       │   ├── apiClient.js
│       │   ├── devisGenerator.js
│       │   ├── imageService.js
│       │   └── offlineQueue.js
│       ├── store/
│       │   └── useStore.js
│       └── utils/
│           ├── reportWebVitals.js
│           └── devisCalculations.js
│
├── migrations/
│   ├── env.py
│   └── versions/
│       ├── a001_baseline_schema.py
│       ├── a002_add_check_constraints.py
│       ├── a003_add_fk_fournisseur.py
│       ├── a004_add_jobs_user_id.py
│       ├── a005_add_user_id_and_perf_indexes.py
│       ├── a006_unique_produits_user_id.py
│       ├── a007_idx_jobs_user_ck_factures_statut.py
│       └── a008_prix_anonymes_community.py
│
├── tests/
│   ├── conftest.py
│   ├── 01_unit/
│   ├── 02_integration/
│   ├── 03_api/
│   ├── 04_e2e/
│   ├── 05_security/
│   ├── 06_performance/
│   ├── 07_data_integrity/
│   └── 08_external_services/
│
├── scripts/
│   ├── analyze_emmet_opportunities.py
│   ├── analyze_spline_opportunities.py
│   ├── design_system_docling.py
│   ├── health_check.py
│   ├── skills_to_prompt.py
│   ├── test_api_e2e.py
│   ├── validate_env.py
│   ├── validate_skills.py
│   ├── validate_all.sh
│   ├── verify_project.ps1
│   └── review.sh
│
├── design-system/docling/
│   └── MASTER.md
│
├── docs/
│   └── (documentation projet)
│
└── AUDIT_BETON/
    └── (01-10 rapports audit)
```

---

## 2. Analyse par domaine

### 2.1 RACINE

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **api.py** | Point d'entrée FastAPI. Définit tous les endpoints (process, status, catalogue, batch, auth, community, export). Lifespan, CORS, rate limit, circuit breaker Gemini, sécurité headers. | Bonne lisibilité, ~867 lignes. Structure claire par blocs. | **Critique** — cœur de l'API. | Extraire les routes dans des routers FastAPI (ex. `routers/invoices.py`, `routers/auth.py`). | Fichier monolithique ; endpoints 10/11 mal numérotés (commentaires). |
| **Makefile** | Cibles dev : install, dev, test, lint, migrate, validate-all, health-check, verify-project, emmet-analyze, design-system, spline-analyze. | Concis, bien documenté. | **Haute** — routine DevOps. | Ajouter `make docker-build` si pertinent. | — |
| **alembic.ini** | Config Alembic pour migrations PostgreSQL. | Standard. | **Haute** — versioning schéma. | — | — |
| **pyproject.toml** | Config projet Python (ruff, pytest, dépendances). | Moderne. | **Haute** — tooling. | — | — |
| **requirements.txt** | Dépendances prod. | Standard. | **Haute** | — | — |
| **render.yaml** | Déploiement Render (services, env). | Standard. | **Haute** — déploiement. | — | — |
| **Dockerfile** | Image Docker multi-stage. | Standard. | **Haute** — conteneurisation. | — | — |
| **Procfile** | Commande démarrage (uvicorn). | Minimal. | **Haute** — Heroku/Render. | — | — |
| **AGENTS.md** | Guide agents IA : skills, règles, commandes, flux multi-agents. | Complet. | **Haute** — onboarding IA. | — | — |

---

### 2.2 BACKEND

#### 2.2.1 Core

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **backend/core/config.py** | Configuration centralisée via pydantic-settings. Valide GEMINI_API_KEY, DATABASE_URL, JWT_SECRET au démarrage. Expose Config (facade). | Bonne séparation, validation stricte. | **Critique** — config unique. | — | `validate_startup` crée des dossiers watchdog même si WATCHDOG_ENABLED=false. |
| **backend/core/db_manager.py** | Gestion pool asyncpg, migrations, CRUD produits/factures/jobs. Pagination cursor, recherche pg_trgm, upsert anti-doublon. | ~678 lignes, bien structuré. Requêtes paramétrées. | **Critique** — couche données. | `get_job` : user_id peut être None mais la requête utilise `user_id = $2` → risque si guest. | `update_user_community_prefs` fait 2 UPDATE séparés au lieu d'un seul. Bug potentiel : `get_job` avec user_id=None ne filtre pas. |
| **backend/core/orchestrator.py** | Pipeline extraction : détection MIME → Factur-X (PDF) ou Gemini (fallback Bytez) → BDD + Storj en parallèle → historique → base communautaire. | Clair, asyncio.to_thread pour I/O bloquant. | **Critique** — orchestration. | — | Import dynamique `CommunityService` dans la boucle (ligne 124). |

#### 2.2.2 Schemas

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **backend/schemas/invoice.py** | Pydantic Product, InvoiceExtractionResult, BatchSaveRequest. Validation famille, calcul TVA, confidence. | Modèles bien typés. | **Haute** — validation stricte. | — | — |

#### 2.2.3 Services

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **backend/services/auth_service.py** | JWT (PyJWT), Argon2id, rehash PBKDF2→Argon2id. create_token, verify_token, hash_password, verify_password. | Propre, rétrocompatibilité. | **Critique** — auth. | — | — |
| **backend/services/gemini_service.py** | Extraction IA via google-genai (async). Structured output, retry 429. Cache par model_id. | Bien isolé, prompts dédiés. | **Critique** — extraction. | — | — |
| **backend/services/facturx_extractor.py** | Extraction XML Factur-X/ZUGFeRD depuis PDF. Conformité facturation électronique. | Spécialisé, namespaces corrects. | **Haute** — factures structurées. | — | Dépendance factur-x optionnelle. |
| **backend/services/image_preprocessor.py** | Prétraitement images (OpenCV) : resize, contraste. | Simple. | **Moyenne** — qualité extraction. | — | — |
| **backend/services/storage_service.py** | Upload S3-compatible (Storj/R2). Clé YYYY/MM/hash_filename. Presigned URLs. | Propre. | **Haute** — stockage PDF. | — | MD5 pour hash (faible) — acceptable pour déduplication non-crypto. |
| **backend/services/watchdog_service.py** | Surveillance dossier magique, traitement auto PDF/images. Débounce 2s. | Clair. | **Haute** — workflow local. | — | `user_id` non passé à `Orchestrator.process_file` dans watchdog → produits sans user_id. |
| **backend/services/bytez_service.py** | Fallback extraction si Gemini échoue (API Bytez). | Optionnel. | **Moyenne** — résilience. | — | — |
| **backend/services/community_service.py** | Base prix communautaire anonyme (k-anonymité). | Spécialisé. | **Moyenne** — fonctionnalité avancée. | — | — |

#### 2.2.4 Utils

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **backend/utils/serializers.py** | Conversion asyncpg Record → JSON (date, Decimal). | Minimal, efficace. | **Haute** — sérialisation. | — | — |

---

### 2.3 FRONTEND (docling-pwa)

#### 2.3.1 Config & entry

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **docling-pwa/src/main.jsx** | Point d'entrée React, Router, ErrorBoundary, Sentry. | Standard. | **Critique** | — | — |
| **docling-pwa/src/App.jsx** | Routes, lazy loading pages, RouteWrapper (auth ou Fragment), LayoutWithNav, Toaster. | Clair, feature flags. | **Critique** | — | — |
| **docling-pwa/src/config/api.js** | API_BASE_URL, ENDPOINTS. | Centralisé. | **Haute** | — | — |
| **docling-pwa/src/config/features.js** | AUTH_REQUIRED depuis VITE_AUTH_REQUIRED. | Minimal. | **Haute** | — | — |

#### 2.3.2 Composants

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **Navbar.jsx** | Navigation bottom avec icônes. | Standard. | **Haute** | — | — |
| **ProtectedRoute.jsx** | Redirection /login si absent token. | Simple. | **Haute** — auth. | — | — |
| **ErrorBoundary.jsx** | Capture erreurs React, affichage fallback. | Standard. | **Haute** | — | — |
| **OfflineBanner.jsx** | Affichage si offline. | Simple. | **Moyenne** — PWA. | — | — |
| **SkeletonCard.jsx** | Skeleton loading. | Réutilisable. | **Moyenne** | — | — |
| **CompareModal.jsx** | Comparaison prix fournisseurs. | Modale. | **Haute** | — | — |
| **CommandPalette.jsx** | Raccourcis clavier. | UX. | **Moyenne** | — | — |
| **SplineScene.jsx** | Intégration 3D Spline. | Spécialisé. | **Moyenne** — visuel. | — | — |
| **EmptyStateIllustration.jsx** | États vides. | UX. | **Moyenne** | — | — |

#### 2.3.3 Pages

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **ScanPage.jsx** | Upload, batch, polling job, compression WebP, offline queue. | ~780 lignes, complexe. | **Critique** — flux principal. | Extraire composants (BatchQueue, UploadZone). | Fichier long, logique dense. |
| **ValidationPage.jsx** | Validation/correction produits extraits, sauvegarde batch. | Flux important. | **Critique** | — | — |
| **CataloguePage.jsx** | Parcours catalogue, filtres, pagination cursor. | Standard. | **Haute** | — | — |
| **HistoryPage.jsx** | Historique factures, lien PDF. | Simple. | **Haute** | — | — |
| **DevisPage.jsx** | Génération devis (PDF/Excel). | Spécialisé. | **Haute** | — | — |
| **SettingsPage.jsx** | Paramètres, watchdog, modèle IA, communauté. | Standard. | **Haute** | — | — |
| **LoginPage.jsx** | Formulaire login. | Standard. | **Haute** | — | — |
| **RegisterPage.jsx** | Inscription. | Standard. | **Haute** | — | — |

#### 2.3.4 Services & store

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **apiClient.js** | Axios, retry 5xx, withCredentials, fallback localStorage token. | Propre. | **Critique** | — | Double source token (cookie + localStorage) — risque confusion. |
| **useStore.js** | Zustand : selectedModel, batchQueue, extractedProducts, actions. Persist selectedModel. | Bien structuré. | **Critique** — état global. | — | — |
| **offlineQueue.js** | File d'attente uploads hors-ligne. | PWA. | **Moyenne** | — | — |
| **imageService.js** | Compression WebP. | Utilitaire. | **Moyenne** | — | — |
| **devisGenerator.js** | Génération PDF/Excel devis. | Spécialisé. | **Haute** | — | — |

---

### 2.4 TESTS

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **tests/conftest.py** | Fixtures : ensure_server_running, real_db_connection, unique_user, authenticated_client, http_client, sample_products. | Tests réels (pas de mock). | **Critique** | — | **Bug** : `authenticated_client` attend `token` dans `login_resp.json()` mais l'API ne renvoie le token que dans le cookie (httpOnly). Le test échouera. Idem `test_register_success` attend `"token" in data` alors que l'API ne renvoie pas token dans le body. |
| **tests/01_unit/** | test_config, test_models, test_orchestrator, test_validators, test_auth_service, test_gemini_service, test_image_preprocessor. | Unitaires. | **Haute** | — | — |
| **tests/02_integration/** | test_database, test_storage. | Intégration. | **Haute** | — | — |
| **tests/03_api/** | test_auth, test_invoices, test_catalogue, test_batch_save, test_health, test_sync, test_stats_history, test_upload_validation, test_reset_admin. | API. | **Haute** | — | Incohérence token (voir conftest). |
| **tests/04_e2e/** | test_scan_flow, test_catalogue_browse, test_settings_sync. | E2E. | **Haute** | — | — |
| **tests/05_security/** | test_auth_bypass, test_headers, test_injection, test_isolation. | Sécurité. | **Haute** | — | — |
| **tests/06_performance/** | locustfile, test_response_times. | Perf. | **Moyenne** | — | — |
| **tests/07_data_integrity/** | test_api_db_coherence, test_constraints, test_transactions. | Intégrité. | **Haute** | — | — |
| **tests/08_external_services/** | test_extraction_reelle. | Coûteux (Gemini). | **Basse** — manuel. | — | — |

---

### 2.5 SCRIPTS

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **scripts/validate_all.sh** | Lint backend (ruff), frontend (eslint), build, skills, pytest unit, vitest. | Pipeline complet. | **Critique** — CI. | — | — |
| **scripts/validate_env.py** | Vérifie .env (GEMINI, DATABASE_URL, JWT). | Sans dotenv. | **Haute** | — | — |
| **scripts/validate_skills.py** | Valide format SKILL.md. | Spécialisé. | **Moyenne** | — | — |
| **scripts/health_check.py** | Health API + DB. | Simple. | **Haute** | — | — |
| **scripts/skills_to_prompt.py** | Génère XML skills pour prompts. | Utilitaire. | **Moyenne** | — | — |
| **scripts/analyze_emmet_opportunities.py** | Analyse opportunités Emmet (JSX). | Spécialisé. | **Basse** | — | — |
| **scripts/analyze_spline_opportunities.py** | Analyse Spline 3D. | Spécialisé. | **Basse** | — | — |
| **scripts/design_system_docling.py** | Génère design-system/docling/MASTER.md. | UI/UX. | **Moyenne** | — | — |
| **scripts/verify_project.ps1** | Vérification complète (Audit Bêton). | PowerShell. | **Haute** | — | — |

---

### 2.6 MIGRATIONS

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **a001_baseline_schema.py** | Tables fournisseurs, produits, jobs, factures. Index pg_trgm. | Baseline. | **Critique** | — | — |
| **a002_add_check_constraints.py** | Contraintes check. | Standard. | **Haute** | — | — |
| **a003_add_fk_fournisseur.py** | FK fournisseur. | Standard. | **Haute** | — | — |
| **a004_add_jobs_user_id.py** | user_id sur jobs. | Multi-tenant. | **Haute** | — | — |
| **a005_add_user_id_and_perf_indexes.py** | user_id produits, index perf. | Multi-tenant. | **Haute** | — | — |
| **a006_unique_produits_user_id.py** | UNIQUE (designation_raw, fournisseur, user_id). | Anti-doublon. | **Haute** | — | — |
| **a007_idx_jobs_user_ck_factures_statut.py** | Index jobs, check factures. | Perf. | **Haute** | — | — |
| **a008_prix_anonymes_community.py** | Table prix communautaire. | Feature. | **Moyenne** | — | — |

---

### 2.7 DOCS & .cursor

| Domaine | Contenu | Utilité |
|---------|---------|---------|
| **docs/** | Documentation projet, workflow, FIX-*.md. | Référence. |
| **.cursor/** | Agents, commands, rules, skills, PROMPT AUDIT. | Guidance IA, audit. |
| **AUDIT_BETON/** | 10 rapports audit (nettoyage, backend, frontend, etc.). | Qualité. |
| **design-system/docling/** | MASTER.md design system. | UI/UX. |

---

## 3. Synthèse des problèmes identifiés

### P0 — Critiques
1. **Tests auth** : `authenticated_client` (conftest.py L124) attend `token = login_resp.json().get("token")`, mais l'API `/api/v1/auth/login` ne renvoie **pas** le token dans le body JSON — uniquement dans le cookie httpOnly `docling-token`. Le test échoue avec "Token manquant dans la réponse login". **Correction** : soit l'API ajoute `token` au JSON pour les clients non-cookie (tests, mobile), soit le test utilise les cookies (httpx les conserve ; retirer l'assertion token et ne pas set Authorization).
2. **DBManager.get_job** : Si `user_id=None` (guest), la requête `WHERE user_id = $2` peut échouer ou ne pas filtrer correctement selon le schéma.

### P1 — Importants
3. **Watchdog** : `Orchestrator.process_file` appelé sans `user_id` → produits sans propriétaire.
4. **api.py** : Fichier monolithique (~867 lignes) — extraire des routers.
5. **apiClient.js** : Double source token (cookie + localStorage) — clarifier la stratégie.

### P2 — Moyens
6. **update_user_community_prefs** : 2 UPDATE séparés au lieu d'un seul.
7. **Orchestrator** : Import dynamique `CommunityService` dans la boucle.
8. **ScanPage.jsx** : Fichier long — extraire sous-composants.

### P3 — Mineurs
9. **config.py** : Création dossiers watchdog même si désactivé.
10. **Endpoints api.py** : Numérotation 10/11 inversée dans les commentaires.

---

## 4. Recommandations prioritaires

1. **Corriger les tests auth** : Soit l'API renvoie `token` dans le body (pour clients non-cookie), soit les tests utilisent les cookies (httpx stocke les cookies automatiquement).
2. **Passer user_id au watchdog** : Créer un user_id système ou demander config pour le dossier magique.
3. **Refactorer api.py** : Créer `routers/invoices.py`, `routers/auth.py`, `routers/catalogue.py`, etc.
4. **Clarifier stratégie token frontend** : Cookie uniquement (httpOnly) ou Bearer + localStorage pour mobile/PWA.

---

## 5. Fichiers racine — analyse complémentaire

| Fichier | Fonction / rôle | Qualité | Utilité | Optimisations | Problèmes |
|---------|-----------------|---------|---------|--------------|-----------|
| **.dockerignore** | Exclut node_modules, venv, .git du contexte Docker. | Standard. | Haute — build. | — | — |
| **.env.example** | Template variables d'environnement. | Documenté. | Haute — onboarding. | — | — |
| **.pre-commit-config.yaml** | Hooks pre-commit (ruff, etc.). | Standard. | Moyenne. | — | — |
| **docker-compose.yml** | Stack API + PostgreSQL local. | Standard. | Haute — dev local. | — | — |
| **nettoyer.ps1** | Script nettoyage cache/build. | PowerShell. | Basse. | — | — |
| **run_local.bat / .sh** | Démarrage backend + frontend. | Simple. | Haute — dev. | — | — |
| **skills-lock.json** | Verrouillage versions skills. | Spécifique projet. | Moyenne. | — | — |

---

## 6. Arborescence exhaustive

Le fichier **`docs/ARBORESCENCE_COMPLETE.txt`** contient la liste de **tous** les fichiers du projet (node_modules, __pycache__, .ruff_cache, .git, etc.).

Pour régénérer :

```powershell
tree /F /A | Out-File -FilePath docs/ARBORESCENCE_COMPLETE.txt -Encoding utf8
```

---

*Document généré par analyse Context Specialist — Docling. Dernière mise à jour : 2026-03-01.*
