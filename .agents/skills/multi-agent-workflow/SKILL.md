---
name: multi-agent-workflow
description: Workflow multi-agents Cursor inspiré de cursor-agents et APM. Use when coordinating complex features, planning handoffs, quality gates, or establishing DevOps routine.
---

# Multi-Agent Workflow — Coordination Cursor

Skill basé sur [cursor-agents](https://github.com/pridiuksson/cursor-agents) et [APM](https://github.com/sdi2200262/agentic-project-management).

## Rôle des agents

| Agent | Rôle | Quand |
|-------|------|-------|
| **System Architect** | Plan, spec, design, coordination | Features complexes, décisions architecture |
| **Feature Developer** | Implémentation, tests | Toute modif code |
| **Security Reviewer** | Revue sécurité, qualité | Auth, endpoints, merge critique |
| **Context Specialist** | Analyse codebase, patterns | Refactos, intégrations |
| **Docs Writer** | Documentation code-first | Fin de feature |

## Two-Tier Memory

- **Long-term** : docs/ (ARCHITECTURE, conventions) — le "pourquoi"
- **Short-term** : codebase live — le "comment"

## Quality Gates obligatoires

1. **Security** : Revue obligatoire si auth, endpoints, données sensibles
2. **Tests** : Réels (pas de mock API externes)
3. **Validation** : `make validate-all` avant "c'est fait"

## Flux standard

```
User → @plan (spec + design)
     → @dev (implémentation)
     → @review (si critique)
     → validate (lint + tests)
     → @docs (mise à jour)
```

## Références

- [cursor-agents process.md](https://github.com/pridiuksson/cursor-agents/blob/master/process.md)
- [cursor-agents backlog.md](https://github.com/pridiuksson/cursor-agents/blob/master/backlog.md)
- [APM workflow](https://agentic-project-management.dev/docs/workflow-overview)
- [Rapport détaillé repos](docs/REPORTS/REPOS-ANALYSE-DETAILLEE-2026.md)
