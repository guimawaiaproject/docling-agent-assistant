# ADR-001: Stack technique

## Statut

Accepté

## Contexte

Docling doit extraire des factures fournisseurs BTP (PDF, photos) via IA, stocker les produits dans une base structurée, et fournir une PWA pour consultation et génération de devis. Contraintes : coût maîtrisé, déploiement cloud, équipe réduite.

## Décision

| Couche | Choix | Alternative considérée |
|--------|-------|-------------------------|
| **Frontend** | React 19 + Vite 5 + Tailwind 4 | Next.js — rejeté (PWA standalone suffisante) |
| **Backend** | FastAPI + Uvicorn | Django — rejeté (async natif FastAPI) |
| **BDD** | Neon PostgreSQL | Supabase — rejeté (Neon serverless + pooler) |
| **IA** | Google Gemini 3 Flash | GPT-4V — rejeté (coût, vision multimodale) |
| **Stockage** | Storj S3 | AWS S3 — rejeté (coût Storj) |

## Conséquences

### Positives

- Stack moderne, async end-to-end
- Neon : scaling automatique, pas de serveur à gérer
- Gemini : vision + traduction intégrée
- PWA : installation mobile, offline-ready

### Négatives

- Dépendance à des services tiers (Neon, Gemini, Storj)
- Migration vers autre provider nécessite adaptation

### Neutres

- React 19 : écosystème mature, maintenabilité

## Références

- [01-ARCHITECTURE.md](../01-ARCHITECTURE.md)
- [Neon docs](https://neon.tech/docs)
