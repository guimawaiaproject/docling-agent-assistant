# Analyse manuelle exhaustive — Docling

**Date** : 2 mars 2026
**Méthode** : Lecture fichier par fichier, ligne par ligne (sans rapports d'audit)
**Périmètre** : api.py, backend/, apps/api/, docling-pwa/, configs, scripts, CI/CD

---

## 1. Structure du projet — Double codebase

Le projet contient **deux implémentations backend** :

| Chemin | Usage | Imports |
|--------|-------|---------|
| `api.py` + `backend/` | Probablement legacy / run local | `from backend.core.config` |
| `apps/api/` | Docker, CI, Makefile, Render | `from core.config` (relatif apps/api) |

**Risque** : Divergence entre les deux. `backend/core/config.py` n'expose pas `COMMUNITY_SALT` dans la facade `Config`, alors que `apps/api/core/config.py` le fait (l.143). Si `api.py` est utilisé avec community_service, `Config.COMMUNITY_SALT` lèverait `AttributeError`.

**Recommandation** : Clarifier l'entrée unique (api.py vs apps/api) et supprimer ou aligner l'autre.

---

## 2. api.py (racine) — Analyse ligne par ligne

### 2.1 Imports et initialisation (1-79)

- **L.64** : `os.getenv("ENVIRONMENT", "production")` — défaut "production" peut masquer des erreurs en dev.
- **L.72-75** : Warning si SENTRY_DSN absent en prod — correct.
- **L.79** : `get_remote_address` pour rate limit — peut être spoofé via X-Forwarded-For en prod (proxy).

### 2.2 Auth (86-113)

- **L.92** : `authorization[7:]` — pas de vérification que la chaîne fait au moins 7 caractères avant le slice (edge case si "Bearer" seul).
- **L.104** : En FREE_ACCESS_MODE, `_GUEST_USER_ID` peut être None si le lifespan n'a pas encore créé le guest — race au démarrage.
- **L.111** : `get_admin_user` — vérification `user.get("role") != "admin"` correcte.

### 2.3 Lifespan (179-212)

- **L.195** : `hash_password("guest-no-login-provisional")` — mot de passe guest en clair dans le code (acceptable pour guest partagé).
- **L.205** : `start_watchdog` avec `Config.DEFAULT_MODEL` — dépend du lifespan, ordre OK.

### 2.4 Endpoints

- **L.303** : `model not in Config.MODELS_DISPONIBLES` — validation correcte.
- **L.314** : `ext not in _ALLOWED_EXTENSIONS` — validation extension.
- **L.323** : `declared_mime not in _ALLOWED_MIMES` — validation MIME.
- **L.330-339** : Lecture par chunks 256 Ko, rejet si > 50 Mo — correct.
- **L.345** : `user_id = int(_user["sub"])` — si `sub` manquant, `KeyError` non géré.
- **L.356** : `get_job(job_id, user_id)` — avec `user_id=None` (guest edge case), la requête SQL `user_id = $2` avec None ne matche pas les jobs créés par le guest (car guest a un user_id). Cohérent.
- **L.424** : `compare_prices` — `search` validé `len(search.strip()) < 2` — correct.
- **L.458** : `samesite="lax"` — OWASP recommande "strict" pour cookies sensibles.
- **L.461** : `max_age=24*3600` — 24h, pas de refresh token.
- **L.506** : `update_community_preferences` — body JSON non validé par schéma Pydantic (`community_consent`, `zone_geo`).
- **L.414-416** : Ordre des commentaires ENDPOINT 10 et 11 inversé (cosmétique).

### 2.5 Health et Vitals

- **L.823** : `POST /api/vitals` — pas de rate limit.
- **L.851** : `GET /health` — vérifie DB via `SELECT 1`, pas de latence mesurée.

---

## 3. backend/core/config.py

- **L.95** : `Path(self.WATCHDOG_FOLDER + "/Traitees")` — si `WATCHDOG_FOLDER` se termine par `/`, on obtient `//Traitees`. Préférer `Path(self.WATCHDOG_FOLDER) / "Traitees"`.
- **L.96** : Idem pour Erreurs.
- **L.117-136** : `Config` facade — `COMMUNITY_SALT` absent. `community_service` l'utilise → `AttributeError` si base prix communautaire activée.
- **L.74** : Pas de validation que `WATCHDOG_FOLDER` n'est pas un chemin sensible (`/etc`, traversal).

---

## 4. backend/core/db_manager.py

### 4.1 Requêtes

- **L.253** : `fournisseur ILIKE ${idx} ESCAPE E'\\\\'` — `_escape_like` appliqué, correct.
- **L.332** : `COUNT(*)` à chaque requête catalogue — peut être lent sur >10k lignes.
- **L.386** : `get_fournisseurs` — pas de LIMIT, peut retourner des milliers de lignes.
- **L.393** : `get_factures_history` — LIMIT appliqué, correct.
- **L.414** : `compare_prices` — `params` correctement construit pour `user_id` optionnel.
- **L.418** : Bug potentiel — `params: tuple = (search_escaped, search, user_id) if user_id is not None else (search_escaped, search)` mais la requête utilise `user_clause = " AND user_id = $3"` quand `user_id` non None. Les placeholders $1, $2, $3 sont corrects. Vérifié OK.
- **L.389-416** : `get_user_export_data` — charge tous les produits et factures en mémoire, pas de LIMIT. Risque OOM pour utilisateurs avec beaucoup de données.

### 4.2 Pool

- **L.136-142** : `min_size=2`, `max_size=10`, `command_timeout=60`, `ssl="require"` — correct.
- Pas de `max_inactive_connection_lifetime` — connexions stale possibles avec Neon.

---

## 5. backend/core/orchestrator.py

- **L.127-136** : Boucle `for p in products_dicts` appelant `CommunityService.insert_anonymous_price` — **N+1** : N requêtes INSERT pour N produits. À remplacer par un batch `INSERT ... VALUES (...), (...), ...`.
- **L.166** : `heic`, `heif` dans mime_map mais pas dans `_ALLOWED_EXTENSIONS` de api.py — incohérence (watchdog accepte heic, upload API non).

---

## 6. backend/services/auth_service.py

- **L.55** : `logger.debug("Token invalide")` — en prod, les tentatives d'auth invalides devraient être en `logger.warning` pour monitoring.
- **L.31** : `JWT_EXPIRY` lu depuis `JWT_EXPIRY_HOURS` au chargement du module — pas de rechargement dynamique (acceptable).

---

## 7. backend/services/storage_service.py

- **L.27-33** : `boto3.client("s3", ...)` — pas de `Config` pour timeout. `put_object` et `generate_presigned_url` peuvent bloquer indéfiniment.
- **L.59** : Sanitisation filename avec `split("/")[-1].split("\\")[-1]` — correct pour path traversal.

---

## 8. backend/services/community_service.py

- **L.98** : `_escape_like(fournisseur)` — correct, évite l'injection LIKE.
- **L.52** : `if not Config.COMMUNITY_SALT` — avec `backend/core/config.py`, `Config.COMMUNITY_SALT` n'existe pas → crash.

---

## 9. backend/services/watchdog_service.py

- **L.103** : `_watchdog_status["folder"]` = `Config.WATCHDOG_FOLDER` au chargement du module — si Config change (tests), la valeur peut être obsolète.
- **L.62** : `path.read_bytes()` — pas de limite de taille, fichier très volumineux pourrait saturer la mémoire.

---

## 10. backend/schemas/invoice.py

- **L.76** : `BatchSaveRequest` — max 500 produits, validation des champs requis. Correct.
- Pas d'exemples dans `Field(...)` pour OpenAPI.

---

## 11. backend/utils/serializers.py

- **L.22** : `serialize_row` retourne une copie, ne mute pas — correct.
- Gère `date`, `datetime`, `Decimal` — correct.

---

## 12. docling-pwa — Frontend

### 12.1 main.jsx

- **L.27** : `Sentry.reactErrorHandler` sur `onUncaughtError`, `onCaughtError`, `onRecoverableError` — correct.
- **L.20** : `tracePropagationTargets` inclut l'API — correct pour tracing distribué.

### 12.2 apiClient.js

- **L.40-42** : Fallback `localStorage.getItem('docling-token')` alors que le cookie httpOnly est prioritaire — incohérence documentée, rétrocompatibilité.
- **L.50** : 401 → `localStorage.removeItem` + redirect /login — correct.
- Pas d'`AbortController` pour annuler les requêtes en cours (ex. changement de page).

### 12.3 App.jsx

- **L.39** : `RouteWrapper = FEATURES.AUTH_REQUIRED ? ProtectedRoute : Fragment` — correct.
- **L.46** : `OfflineBanner` en haut — correct.

### 12.4 index.html

- **L.7** : CSP avec `'unsafe-inline'` et `'unsafe-eval'` — nécessaire pour Vite dev, à restreindre en prod si possible.
- **L.2** : `lang="fr"` — correct.

### 12.5 useStore.js (docling-pwa)

- **L.47** : `devtools(persist(...))` — pas de `enabled: import.meta.env.DEV`, devtools actif en prod.

---

## 13. Pre-commit et Ruff

- **L.11** : `files: ^(apps/api/|scripts/|tests/)` — **api.py** et **backend/** ne sont pas couverts par Ruff.
- **L.27** : Prettier sur `^apps/pwa/src/` — **docling-pwa** n'est pas formaté si c'est le frontend utilisé.

---

## 14. Dockerfile

- **L.14** : `COPY apps/api/` — n'inclut pas `api.py` ni `backend/`. Cohérent si l'entrée est `apps/api/main.py`.
- **L.15** : `COPY .env.example .env` — écrase toute variable d'environnement avec les valeurs par défaut. En prod, les vars sont injectées par le runtime (Render), donc .env peut être vide.
- **L.23** : `CMD ["uvicorn", "main:app", ...]` — utilise `main` de apps/api. PYTHONPATH=/app/apps/api. Cohérent.

---

## 15. pyproject.toml (racine)

- **L.1-15** : Dépendances incluent `streamlit`, `pandas`, `openpyxl` — projet "docling-agent-assistant" différent de l'API FastAPI. Probablement un outil Streamlit séparé.
- **L.21** : `testpaths = ["apps/api"]` — les tests sont dans apps/api.
- **L.48** : `ignore = ["E501", "B008"]` — E501 (line length) ignoré.

---

## 16. requirements.txt

- Pas de versions épinglées avec hash (`--require-hashes`) — reproductibilité limitée.
- `python-dotenv` présent mais `pydantic-settings` charge .env — redondant.

---

## 17. health_check.py

- **L.39** : `from core.config import Config` — suppose sys.path avec apps/api. Correct.
- **L.43** : `Config.DATABASE_URL` — nécessite .env chargé. pydantic-settings charge depuis le chemin du projet. Le script ajoute `apps/api` au path mais pas la racine — `.env` est à la racine. `_env_path()` dans apps/api pointe vers la racine. Vérifier que health_check s'exécute depuis la racine.

---

## 18. CI (ci.yml)

- **L.70-75** : `pip-audit` avec `continue-on-error: true` — les CVE ne bloquent pas le build.
- **L.99-101** : `npm audit` avec `continue-on-error: true` — idem.
- **L.65** : `--cov-fail-under=65` — seuil de couverture.

---

## 19. Synthèse des problèmes identifiés

### Critique

| Fichier | Ligne | Problème |
|---------|-------|----------|
| backend/core/config.py | 117-136 | `COMMUNITY_SALT` absent de Config → crash si community_service utilisé avec api.py |
| backend/core/config.py | 95-96 | Concaténation path `WATCHDOG_FOLDER + "/Traitees"` fragile |
| backend/core/db_manager.py | 389-416 | `get_user_export_data` sans LIMIT → OOM |
| backend/core/orchestrator.py | 127-136 | N+1 insert_anonymous_price |

### Majeur

| Fichier | Ligne | Problème |
|---------|-------|----------|
| backend/services/storage_service.py | 27-33 | boto3 sans timeout |
| backend/core/db_manager.py | 386 | get_fournisseurs sans LIMIT |
| backend/core/db_manager.py | 332 | COUNT(*) catalogue à chaque requête |
| api.py | 506 | update_community_preferences body non validé |
| api.py | 458 | SameSite=lax au lieu de strict |
| backend/services/auth_service.py | 55 | logger.debug pour token invalide |
| .pre-commit-config.yaml | 11 | api.py et backend/ exclus de Ruff |
| docling-pwa useStore | 47 | devtools actif en prod |

### Mineur

| Fichier | Ligne | Problème |
|---------|-------|----------|
| api.py | 414-416 | Ordre commentaires ENDPOINT 10/11 |
| api.py | 823 | POST /api/vitals sans rate limit |
| api.py | 92 | authorization[7:] sans vérification longueur |
| backend/core/config.py | 74 | Pas de validation WATCHDOG_FOLDER |
| watchdog_service.py | 62 | read_bytes sans limite taille |
| orchestrator | 166 | heic/heif dans mime_map mais pas dans api.py |

---

## 20. Recommandations prioritaires

1. **Unifier la config** : Ajouter `COMMUNITY_SALT` à `backend/core/config.py` Config, ou confirmer que seul apps/api est utilisé.
2. **Corriger les paths** : `Path(WATCHDOG_FOLDER) / "Traitees"` au lieu de concaténation.
3. **Batch insert_anonymous_price** : Une requête INSERT multi-VALUES.
4. **LIMIT export_my_data** : Pagination ou LIMIT 50000.
5. **Timeout boto3** : `Config=botocore.config.Config(connect_timeout=30, read_timeout=60)`.
6. **Ruff** : Inclure `api.py` et `backend/` dans pre-commit.
7. **logger.warning** pour token invalide en prod.
8. **Schéma Pydantic** pour update_community_preferences.

---

## 21. Compléments — Frontend (suite)

### 21.1 devisGenerator.js

- **L.8-18** et **L.24-33** : `getNextCounter()` et `getPreviewDevisNum()` — **duplication** : même logique (year, stored, counter). Extraire en une fonction commune.
- **L.61-66** : `settings.logo` — si base64 PNG volumineux, `doc.addImage()` peut consommer beaucoup de mémoire.
- **L.39** : `getSettings()` — try/catch sur JSON.parse, correct.

### 21.2 reportWebVitals.js

- **L.31** : `API_BASE_URL + '/api/vitals'` — correct pour prod. L’endpoint existe dans api.py et apps/api/main.py.
- **L.21** : `isDev` — en dev, console.log uniquement ; en prod, sendBeacon.

### 21.3 imageService.js

- **L.1** : `MAX_SIZE = 2000` — limite correcte pour redimensionnement.
- **L.28** : `URL.revokeObjectURL(url)` — libération correcte après compression.

### 21.4 useStore.js (complet)

- **L.47** : `devtools(persist(...))` — pas de `enabled: import.meta.env.DEV` → **devtools actif en prod**.
- **L.94-96** : `addToQueue` — déduplication par `name__size`, correct.
- **L.150-156** : `partialize` — ne persiste que `selectedModel`, pas `batchQueue` ; cohérent.

### 21.5 categories.js

- Constantes simples, aucune anomalie.

### 21.6 vite.config.js

- **L.58-66** : `manualChunks` — react-core, router, pdf-gen, excel-gen, etc. — correct.
- **L.55** : `chunkSizeWarningLimit: 600` — avertissement à 600 Ko.

### 21.7 CataloguePage

- **Import statique** : `import ExcelJS from 'exceljs'` — ~917 kB chargé au montage de la page, même si l’utilisateur n’exporte pas en Excel. **Recommandation** : `const ExcelJS = lazy(() => import('exceljs'))` ou chargement dynamique au clic sur export.

### 21.8 Composants

- **CommandPalette** : `Ctrl+K` / `Cmd+K`, navigation clavier, pas de fuite mémoire.
- **Navbar** : `navigator.onLine`, écouteurs online/offline correctement nettoyés.
- **SplineScene** : `lazy(() => import('@splinetool/react-spline'))`, `renderOnDemand` — correct.
- **OfflineBanner** : affichage conditionnel selon `navigator.onLine`.

### 21.9 DevisPage — fetchProducts

- **L.87** : `Array.isArray(data) ? data : (data.products || [])` — gère correctement `{ products: [...] }` et cas dégradés.

### 21.10 offlineQueue.js

- **Pas de limite** sur `file.arrayBuffer()` — pour des fichiers très volumineux (ex. PDF > 100 Mo), risque **OOM** côté client. Recommandation : limiter la taille max par fichier ou utiliser un streaming.

### 21.11 ProtectedRoute

- Vérifie `localStorage.getItem('docling-token')` alors que l’auth repose sur un **cookie httpOnly**. En mode cookie-only, le token n’est pas dans localStorage → la vérification peut être obsolète. À aligner avec la stratégie d’auth réelle.

### 21.12 ScanPage

- **L.519** : `window.confirm` pour vider la file — UX basique ; envisager une modal plus accessible.

### 21.13 ValidationPage

- `handleRemove` sans confirmation — suppression immédiate d’un produit, risque de clic accidentel.

---

## 22. Scripts et workflows

### 22.1 prettier_precommit.js

- **L.11** : Filtre `files.includes('apps/pwa/')` — cohérent avec pre-commit `files: ^apps/pwa/src/`.
- **L.17** : `pnpm --filter docling-pwa` — apps/pwa a `"name": "docling-pwa"` dans package.json, donc le filtre est correct.

### 22.2 pnpm-workspace.yaml

- **L.2** : `packages: ['apps/pwa']` — seul apps/pwa est dans le workspace. **docling-pwa** (racine) n’est pas dans le workspace. Le déploiement et la CI utilisent **apps/pwa**.

### 22.3 deploy.yml

- **L.38** : `working-directory: apps/pwa` — frontend déployé depuis apps/pwa.
- **L.59** : `VITE_API_URL` depuis secrets — correct.

### 22.4 tests.yml

- **L.14** : `working-directory: apps/api` — tests backend depuis apps/api.
- **L.42** : `alembic upgrade head` — migrations appliquées avant tests.

---

## 23. Double frontend — docling-pwa vs apps/pwa

| Chemin        | Usage                    | Workspace |
|---------------|--------------------------|-----------|
| `docling-pwa/` | Probablement legacy/dev  | Non       |
| `apps/pwa/`    | CI, deploy, pre-commit   | Oui       |

**Risque** : Divergence entre les deux. Les deux ont une structure proche (features/, components/, etc.). **Recommandation** : Conserver une seule source de vérité (apps/pwa) et supprimer ou documenter docling-pwa comme copie de travail.

---

## 24. Synthèse mise à jour — Problèmes additionnels

### Mineur (ajouts)

| Fichier              | Problème |
|----------------------|----------|
| devisGenerator.js    | Duplication getNextCounter / getPreviewDevisNum |
| devisGenerator.js    | settings.logo base64 volumineux → risque mémoire |
| CataloguePage.jsx    | Import statique ExcelJS (~917 kB) au montage |
| docling-pwa vs apps/pwa | Double codebase frontend |

---

*Analyse effectuée par lecture manuelle des fichiers sources — 2 mars 2026. Complétée avec devisGenerator, reportWebVitals, imageService, useStore, categories, vite.config, composants, scripts, workflows et double frontend.*
