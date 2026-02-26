# Docling PWA — Frontend

React 19 + Vite 5 + Tailwind 4. PWA installable avec service worker (Workbox).

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Scan | `/scan` | Upload PDF/photo, file de traitement IA |
| Validation | `/validation` | Édition des produits extraits avant sauvegarde |
| Catalogue | `/catalogue` | Recherche, filtres, export CSV/Excel, comparateur prix |
| Devis | `/devis` | Création devis PDF depuis le catalogue |
| Historique | `/history` | Audit trail des factures traitées |
| Réglages | `/settings` | Test connexion API, choix modèle IA, statut watchdog |

## Installation

```bash
npm install
```

## Démarrage (dev)

```bash
npm run dev
```

Ouvre la PWA sur `https://localhost:5173` (HTTPS requis pour caméra et install prompt).

## Variables d'environnement (VITE_*)

Créer un fichier `.env` à la racine de `docling-pwa/` ou définir dans l'hébergeur (Netlify).

| Variable | Description | Défaut |
|----------|-------------|--------|
| `VITE_API_URL` | URL de l'API backend | `http://localhost:8000` (dev) ou `/api` (prod si non défini) |
| `VITE_TVA_RATE` | Taux TVA/IVA pour le calcul TTC | `0.21` (21% IVA espagnol) |
| `VITE_SENTRY_DSN` | DSN Sentry pour monitoring erreurs frontend | _(vide = désactivé)_ |

## Build production

```bash
npm run build
```

Génère le dossier `dist/` avec :
- PWA manifest (`manifest.webmanifest`)
- Service worker (Workbox, cache offline)
- Code splitté par route (lazy loading)

## Tests

```bash
# Lancer les tests (Vitest + Testing Library)
npm test

# Mode watch (développement)
npm run test:watch

# Avec couverture
npm run test:coverage
```

**43 tests** répartis sur 3 fichiers :
- `CompareModal.test.jsx` — 17 tests (accessibilité, recherche, debounce)
- `useStore.test.js` — tests Zustand (état, queue, products)
- `apiClient.test.js` — tests intercepteur Bearer, retry, erreurs

## Lint

```bash
npm run lint
```

ESLint 9 avec plugins `react-hooks` et `react-refresh`.

## Stack technique

| Lib | Version | Rôle |
|-----|---------|------|
| React | 19 | UI |
| Vite | 5 | Bundler + dev server |
| Tailwind CSS | 4 | Styles utilitaires |
| Zustand | 5 | State management |
| Axios | 1.x | Client HTTP (intercepteur JWT) |
| Framer Motion | 12 | Animations |
| Recharts | 3 | Graphiques dashboard |
| jsPDF | 4 | Génération devis PDF |
| Lucide React | 0.5x | Icônes |
| Sonner | 2 | Toasts |
| vite-plugin-pwa | 0.21 | PWA + Workbox |
| Vitest | 3 | Tests unitaires |
| Testing Library | 16 | Tests composants React |
| @sentry/react | 9 | Monitoring erreurs |

## Déploiement (Netlify)

1. Connecter le repo GitHub
2. Base directory : `docling-pwa`
3. Build command : `npm run build`
4. Publish directory : `docling-pwa/dist`
5. Variables d'environnement : `VITE_API_URL`, `VITE_SENTRY_DSN`
