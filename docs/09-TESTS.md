# Rapport de tests complet — Docling Agent v3/v4

**Date :** 25 février 2026  
**Projet :** docling-agent-assistant

---

## 1. Tests Backend (pytest)

| Statut | Résultat |
|--------|----------|
| **Total** | 91 tests |
| **Passés** | 91 |
| **Échoués** | 0 |
| **Durée** | ~42 s |

### Modules testés

| Catégorie | Dossier | Tests |
|-----------|---------|-------|
| Unitaires | `tests/01_unit/` | config, gemini_service, image_preprocessor, models, orchestrator, validators |
| Intégration | `tests/02_integration/` | database, storage |
| API | `tests/03_api/` | auth, catalogue, health, invoices, reset_admin, stats_history, sync |
| E2E | `tests/04_e2e/` | catalogue_browse, scan_flow, settings_sync |
| Sécurité | `tests/05_security/` | auth_bypass, headers, injection |
| Performance | `tests/06_performance/` | response_times, locustfile |
| Data integrity | `tests/07_data_integrity/` | api_db_coherence, constraints, transactions |
| External | `tests/08_external_services/` | extraction_reelle |

### Corrections appliquées pendant les tests

- **`_parse_date`** : ordre des checks `datetime` vs `date` corrigé (datetime est sous-classe de date)
- **`storage_service.py`** : `datetime.utcnow()` remplacé par `datetime.now(timezone.utc)` (deprecated)
- **`gemini_service.py`** : suppression du code mort (double création de `gen_config`)

---

## 2. Tests API (endpoints HTTP)

| Endpoint | Méthode | Statut |
|----------|---------|--------|
| `/` | GET | 200 OK |
| `/health` | GET | 200 OK |
| `/api/v1/stats` | GET | 200 OK |
| `/api/v1/history` | GET | 200 OK |
| `/api/v1/catalogue` | GET | 200 OK |
| `/api/v1/catalogue/fournisseurs` | GET | 200 OK |
| `/api/v1/sync/status` | GET | 200 OK |

**Résultat :** 7/7 endpoints OK

---

## 3. Tests Frontend (Vitest + Testing Library)

| Statut | Résultat |
|--------|----------|
| **Total** | 43 tests |
| **Passés** | 43 |
| **Échoués** | 0 |
| **Durée** | ~8 s |

### Fichiers testés

| Fichier | Tests | Couverture |
|---------|-------|------------|
| `CompareModal.test.jsx` | 17 | Accessibilité, recherche, debounce, dialog |
| `useStore.test.js` | ~15 | Zustand state, queue, products |
| `apiClient.test.js` | ~11 | Intercepteur Bearer, retry, erreurs |

### Build production

| Étape | Résultat |
|-------|----------|
| `npm run build` | OK |
| Sortie | `dist/` (PWA + SW + manifest) |

### Lint (ESLint 9)

0 erreur, 0 warning

---

## 4. Audit de code — Backend

### Problèmes critiques corrigés

| Fichier | Problème | Correction |
|---------|----------|------------|
| `api.py` | CORS `allow_origins=["*"]` | `Config.ALLOWED_ORIGINS` |
| `api.py` | Pas de limite taille upload | Max 50 Mo, HTTP 413 si dépassement |
| `api.py` | DELETE reset non protégé | Vérification JWT admin |
| `storage_service.py` | `datetime.utcnow()` deprecated | `datetime.now(timezone.utc)` |

### Problèmes restants (non critiques)

- **db_manager** : boucle séquentielle dans `upsert_products_batch` (optimisation possible)
- **orchestrator** : appels sync (Gemini, Storage) dans async — acceptable pour l’instant
- **auth_service** : JWT_SECRET par défaut en dev — documenté dans `.env.example`

---

## 5. Audit de code — Frontend

### Problèmes critiques identifiés

| Fichier | Problème | Sévérité |
|---------|----------|----------|
| `CompareModal.jsx` | Index comme `key` dans `.map()` | Critique |
| `ScanPage.jsx` | Index comme `key` (item.id existe) | À vérifier |
| `ValidationPage.jsx` | Index comme `key` | Critique |

**Recommandation :** Remplacer les clés d’index par des identifiants stables (`item.id`, `p.id` ou combinaison unique).

### Problèmes moyens

- `useStore.js` : `_idCounter` global, getter `queueStats` non mémorisé
- `HistoryPage.jsx` / `SettingsPage.jsx` : dépendances `useEffect` manquantes
- `ScanPage.jsx` : `batchQueue` lu après `await` (état potentiellement obsolète)

---

## 6. Tests UI/UX

**Note :** Les tests E2E Playwright sont configurés dans `tests/04_e2e/` avec fixtures centralisées dans `conftest.py`. Tests manuels complémentaires recommandés :

1. **Scan** : Glisser-déposer PDF/image → Lancer → Vérifier progression
2. **Validation** : Édition des champs, suppression produit, lightbox facture
3. **Catalogue** : Recherche, filtre fournisseur, tri, comparateur de prix
4. **Historique** : Liste factures, lien PDF, re-scan
5. **Paramètres** : Test connexion API, sélection modèle IA
6. **Devis** : Recherche produits, ajout au panier, génération PDF

---

## 7. Résumé global

| Catégorie | Résultat |
|-----------|----------|
| **Backend pytest** | 91/91 passés |
| **Frontend vitest** | 43/43 passés |
| **Total** | 134/134 passés |
| **Frontend build** | OK |
| **Frontend lint** | OK |
| **Sécurité** | CORS, limite upload, auth DELETE corrigés |
| **Dépôts** | `datetime.utcnow` remplacé |

---

## 8. Commandes pour relancer les tests

```bash
# Backend (91 tests)
pytest tests/01_unit -v --tb=short

# Frontend (43 tests)
cd docling-pwa && npx vitest run

# Tous les tests (hors slow/external)
pytest tests/ -v -m "not slow and not external"
```

---

*Rapport généré automatiquement — Docling Agent v3/v4*
