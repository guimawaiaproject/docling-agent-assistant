# Contribuer à Docling Agent

Merci de votre intérêt pour le projet. Ce guide décrit les conventions à suivre.

---

## Principes

1. **Incrémental** : changements petits, validés à chaque étape
2. **Ne pas casser** : `make validate-all` avant de terminer
3. **Une chose à la fois** : un endpoint, un composant, une migration

---

## Prérequis

- Python 3.11+
- Node.js 20+
- PostgreSQL 16 (ou branche Neon)

---

## Installation locale

```bash
# Backend (uv)
cd apps/api && uv sync

# Frontend
cd apps/pwa && pnpm install
```

---

## Avant de modifier

1. **Lire** les fichiers concernés
2. **Vérifier** s'il existe une spec dans `docs/workflow/1_planning/`
3. **Ne pas** supprimer ou réécrire sans comprendre l'existant
4. **Ne pas** changer plusieurs couches en même temps

---

## Pendant les modifications

1. **Respecter** les conventions (backend, frontend, tests)
2. **Réutiliser** l'existant : composants, services, patterns
3. **Pas de cleanup** en passant — uniquement ce qui est demandé

---

## Après les modifications

**Obligatoire** : exécuter

```bash
make validate-all
```

Si échec → corriger avant de finir.

---

## Lancer les tests

```bash
# Backend (apps/api)
cd apps/api && uv run pytest tests -v --tb=short

# Tests rapides (sans E2E/external)
cd apps/api && uv run pytest tests -v -m "not e2e and not external"

# Frontend
cd apps/pwa && pnpm test

# E2E Playwright (serveur + frontend requis)
playwright install chromium
cd apps/api && uv run pytest tests/e2e -v -m e2e
```

Tous les tests doivent passer **avant** de soumettre une PR.

---

## Lint obligatoire

```bash
# Backend
cd apps/api && uv run ruff check .

# Frontend
cd apps/pwa && pnpm run lint
```

Le lint est vérifié en CI. Une PR avec des erreurs de lint sera rejetée.

---

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

---

## Workflow Pull Request

1. **Créer une branche** depuis `main` :
   ```bash
   git checkout -b fix/description-courte
   ```

2. **Commiter** en suivant la convention ci-dessus (un commit par changement logique).

3. **Vérifier** que tous les tests passent et le lint est propre.

4. **Pousser** et ouvrir une PR vers `main` :
   ```bash
   git push -u origin fix/description-courte
   ```

5. **Description de PR** : inclure un résumé des changements, les fichiers modifiés, et les critères de validation ("Done when").

---

## Workflow par stage

| Stage | Dossier | Action |
|-------|---------|--------|
| Idée | `docs/workflow/0_backlog/` | Fichier .md par idée |
| Planning | `docs/workflow/1_planning/` | spec.md, design.md |
| Implémentation | `docs/workflow/2_inprogress/` | Coder selon spec |
| Livré | `docs/workflow/3_completed/` | summary.md |

**Règle** : pas de code en `2_inprogress/` sans spec validée.

---

## Revue code

- **Critique** (auth, endpoints, données sensibles) : `make review` ou agent Security Reviewer
- **Standard** : ruff + eslint via `make validate-all`

---

## Références

- [Développement](development.md)
- [Workflow](../workflow/README.md)
- [.cursor/rules/development-workflow.mdc](../../.cursor/rules/development-workflow.mdc)
