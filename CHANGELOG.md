# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.
Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## [3.0.0] — 2026-02-26

### Phase 0 — Urgences absolues
- **Sécurisé** `DELETE /api/v1/catalogue/reset` (auth admin obligatoire)
- **Supprimé** fallback `JWT_SECRET` — fail-fast au démarrage
- **Migré** JWT maison vers PyJWT (`create_token`, `verify_token`)
- **Corrigé** token lu en query param → `Authorization: Bearer` header
- **Ajouté** `get_current_user` + `Depends` sur tous les endpoints métier
- **Corrigé** division par zéro dans le schéma invoice Pydantic
- **Sécurisé** parsing XML Factur-X contre XXE (`resolve_entities=False`, `no_network=True`)
- **Ajouté** CI baseline GitHub Actions

### Phase 1 — Sécurité complète
- **Ajouté** upload chunked avec validation taille max (50 Mo) et MIME allowlist
- **Ajouté** rate limiting sur endpoints auth via `slowapi`
- **Restreint** CORS (méthodes, headers explicites)
- **Uniformisé** erreurs 500 génériques (détails masqués, logs complets)
- **Migré** hash passwords vers argon2id avec rehash transparent pbkdf2
- **Ajouté** protection CSV formula injection à l'export
- **Filtré** origines CORS vides dans config
- **Documenté** `JWT_SECRET` obligatoire dans `.env.example`

### Phase 2 — Performance & architecture runtime
- **Ajouté** `React.lazy` + `Suspense` pour lazy-loading des pages PWA
- **Parallélisé** upload S3 + sauvegarde DB avec `asyncio.gather`
- **Corrigé** N+1 query dans `compare_prices` avec batch SQL
- **Extrait** utilitaire `serialize_row` (DRY serialization)
- **Remplacé** boucles manuelles de sérialisation par `serialize_row`
- **Retiré** getter Zustand non-réactif (`queueStats`)
- **Centralisé** constante `FAMILLES` dans `constants/categories.js`
- **Optimisé** `IDBObjectStore.count()` et supprimé exports morts
- **Créé** `apiClient` Axios partagé avec intercepteur Bearer
- **Corrigé** fuite mémoire `URL.revokeObjectURL` dans ScanPage
- **Ajouté** `AbortController` dans polling ScanPage et CompareModal
- **Ajouté** debounce recherche dans CompareModal
- **Durci** résolution `VITE_API_URL` en production (note : fallback `/api` si non défini en dev)
- **Encapsulé** circuit breaker Gemini dans classe thread-safe

### Phase 3 — Base de données & migrations
- **Initialisé** Alembic avec migration baseline du schéma existant
- **Ajouté** CHECK constraints via migration Alembic
- **Ajouté** FK `produits.fournisseur → fournisseurs.nom` via migration avec auto-insert orphelins
- **Corrigé** gestion SSL asyncpg dans `alembic env.py`
- **Ajouté** logging erreurs silencieuses `prix_historique`
- **Migré** config vers `pydantic-settings` (`BaseSettings`)
- **Supprimé** double source `DATABASE_URL`
- **Remplacé** `__import__("asyncio")` par import propre

### Phase 4 — Nettoyage code mort & dépendances
- **Supprimé** imports morts backend (image_preprocessor, gemini_service, orchestrator)
- **Supprimé** méthode DB `get_price_history` inutilisée
- **Supprimé** exports frontend inutilisés (imageService, offlineQueue, SettingsPage)
- **Corrigé** `useState` dead search state dans CataloguePage
- **Supprimé** bloc styling XLSX inactif
- **Déplacé** tooling JS vers `devDependencies`
- **Supprimé** `@types/react*` (projet JS pur)
- **Supprimé** Pillow inutilisé
- **Pinné** dépendances Python + ajouté `requirements-dev.txt`
- **Ajouté** `lxml` explicite dans requirements

### Phase 5 — DevOps & CI/CD
- **Amélioré** health check avec validation DB réelle
- **Corrigé** `run_local.bat` pour kill ciblé par port/PID
- **Ajouté** `node_modules/` dans `.gitignore`
- **Recréé** `docker-compose.yml` complet
- **Créé** `.dockerignore` optimisé
- **Ajouté** `HEALTHCHECK` dans Dockerfile
- **Ajouté** service PostgreSQL 16 dans CI
- **Ajouté** jobs lint backend (ruff) et frontend (eslint) en CI
- **Créé** `run_local.sh` cross-platform
- **Créé** `Makefile` développeur
- **Ajouté** environnement staging (`.env.staging`, `docs/staging-setup.md`)

### Phase 6 — Tests
- **Unifié** config pytest dans `pyproject.toml` (supprimé `pytest.ini` dupliqués)
- **Centralisé** fixtures Playwright E2E dans `conftest.py`
- **Corrigé** Vitest `NODE_ENV` pour React 19 et `File.size` read-only dans tests
- **Résultat** : 91 tests backend + 43 tests frontend = 134/134 verts

### Phase 7 — Accessibilité & UX
- **Ajouté** sémantique `role="dialog"` + `aria-modal` + `aria-label` sur lightbox et CompareModal
- **Ajouté** `aria-label` sur tous les boutons icon-only
- **Ajouté** labels HTML explicites sur tous les formulaires (Devis, Validation)
- **Remplacé** faux tableau `<div>` par `<table>` sémantique dans CataloguePage
- **Ajouté** `ErrorBoundary` global React avec messages utilisateur

### Phase 8 — I18N, docs, polish (en cours)
- **Externalisé** taux TVA via `VITE_TVA_RATE` dans ValidationPage
- **Corrigé** accents français manquants dans DevisPage (Générez, sélectionnés, etc.)

### Hotfixes
- **Corrigé** nom modèle par défaut `gemini-3-flash` → `gemini-3-flash-preview` dans endpoint process
- **Ajouté** validation `DEFAULT_AI_MODEL` dans `Config.validate_startup()`
- **Corrigé** `ValueError` non attrapé dans `verify_token` (sub non-numérique)
- **Ajouté** validation `JWT_SECRET` centralisée dans `Config.validate_startup()`
