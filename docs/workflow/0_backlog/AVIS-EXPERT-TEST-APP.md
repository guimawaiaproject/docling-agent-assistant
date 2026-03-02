# Avis d'expert — Test applicatif Docling

**Date** : 2026-02-28  
**Contexte** : QA/DevOps — démarrage, tests API, vérification structure frontend

---

## 1. Résumé des tests

### 1.1 Démarrage

| Composant | Statut | Détails |
|-----------|--------|---------|
| Backend (uvicorn) | OK | Port 8000, health /health répond |
| Base de données | OK | status: ok, db: connected, ersion: 3.0.0 |
| Frontend (Vite) | OK | Port 5174 (5173 occupé), prêt en ~2 s |

### 1.2 Endpoints API testés

| Endpoint | Statut | Temps réponse | Remarque |
|----------|--------|---------------|----------|
| GET /health | 200 | < 1 s | OK |
| GET /api/v1/catalogue | 200 | **~3,1 s** | Lent pour 7 produits |
| GET /api/v1/history | 200 | ~7 s | 4 factures, 1 en erreur |
| GET /api/v1/stats | 200 | ~7 s | OK |

### 1.3 Frontend

- **URL** : https://localhost:5174/
- **Statut** : 200, HTML servi (SPA)
- **CORS** : OK (requêtes cross-origin acceptées)
- **Config** : VITE_AUTH_REQUIRED=false, VITE_API_URL=http://localhost:8000

### 1.4 Structure des routes (App.jsx)

| Route | Page | Navbar |
|-------|------|--------|
| / | Redirect → /scan | — |
| /scan | ScanPage | Scanner |
| /catalogue | CataloguePage | Catalogue |
| /devis | DevisPage | Devis |
| /history | HistoryPage | Historique |
| /settings | SettingsPage | Règlages |
| /validation | ValidationPage | — |

### 1.5 Fonctionnalités Scan (analyse code)

- Dropzone (react-dropzone) : data-testid="scan-dropzone"
- Upload direct ou file picker
- File d'attente batch, compression WebP pour images
- Mode hors ligne : offlineQueue, nqueueUpload, getPendingUploads
- Caméra + overlay pour analyse IA
- Choix modèle IA (Gemini)

---

## 2. Points forts

1. **Stack cohérente** : FastAPI, React 19, Vite, Tailwind, Zustand
2. **Health check** fiable et base connectée
3. **PWA** avec support offline (OfflineBanner, offlineQueue)
4. **CORS** correctement configuré pour dev
5. **Accès dev sans login** : FREE_ACCESS_MODE + VITE_AUTH_REQUIRED=false
6. **Lazy loading** des pages (Suspense + PageLoader)
7. **Navbar** fixe en bas, indicateur hors ligne

---

## 3. Points faibles et risques

| Priorité | Problème | Impact |
|----------|----------|--------|
| P1 | **Catalogue API ~3 s** pour 7 produits | UX dégradée, impression de lenteur |
| P2 | Historique : 1 facture en statut rreur | À investiguer (FONTFREDA C52300306) |
| P2 | Pas de tests E2E navigateur exécutés | Validation UX limitée à l’analyse de code |
| P3 | Port 5173 déjà utilisé → 5174 | Risque de confusion si doc référence 5173 |

---

## 4. Recommandations

1. **Performance catalogue** : Profiler la requête /api/v1/catalogue (index DB, N+1, cold start).
2. **Tests E2E** : Ajouter Playwright ou Cypress pour valider flux Scan → Catalogue → Historique en conditions réelles.
3. **Erreur FONTFREDA** : Consulter les logs backend et le statut Gemini pour cette facture.
4. **Documentation** : Mettre à jour la doc si le port frontend par défaut change (5173 vs 5174).

---

## 5. Périmètre des tests

- **Effectués** : Démarrage serveurs, health check, appels API (PowerShell), analyse du code source (routes, Navbar, ScanPage).
- **Non effectués** : Navigation réelle dans un navigateur, upload de fichier, interactions UI (clics, formulaires), tests visuels.

---

*Rapport généré dans le cadre d’une mission QA/DevOps. Pour une validation UX complète, exécuter des tests E2E avec un outil de type Playwright.*
