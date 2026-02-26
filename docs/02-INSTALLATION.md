# Installation — Docling Agent

## Prérequis

- Python 3.11+
- Node.js 20+
- Compte Neon (https://neon.tech) avec une base PostgreSQL
- Clé API Google Gemini (https://aistudio.google.com)

---

## Backend

```bash
git clone <repo-url>
cd docling-agent-assistant

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt -r requirements-dev.txt

cp .env.example .env
# Remplir GEMINI_API_KEY, DATABASE_URL et JWT_SECRET dans .env
```

---

## Base de données

Les migrations sont gérées par **Alembic**. Après avoir configuré `DATABASE_URL` dans `.env` :

```bash
alembic upgrade head
```

Cela crée toutes les tables, contraintes et index nécessaires.

---

## Frontend

```bash
cd docling-pwa
npm install
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
venv\Scripts\activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend :**
```bash
cd docling-pwa
npm run dev
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
- Voir [staging-setup.md](staging-setup.md) pour la séquence de déploiement complète
