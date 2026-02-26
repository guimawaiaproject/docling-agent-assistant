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
- [x] Fix `requirements.txt` (retrait `pydantic-settings`, `openpyxl` inutilises; ajout `boto3`)
- [x] Fix `db_manager.py` (deduplication code SQL upsert)
- [x] Nettoyage `.env.example` (toutes les variables documentees)

---

## Points d'attention restants

### Backend

1. **Archivage cloud PDF (Storj S3)**
   - `backend/core/config.py` declare deja `STORJ_BUCKET`, `STORJ_ACCESS_KEY`, etc.
   - `boto3` est dans `requirements.txt`
   - Il manque : `backend/services/storage_service.py` (upload/download S3)
   - Il manque : integration dans `orchestrator.py` (upload apres extraction)
   - Il manque : colonne `pdf_url` dans `schema_neon.sql` et dans `db_manager.py`
   - Statut : **NON IMPLEMENTE**

2. **Watchdog (`watchdog_service.py`)**
   - Le service existe et est importe dans `api.py` (lifespan)
   - Verifier qu'il fonctionne correctement (chemin Windows vs Linux)
   - Le dossier `Docling_Factures/` doit etre cree manuellement si WATCHDOG_ENABLED=true

3. **Schema SQL (`schema_neon.sql`)**
   - Contient `CREATE EXTENSION IF NOT EXISTS vector` mais aucune colonne vector n'est utilisee
   - A nettoyer si les embeddings ne sont pas prevus a court terme

4. **Gestion erreurs Gemini**
   - `gemini_service.py` gere le rate-limit (429) avec retry
   - Pas de circuit-breaker si le modele est down pendant longtemps

5. **Tests**
   - Aucun test unitaire ou d'integration dans le projet actuellement
   - A prevoir : tests `pytest` pour pipeline extraction, db_manager, API endpoints

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

| # | Tache | Effort | Impact |
|---|-------|--------|--------|
| 1 | Implementer stockage cloud S3 (Storj) | Moyen | Archivage + tracabilite factures |
| 2 | Ajouter colonne `pdf_url` au schema + API | Faible | Lien direct vers le PDF original |
| 3 | Reecrire `SettingsPage` (config utilisateur) | Moyen | UX |
| 4 | Tests unitaires (pipeline, BDD, API) | Moyen | Fiabilite |
| 5 | Nettoyer extension `vector` du schema SQL | Faible | Proprete |
| 6 | PWA manifest check apres build | Faible | Installation mobile |
| 7 | CI/CD pipeline (GitHub Actions) | Moyen | Qualite |

---

## Variables d'environnement

| Variable | Obligatoire | Description |
|----------|:-----------:|-------------|
| `GEMINI_API_KEY` | Oui | Cle API Google Gemini |
| `DATABASE_URL` | Oui | URL PostgreSQL Neon |
| `DEFAULT_AI_MODEL` | Non | Modele IA (defaut: gemini-3-flash-preview) |
| `WATCHDOG_FOLDER` | Non | Dossier surveille (defaut: ./Docling_Factures) |
| `WATCHDOG_ENABLED` | Non | Activer watchdog (defaut: false) |
| `STORJ_BUCKET` | Non | Bucket S3 pour archivage PDF |
| `STORJ_ACCESS_KEY` | Non | Cle acces Storj |
| `STORJ_SECRET_KEY` | Non | Cle secrete Storj |
| `STORJ_ENDPOINT` | Non | Endpoint S3 Storj |
| `PWA_URL` | Non | URL frontend en production (CORS) |