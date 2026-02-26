# Audit Frontend — Docling Agent

## Structure des pages

| Page | Fichier | Rôle |
|------|---------|------|
| Scan | `ScanPage.jsx` | Upload, photo, sélection dossier, file de traitement |
| Validation | `ValidationPage.jsx` | Édition produits extraits avant sauvegarde |
| Catalogue | `CataloguePage.jsx` | Recherche, filtres, export CSV/Excel, comparaison |
| Devis | `DevisPage.jsx` | Création devis PDF depuis le catalogue |
| Historique | `HistoryPage.jsx` | Audit trail factures, stats, re-scan |
| Réglages | `SettingsPage.jsx` | Test API, choix modèle IA, statut watchdog |

---

## Composants

| Composant | Fichier | Rôle |
|-----------|---------|------|
| Navbar | `Navbar.jsx` | Navigation 5 onglets |
| CompareModal | `CompareModal.jsx` | Comparaison de prix entre produits |

---

## State management (Zustand)

- **useStore.js** : `batchQueue`, `extractedProducts`, `selectedModel`, `currentJob`, etc.
- **Persist** : `selectedModel` uniquement (localStorage)
- **queueStats** : getter calculé (total, pending, done, error)

---

## Corrections appliquées

| Fichier | Problème | Correction |
|---------|----------|------------|
| `api.js` | Template literals mal formés | Correction des backticks |
| `CataloguePage.jsx` | CompareModal mal placé, setCompareSearch unused | Déplacement modal, suppression variable |
| `ScanPage.jsx` | inputRef null au clic caméra | Guard `if (!inputRef?.current) return` |
| `ScanPage.jsx` | batchQueue obsolète après await | `useDoclingStore.getState().batchQueue` |
| `ScanPage.jsx` | Items affichés vides | Fallback `item.name \|\| item.file?.name \|\| 'Fichier'` |
| `useStore.js` | Status initial 'compressing' | Passage à 'pending' pour activer Lancer |
| `vite.config.js` | Conflit React production/dev | Suppression du `define` problématique |

---

## Points d'attention restants

- **CompareModal** : utiliser des clés stables (id) au lieu d'index dans les `.map()`
- **ValidationPage** : idem pour les clés
- **useEffect** : dépendances manquantes dans HistoryPage, SettingsPage
- **Chunks** : build > 500 Ko (recommandation code-split)

---

## Config API

- `docling-pwa/src/config/api.js` : `API_BASE_URL` = `import.meta.env.VITE_API_URL || 'http://localhost:8000'`
