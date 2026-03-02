# Migration legacy → apps/ — Terminée

**Date** : 2 mars 2026
**Statut** : Terminé

## Objectif

Conserver **apps/** comme seule source de vérité. Suppression de `api.py`, `backend/` et `docling-pwa/`.

## Périmètre supprimé

| Chemin | Remplacé par |
|--------|--------------|
| `api.py` | `apps/api/main.py` |
| `backend/` | `apps/api/core/`, `apps/api/services/`, etc. |
| `docling-pwa/` | `apps/pwa/` |

## Déjà aligné sur apps/

- **Dockerfile** : `COPY apps/api/`, `uvicorn main:app` depuis `apps/api`
- **Procfile** : `cd apps/api && uvicorn main:app`
- **render.yaml** : utilise le Dockerfile
- **run_dev.sh** : `apps/api` + `apps/pwa`
- **deploy.yml** : `working-directory: apps/pwa`
- **tests.yml** : `working-directory: apps/api`
- **pnpm-workspace** : `packages: ['apps/pwa']`

## Modifications effectuées

1. **scripts/validate_all.ps1** : ruff sur `apps/api`, frontend sur `apps/pwa`, pytest depuis `apps/api`
2. **scripts/fix-npm-windows.ps1** : cible `apps/pwa` au lieu de `docling-pwa`
3. **DEPRECATED.md** : notice à la racine
4. **api.py** : en-tête DEPRECATED
5. **backend/** : README DEPRECATED
6. **docling-pwa/** : README DEPRECATED
7. **Docs** : 02-INSTALLATION, AI-INTEGRATION, AGENTS.md mis à jour

## Prochaine étape (optionnel)

- Supprimer `api.py`, `backend/`, `docling-pwa/` après validation complète que tout fonctionne avec apps/ uniquement.
