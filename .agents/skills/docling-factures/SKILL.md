---
name: docling-factures
description: Extraction automatisée de factures fournisseurs BTP, pipeline IA Gemini, catalogue de prix, API FastAPI et PWA React. Use when working on invoice extraction, catalogue BTP, Docling API, watchdog folder, Gemini integration, product upsert, devis generation, or PWA frontend.
---

# Docling Factures — Catalogue BTP Intelligent

Application d'extraction de factures PDF/photos (catalan/espagnol) vers un catalogue de prix structuré en français.

## Architecture

```
api.py                    # FastAPI — endpoints principaux
backend/
  core/
    config.py             # Pydantic-settings (.env)
    db_manager.py         # PostgreSQL Neon (asyncpg, cursor pagination)
    orchestrator.py      # Pipeline: prétraitement → Gemini → DB
  services/
    gemini_service.py    # Google Gemini (extraction IA)
    image_preprocessor.py # OpenCV (CLAHE, débruitage)
    facturx_extractor.py # Factur-X/ZUGFeRD (PDF structurés)
    watchdog_service.py  # Surveillance dossier magique
    auth_service.py      # JWT + argon2id
  schemas/invoice.py     # Product, BatchSaveRequest
docling-pwa/             # React 19 + Vite + Tailwind
```

## Pipeline d'extraction

1. **Détection MIME** — PDF ou image (jpg, png, webp)
2. **Factur-X** — Si PDF structuré → extraction XML sans IA
3. **Fallback Gemini** — Prétraitement image (OpenCV) si besoin, puis Gemini
4. **Upsert BDD** — `ON CONFLICT (designation_raw, fournisseur, user_id) DO UPDATE`
5. **Historique** — Log dans `factures_traitees`

## API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/invoices/process` | Upload facture → extraction async (job_id) |
| GET | `/api/v1/invoices/status/{job_id}` | Statut job |
| GET | `/api/v1/catalogue` | Catalogue paginé (cursor, search, famille, fournisseur) |
| POST | `/api/v1/catalogue/batch` | Sauvegarde batch (validation PWA) |
| GET | `/api/v1/catalogue/fournisseurs` | Liste fournisseurs |
| GET | `/api/v1/stats` | Stats dashboard |
| GET | `/api/v1/history` | Historique factures |
| GET | `/api/v1/sync/status` | Statut watchdog |

## Schéma Product

```python
# backend/schemas/invoice.py
fournisseur, designation_raw, designation_fr, famille, unite,
prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,
numero_facture, date_facture, confidence, source
```

**Familles valides** : Armature, Cloison, Climatisation, Plomberie, Électricité, Menuiserie, Couverture, Carrelage, Isolation, Peinture, Outillage, Consommable, Maçonnerie, Terrassement, Autre

## Base de données (Neon PostgreSQL)

- **Connexion** : `DATABASE_URL` avec `-pooler` pour PgBouncer
- **Recherche** : `pg_trgm` sur `designation_raw` et `designation_fr`
- **Pagination** : cursor-based (pas OFFSET)

## Variables d'environnement

| Variable | Obligatoire | Description |
|----------|-------------|-------------|
| GEMINI_API_KEY | Oui | Clé API Google Gemini |
| DATABASE_URL | Oui | PostgreSQL Neon |
| JWT_SECRET | Oui | Secret JWT |
| WATCHDOG_FOLDER | Non | Dossier magique (défaut: ./Docling_Factures) |
| DEFAULT_AI_MODEL | Non | gemini-3-flash-preview |

## Frontend (docling-pwa)

- **State** : Zustand (`useStore.js`)
- **Endpoints** : `src/config/api.js` → ENDPOINTS
- **Pages** : Scan, Validation, Catalogue, Devis, History, Settings

## Commandes utiles

```bash
make dev              # Backend + frontend
make migrate          # alembic upgrade head
make validate-skills  # Valider les Agent Skills
```

## Références

- [Architecture détaillée](references/architecture.md)
- [API complète](references/api.md)
