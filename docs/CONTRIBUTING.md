# Contribution — Docling

Workflow de contribution pour développeurs et agents IA.

---

## Principes

1. **Incrémental** : changements petits, validés à chaque étape
2. **Ne pas casser** : `make validate-all` avant de terminer
3. **Une chose à la fois** : un endpoint, un composant, une migration

---

## Avant de modifier

1. **Lire** les fichiers concernés
2. **Vérifier** s'il existe une spec dans `docs/workflow/1_planning/`
3. **Ne pas** supprimer ou réécrire sans comprendre l'existant
4. **Ne pas** changer plusieurs couches en même temps

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

## Revue code

- **Critique** (auth, endpoints, données sensibles) : `make review` ou agent Security Reviewer
- **Standard** : ruff + eslint via `make validate-all`

---

## Références

- [DEVELOPER-ONBOARDING.md](DEVELOPER-ONBOARDING.md)
- [workflow/README.md](workflow/README.md)
- [.cursor/rules/development-workflow.mdc](../.cursor/rules/development-workflow.mdc)
