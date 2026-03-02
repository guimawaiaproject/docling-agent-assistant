# Configuration Sentry — Docling

Ce document décrit la configuration Sentry pour le monitoring des erreurs (frontend PWA + backend API).

## État actuel (MCP Sentry)

- **Organisation** : `guimawaiaproject` (https://guimawaiaproject.sentry.io)
- **Région** : EU (de.sentry.io)
- **Projets** : Aucun projet créé — les DSN ne peuvent pas être configurés tant que les projets n'existent pas

## Étapes pour activer Sentry

### 1. Créer les projets dans Sentry

1. Aller sur https://guimawaiaproject.sentry.io
2. **Create Project** → créer deux projets :
   - **docling-pwa** (platform: React)
   - **docling-api** (platform: Python/FastAPI)
3. Copier les DSN fournis pour chaque projet

### 2. Configurer les variables d'environnement

| Variable | Emplacement | Description |
|----------|-------------|-------------|
| `SENTRY_DSN` | Backend (api.py, apps/api) | DSN du projet docling-api |
| `VITE_SENTRY_DSN` | Frontend (docling-pwa, apps/pwa) | DSN du projet docling-pwa |

Dans `.env` (racine) :

```env
SENTRY_DSN=https://xxx@xxx.ingest.de.sentry.io/xxx
VITE_SENTRY_DSN=https://xxx@xxx.ingest.de.sentry.io/xxx
```

### 3. Déploiement (Render, Netlify, etc.)

- **Backend** : Ajouter `SENTRY_DSN` dans les variables d'environnement du service
- **Frontend** : Ajouter `VITE_SENTRY_DSN` (préfixe VITE_ pour exposition au build)

## Configuration technique

### Frontend (React 19 + @sentry/react v10)

- **ErrorBoundary** : `Sentry.captureException()` dans `componentDidCatch` pour remonter les erreurs
- **React 19** : `reactErrorHandler` sur `createRoot` (onUncaughtError, onCaughtError, onRecoverableError)
- **Traces** : `tracePropagationTargets` inclut l'URL de l'API pour le tracing distribué
- **Sample rate** : 1.0 en dev, 0.1 en prod

### Backend (FastAPI + sentry-sdk)

- Initialisation conditionnelle si `SENTRY_DSN` présent
- Warning en production si DSN absent
- `traces_sample_rate: 0.1`, `release: docling-agent@3.0.0`

## Erreurs corrigées (audit 2026-03)

| Problème | Correction |
|----------|------------|
| ErrorBoundary ne remontait pas les erreurs à Sentry | Ajout de `Sentry.captureException()` dans `componentDidCatch` |
| React 19 non pris en charge | Ajout de `reactErrorHandler` sur `createRoot` |
| Traces non propagées vers l'API | Configuration de `tracePropagationTargets` |
| Sample rate identique dev/prod | 1.0 en dev, 0.1 en prod |

## Vérification

1. Avec DSN configuré, déclencher une erreur de test :
   ```js
   throw new Error('Sentry Test Error')
   ```
2. Vérifier dans Sentry → Issues que l'erreur apparaît
3. Optionnel : configurer l'upload des source maps (Vite) pour des stack traces lisibles

## Références

- [Sentry React](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry FastAPI](https://docs.sentry.io/platforms/python/integrations/fastapi/)
- MCP Sentry : `user-Sentry` (find_organizations, search_issues, search_events)
