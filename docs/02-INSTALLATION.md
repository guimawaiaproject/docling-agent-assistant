# Installation — Docling Agent

## Prérequis

- Python 3.10+
- Node.js 18+
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

pip install -r requirements.txt

copy .env.example .env
# Remplir GEMINI_API_KEY et DATABASE_URL dans .env
```

---

## Base de données

Exécuter le contenu de `backend/schema_neon.sql` dans la console SQL de Neon.

---

## Frontend

```bash
cd docling-pwa
npm install
```

---

## Lancement (dev local)

### Méthode tout-en-un (Windows)

```bash
run_local.bat
```

Lance l'API FastAPI sur `http://localhost:8000` et la PWA Vite sur `https://localhost:5173`.

### Méthode manuelle (2 terminaux)

**Terminal 1 — Backend :**
```bash
venv\Scripts\activate
python api.py
# ou : uvicorn api:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend :**
```bash
cd docling-pwa
npx vite --port 5173
```

---

## Accès

| Service | URL |
|---------|-----|
| PWA | https://localhost:5173 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |
| Docs API | http://localhost:8000/docs |

---

## Dossier Magique (Watchdog)

Quand l'API tourne, le dossier `Docling_Factures/` est surveillé en permanence. Déposez un PDF ou une image dedans : il sera traité automatiquement par Gemini, puis déplacé vers `Docling_Factures/Traitees/` (ou `Erreurs/` en cas d'échec).

---

## Déploiement production

- **Backend** : Render (`Procfile` inclus) ou Railway
- **Frontend** : Netlify (`npm run build` → déployer `dist/`)
- **BDD** : Neon PostgreSQL (déjà cloud)
