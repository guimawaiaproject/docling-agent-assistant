# Architecture Frontend

## Stack

| Technologie | Usage |
|-------------|-------|
| **React 19** | UI, hooks |
| **Vite 5** | Build, HMR, PWA |
| **Tailwind 4** | Styles |
| **Zustand** | State management |

---

## Structure

```
docling-pwa/src/
├── pages/           # ScanPage, ValidationPage, CataloguePage, DevisPage, HistoryPage, SettingsPage
├── components/      # Navbar, CompareModal, ErrorBoundary, OfflineBanner
├── config/api.js    # URLs endpoints centralisées
├── services/        # apiClient, imageService, devisGenerator, offlineQueue
├── store/useStore.js
└── constants/       # categories.js (FAMILLES)
```

---

## Pages principales

| Page | Rôle |
|------|------|
| **Scanner** | Upload photo/PDF, file de traitement, lancement extraction |
| **Validation** | Validation des produits extraits avant sauvegarde |
| **Catalogue** | Recherche, filtres, export CSV/Excel, comparaison prix |
| **Devis** | Sélection produits, quantités, génération PDF |
| **Historique** | Audit trail factures, stats, coût API |
| **Réglages** | Connexion API, modèle IA, dossier magique |

---

## Optimisations

- **React.lazy** + **Suspense** : lazy-loading des pages
- **apiClient** Axios partagé avec intercepteur Bearer
- **AbortController** : annulation polling ScanPage, CompareModal
- **Debounce** : recherche CompareModal
- **URL.revokeObjectURL** : libération mémoire ScanPage

---

## Références

- [Vue d'ensemble](overview.md)
- [Analyse UI](ui-analysis.md) — Analyse détaillée des 5 écrans
