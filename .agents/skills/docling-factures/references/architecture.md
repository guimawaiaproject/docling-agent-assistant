# Architecture Docling — Référence

## Stack technique

- **Backend** : FastAPI, asyncpg, Google Gemini, OpenCV, Factur-X, Alembic
- **Frontend** : React 19, Vite 5, Tailwind, Zustand
- **Base** : Neon PostgreSQL (serverless)
- **Déploiement** : Render (API), Netlify (PWA)

## Flux utilisateur

1. **Scan** : Upload PDF/image → job async → polling status
2. **Validation** : Ajuster produits extraits → batch save
3. **Catalogue** : Consultation, filtres, recherche floue
4. **Devis** : Export Excel/PDF depuis le catalogue

## Sécurité

- JWT (httpOnly cookie ou Bearer)
- Argon2id pour les mots de passe
- Rate limiting (SlowAPI)
