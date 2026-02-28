# ⚡ 09 — AUDIT PERFORMANCE
# Backend · Frontend · Bundle · Requêtes DB · Re-renders
# Phase 09 — Audit Bêton Docling Agent v3

---

## PRINCIPE

```
La performance ne se suppose pas. Elle se mesure.
Pour chaque vecteur :
  → Identifier les goulots potentiels
  → Vérifier le code qui optimise
  → Si optimisation absente ou insuffisante → 🟠 CRITIQUE
```

---

## P1 — BACKEND

### P1.1 — Requêtes N+1

| Endpoint / Méthode | Statut | Détail |
|--------------------|--------|--------|
| `get_catalogue` | ✅ OK | Une requête SELECT + une COUNT(*) séparée (pas de boucle) |
| `compare_prices_with_history` | ✅ OK | Batch-load : 1 query produits + 1 query prix_historique WHERE produit_id = ANY($1) — N+1 évité |
| `upsert_products_batch` | ✅ OK | Boucle dans une transaction unique, pas de N+1 par requête HTTP |
| `get_stats` | ✅ OK | 2 requêtes (stats + familles) — acceptable, pas de boucle |
| `get_factures_history` | ✅ OK | Une seule requête |

**Conclusion** : Pas de N+1 critique. `compare_prices_with_history` a été corrigé en batch-load.

---

### P1.2 — Index DB

| Table | Index | Colonnes | Statut |
|-------|-------|----------|--------|
| produits | idx_produits_famille | famille | ✅ |
| produits | idx_produits_fournisseur | fournisseur | ✅ |
| produits | idx_produits_updated | updated_at DESC | ✅ |
| produits | idx_trgm_raw | designation_raw (GIN pg_trgm) | ✅ |
| produits | idx_trgm_fr | designation_fr (GIN pg_trgm) | ✅ |
| produits | idx_produits_search_combined | concat designation_raw/fr/fournisseur | ✅ |
| produits | idx_produits_user_id | user_id | ✅ |
| produits | idx_produits_user_famille | user_id, famille | ✅ |
| produits | idx_produits_user_fournisseur | user_id, fournisseur | ✅ |
| factures | idx_factures_user_id | user_id | ✅ |
| factures | idx_factures_user_date | user_id, created_at DESC | ✅ |
| jobs | idx_jobs_created | created_at DESC | ✅ |
| jobs | idx_jobs_user_id | user_id | ✅ |
| prix_historique | idx_prixhist_produit | produit_id, recorded_at DESC | ✅ |

**Conclusion** : Indexation complète. Colonnes filtrées/triées couvertes.

---

### P1.3 — Pagination

| Endpoint | Pagination | Limite | Statut |
|----------|------------|--------|--------|
| GET /api/v1/catalogue | Cursor-based | limit ≤ 200 | ✅ |
| GET /api/v1/history | LIMIT | limit ≤ 200 | ✅ |
| GET /api/v1/catalogue/fournisseurs | Aucune | — | 🟠 |
| GET /api/v1/export/my-data | Aucune | Tout en mémoire | 🟠 |
| GET /api/v1/stats | N/A | Agrégation | ✅ |

**Conclusion** : Catalogue et history paginés. Fournisseurs et export sans limite.

---

### P1.4 — Timeout

| Composant | Timeout | Statut |
|-----------|---------|--------|
| asyncpg pool | command_timeout=30 | ✅ |
| Gemini API (google-genai) | Aucun explicite | 🟠 |
| boto3 S3 (StorageService) | Aucun explicite | 🟠 |
| httpx (tests) | 30s | ✅ |

**Conclusion** : DB pool OK. Appels externes (Gemini, S3) sans timeout explicite → risque de blocage.

---

### P1.5 — Cache

| Donnée | Cache | Statut |
|--------|-------|--------|
| GeminiService | Par model_id (singleton) | ✅ |
| Catalogue | Aucun | ⚪ |
| Fournisseurs | Aucun | ⚪ |
| Stats | Aucun | ⚪ |

**Conclusion** : Pas de cache applicatif pour données fréquentes (catalogue, fournisseurs, stats). Acceptable pour usage actuel, à envisager si trafic augmente.

---

### P1.6 — Pool connexions

```python
# backend/core/db_manager.py
cls._pool = await asyncpg.create_pool(
    Config.DATABASE_URL,
    min_size=2,
    max_size=10,
    command_timeout=30,
    ssl="require",
)
```

| Paramètre | Valeur | Statut |
|-----------|--------|--------|
| min_size | 2 | ✅ |
| max_size | 10 | ✅ |
| command_timeout | 30s | ✅ |
| ssl | require | ✅ |

**Conclusion** : Pool asyncpg correctement configuré. Compatible Neon avec URL -pooler.

---

## P2 — FRONTEND

### P2.1 — Bundle size

Build exécuté : `npm run build` (docling-pwa)

| Chunk | Taille (min) | Gzip | Objectif <500 KB | Statut |
|-------|--------------|------|------------------|--------|
| excel-gen-PD3EehxT.js | 938.17 kB | 270.83 kB | ❌ | 🟠 CRITIQUE |
| pdf-gen-BvX6gh7q.js | 421.59 kB | 138.39 kB | ✅ | ⚠️ |
| charts-sJSE7_xt.js | 328.40 kB | 98.84 kB | ✅ | ⚠️ |
| index-DQSa_Mvc.js | 231.07 kB | 71.75 kB | ✅ | ⚪ |
| html2canvas.esm | 201.42 kB | 48.03 kB | ✅ | ⚪ |
| index.es (Sentry) | 150.51 kB | 51.46 kB | ✅ | ⚪ |
| ui-motion (framer+lucide) | 146.37 kB | 46.01 kB | ✅ | ⚪ |
| dropzone | 61.37 kB | 17.26 kB | ✅ | ⚪ |
| router | 48.83 kB | 17.09 kB | ✅ | ⚪ |
| CataloguePage | 37.61 kB | 11.52 kB | ✅ | ⚪ |
| apiClient | 37.53 kB | 15.06 kB | ✅ | ⚪ |

**Conclusion** : excel-gen > 500 KB (objectif). pdf-gen et charts proches. Chunks lourds déjà en manualChunks (code-split), mais excel-gen chargé dès CataloguePage (export Excel).

---

### P2.2 — Lazy loading

| Composant | React.lazy | Suspense | Statut |
|-----------|------------|----------|--------|
| ScanPage | ✅ | ✅ | ✅ |
| ValidationPage | ✅ | ✅ | ✅ |
| CataloguePage | ✅ | ✅ | ✅ |
| HistoryPage | ✅ | ✅ | ✅ |
| SettingsPage | ✅ | ✅ | ✅ |
| DevisPage | ✅ | ✅ | ✅ |
| LoginPage | ✅ | ✅ | ✅ |
| RegisterPage | ✅ | ✅ | ✅ |

**Conclusion** : Toutes les pages en lazy + Suspense avec PageLoader. Pas de chargement synchrone des routes lourdes.

---

### P2.3 — Re-renders (useMemo / useCallback)

| Page / Composant | useMemo | useCallback | Statut |
|------------------|---------|-------------|--------|
| CataloguePage | filtered, virtualizer deps | fetchCatalogue, loadMore | ✅ |
| CompareModal | chartData | doSearch, handleInputChange | ✅ |
| DevisPage | filtered | fetchProducts | ✅ |
| LoginPage | — | handleSubmit | ✅ |
| RegisterPage | — | handleSubmit | ✅ |

**Conclusion** : useMemo/useCallback utilisés sur les props/state coûteux (filtrage, callbacks API).

---

### P2.4 — Images

| Usage | Lazy load | Dimensions | Statut |
|-------|-----------|------------|--------|
| Icons (lucide-react) | N/A (SVG) | — | ✅ |
| PWA icons | — | 192x192, 512x512 | ✅ |
| Pas d'images lourdes dans l'app | — | — | ⚪ |

**Conclusion** : Pas d'images volumineuses. Icons SVG légers.

---

### P2.5 — Virtualisation

| Page | Liste | Virtualisation | Statut |
|------|-------|----------------|--------|
| CataloguePage | Produits (table + cards) | @tanstack/react-virtual | ✅ |
| HistoryPage | Historique factures | Aucune (limit 50) | ⚪ |
| DevisPage | Produits devis | Aucune | ⚪ |

**Conclusion** : CataloguePage virtualise correctement. History limité à 50 → pas critique. DevisPage : liste généralement courte.

---

## P3 — FINDINGS [P-001] à [P-XXX]

| ID | Sévérité | Domaine | Description |
|----|----------|---------|-------------|
| [P-001] | 🟠 CRITIQUE | Backend | Gemini API sans timeout explicite — risque de blocage si API lente |
| [P-002] | 🟠 CRITIQUE | Backend | COUNT(*) sur produits à chaque requête catalogue — lent sur grosses tables (>10k lignes) |
| [P-003] | 🟠 | Backend | get_fournisseurs sans pagination — peut retourner des milliers de lignes |
| [P-004] | 🟠 | Backend | export_my_data charge tout en mémoire — risque OOM pour utilisateurs avec gros catalogue |
| [P-005] | 🟠 CRITIQUE | Frontend | Chunk excel-gen 938 kB (>500 KB) — chargé avec CataloguePage |
| [P-006] | ⚠️ | Frontend | Chunk pdf-gen 421 kB — acceptable mais lourd |
| [P-007] | ⚠️ | Frontend | Chunk charts 328 kB — chargé avec DevisPage/Settings |
| [P-008] | ⚠️ | Backend | StorageService boto3 sans timeout — risque blocage upload/download |
| [P-009] | ⚪ | Backend | Pas de cache applicatif catalogue/fournisseurs — acceptable pour trafic actuel |
| [P-010] | ✅ | Backend | compare_prices_with_history : N+1 corrigé par batch-load |
| [P-011] | ✅ | Backend | Pool asyncpg min 2 / max 10, command_timeout 30s |
| [P-012] | ✅ | Backend | Index DB complets (famille, fournisseur, user_id, pg_trgm, etc.) |
| [P-013] | ✅ | Frontend | Lazy loading routes + Suspense |
| [P-014] | ✅ | Frontend | Virtualisation CataloguePage (@tanstack/react-virtual) |
| [P-015] | ✅ | Frontend | useMemo/useCallback sur CataloguePage, CompareModal, DevisPage |

---

## P4 — COMMANDES DE VÉRIFICATION

```bash
# Bundle size (frontend)
cd docling-pwa && npm run build
# Vérifier les warnings chunkSizeWarningLimit et les tailles dist/assets/*.js

# Analyse bundle détaillée (optionnel)
npx vite-bundle-visualizer  # si installé

# Backend — health + perf DB
curl -s http://localhost:8000/health

# Tests performance (optionnel)
pytest backend/tests/ -k "perf" -v  # si tests perf existants
```

---

## P5 — RECOMMANDATIONS

### Priorité haute
1. **[P-001]** Ajouter timeout explicite sur appels Gemini (ex. 60–120s via config google-genai)
2. **[P-002]** Remplacer COUNT(*) par estimation (pg_stat ou COUNT(*) avec index) ou cache court (ex. 30s) pour total catalogue
3. **[P-005]** Lazy-load excel-gen : `const exportExcel = () => import('./utils/excelExport').then(m => m.exportExcel(data))` — charger uniquement au clic Export Excel

### Priorité moyenne
4. **[P-003]** Limiter get_fournisseurs (ex. LIMIT 500) ou pagination
5. **[P-004]** Paginer export_my_data ou streamer le JSON
6. **[P-008]** Configurer timeout boto3 (connect_timeout, read_timeout)

### Priorité basse
7. **[P-009]** Cache court (30–60s) pour catalogue/fournisseurs si trafic augmente
8. **[P-006][P-007]** Envisager lazy-load charts/pdf-gen si pages Devis/Settings deviennent lentes

---

## P6 — GATE P

```
Critères :
- Au moins un 🟠 CRITIQUE non résolu → FAIL
- Tous les 🟠 CRITIQUE résolus ou mitigés → PASS
```

**État actuel** :
- [P-001] Gemini sans timeout — CRITIQUE
- [P-002] COUNT(*) catalogue — CRITIQUE
- [P-005] excel-gen > 500 KB — CRITIQUE

---

## GATE P : **FAIL**

---

*Phase 09 — Audit Performance — Docling Agent v3 — 2026-02-28*
