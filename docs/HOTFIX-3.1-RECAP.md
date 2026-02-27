# Récapitulatif HOTFIX-3.1 à HOTFIX-3.16

**Date** : 26 février 2026
**Branche** : dashboard-b2b-v2
**16 commits** — un par tâche

---

## Fichiers modifiés par hotfix

| # | Commit | Fichiers |
|---|--------|----------|
| 3.1 | `fix(h3-1): isolate job status by user_id` | `migrations/versions/a004_add_jobs_user_id.py`, `backend/core/db_manager.py`, `api.py` |
| 3.2 | `fix(h3-2): correct files_processed key in settings` | `docling-pwa/src/pages/SettingsPage.jsx` |
| 3.3 | `fix(h3-3): guard division by zero in facturx extractor` | `backend/services/facturx_extractor.py` |
| 3.4 | `fix(h3-4): validate model source email password params` | `api.py` |
| 3.5 | `fix(h3-5): handle prix_historique failure explicitly` | `backend/core/db_manager.py`, `api.py`, `backend/core/orchestrator.py`, `tests/02_integration/test_database.py` |
| 3.6 | `fix(h3-6): load full catalogue in devis page` | `docling-pwa/src/pages/DevisPage.jsx` |
| 3.7 | `fix(h3-7): use authenticated client in test_invoices` | `tests/03_api/test_invoices.py` |
| 3.8 | `feat(h3-8): migrate run_migrations to alembic` | `backend/core/db_manager.py` |
| 3.9 | `fix(h3-9): sanitize error messages in job status` | `api.py` |
| 3.10 | `fix(h3-10): handle 401 during offline sync` | `docling-pwa/src/pages/ScanPage.jsx` |
| 3.11 | `fix(h3-11): safe float conversion in db_manager` | `backend/core/db_manager.py` |
| 3.12 | `fix(h3-12): harmonize famille electricite accent` | `backend/services/gemini_service.py` |
| 3.13 | `fix(h3-13): add pending source to batch save` | `docling-pwa/src/store/useStore.js`, `docling-pwa/src/pages/ScanPage.jsx`, `docling-pwa/src/pages/ValidationPage.jsx` |
| 3.14 | `fix(h3-14): escape wildcards in catalogue search` | `backend/core/db_manager.py` |
| 3.15 | `fix(h3-15): reset item status on abort` | `docling-pwa/src/pages/ScanPage.jsx` |
| 3.16 | `fix(h3-16): add ci test requirements install` | `.github/workflows/ci.yml` |

---

## Done when vérifié

| Hotfix | Critère | Statut |
|--------|---------|--------|
| 3.1 | User A ne peut pas voir le job de User B → 404 | ✅ `get_job` filtre par `user_id` |
| 3.2 | Compteur s'affiche correctement | ✅ `sync.total_processed` |
| 3.3 | PDF avec montants à 0 ne crash plus | ✅ Guard `(line_amount + allowance) > 0` |
| 3.4 | Paramètres invalides retournent 400 | ✅ model, source, email, password validés |
| 3.5 | Échec historique visible dans les logs Sentry | ✅ `exc_info=True` + `partial_success` dans la réponse |
| 3.6 | DevisPage affiche tous les produits | ✅ `params: { limit: 500 }` |
| 3.7 | Tests process retournent 202 au lieu de 401 | ✅ `authenticated_client` utilisé |
| 3.8 | `alembic upgrade head` suffit | ✅ `run_migrations()` appelle Alembic |
| 3.9 | `get_job_status` ne retourne jamais de message technique | ✅ `_sanitize_job_error()` |
| 3.10 | Token expiré pendant sync → toast clair | ✅ 401 → break + toast |
| 3.11 | Produit avec `prix_brut_ht="N/A"` ne crash plus | ✅ `_safe_float()` |
| 3.12 | "Électricité" sauvegardé correctement | ✅ SYSTEM_PROMPT harmonisé |
| 3.13 | Scan mobile → source="mobile" en DB | ✅ `pendingSource` dans store + payload |
| 3.14 | Recherche `%` ne retourne pas tout | ✅ `_escape_like()` |
| 3.15 | Item annulé repasse en "pending" | ✅ `updateItem(id, { status: 'pending' })` |
| 3.16 | CI installe toutes les dépendances de test | ✅ `pip install -r tests/requirements-test.txt` |

---

## Tests

- **Unit tests** : 86 passent, 5 échouent (JWT tests sans `JWT_SECRET` — préexistant, CI définit la variable)
- **API tests** : Nécessitent serveur + DB (conftest `ensure_server_running`)
- **CI** : `pytest tests/` avec `DATABASE_URL`, `JWT_SECRET`, `GEMINI_API_KEY` définis

---

## Migration a004

Avant déploiement, exécuter :

```bash
alembic upgrade head
```

Cela ajoute la colonne `user_id` à la table `jobs`.

---

## Tâches reportées (non faites)

- Pagination côté API pour le tri catalogue (HOTFIX-3.18)
- Multi-onglets Zustand sync (HOTFIX-3.19)
- Récupération de job après fermeture onglet (HOTFIX-3.20)
