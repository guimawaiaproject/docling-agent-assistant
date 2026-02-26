# Contribuer à Docling Agent

Merci de votre intérêt pour le projet. Ce guide décrit les conventions à suivre.

## Prérequis

- Python 3.11+
- Node.js 20+
- PostgreSQL 16 (ou branche Neon)

## Installation locale

```bash
# Backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt -r requirements-dev.txt

# Frontend
cd docling-pwa
npm install
```

## Lancer les tests

```bash
# Backend — tests unitaires (rapide, sans serveur)
pytest tests/01_unit -v --tb=short

# Frontend — tests Vitest
cd docling-pwa && npx vitest run

# Tests API (nécessite serveur + DB)
pytest tests/03_api -v --tb=short

# E2E Playwright
playwright install chromium
pytest tests/04_e2e -v -m e2e
```

Tous les tests doivent passer **avant** de soumettre une PR.

## Lint obligatoire

```bash
# Backend
ruff check backend/ api.py

# Frontend
cd docling-pwa && npm run lint
```

Le lint est vérifié en CI. Une PR avec des erreurs de lint sera rejetée.

## Convention de commits

Le projet suit un format strict :

```
<type>(<phase>-<numero>): <description courte>
```

### Types autorisés

| Type         | Usage                                    |
|--------------|------------------------------------------|
| `fix`        | Correction de bug                        |
| `feat`       | Nouvelle fonctionnalité                  |
| `refactor`   | Refactoring sans changement fonctionnel  |
| `perf`       | Amélioration de performance              |
| `test`       | Ajout ou correction de tests             |
| `docs`       | Documentation uniquement                 |
| `chore`      | Maintenance (dépendances, CI, config)    |
| `build`      | Changements de build/packaging           |
| `ci`         | Changements CI/CD                        |
| `ops`        | Changements opérationnels (infra, deploy)|

### Exemples

```
fix(1-2): add rate limiting on auth endpoints
feat(3-0): initialize alembic baseline migration
refactor(7-5): replace div grid with semantic table
docs(8-5): add changelog
```

Pour les hotfixes hors phase :

```
fix(hotfix): correct default model name in process endpoint
```

## Workflow Pull Request

1. **Créer une branche** depuis `dashboard-b2b-v2` :
   ```bash
   git checkout -b fix/description-courte
   ```

2. **Commiter** en suivant la convention ci-dessus (un commit par changement logique).

3. **Vérifier** que tous les tests passent et le lint est propre.

4. **Pousser** et ouvrir une PR vers `dashboard-b2b-v2` :
   ```bash
   git push -u origin fix/description-courte
   ```

5. **Description de PR** : inclure un résumé des changements, les fichiers modifiés, et les critères de validation ("Done when").

## Structure du projet

```
docling-agent-assistant/
├── api.py                    # Routeur FastAPI
├── backend/                  # Services, schémas, config
├── docling-pwa/              # Frontend React (Vite)
├── migrations/               # Alembic
├── tests/                    # Tests par catégorie (01_unit → 08_external)
├── docs/                     # Documentation technique
└── scripts/                  # Scripts utilitaires
```

## Questions ?

Ouvrez une issue GitHub avec le label `question`.
