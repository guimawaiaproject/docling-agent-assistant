# Workflow — Système de dossiers par stage

Structure inspirée de [Chris Dunlop](https://medium.com/realworld-ai-use-cases/cursor-ai-tip-my-folder-system-trick-that-cut-my-requests-down-by-50-7585c8c248dd) pour réduire le contexte et améliorer la collaboration humain-IA.

## Principe

- **4 stages** : backlog → planning → in-progress → completed
- **Stage Gate Prompts** : Cursor charge uniquement le contexte du stage actif (via règles `globs`)
- **Effet** : moins de tokens, réponses plus ciblées, meilleur travail

## Structure

```
docs/workflow/
├── 0_backlog/          # Idées brutes
├── 1_planning/         # Spec + design (STAGE_GATE_PROMPT_PLAN)
├── 2_inprogress/       # Implémentation (STAGE_GATE_PROMPT_PROG)
└── 3_completed/        # Livré (STAGE_GATE_PROMPT_COMPL)
```

## Utilisation

1. **Nouvelle idée** → créer `0_backlog/ma-feature.md`
2. **Prêt à planifier** → déplacer dans `1_planning/ma-feature/`, créer README, spec, design
3. **Prêt à coder** → déplacer dans `2_inprogress/ma-feature/`, implémenter, tenir implementation_notes
4. **Terminé** → déplacer dans `3_completed/ma-feature/`, ajouter summary.md

## Règles Cursor

Quand tu édites un fichier dans un stage, la règle correspondante se charge automatiquement :

- `docs/workflow/1_planning/**` → workflow-planning
- `docs/workflow/2_inprogress/**` → workflow-inprogress
- `docs/workflow/3_completed/**` → workflow-completed
