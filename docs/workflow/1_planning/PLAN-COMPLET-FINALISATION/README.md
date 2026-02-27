# Plan complet — Finalisation Docling en mode senior

**Objectif** : Finir le projet sans régression, sans que les agents cassent le code.

**Principe** : Une étape à la fois. Checkpoint avant chaque phase. Validation obligatoire après chaque modification.

---

## Vue d'ensemble

| Phase | Contenu | Durée estimée |
|-------|---------|---------------|
| **0** | Optimiser les agents (cursor-senior-2026) | 2h |
| **1** | Préparer Docling (règles, baseline) | 1h |
| **2** | Sprint 1 — Urgences (jobs, clés React, etc.) | 1 semaine |
| **3** | Sprint 2 — Priorités hautes | 2 semaines |
| **4** | Sprint 3+ — Moyen terme | Optionnel |

---

## Règles anti-régression (OBLIGATOIRES)

1. **Checkpoint git** avant chaque phase ou tâche majeure
2. **make validate-all** après chaque modification (agent l'exécute)
3. **Une seule chose à la fois** : pas de backend + frontend + config en même temps
4. **Spec avant code** : déplacer en `2_inprogress/` uniquement avec spec validée
5. **Pas de "c'est fait"** sans validation verte

---

## Références

- **[PLAN-A-Z-DETAILLE.md](PLAN-A-Z-DETAILLE.md)** — Plan complet avec agents et outils par tâche
- [spec.md](spec.md) — Détail des phases
- [ETAPES.md](ETAPES.md) — Exécution pas à pas
- [13-PLAN-OPTIMISATION.md](../../13-PLAN-OPTIMISATION.md) — Sprints techniques
- [development-workflow](../../../../.cursor/rules/development-workflow.mdc) — Règles dev
