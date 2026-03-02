# Installation — Docling Agent

## Prérequis

- Python 3.11+
- Node.js 20+
- Compte Neon (https://neon.tech) avec une base PostgreSQL
- Clé API Google Gemini (https://aistudio.google.com)

---

## Installation rapide

```bash
git clone <repo-url>
cd docling

# Setup initial (.env + uv + pnpm)
make setup                    # Linux/Mac
# ou: powershell -File scripts\setup.ps1   # Windows

# Avec build + migrations + lancement :
# powershell -File scripts\setup.ps1 -Build -Migrate -Launch
# ./scripts/setup.sh --build --migrate --launch
```

Puis remplir `GEMINI_API_KEY`, `DATABASE_URL` et `JWT_SECRET` dans `.env`.

## Backend (manuel)

```bash
cd apps/api && uv sync --all-extras   # deps + dev (pytest, playwright, etc.)
```

---

## Base de données

Les migrations sont gérées par **Alembic**. Après avoir configuré `DATABASE_URL` dans `.env` :

```bash
cd apps/api && uv run alembic upgrade head
```

Cela crée toutes les tables, contraintes et index nécessaires.

---

## Frontend

```bash
cd apps/pwa
pnpm install
```

---

## Lancement (dev local)

### Méthode rapide

```bash
make dev              # Linux/Mac
run_local.bat         # Windows
```

Lance l'API FastAPI sur `http://localhost:8000` et la PWA Vite sur `https://localhost:5173`.

### Méthode manuelle (2 terminaux)

**Terminal 1 — Backend :**
```bash
cd apps/api && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend :**
```bash
cd apps/pwa && pnpm exec vite
```

---

## Accès

| Service | URL |
|---------|-----|
| PWA | https://localhost:5173 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |
| Swagger | http://localhost:8000/docs |

---

## Dossier Magique (Watchdog)

Quand l'API tourne, le dossier `Docling_Factures/` est surveillé en permanence. Déposez un PDF ou une image dedans : il sera traité automatiquement par Gemini, puis déplacé vers `Docling_Factures/Traitees/` (ou `Erreurs/` en cas d'échec).

---

## Déploiement production

- **Backend** : Render (`Procfile` inclus) ou Railway
- **Frontend** : Netlify (`npm run build` → déployer `dist/`)
- **BDD** : Neon PostgreSQL + migrations Alembic
- Voir [Déploiement](deployment.md) pour la séquence complète
