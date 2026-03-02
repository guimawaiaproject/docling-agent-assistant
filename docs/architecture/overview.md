# Architecture — Docling Agent v3

## Cas d'usage

Un chef de chantier BTP reçoit des factures de fournisseurs espagnols/catalans (BigMat, Discor, Guerin Roses, etc.). Il les uploade via la PWA mobile ou les dépose dans le dossier magique. L'application :

1. Analyse le document via **Gemini 3 Flash** (vision multimodale)
2. Extrait chaque ligne produit (désignation, prix, remise, TVA IVA 21%)
3. Traduit du catalan/espagnol vers le français
4. Classe par famille BTP (Maçonnerie, Plomberie, Carrelage, etc.)
5. Vérifie l'arithmétique avec un score de confidence (high/low)
6. Stocke dans un catalogue **PostgreSQL Neon** avec dédoublonnage intelligent

**Objectif final :** constituer une **base de prix matériaux** réutilisable pour chiffrer des devis.

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React 19 + Vite 5 + Tailwind 4 (PWA installable) |
| Backend | FastAPI + Uvicorn (async) |
| Base de données | PostgreSQL Neon (serverless, cloud) |
| IA | Google Gemini 3 Flash (vision + code execution) |
| Prétraitement image | OpenCV (CLAHE, débruitage, WebP) |
| Watchdog | watchdog library (surveillance dossier local) |
| Stockage cloud | Storj S3-compatible (boto3) |

---

## Architecture détaillée

```
docling/
+-- apps/
|   +-- api/                            # Backend FastAPI
|   |   +-- main.py                     # Routeur (async + BackgroundTasks)
|   |   +-- core/                       # config, db_manager, orchestrator
|   |   +-- services/                   # gemini, auth, storage, watchdog
|   |   +-- schemas/                    # invoice.py (Pydantic)
|   |   +-- migrations/                  # Alembic (a001..a008)
|   |   +-- tests/                      # pytest
|   |
|   +-- pwa/                            # Frontend React PWA
|       +-- src/
|       |   +-- features/               # scan, catalogue, devis, auth
|       |   +-- shared/                 # config, lib, ui
|       |   +-- store/useStore.js       # Zustand
|       +-- vite.config.js
|
+-- scripts/                            # validate_all, health_check, etc.
+-- docs/                               # MkDocs
```

---

## Pipeline d'extraction

```
Photo / PDF facture
    |
    v
Prétraitement OpenCV (si image : CLAHE, débruitage, resize, WebP)
    |
    v
Gemini 3 Flash (extraction structurée JSON + traduction FR + classification BTP)
    |
    v
Validation Pydantic (auto-calcul TVA, vérification arithmétique, confidence score)
    |
    v
PostgreSQL Neon (upsert anti-doublon sur designation_raw + fournisseur)
    |
    v
Stockage cloud Storj (optionnel)
    |
    v
Catalogue PWA (recherche, filtres, export CSV/Excel)
```

---

## Optimisations backend (2026)

- **asyncio.to_thread()** : Gemini, OpenCV, boto3 exécutés dans un thread pool → vrai parallélisme
- **Cache GeminiService** : une instance par model_id (pas de réinit à chaque fichier)
- **Sémaphore** : max 3 extractions Gemini concurrentes (évite rate limit 429)
- **Pagination cursor** : catalogue paginé (pas de OFFSET coûteux)
