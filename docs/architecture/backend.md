# Architecture Backend

## Services principaux

| Service | Fichier | Rôle |
|---------|---------|------|
| **Orchestrator** | `orchestrator.py` | Pipeline prétraitement → Gemini → validation → DB |
| **Gemini** | `gemini_service.py` | Extraction IA, retry rate-limit, cache par model_id |
| **Image** | `image_preprocessor.py` | CLAHE, débruitage, WebP (photos uniquement) |
| **Storage** | `storage_service.py` | Upload S3 Storj (boto3) |
| **Watchdog** | `watchdog_service.py` | Surveillance dossier magique |
| **Auth** | `auth_service.py` | JWT (PyJWT) + hash argon2id |

---

## Configuration (.env)

### Obligatoires

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Clé API Google Gemini |
| `DATABASE_URL` | URL PostgreSQL Neon (`postgresql://...?sslmode=require`) |
| `JWT_SECRET` | Secret JWT — `openssl rand -hex 32` |

### Optionnelles

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DEFAULT_AI_MODEL` | `gemini-3-flash-preview` | Modèle IA |
| `WATCHDOG_FOLDER` | `./Docling_Factures` | Dossier surveillé |
| `WATCHDOG_ENABLED` | `true` | Activer le dossier magique |
| `STORJ_BUCKET` | `docling-factures` | Bucket S3 |
| `STORJ_ACCESS_KEY` | (vide) | Stockage désactivé si vide |
| `STORJ_SECRET_KEY` | (vide) | Stockage désactivé si vide |
| `JWT_EXPIRY_HOURS` | `24` | Durée de validité token |
| `SENTRY_DSN` | (vide) | Monitoring erreurs |
| `FREE_ACCESS_MODE` | `false` | Accès sans auth (dev) |

---

## Base de données

- **Neon PostgreSQL** : serverless, pooler (`-pooler` dans l'URL)
- **Migrations** : Alembic (`alembic upgrade head`)
- **Upsert** : anti-doublon sur `designation_raw` + `fournisseur` + `user_id`
- **Pagination** : cursor-based (pas d'OFFSET)

---

## Références

- [ADR-001 Stack technique](ADR-001-stack-technique.md)
- [Vue d'ensemble](overview.md)
