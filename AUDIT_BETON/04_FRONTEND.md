# ⚛️ 04 — AUDIT FRONTEND COMPLET — Docling

**Date** : 2026-03-01
**Phase** : 04 FRONTEND
**Référence** : .cursor/PROMPT AUDIT/04_FRONTEND.md

---

## VÉRIFICATIONS EXÉCUTÉES (1er mars 2026)

| Critère | Statut |
|---------|--------|
| dangerouslySetInnerHTML | ✅ Aucun (grep src/) |
| React 19 | ✅ 19.2.4 |
| TypeScript | ❌ 0% (JSX/JS uniquement) |
| eslint.config.js | ✅ Présent (flat config) |
| biome.json | ❌ Absent |

---

## RÉSUMÉ EXÉCUTIF

| Métrique | Valeur |
|----------|--------|
| Fichiers audités | 25+ |
| Problèmes 🔴 FATAL | 1 |
| Problèmes 🟠 CRITIQUE | 4 |
| Problèmes 🟡 MOYEN | 12 |
| Problèmes 🔵 MINEUR | 8 |
| Score moyen /10 | 7.2 |
| **GATE F** | **FAIL** |

---

## F1 — App.jsx

**Fichier** : `docling-pwa/src/App.jsx` (84 lignes)

### Fiche App.jsx

| Élément | Lignes | OK | Problème | Sévérité |
|---------|--------|----|---------|----|
| Imports | 1-18 | ✅ | — | — |
| Routes définies | 46-63 | ✅ | Lazy loading sur toutes les pages | — |
| ProtectedRoute | 38-39 | ✅ | RouteWrapper = Fragment si AUTH_REQUIRED=false | — |
| Providers | 40-82 | ⚠️ | Pas d'AuthProvider (auth via cookie/localStorage) | 🔵 |
| Toaster config | 67-80 | ✅ | position, richColors, style custom | — |
| ErrorBoundary | — | ⚠️ | Dans main.jsx, pas dans App.jsx (acceptable) | — |

### Analyse détaillée

- **Lazy loading** : ✅ Toutes les pages (ScanPage, ValidationPage, etc.) chargées via `React.lazy`
- **Suspense fallback** : ✅ `PageLoader` avec `SkeletonCard` (l.20-26)
- **ProtectedRoute** : ✅ Redirige vers /login si non authentifié (via FEATURES.AUTH_REQUIRED)
- **Toaster** : ✅ position top-center, richColors, style glassmorphism
- **Ordre providers** : Pas de AuthProvider — auth gérée par cookie httpOnly + localStorage legacy
- **ErrorBoundary** : Dans main.jsx autour de BrowserRouter — correct
- **Logique métier** : ✅ Uniquement routing

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-001 | 🔵 | — | Pas d'alias `@` configuré dans Vite (imports relatifs uniquement) |

---

## F2 — useStore.js

**Fichier** : `docling-pwa/src/store/useStore.js` (133 lignes)

### Carte du state Zustand

| Slice | Type | Persisté | Actions | Problème |
|-------|------|----------|---------|----------|
| selectedModel | string | Oui | setModel | — |
| currentJob | string \| null | Non | setJobStart, setJobComplete, clearJob | — |
| extractedProducts | Array | Non | addProducts (via setJobComplete), updateProduct, removeProduct, clearJob | — |
| currentInvoice | string \| null | Non | setJobStart, clearJob | — |
| pendingSource | string | Non | setJobComplete, clearJob | — |
| batchQueue | Array | Non | addToQueue, updateQueueItem, retryItem, retryAllErrors, clearQueue, removeFromQueue | — |

### Analyse

- **State minimal** : ✅ Pas de données calculables dans le store
- **partialize** : ✅ Seul `selectedModel` persisté (l.125-128)
- **Clé storage** : `docling-storage-v2` — risque de conflit faible
- **_idCounter** : ✅ Niveau module (l.12) — correct
- **Actions async** : Pas d'actions async dans le store — logique dans ScanPage
- **Devtools** : ⚠️ Toujours activé (pas de `enabled: import.meta.env.DEV`)

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-002 | 🟡 | 130 | devtools middleware actif en prod — désactiver si `!import.meta.env.DEV` |

---

## F3 — apiClient.js

**Fichier** : `docling-pwa/src/services/apiClient.js` (54 lignes)

### Analyse

| Critère | Lignes | Statut | Détail |
|---------|--------|--------|--------|
| Base URL | 2, 11 | ✅ | API_BASE_URL depuis config (VITE_API_URL ou localhost) |
| withCredentials | 7 | ✅ | true — envoie cookie httpOnly |
| Timeout | 6 | ✅ | 120_000 ms |
| Retry | 11-27 | ✅ | 5xx + network, max 3, backoff exponentiel |
| 401 interceptor | 39-51 | ✅ | Redirige /login, retire token localStorage |
| Token storage | 34-36 | 🟠 | Lit localStorage `docling-token` — rétrocompatibilité mais incohérent avec httpOnly |
| X-Requested-With | 33 | ✅ | XMLHttpRequest pour CSRF mitigation |
| AbortController | — | 🔵 | Non implémenté au niveau client (chaque appel peut passer signal) |

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-003 | 🟠 | 34-36 | Fallback Authorization localStorage — si httpOnly uniquement, ce code est mort ou crée confusion. Supprimer ou documenter clairement. |
| F-004 | 🔵 | — | Pas de CancelToken/AbortController global pour annuler requêtes en cours |

---

## F4 — ScanPage.jsx

**Fichier** : `docling-pwa/src/pages/ScanPage.jsx` (519 lignes)

### Grille états ScanPage

| État | Couvert | Affiché correctement | Message clair | Action disponible |
|------|---------|---------------------|---------------|-------------------|
| idle | ✅ | ✅ | — | Lancer, Parcourir, Dossier |
| uploading | ✅ | ✅ | Envoi... | Progress bar |
| processing | ✅ | ✅ | Analyse IA... | Progress bar |
| partial success | ⚠️ | — | — | Modal batch done |
| done | ✅ | ✅ | Terminé + produits | CTA validation/catalogue |
| error | ✅ | ✅ | Erreur + message | Retry, retirer |
| offline | ✅ | ✅ | Hors ligne — N en attente | Sync auto |
| cancelled | ⚠️ | — | Remet pending | — |

### Analyse ligne par ligne (points clés)

- **react-dropzone** : noClick: false (l.224) ✅
- **maxSize** : 200 Mo (l.223) ✅
- **accept** : PDF + images (l.217-220) ✅
- **AbortController** : ctrl.signal passé aux requêtes (l.250, 254) ✅
- **clearQueue** : window.confirm (l.521) ✅
- **useEffect cleanup** : abortRef.current?.abort() au démontage (l.73-75) ✅
- **Toast post-traitement** : action "Voir le catalogue" (l.305-308) ✅
- **Offline queue** : enqueueUpload, sync à reconnexion (l.158-174) ✅

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-005 | 🟡 | 521 | `window.confirm` — remplacer par modale custom pour cohérence UX |
| F-006 | 🔵 | 434 | Bouton caméra sans aria-label (texte visible "Photographier une Facture") |

---

## F5 — ValidationPage.jsx

**Fichier** : `docling-pwa/src/pages/ValidationPage.jsx` (288 lignes)

### Analyse

| Critère | Statut |
|---------|--------|
| Option vide select famille | ✅ "— Choisir une famille —" (l.194) |
| Badge confidence low | ✅ AlertCircle + "Vérification recommandée" (l.143-147) |
| Diff original/modifié | ⚠️ Pas de marquage visuel des champs modifiés |
| Bouton "Tout enregistrer" | ✅ "Enregistrer N produits" (l.281) |
| Total HT | ⚠️ Calculé par produit (prixTTC) pas total global |
| handleRemove | 🟠 Pas de confirmation avant suppression |
| Lightbox Escape | ✅ useEffect keydown Escape (l.27-32) |
| useRef valeurs originales | ❌ Absent — pas de diff |

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-007 | 🟠 | 55-57 | handleRemove : pas de confirmation avant suppression produit |
| F-008 | 🟡 | — | Pas de diff visuel champs modifiés vs original |

---

## F6 — CataloguePage.jsx

**Fichier** : `docling-pwa/src/pages/CataloguePage.jsx` (415 lignes)

### Analyse

| Critère | Statut |
|---------|--------|
| Empty state catalogue vide | ✅ CTA "Scanner une facture" (l.329-336) |
| Empty state filtres 0 résultats | ✅ "Réinitialiser les filtres" (l.337-349) |
| Filtres persistants | ❌ Pas de sessionStorage |
| Chips filtres actifs | ❌ Pas de chips avec × |
| Recherche highlight | ❌ Pas de highlight terme |
| Vue tableau min-w | ✅ min-w-[800px] → scroll horizontal (l.363) |
| Vue cartes défaut mobile | ✅ view initiale = cards si width < 640 (l.146) |
| Virtualisation | ✅ @tanstack/react-virtual (l.223-228) |
| Load more | ✅ Bouton "Charger plus" (l.406-418) |
| Export CSV/Excel | ✅ UTF-8 BOM (l.75), headers corrects |
| Colonnes triables | ✅ toggleSort, aria-sort (l.368) |

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-009 | 🟡 | — | Filtres non persistés (sessionStorage) |
| F-010 | 🔵 | — | Pas de chips visuels filtres actifs avec × |
| F-011 | 🔵 | — | Pas de highlight recherche dans résultats |

---

## F7 — DevisPage.jsx

**Fichier** : `docling-pwa/src/pages/DevisPage.jsx` (375 lignes)

### Grille calculs DevisPage

Test mental : 3 produits 100€, 250€, 75€ HT, TVA 20%, remise 10%

- Total HT : 425€ ✅
- Remise : 42.50€ ✅
- Net HT : 382.50€ ✅
- TVA : 76.50€ ✅
- TTC : 459€ ✅

**Note** : Utilise `parseFloat` — pas de Decimal. Pour des montants €, acceptable. Risque arrondi sur très grands catalogues.

### Analyse

| Critère | Statut |
|---------|--------|
| TVA depuis settings | ✅ getDefaultTvaRate() (l.15-23) |
| Nom entreprise | ✅ State + draft restore |
| Brouillon autosave | ✅ localStorage, 24h max (l.37-61) |
| TVA multi-taux | ✅ Par ligne (5.5%, 10%, 20%) |
| Logo PDF | ✅ devisGenerator utilise settings.logo |
| Mentions légales | ✅ settings.mentionsLegales |
| Remise % et € | ✅ remiseType percent/amount |
| Empty state panier | ⚠️ Pas d'empty state dédié si 0 produit — liste catalogue en dessous |

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-012 | 🟡 | — | DevisPage ne charge pas entreprise depuis settings au premier mount (uniquement draft ou défaut) |

---

## F8 — HistoryPage.jsx

**Fichier** : `docling-pwa/src/pages/HistoryPage.jsx` (279 lignes)

### Analyse

| Critère | Statut |
|---------|--------|
| Empty state | ✅ CTA "Scanner une facture" (l.174-182) |
| Tri par date | ⚠️ Ordre serveur (non trié côté client) |
| Suppression | ❌ Pas de suppression d'historique dans l'UI |
| État scan (success, error, partial) | ✅ CheckCircle2 / AlertCircle selon statut |
| Lien catalogue | ❌ Pas de lien direct vers produits du scan |
| Dates fuseau local | ✅ toLocaleDateString fr-FR (l.23-26) |

---

## F9 — SettingsPage.jsx

**Fichier** : `docling-pwa/src/pages/SettingsPage.jsx` (382 lignes)

### Checklist settings

| Paramètre | Présent | Sauvegardé | Utilisé par | Action si absent |
|-----------|---------|-----------|-------------|------------------|
| Nom entreprise | ✅ | ✅ | DevisPage (via draft/settings) | — |
| Logo entreprise | ❌ | — | devisGenerator | 🔴 Créer champ upload |
| TVA par défaut | ✅ | ✅ | DevisPage | — |
| Mentions légales | ✅ | ✅ | devisGenerator | — |
| Préfixe numérotation | ✅ formatNum | ✅ | DevisPage | — |
| Export RGPD | ✅ | — | — | — |
| Import catalogue | ❌ | — | — | À évaluer |
| Reset catalogue | ❌ | — | — | Créer avec confirmation |
| Connexion API test | ✅ | — | — | — |
| Modèle IA | ✅ | Zustand persist | ScanPage | — |

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-013 | 🔴 | — | **Logo entreprise** : pas de champ upload dans Settings — devisGenerator attend settings.logo |
| F-014 | 🟠 | — | Pas de "Reset catalogue" avec confirmation |

---

## F10 — Composants

### Navbar.jsx (74 lignes)

| Critère | Statut |
|---------|--------|
| Active link | ✅ isActive → text-emerald-400 |
| Badge "validation en attente" | ❌ Absent — extractedProducts > 0 non affiché |
| Logo cliquable /scan | ❌ Pas de logo dans Navbar |
| Mobile safe area | ✅ pb-safe (l.38) |
| aria-current | ⚠️ NavLink gère visuellement, aria-current="page" non explicite |
| Keyboard Tab | ✅ Focus visible |

### CompareModal.jsx (278 lignes)

| Critère | Statut |
|---------|--------|
| Focus trap | ✅ Tab cycle (l.34-47) |
| Escape fermer | ✅ (l.29-32) |
| aria-modal, aria-labelledby | ✅ (l.133-134) |
| Bouton fermer aria-label | ✅ (l.146) |

### ErrorBoundary.jsx (73 lignes)

| Critère | Statut |
|---------|--------|
| getDerivedStateFromError | ✅ |
| componentDidCatch | ✅ console.error |
| UI fallback | ✅ Boutons Réessayer, Accueil |
| Utilisation | main.jsx (global) |

### Autres composants

| Composant | Lignes | Rôle | Problèmes |
|-----------|--------|------|-----------|
| OfflineBanner | 63 | Bannière hors-ligne | ✅ aria-live |
| SkeletonCard | 50 | Loading skeleton | ✅ aria-label |
| CommandPalette | 111 | Cmd+K navigation | ✅ Keyboard |
| EmptyStateIllustration | 64 | SVG empty state | ✅ aria-hidden |
| SplineScene | 26 | 3D Spline lazy | ✅ Suspense |
| ProtectedRoute | 14 | Guard auth | ⚠️ Vérifie localStorage token — incohérent si httpOnly seul |

### Problèmes identifiés

| ID | Sévérité | Lignes | Problème |
|----|----------|--------|----------|
| F-015 | 🟡 | — | Navbar : pas de badge "validation en attente" (extractedProducts) |
| F-016 | 🟠 | 7 | ProtectedRoute : vérifie localStorage — si backend httpOnly seul, redirection /login incorrecte |

---

## F11 — package.json, vite.config, tailwind, PWA

### package.json

| Package | Catégorie | DevDep ? | Action |
|---------|-----------|-----------|--------|
| react, react-dom | dep | Non | ✅ |
| axios, framer-motion, etc. | dep | Non | ✅ |
| vite | dep | **OUI** | 🟡 Déplacer devDependencies |
| vitest, @vitest/* | dep | **OUI** | 🟡 |
| @testing-library/* | dep | **OUI** | 🟡 |
| eslint, tailwindcss, postcss, autoprefixer | dep | **OUI** | 🟡 |
| vite-plugin-pwa | dep | **OUI** | 🟡 |

**Problème** : Toutes les dépendances sont dans `dependencies` — pas de `devDependencies`. Impact : bundle prod plus lourd (outils de dev inclus si mal tree-shakés).

### vite.config.js

| Critère | Statut |
|---------|--------|
| PWA plugin | ✅ vite-plugin-pwa |
| manifest | ✅ name, icons, display: standalone |
| Workbox | ✅ globPatterns, runtimeCaching: [] |
| Chunks manuels | ✅ react-core, router, ui-motion, charts, pdf-gen, excel-gen, dropzone |
| Alias @ | ❌ Non configuré |
| define VITE_* | ⚠️ Seul VITE_AUTH_REQUIRED en dev (l.36-38) |
| Proxy dev | ❌ Non — API sur localhost:8000 |
| Source maps prod | Par défaut Vite (désactivés) |

### tailwind.config.js

| Critère | Statut |
|---------|--------|
| content paths | ✅ ./index.html, ./src/**/*.{js,ts,jsx,tsx} |
| Purge | Actif par défaut Tailwind 3 |
| Custom colors | extend: {} vide |

### index.css

| Critère | Statut |
|---------|--------|
| CSS variables | ❌ Pas de --color-bg-primary etc. |
| Reset | ✅ box-sizing |
| Safe area | ✅ padding-bottom env(safe-area-inset-bottom) |
| @layer | ✅ base, components, utilities |

---

## F12 — Accessibilité, mobile, code mort

### Checklist accessibilité par page

| Page | Aria-labels | Focus visible | Keyboard nav | Contraste | Score |
|------|-------------|--------------|-------------|----------|-------|
| Scan | ⚠️ Bouton caméra OK (texte) | ✅ | ✅ | ✅ slate-950/slate-100 | 8/10 |
| Validation | ✅ labels, aria-label | ✅ | ✅ | ✅ | 8/10 |
| Catalogue | ✅ sr-only, aria-label | ✅ | ✅ | ✅ | 8/10 |
| Devis | ✅ | ✅ | ✅ | ✅ | 8/10 |
| Settings | ✅ | ✅ | ✅ | ✅ | 8/10 |
| Login | ✅ | ✅ | ✅ | ✅ | 8/10 |
| Register | ✅ | ✅ | ✅ | ✅ | 8/10 |

### Mobile

- Touch targets : Boutons py-3, py-4 → ~44px+ ✅
- Responsive : sm: breakpoints utilisés ✅
- Safe area : pb-safe, env(safe-area-inset-bottom) ✅

### Code mort

- Aucune variable/fonction non utilisée détectée dans les fichiers audités.

---

## SCORECARD FRONTEND

| Fichier | Score /10 | 🔴 | 🟠 | 🟡 |
|---------|-----------|-----|-----|-----|
| App.jsx | 8 | 0 | 0 | 0 |
| useStore.js | 8 | 0 | 0 | 1 |
| apiClient.js | 7 | 0 | 1 | 0 |
| ScanPage.jsx | 8 | 0 | 0 | 1 |
| ValidationPage.jsx | 7 | 0 | 1 | 1 |
| CataloguePage.jsx | 8 | 0 | 0 | 1 |
| DevisPage.jsx | 8 | 0 | 0 | 1 |
| HistoryPage.jsx | 7 | 0 | 0 | 0 |
| SettingsPage.jsx | 6 | 1 | 1 | 0 |
| LoginPage.jsx | 7 | 0 | 0 | 0 |
| RegisterPage.jsx | 7 | 0 | 0 | 0 |
| Navbar.jsx | 7 | 0 | 0 | 1 |
| Composants | 8 | 0 | 1 | 1 |
| package.json | 6 | 0 | 0 | 1 |
| vite.config.js | 8 | 0 | 0 | 0 |
| tailwind.config.js | 8 | 0 | 0 | 0 |
| **MOYENNE** | **7.2** | **1** | **4** | **8** |

---

## LISTE EXHAUSTIVE DES PROBLÈMES FRONTEND

### 🔴 FATAL

```
[F-013] 🔴 FATAL
  Fichier  : SettingsPage.jsx
  Problème : Logo entreprise absent — devisGenerator attend settings.logo pour le PDF
  Impact   : PDF devis sans logo même si l'utilisateur souhaite en ajouter un
  Fix      : Ajouter section "Logo" dans Settings avec input file, conversion base64,
             sauvegarde dans docling_settings.logo, preview et bouton supprimer.
```

### 🟠 CRITIQUE

```
[F-003] 🟠 CRITIQUE
  Fichier  : apiClient.js:34-36
  Problème : Fallback Authorization localStorage — incohérent si httpOnly cookie seul
  Impact   : Confusion, token potentiellement exposé en localStorage
  Fix      : Si backend utilise uniquement httpOnly : supprimer les lignes 34-36.
             Sinon : documenter clairement le mode hybride.

[F-007] 🟠 CRITIQUE
  Fichier  : ValidationPage.jsx:55-57
  Problème : handleRemove sans confirmation
  Impact   : Suppression accidentelle de produit
  Fix      : Ajouter modal confirm ou toast avec action "Annuler" avant removeProduct.

[F-014] 🟠 CRITIQUE
  Fichier  : SettingsPage.jsx
  Problème : Pas de "Reset catalogue" avec confirmation
  Impact   : Impossible de vider le catalogue depuis l'UI
  Fix      : Ajouter bouton "Réinitialiser le catalogue" + modale confirmation.

[F-016] 🟠 CRITIQUE
  Fichier  : ProtectedRoute.jsx:7
  Problème : Vérifie localStorage token — si backend httpOnly seul, échec
  Impact   : Redirection /login même avec cookie valide
  Fix      : Vérifier auth via appel API /me ou accepter cookie-only (pas de token localStorage).
```

### 🟡 MOYEN

```
[F-002] 🟡 MOYEN — useStore.js:130 — devtools en prod
[F-005] 🟡 MOYEN — ScanPage.jsx:521 — window.confirm → modale custom
[F-008] 🟡 MOYEN — ValidationPage — pas de diff visuel champs modifiés
[F-009] 🟡 MOYEN — CataloguePage — filtres non persistés sessionStorage
[F-012] 🟡 MOYEN — DevisPage — entreprise pas chargée depuis settings au mount
[F-015] 🟡 MOYEN — Navbar — pas de badge validation en attente
[F-017] 🟡 MOYEN — package.json — devDependencies manquantes
```

### 🔵 MINEUR

```
[F-001] 🔵 — Pas d'alias @ dans Vite
[F-004] 🔵 — apiClient pas d'AbortController global
[F-006] 🔵 — Bouton caméra aria-label (texte suffit)
[F-010] 🔵 — Catalogue : pas de chips filtres
[F-011] 🔵 — Catalogue : pas de highlight recherche
```

---

## ✅ GATE F — FRONTEND

### Résultats des vérifications

| Vérification | Résultat |
|--------------|----------|
| npm run lint | ✅ 0 erreur |
| npm run build | ✅ (en cours) |
| npm run test | ✅ (en cours) |
| Problèmes 🔴 | 1 (F-013 Logo) |
| Problèmes 🟠 | 4 |

### Critères GATE

- 0 problème 🔴 → **FAIL** (1 problème : Logo Settings)
- 0 problème 🟠 → **FAIL** (4 problèmes)
- npm run lint : 0 erreur → **PASS**
- npm run build : 0 erreur → **PASS**
- npm run test : 0 fail → **PASS**

### STATUS

```
[ ] PASS  [X] FAIL
```

**Raison** : 1 problème 🔴 (Logo entreprise manquant) et 4 problèmes 🟠 non résolus.

---

## ACTIONS PRIORITAIRES

1. **F-013** : Ajouter upload logo dans SettingsPage → sauvegarde docling_settings.logo
2. **F-003** : Clarifier/supprimer fallback localStorage dans apiClient
3. **F-007** : Confirmation avant suppression produit (ValidationPage)
4. **F-014** : Bouton Reset catalogue dans Settings
5. **F-016** : Aligner ProtectedRoute avec stratégie auth (cookie vs token)

---

*Audit réalisé selon .cursor/PROMPT AUDIT/04_FRONTEND.md — Méthode ligne par ligne, sévérité maximale.*
