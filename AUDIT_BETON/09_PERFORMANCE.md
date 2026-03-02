# ⚡ 09 — AUDIT PERFORMANCE
# Backend · Frontend · Bundle · Requêtes DB · Re-renders
# Exécuté le 1er mars 2026 — Phase 09 Audit Bêton Docling
# Agent : context-specialist

---

## VÉRIFICATIONS (1er mars 2026)

| Critère | Statut |
|---------|--------|
| N+1 get_catalogue | ✅ OK |
| N+1 insert_anonymous_price | 🟠 À batchifier |
| Lazy loading pages | ✅ React.lazy |
| @tanstack/react-virtual | ✅ CataloguePage |
| Index DB | ✅ Complets |

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

## SYNTHÈSE DES AUDITS 03–08 (ASPECTS PERFORMANCE)

### Backend (03_BACKEND, 05_BASE_DE_DONNEES)

| Aspect | Audit 03 | Audit 05 | Synthèse |
|--------|----------|----------|----------|
| **db_manager** | Pas de N+1 sur get_catalogue, compare_prices_with_history batch | get_user_export_data sans LIMIT | D-003 : export charge tout en mémoire |
| **orchestrator** | B-007 : N+1 insert_anonymous_price (boucle for) | — | Une requête par produit communautaire |
| **api** | get_catalogue limit≤200, get_history limit≤200 | — | Pagination OK |
| **Pool asyncpg** | — | min 2, max 10, command_timeout | Config.DB_COMMAND_TIMEOUT=60s |
| **Index DB** | — | idx_produits_*, idx_jobs_user_id, pg_trgm | Couverture complète |
| **Gemini** | Timeout Config.GEMINI_TIMEOUT_MS | — | ✅ 180000 ms (3 min) dans gemini_service |

### Frontend (04_FRONTEND, 08_BUILD)

| Aspect | Audit 04 | Audit 08 | Synthèse |
|--------|----------|----------|----------|
| **Lazy loading** | Toutes pages React.lazy + Suspense | — | ✅ |
| **Virtualisation** | CataloguePage @tanstack/react-virtual | — | ✅ |
| **useMemo/useCallback** | CataloguePage, CompareModal, DevisPage | — | ✅ |
| **Bundle** | — | excel-gen 938 kB, pdf-gen 421 kB, charts 328 kB | Chunks >500 KB |
| **Excel import** | — | CataloguePage import statique exceljs | Chargé avec page catalogue |

### Sécurité (06_SECURITE) — impact perf

- Rate limit /process 20/min, circuit breaker Gemini, sémaphore extraction (3) → évite surcharge.

---

## P1 — BACKEND

### P1.1 — Requêtes N+1

| Endpoint / Méthode | Statut | Détail |
|--------------------|--------|--------|
| `get_catalogue` | ✅ OK | 1 SELECT + 1 COUNT(*) — pas de boucle |
| `compare_prices_with_history` | ✅ OK | Batch-load WHERE produit_id = ANY($1) |
| `upsert_products_batch` | ✅ OK | Transaction unique, pas de N+1 |
| `get_stats`, `get_factures_history` | ✅ OK | Requêtes agrégées |
| **orchestrator insert_anonymous_price** | 🟠 N+1 | Boucle `for p in products_dicts` → N requêtes (l.127-136) |

**Conclusion** : N+1 restant dans base prix communautaire. Batch `INSERT ... VALUES ($1,$2,...), ($3,$4,...)` recommandé.

---

### P1.2 — Index DB

| Table | Index | Colonnes | Statut |
|-------|-------|----------|--------|
| produits | idx_produits_user_id | user_id | ✅ |
| produits | idx_produits_famille | famille | ✅ |
| produits | idx_produits_fournisseur | fournisseur | ✅ |
| produits | idx_produits_user_famille | user_id, famille | ✅ |
| produits | idx_produits_user_fournisseur | user_id, fournisseur | ✅ |
| produits | idx_trgm_raw, idx_trgm_fr | designation (GIN pg_trgm) | ✅ |
| jobs | idx_jobs_created, idx_jobs_user_id | created_at, user_id | ✅ |
| factures | idx_factures_user_id, idx_factures_user_date | user_id, created_at | ✅ |
| prix_historique | idx_prixhist_produit | produit_id, recorded_at | ✅ |
| prix_anonymes | idx_prix_anonymes_hash_zone, idx_prix_anonymes_fournisseur | produit_hash, zone_geo, fournisseur | ✅ |

**Conclusion** : Indexation complète (Audit 05 D3). Colonnes filtrées/triées couvertes.

---

### P1.3 — Pagination

| Endpoint | Pagination | Limite | Statut |
|----------|------------|--------|--------|
| GET /api/v1/catalogue | Cursor-based | limit ≤ 200 | ✅ |
| GET /api/v1/history | LIMIT | limit ≤ 200 | ✅ |
| GET /api/v1/catalogue/fournisseurs | Aucune | — | 🟠 |
| GET /api/v1/export/my-data | Aucune | Tout en mémoire | 🟠 |
| GET /api/v1/stats | N/A | Agrégation | ✅ |

**Conclusion** : Catalogue et history paginés. Fournisseurs et export sans limite (D-003).

---

### P1.4 — Timeout

| Composant | Timeout | Source | Statut |
|-----------|---------|--------|--------|
| asyncpg pool | 60s | Config.DB_COMMAND_TIMEOUT | ✅ |
| Gemini API | 180000 ms (3 min) | Config.GEMINI_TIMEOUT_MS, gemini_service:136 | ✅ |
| boto3 S3 (StorageService) | Aucun | put_object sans Config | 🟠 |
| httpx (apiClient) | 120s | apiClient.js | ✅ |

**Conclusion** : Gemini a un timeout explicite (correction depuis audit précédent). S3 sans timeout → risque blocage upload.

---

### P1.5 — Cache

| Donnée | Cache | Statut |
|--------|-------|--------|
| GeminiService | Par model_id (singleton) | ✅ |
| Catalogue, fournisseurs, stats | Aucun | ⚪ Acceptable trafic actuel |

---

### P1.6 — Pool connexions

```python
# backend/core/db_manager.py:136-143
cls._pool = await asyncpg.create_pool(
    Config.DATABASE_URL,
    min_size=2,
    max_size=10,
    command_timeout=Config.DB_COMMAND_TIMEOUT,  # 60s
    ssl="require",
)
```

| Paramètre | Valeur | Statut |
|-----------|--------|--------|
| min_size | 2 | ✅ |
| max_size | 10 | ✅ |
| command_timeout | 60s | ✅ |
| ssl | require | ✅ |

**Conclusion** : Pool asyncpg correctement configuré. Compatible Neon -pooler.

---

## P2 — FRONTEND

### P2.1 — Bundle size

**Build exécuté** : `npm run build` (docling-pwa) — dist/assets mesurés le 1er mars 2026.

| Chunk | Taille (min) | Gzip estimé | Objectif <500 KB | Statut |
|-------|--------------|-------------|------------------|--------|
| react-spline | **2005 kB** | ~600 kB | ❌ | 🟠 CRITIQUE |
| physics | **1941 kB** | ~580 kB | ❌ | 🟠 CRITIQUE |
| excel-gen | **917 kB** | ~270 kB | ❌ | 🟠 CRITIQUE |
| pdf-gen | 412 kB | ~138 kB | ✅ | ⚠️ |
| charts | 321 kB | ~98 kB | ✅ | ⚠️ |
| index | 230 kB | ~71 kB | ✅ | ⚪ |
| html2canvas | 198 kB | ~48 kB | ✅ | ⚪ |
| opentype | 169 kB | — | ✅ | ⚪ |
| index.es (Sentry) | 147 kB | ~51 kB | ✅ | ⚪ |
| ui-motion | 143 kB | ~46 kB | ✅ | ⚪ |
| CataloguePage | 37 kB | ~11 kB | ✅ | ⚪ |

**Conclusion** :
- **Spline 3D** : react-spline + physics ≈ 4 MB — chargé en lazy via SplineScene (ScanPage, ValidationPage, SettingsPage, DevisPage). Impact : première visite /scan ou /devis charge ~4 MB.
- **excel-gen** : 917 kB — import statique dans CataloguePage (`import ExcelJS from 'exceljs'`). Chargé dès ouverture catalogue, pas au clic Export.
- Objectif <500 KB gzippé : excel-gen, react-spline, physics dépassent.

---

### P2.2 — Lazy loading

| Composant | React.lazy | Suspense | Statut |
|-----------|------------|----------|--------|
| ScanPage, ValidationPage, CataloguePage, etc. | ✅ | ✅ PageLoader | ✅ |
| SplineScene | ✅ | `lazy(() => import('@splinetool/react-spline'))` | ✅ |
| exceljs | ❌ | Import statique dans CataloguePage | 🟠 |

**Conclusion** : Routes lazy. ExcelJS chargé avec CataloguePage au lieu d’un dynamic import au clic Export.

---

### P2.3 — Re-renders (useMemo / useCallback)

| Page / Composant | useMemo | useCallback | Statut |
|------------------|---------|-------------|--------|
| CataloguePage | filtered, virtualizer deps | fetchCatalogue, loadMore | ✅ |
| CompareModal | chartData | doSearch, handleInputChange | ✅ |
| DevisPage | filtered | fetchProducts | ✅ |

**Conclusion** : useMemo/useCallback utilisés sur props/state coûteux.

---

### P2.4 — Images

| Usage | Lazy load | Dimensions | Statut |
|-------|-----------|------------|--------|
| Icons (lucide-react) | N/A (SVG) | — | ✅ |
| PWA icons | — | 192x192, 512x512 | ✅ |

**Conclusion** : Pas d’images lourdes.

---

### P2.5 — Virtualisation

| Page | Liste | Virtualisation | Statut |
|------|-------|----------------|--------|
| CataloguePage | Produits (table + cards) | @tanstack/react-virtual | ✅ |
| HistoryPage | Historique factures | Aucune (limit 50) | ⚪ |
| DevisPage | Produits devis | Aucune | ⚪ |

**Conclusion** : CataloguePage virtualise. History limité à 50 → acceptable.

---

## P3 — FINDINGS [P-001] À [P-XXX]

| ID | Sévérité | Domaine | Description |
|----|----------|---------|-------------|
| [P-001] | 🟠 | Backend | N+1 insert_anonymous_price — N requêtes pour N produits (orchestrator:127-136) |
| [P-002] | 🟡 | Backend | COUNT(*) catalogue à chaque requête — lent sur >10k lignes (db_manager:332) |
| [P-003] | 🟠 | Backend | get_fournisseurs sans pagination — peut retourner des milliers de lignes |
| [P-004] | 🟠 | Backend | export_my_data charge tout en mémoire — risque OOM (D-003) |
| [P-005] | 🟠 | Backend | StorageService boto3 sans timeout — risque blocage upload |
| [P-006] | 🟠 | Frontend | excel-gen 917 kB — import statique, chargé avec CataloguePage |
| [P-007] | 🟠 | Frontend | Spline 3D ~4 MB (react-spline + physics) — chargé sur /scan, /validation, /settings, /devis |
| [P-008] | ⚪ | Frontend | pdf-gen 412 kB, charts 321 kB — acceptable, déjà en manualChunks |
| [P-009] | ✅ | Backend | Gemini timeout Config.GEMINI_TIMEOUT_MS (3 min) |
| [P-010] | ✅ | Backend | Pool asyncpg min 2 / max 10, command_timeout 60s |
| [P-011] | ✅ | Backend | Index DB complets |
| [P-012] | ✅ | Frontend | Lazy loading routes + Suspense |
| [P-013] | ✅ | Frontend | Virtualisation CataloguePage |
| [P-014] | ✅ | Frontend | useMemo/useCallback sur CataloguePage, CompareModal, DevisPage |

---

## P4 — COMMANDES DE VÉRIFICATION

```bash
# Bundle size (frontend)
cd docling-pwa && npm run build
# Vérifier dist/assets/*.js — tailles avec :
# PowerShell: Get-ChildItem dist/assets/*.js | Sort-Object Length -Descending | Select Name, @{N='KB';E={[math]::Round($_.Length/1KB,2)}}

# Analyse bundle détaillée (optionnel)
npx vite-bundle-visualizer  # si installé

# Backend — health
curl -s http://localhost:8000/health

# Tests performance (si existants)
pytest tests/06_performance/ -v
```

---

## P5 — RECOMMANDATIONS

### Priorité haute
1. **[P-006]** Lazy-load exceljs : `const exportExcel = async (data) => { const ExcelJS = (await import('exceljs')).default; ... }` — charger uniquement au clic Export Excel.
2. **[P-001]** Batch insert_anonymous_price : une requête `INSERT ... VALUES (...), (...), ...` au lieu de N requêtes.
3. **[P-005]** Configurer timeout boto3 : `Config=botocore.config.Config(connect_timeout=30, read_timeout=60)` dans `_get_client()`.

### Priorité moyenne
4. **[P-003]** Limiter get_fournisseurs (ex. LIMIT 500) ou pagination.
5. **[P-004]** Paginer export_my_data ou streamer le JSON (LIMIT 50000).
6. **[P-002]** Remplacer COUNT(*) par estimation (pg_stat) ou cache court (30s) pour total catalogue.
7. **[P-007]** Envisager Spline conditionnel (feature flag) ou scène allégée pour mobile.

### Priorité basse
8. Cache court (30–60s) pour catalogue/fournisseurs si trafic augmente.

---

## P6 — GATE P

```
Critères :
- Au moins un 🟠 CRITIQUE non résolu → FAIL
- Tous les 🟠 CRITIQUE résolus ou mitigés → PASS
```

**État actuel** :
- [P-001] N+1 insert_anonymous_price — 🟠
- [P-003] get_fournisseurs sans pagination — 🟠
- [P-004] export_my_data sans LIMIT — 🟠
- [P-005] StorageService sans timeout — 🟠
- [P-006] excel-gen import statique — 🟠
- [P-007] Spline ~4 MB — 🟠

---

## GATE P : **FAIL**

---

*Phase 09 — Audit Performance — Docling — 1er mars 2026 — Synthèse audits 03-08*
