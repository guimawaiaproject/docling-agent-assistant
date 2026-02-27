# Baseline — Docling Fév. 2026

**Date** : 27 février 2026

**Objectif** : Capturer l'état stable du projet avant les modifications du plan de finalisation.

---

## Validation

| Check | Résultat |
|-------|----------|
| ruff (backend) | OK |
| eslint (frontend) | OK |
| pytest | OK |
| vitest | OK |
| validate-skills | OK |
| health-check (API + DB) | OK |

**Commande** : `make validate-all` ou `scripts/validate_all.ps1`

---

## Fonctionnalités vérifiées

- [x] Scan : upload PDF → extraction → produits
- [x] Validation : ajuster produits → batch save
- [x] Catalogue : consultation, filtres
- [x] Devis : export Excel/PDF
- [x] History : liste factures, bouton Voir PDF
- [x] Auth : login, register, JWT

---

## Commit baseline

```
git commit -m "chore: baseline avant plan finalisation"
```
