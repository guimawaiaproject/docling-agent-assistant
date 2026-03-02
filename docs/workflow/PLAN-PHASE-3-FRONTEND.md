# Plan d'optimisation — Phase 3 : Migration frontend

**Objectif** : Migrer `docling-pwa` vers `apps/pwa`, configurer pnpm workspaces, puis adopter progressivement une architecture Feature-Sliced Design.

**Contexte actuel** :
- Structure : `pages/`, `components/`, `services/`, `store/`, `config/`, `constants/`, `utils/`
- 8 pages, 12 composants, 4 services, 1 store
- ScanPage ~780 lignes (priorité refacto)
- Tests : Vitest, `__tests__/` et `**/__tests__/`

---

## Étape 3.1 — Stabiliser le déplacement (prérequis)

### 3.1.1 Corriger l'installation pnpm

**Problème** : `pnpm install` depuis la racine avec workspace peut déplacer `node_modules` (hoisting). Le build échoue si `vite` n'est pas trouvé.

**Actions** :
1. Supprimer `apps/pwa/node_modules` et `apps/pwa/package-lock.json` (garder `pnpm-lock.yaml`)
2. Exécuter `pnpm install` depuis la racine
3. Vérifier que `apps/pwa/node_modules/.bin/vite` existe ou que `pnpm exec vite` fonctionne
4. Mettre à jour les scripts `package.json` si besoin : `"build": "vite build"` (pnpm résout les binaires)

**Alternative** : Si le workspace pose problème, exécuter `pnpm install` directement dans `apps/pwa/` sans workspace (temporaire).

### 3.1.2 Charger `.env` depuis la racine

Dans `apps/pwa/vite.config.js` :

```js
import { loadEnv } from 'vite'
import path from 'path'

export default defineConfig(({ mode }) => {
  const rootDir = path.resolve(__dirname, '../..')
  const env = loadEnv(mode, rootDir, '')
  return {
    // ...
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || 'http://localhost:8000'),
      'import.meta.env.VITE_AUTH_REQUIRED': JSON.stringify(env.VITE_AUTH_REQUIRED ?? 'false'),
    },
  }
})
```

### 3.1.3 Checklist de validation

- [ ] `pnpm run build` (depuis apps/pwa ou racine) réussit
- [ ] `pnpm run test` passe
- [ ] `pnpm run dev` lance le serveur
- [ ] Les variables `VITE_*` sont chargées depuis `.env` racine

---

## Étape 3.2 — Configuration pnpm et alias Vite

### 3.2.1 Alias pour les imports

Ajouter dans `vite.config.js` :

```js
import path from 'path'

resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
    '@/shared': path.resolve(__dirname, './src/shared'),
    '@/features': path.resolve(__dirname, './src/features'),
  },
},
```

### 3.2.2 pnpm-workspace.yaml

Vérifier que `pnpm-workspace.yaml` à la racine contient :

```yaml
packages:
  - 'apps/pwa'
```

Déplacer `pnpm.overrides` de `apps/pwa/package.json` vers `package.json` racine si nécessaire.

---

## Étape 3.3 — Migration Feature-Sliced (progressive)

### Principe

Ne pas tout réécrire d'un coup. **Feature pilote : auth** (LoginPage, RegisterPage, ProtectedRoute, peu de dépendances).

### Structure cible

```
apps/pwa/src/
├── app/                    # Point d'entrée, routes
│   ├── App.jsx
│   ├── main.jsx
│   └── routes.jsx
├── shared/                 # Réutilisable
│   ├── ui/                 # SkeletonCard, ErrorBoundary, EmptyStateIllustration
│   ├── lib/                # apiClient, imageService, offlineQueue
│   └── config/             # api.js, features.js
├── features/
│   ├── auth/               # LoginPage, RegisterPage, ProtectedRoute
│   ├── scan/               # ScanPage
│   ├── validation/         # ValidationPage
│   ├── catalogue/          # CataloguePage, CompareModal
│   ├── history/            # HistoryPage
│   ├── devis/              # DevisPage, devisGenerator
│   └── settings/           # SettingsPage
└── widgets/                # Navbar, OfflineBanner, CommandPalette
```

### Ordre de migration

| Priorité | Feature | Fichiers | Complexité | Dépendances |
|----------|---------|----------|------------|-------------|
| 1 | **auth** | LoginPage, RegisterPage, ProtectedRoute | Faible | config, apiClient |
| 2 | **shared** | ui/, lib/, config/ | Moyenne | Aucune |
| 3 | **history** | HistoryPage | Faible | shared, apiClient |
| 4 | **settings** | SettingsPage | Moyenne | shared, store |
| 5 | **catalogue** | CataloguePage, CompareModal | Moyenne | shared, store |
| 6 | **devis** | DevisPage, devisGenerator | Moyenne | shared, store |
| 7 | **validation** | ValidationPage | Haute | shared, store |
| 8 | **scan** | ScanPage | Très haute | shared, store, offlineQueue |

### 3.3.1 Feature pilote : auth

**Actions** :
1. Créer `src/features/auth/`
2. Déplacer `LoginPage.jsx`, `RegisterPage.jsx`, `ProtectedRoute.jsx` → `features/auth/`
3. Créer `features/auth/index.js` (réexport)
4. Mettre à jour les imports dans `App.jsx`
5. Lancer les tests, build, dev
6. Commit : `feat(pwa): migrate auth to Feature-Sliced`

### 3.3.2 Shared

**Actions** :
1. Créer `src/shared/ui/` → déplacer SkeletonCard, ErrorBoundary, EmptyStateIllustration
2. Créer `src/shared/lib/` → déplacer apiClient, imageService, offlineQueue
3. Créer `src/shared/config/` → déplacer api.js, features.js
4. Mettre à jour tous les imports (rechercher `../components/`, `../services/`, `../config/`)
5. Mettre à jour les alias Vite si nécessaire

### 3.3.3 Pages restantes

Itérer feature par feature, en validant après chaque migration :
- `pnpm run build`
- `pnpm run test`
- Test manuel des routes concernées

---

## Étape 3.4 — Décomposition ScanPage (priorité haute)

**Problème** : ScanPage ~780 lignes, logique dense (upload, batch, polling, offline, etc.).

### Sous-composants à extraire

| Composant | Responsabilité | Lignes estimées |
|-----------|----------------|-----------------|
| `UploadZone` | Zone dropzone, sélection fichiers | ~80 |
| `BatchQueue` | Liste des fichiers en attente, progression | ~120 |
| `JobStatusCard` | Affichage statut d'un job (polling) | ~60 |
| `useScanUpload` | Hook custom : logique upload + API | ~150 |
| `useBatchQueue` | Hook : gestion file d'attente | ~80 |

### Plan d'extraction

1. Créer `features/scan/scanPage/` (ou `features/scan/components/`)
2. Extraire `UploadZone` en premier (peu de dépendances)
3. Extraire `BatchQueue`
4. Extraire les hooks `useScanUpload`, `useBatchQueue`
5. Refactoriser `ScanPage.jsx` pour utiliser ces composants
6. Garder la logique métier dans les hooks, l'UI dans les composants

---

## Étape 3.5 — Tests et validation

### 3.5.1 Mise à jour des chemins de test

Après migration :
- `src/__tests__/` → peut rester ou être déplacé vers `shared/__tests__/`, `features/*/__tests__/`
- `src/pages/__tests__/` → `src/features/*/__tests__/`
- Vérifier `vite.config.js` : `include` pour Vitest

### 3.5.2 Checklist finale Phase 3

- [ ] `pnpm run build` OK
- [ ] `pnpm run test` OK
- [ ] `pnpm run lint` OK
- [ ] Toutes les routes fonctionnent
- [ ] PWA (manifest, service worker) OK
- [ ] Pas de régression visuelle

---

## Estimation du temps

| Étape | Durée | Blocants |
|-------|-------|----------|
| 3.1 Stabilisation | 30 min | Fix node_modules / pnpm |
| 3.2 Config | 15 min | — |
| 3.3.1 auth | 45 min | — |
| 3.3.2 shared | 1 h | Imports multiples |
| 3.3.3 Pages 2–8 | 2–3 h | Dépendances croisées |
| 3.4 ScanPage | 2 h | Complexité |
| 3.5 Tests | 30 min | — |

**Total** : 6–8 h (sur 1–2 jours)

---

## Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| pnpm workspace casse le build | Tester `pnpm install` dans apps/pwa seul |
| Imports cassés après déplacement | Utiliser alias `@/` dès le début |
| ScanPage trop couplé | Extraire par petits blocs, tester à chaque étape |
| Récursion dans les imports | Respecter les couches FSD (shared → features → app) |

---

## Références

- [Feature-Sliced Design](https://feature-sliced.design/)
- [Vite resolve.alias](https://vitejs.dev/config/shared-options.html#resolve-alias)
- [pnpm workspaces](https://pnpm.io/workspaces)
