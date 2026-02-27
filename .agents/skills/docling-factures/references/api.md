# API Docling — Référence

## Auth

- `POST /api/v1/auth/login` — email, password
- `POST /api/v1/auth/register` — email, password
- `POST /api/v1/auth/logout` — invalide le token

## Factures

- `POST /api/v1/invoices/process` — multipart: file, model_id?, source?
- `GET /api/v1/invoices/status/{job_id}` — { status, products?, error? }

## Catalogue

- `GET /api/v1/catalogue` — query: famille, fournisseur, search, limit, cursor
- `POST /api/v1/catalogue/batch` — body: { produits, source }
- `GET /api/v1/catalogue/fournisseurs` — liste distincte
- `GET /api/v1/catalogue/compare` — comparaison produits

## Autres

- `GET /api/v1/stats` — nb produits, nb factures
- `GET /api/v1/history` — liste factures traitées
- `GET /api/v1/history/{id}/pdf` — téléchargement PDF
- `GET /api/v1/sync/status` — watchdog status
