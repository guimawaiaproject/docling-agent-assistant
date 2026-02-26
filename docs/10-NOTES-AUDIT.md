# NOTES D'AUDIT - Docling Agent v3

> Genere le 24/02/2026 apres audit complet du codebase.
> Ce fichier recense ce qui reste a faire, les points d'attention, et les decisions prises.

---

## Nettoyage effectue

- [x] Suppression des fichiers morts : `folder_watcher.py`, `monitoring.py`, `migrate_factures.py`, `fix_db.py`, `audit_script.py`, `process_test_folder.py`, `patch_sdk.py`, `verify_app.py`, `setup.bat`, `pytest.ini`, `test_win32.py`, `setup.sh`, `diag_shortcuts.py`, `docker-compose.yml`, `app.py` (Streamlit), `.streamlit/config.toml`
- [x] Suppression dossiers obsoletes : `backend/middleware/`, `tests/`, `mnt/`, `docling-pwa/dist/`, `docling-pwa/src/assets/react.svg`, `docling-pwa/src/App.css`, `data_cache.db*`
- [x] Suppression fichiers temporaires Vite : `vite.config.js.timestamp-*.mjs`
- [x] Suppression docs obsoletes : `RAPPORT_AUDIT.md`, `cahier_des_charges_premium.md`, `PLAN_TECHNIQUE_DOCLING_AGENT.md`
- [x] Fix `Dockerfile` (suppression reference a `app.py` Streamlit)
- [x] Fix `App.jsx` et `Navbar.jsx` (HistoryPage jamais accessible, maintenant branche)
- [x] Fix `requirements.txt` (retrait `openpyxl` inutilise; ajout `boto3`, `pydantic-settings` utilise depuis Phase 3)
- [x] Fix `db_manager.py` (deduplication code SQL upsert)
- [x] Nettoyage `.env.example` (toutes les variables documentees)

---

## Points d'attention restants

### Backend

1. **Archivage cloud PDF (Storj S3)**
   - `backend/services/storage_service.py` implemente (upload/download S3 via boto3)
   - Integration dans `orchestrator.py` (upload parallele avec asyncio.gather)
   - Statut : **IMPLEMENTE** (Phase 2)

2. **Watchdog (`watchdog_service.py`)**
   - Le service existe et est importe dans `api.py` (lifespan)
   - Verifier qu'il fonctionne correctement (chemin Windows vs Linux)
   - Le dossier `Docling_Factures/` doit etre cree manuellement si WATCHDOG_ENABLED=true

3. **Schema SQL (`schema_neon.sql`)**
   - Contient `CREATE EXTENSION IF NOT EXISTS vector` mais aucune colonne vector n'est utilisee
   - A nettoyer si les embeddings ne sont pas prevus a court terme

4. **Gestion erreurs Gemini**
   - `gemini_service.py` gere le rate-limit (429) avec retry
   - Circuit-breaker implemente dans `api.py` (`_GeminiCircuitBreaker`, seuil 5 erreurs consecutives)
   - Statut : **IMPLEMENTE** (Phase 2)

5. **Tests**
   - 91 tests backend (pytest) + 43 tests frontend (Vitest) = 134 tests
   - Couvre : unit, integration, API, E2E Playwright, securite, performance, data integrity
   - Config unifiee dans `pyproject.toml`
   - Statut : **IMPLEMENTE** (Phase 6)

### Frontend

6. **SettingsPage**
   - La page existe mais est tres basique
   - Pourrait inclure : choix du modele IA, toggle watchdog, test connexion BDD

7. **HistoryPage**
   - Nouvellement branchee dans le routeur
   - Verifier que l'endpoint `/api/v1/history` renvoie bien les donnees attendues

8. **Export Excel**
   - `xlsx` est dans les dependances frontend
   - Verifier que l'export fonctionne depuis CataloguePage

9. **PWA Manifest**
   - `manifest.webmanifest` a ete supprime
   - Le plugin `vite-plugin-pwa` dans `vite.config.js` devrait le regenerer automatiquement
   - A verifier apres `npm run build`

10. **Mode HTTPS local**
    - `vite.config.js` utilise `@vitejs/plugin-basic-ssl` pour HTTPS en dev
    - Necessaire pour les fonctionnalites PWA (camera, install prompt)

---

## Prochaines etapes suggerees (par priorite)

| # | Tache | Statut | Effort |
|---|-------|--------|--------|
| 1 | Stockage cloud S3 (Storj) | **FAIT** (Phase 2) | - |
| 2 | Tests unitaires + integration + E2E | **FAIT** (Phase 6, 134 tests) | - |
| 3 | CI/CD pipeline (GitHub Actions) | **FAIT** (Phase 5) | - |
| 4 | Reecrire `SettingsPage` (config utilisateur) | A faire | Moyen |
| 5 | Nettoyer extension `vector` du schema SQL | A faire | Faible |
| 6 | PWA manifest check apres build | Verifie OK | - |

---

## Variables d'environnement

| Variable | Obligatoire | Description |
|----------|:-----------:|-------------|
| `GEMINI_API_KEY` | Oui | Cle API Google Gemini |
| `DATABASE_URL` | Oui | URL PostgreSQL Neon |
| `DEFAULT_AI_MODEL` | Non | Modele IA (defaut: gemini-3-flash-preview) |
| `WATCHDOG_FOLDER` | Non | Dossier surveille (defaut: ./Docling_Factures) |
| `WATCHDOG_ENABLED` | Non | Activer watchdog (defaut: true) |
| `STORJ_BUCKET` | Non | Bucket S3 pour archivage PDF |
| `STORJ_ACCESS_KEY` | Non | Cle acces Storj |
| `STORJ_SECRET_KEY` | Non | Cle secrete Storj |
| `STORJ_ENDPOINT` | Non | Endpoint S3 Storj |
| `PWA_URL` | Non | URL frontend en production (CORS) |
| `JWT_SECRET` | **Oui** | Secret JWT (generer avec openssl rand -hex 32) |
| `JWT_EXPIRY_HOURS` | Non | Duree token JWT (defaut: 24h) |
| `SENTRY_DSN` | Non | DSN Sentry backend (monitoring) |
| `ENVIRONMENT` | Non | Nom environnement (defaut: production) |
| `VITE_TVA_RATE` | Non | Taux TVA frontend (defaut: 0.21) |
| `VITE_SENTRY_DSN` | Non | DSN Sentry frontend |