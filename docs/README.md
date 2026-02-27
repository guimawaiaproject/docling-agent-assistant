# Docling Agent v3 — Documentation

Application d'extraction automatisée de factures fournisseurs pour le secteur BTP. Transforme des factures PDF ou photos en un catalogue de prix structuré, consultable et exportable.

---

## Index par rôle

| Rôle | Point d'entrée |
|------|----------------|
| **Nouveau dev / IA** | [DEVELOPER-ONBOARDING.md](DEVELOPER-ONBOARDING.md) |
| **Profil projet (IA)** | [PROJECT-PROFILE.md](PROJECT-PROFILE.md) |
| **Contribution** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Plan finalisation** | [workflow/1_planning/PLAN-COMPLET-FINALISATION/README.md](workflow/1_planning/PLAN-COMPLET-FINALISATION/README.md) |
| **Architecture** | [architecture/README.md](architecture/README.md) |
| **Glossaire** | [GLOSSARY.md](GLOSSARY.md) |

---

## Démarrage rapide (5 min)

1. Lire **[01-ARCHITECTURE.md](01-ARCHITECTURE.md)** pour le flux
2. Suivre **[02-INSTALLATION.md](02-INSTALLATION.md)** pour lancer
3. Consulter **[03-API.md](03-API.md)** pour les endpoints
4. Parcourir **[13-PLAN-OPTIMISATION.md](13-PLAN-OPTIMISATION.md)** pour la roadmap

---

## Index des documents

| Document | Description |
|----------|-------------|
| **[01-ARCHITECTURE.md](01-ARCHITECTURE.md)** | Stack, structure, pipeline détaillé |
| **[02-INSTALLATION.md](02-INSTALLATION.md)** | Installation pas à pas |
| **[03-API.md](03-API.md)** | Endpoints, schémas, limites |
| **[04-SERVICES-ET-CONFIG.md](04-SERVICES-ET-CONFIG.md)** | 6 services backend, .env |
| **[05-AUDIT-BACKEND.md](05-AUDIT-BACKEND.md)** | Optimisations 2026, risques |
| **[06-AUDIT-FRONTEND.md](06-AUDIT-FRONTEND.md)** | Pages, composants, corrections |
| **[07-ANALYSE-UI.md](07-ANALYSE-UI.md)** | Analyse des 5 écrans |
| **[08-AVIS-CONCURRENTS.md](08-AVIS-CONCURRENTS.md)** | Avis clients, attentes |
| **[09-TESTS.md](09-TESTS.md)** | Rapport tests (134 backend+frontend) |
| **[10-NOTES-AUDIT.md](10-NOTES-AUDIT.md)** | Notes d'audit, prochaines étapes |
| **[12-EXPERT-REPORT.md](12-EXPERT-REPORT.md)** | Rapport d'expert, SWOT, roadmap, écosystème BTP |
| **[13-PLAN-OPTIMISATION.md](13-PLAN-OPTIMISATION.md)** | Plan chronologique avec tests de vérification |
| **[AI-INTEGRATION.md](AI-INTEGRATION.md)** | Intégration AI-first — agents, rules, commands, scripts |
| **[workflow/README.md](workflow/README.md)** | Workflow par stages (backlog → planning → in-progress → completed) |
| **[ai-library/README.md](ai-library/README.md)** | Bibliothèque IA complète (éditeurs, agents, tests, doc, MCP) |
| **[DEVELOPER-ONBOARDING.md](DEVELOPER-ONBOARDING.md)** | Guide onboarding (30 min) |
| **[PROJECT-PROFILE.md](PROJECT-PROFILE.md)** | Profil projet IA-friendly |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Workflow contribution |
| **[GLOSSARY.md](GLOSSARY.md)** | Glossaire BTP, technique, IA |
| **[architecture/README.md](architecture/README.md)** | ADR, décisions architecturales |
| **[workflow/1_planning/PLAN-COMPLET-FINALISATION/README.md](workflow/1_planning/PLAN-COMPLET-FINALISATION/README.md)** | **Plan complet finalisation** — étapes, anti-régression |

---

## Agent Skills (IA)

Le projet utilise le format [Agent Skills](https://agentskills.io) pour guider les agents IA :

- **neon-postgres** : Neon, PostgreSQL serverless, asyncpg
- **docling-factures** : Extraction factures, API, catalogue BTP

Voir [AGENTS.md](../AGENTS.md) et `.cursor/rules/agent-skills.mdc`. Validation : `make validate-skills`.

---

## Résumé projet

**Cas d'usage :** Un chef de chantier BTP reçoit des factures de fournisseurs espagnols/catalans. Il les uploade via la PWA ou les dépose dans le dossier magique. L'application extrait les lignes produit via **Gemini 3 Flash**, traduit en français, classe par famille BTP et stocke dans un catalogue **PostgreSQL Neon**.

**Objectif :** Base de prix matériaux réutilisable pour chiffrer des devis.

**Stack :** React 19 + Vite 5 + Tailwind 4 (PWA) | FastAPI + Uvicorn | PostgreSQL Neon | Google Gemini 3 Flash | OpenCV | Storj S3

---

## Accès rapide

| Service | URL (dev local) |
|---------|-----------------|
| PWA | https://localhost:5173 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |
| Docs API | http://localhost:8000/docs |

---

## Déploiement

- **Backend** : Render (Procfile) ou Railway
- **Frontend** : Netlify (`npm run build` → déployer `dist/`)
- **BDD** : Neon PostgreSQL (déjà cloud)

---

*Dernière mise à jour : Fév. 2026*
