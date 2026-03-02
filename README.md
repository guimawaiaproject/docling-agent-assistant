# Docling Agent v3 — Catalogue BTP Intelligent

Extraction automatisée de factures fournisseurs BTP. PDF/photos (CA/ES) → catalogue structuré exportable en français.

## Démarrage rapide

```bash
git clone <repo-url>
cd docling

# Dépendances
cd apps/api && uv sync && cd ../..
pnpm install

# Config
cp .env.example .env
# Remplir GEMINI_API_KEY, DATABASE_URL, JWT_SECRET

# Migrations
cd apps/api && uv run alembic upgrade head && cd ../..

# Lancer
make dev              # Linux/Mac
run_local.bat         # Windows (avec pre-launch check)
```

| Service | URL |
|---------|-----|
| PWA | https://localhost:5173 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Docs | http://localhost:8100 (`make docs`) |

## Stack

- **Frontend** : React 19 + Vite 5 + Tailwind 4 (PWA)
- **Backend** : FastAPI + Uvicorn (uv)
- **BDD** : Neon PostgreSQL
- **IA** : Google Gemini 3 Flash

## Documentation

- [docs/index.md](docs/index.md) — Accueil
- [docs/guides/installation.md](docs/guides/installation.md) — Installation
- [docs/guides/contributing.md](docs/guides/contributing.md) — Contribution

```bash
make docs   # MkDocs sur http://localhost:8100
```

## Licence

[MIT](LICENSE)
