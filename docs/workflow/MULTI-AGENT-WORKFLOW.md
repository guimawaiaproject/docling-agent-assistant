# Flux multi-agents — Projet quelconque

Workflow pour Cursor sur **n'importe quel projet**. Synthèse de [cursor-agents](https://github.com/pridiuksson/cursor-agents) et [APM](https://github.com/sdi2200262/agentic-project-management).

Référence : [.cursor/WORKFLOW.md](../../.cursor/WORKFLOW.md).

---

## Philosophie

| Principe | Application |
|----------|-------------|
| **Spécialisation** | Chaque agent a un rôle précis |
| **Qualité obligatoire** | Valider avant "c'est fait" |
| **Mémoire** | docs/ (pourquoi) + codebase (comment) |
| **Tests réels** | Pas de mock des API externes |
| **Sécurité** | Review obligatoire si critique |

---

## Agents (cursor-agents)

| Agent | Rôle | Quand |
|-------|------|-------|
| **System Architect** | Plan, spec, design, coordination | Features complexes |
| **Feature Developer** | Implémentation, tests | Toute modif code |
| **Security Reviewer** | Revue sécurité, qualité | Auth, endpoints, merge |
| **Context Specialist** | Analyse codebase, patterns | Refactos, intégrations |
| **Docs Writer** | Documentation code-first | Fin de feature |

---

## Flux

```
User → @plan (spec + design)
     → @dev (implémentation)
     → @review (si critique)
     → validate (lint + tests)
     → @docs (mise à jour)
```

---

## Quality Gates (cursor-agents)

1. **Security** : Revue obligatoire pour auth, endpoints, données sensibles
2. **Tests** : CI-Lite (rapide) + Integration (réel) selon projet
3. **Documentation** : Code-first, semantic landmarks

---

## Stage Gate (Docling)

| Stage | Dossier | Action |
|-------|---------|--------|
| Idée | `0_backlog/` | Fichier .md par idée |
| Planning | `1_planning/` | spec.md, design.md |
| Im progress | `2_inprogress/` | Implémentation, implementation_notes.md |
| Livré | `3_completed/` | summary.md |

---

## APM — Projets longs

Si contexte saturé ou projet multi-sessions :

- **Handover** : Documenter dans Memory Log avant nouvelle session
- **Ad-Hoc** : Déléguer debug/research à agent temporaire
- **Manager** : `apm init` pour workflow APM complet

---

## Adapter au projet

- **Paths** : docs/planning/, docs/{feature}/ — adapter selon structure existante
- **Validation** : npm test, pytest, make validate-all, etc.
- **Conventions** : .cursor/rules, README, docs/

---

## Références

- [cursor-agents](https://github.com/pridiuksson/cursor-agents) — process.md, backlog.md, wf-testing.md
- [APM](https://github.com/sdi2200262/agentic-project-management) — Setup Phase, Task Loop, Handover
- [Rapport détaillé](REPORTS/REPOS-ANALYSE-DETAILLEE-2026.md)
