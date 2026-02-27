# Rapport détaillé — Dépôts de référence

**Date** : 27 février 2026  
**Objectif** : Synthèse ligne par ligne des dépôts partagés pour alimenter AGENTS, SKILLS, WORKFLOW, RULES et routine DevOps senior.

---

## 1. awesome-ai-coding-tools

**URL** : https://github.com/ai-for-developers/awesome-ai-coding-tools  
**Type** : Liste curated d'outils IA pour le développement  
**Taille** : ~725 lignes, 20+ catégories

### Structure

| Fichier | Contenu |
|---------|---------|
| readme.md | Liste principale (40 KB) |
| CONTRIBUTING.md | Guide contribution |
| LICENSE | MIT |

### Catégories (extrait)

| Catégorie | Outils clés | Usage |
|-----------|-------------|-------|
| AI Code Assistants & Editors | Cursor, Cody, Windsurf, Aider, Phind, Zed, Claude Desktop | Éditeurs IA, autocomplétion |
| AI App Builders | Bolt.new, Dyad.sh, Lovable, Capacity, Rocket.new | Apps full-stack depuis prompts |
| AI Tools for Developers | Supercode.sh, SpecStory, Task Master, Context7, Memory Bank | Extensions, MCP, workflow |
| AI Code Completion | Copilot, Codeium, Tabnine, Refact.ai, Continue | Autocomplétion |
| Code Review & Refactoring | Qodo, Sourcery, Gito, CodeRabbit, DeepSource | Revue code, qualité |
| Coding Agents | Claude Code, Gemini CLI, Aider, OpenHands, Cline, GPT Engineer | Agents autonomes |
| PR Review Agents | Sweep, Greptile, CodeRabbit, What The Diff | Revue PR |
| Testing & QA | Qodo, Meticulous, TestRigor, Mabl, Applitools, Launchable | Tests automatisés |
| Documentation | Mintlify, Trelent, GPTutor, README-AI | Génération doc |
| MCP Server/Tools | MCP Server Finder, Cursor MCP Directory, PulseMCP | MCP servers |
| DevOps & Infrastructure | Harness, GitLab AI, Datadog, PagerDuty | CI/CD, monitoring |
| Security | Snyk, GitGuardian, Bearer CLI, Semgrep | Vulnérabilités, secrets |

### Points clés pour Docling

- **Context7** : MCP doc à jour pour LLMs
- **Qodo** : Tests + qualité
- **Gito** : Revue code open-source, GitHub Actions
- **Agent Skills** : agentskills.io — format pour étendre les agents

---

## 2. cursor-agents (pridiuksson)

**URL** : https://github.com/pridiuksson/cursor-agents  
**Type** : Template multi-agents pour Cursor (Claude + Gemini CLI + Qwen Code)  
**Philosophie** : Engineering over hacking — code production-ready, pas des démos

### Fichiers analysés

| Fichier | Lignes | Contenu |
|---------|--------|---------|
| readme.md | ~300 | Vue d'ensemble, comparaison, philosophie |
| process.md | 497 | Workflow en action, exemples réels |
| backlog.md | 90 | Roadmap MVP, EPICs, STORYs |
| vs-cursor.md | 220 | Pourquoi Cursor adopte ce workflow |
| wf-testing.md | 290 | Stratégie QA, 3 tiers, quality gates |
| geminicli.md | ~300 | Guide Gemini CLI |
| kiro.md | ~1500 | Guide Kiro (très long) |

### Architecture multi-agents

| Agent | Modèle | Rôle | Quand l'utiliser |
|-------|--------|------|------------------|
| **System Architect** | Claude | Planification stratégique, coordination | Features complexes, décisions architecture |
| **Security Reviewer** | Qwen Code | Revue sécurité, validation architecture | Tout code production, chemins critiques |
| **Context Specialist** | Gemini CLI | Analyse codebase, découverte de patterns | Refactos larges, intégrations complexes |
| **Feature Developer** | Claude | Implémentation, tests | Tout développement |
| **Documentation Writer** | Claude | Transfert de connaissance, maintenance | Fin de feature, changements architecture |

### Principes clés

1. **Two-Tier Memory**
   - **Long-term** : docs stables (ARCHITECTURE.md, agents.md) — le "pourquoi"
   - **Short-term** : codebase live — le "comment"

2. **Quality Gates obligatoires**
   - Security review si critique
   - Tests réels (pas de mock des API externes)
   - Documentation code-first validée

3. **Orchestration explicite**
   - Handoffs déterministes
   - Decision trees, diagrammes Mermaid
   - Pas d'ambiguïté sur les étapes

4. **Stratégie QA (wf-testing.md)**
   - **Tier 1 CI-Lite** : ~60s, bloque merge (lint, unit, config)
   - **Tier 2 Local Integration** : API/DB réels, manuel
   - **Tier 3 Browser** : E2E on-demand (Browserbase MCP)

### Exemple de coordination (process.md)

```
SA (Claude) → GC (Gemini) : "Analyse les patterns API existants"
GC → SA : "3 patterns : RLS auth, Zod validation, error handling"
SA → QC (Qwen) : "Revue sécurité du design endpoint"
QC → SA : "Gaps : rate limiting, sanitization, audit logging"
SA → Intégration → Exemple production-ready
```

---

## 3. agentic-project-management (APM)

**URL** : https://github.com/sdi2200262/agentic-project-management  
**Type** : Framework de gestion de projet avec workflows multi-agents structurés  
**Install** : `npm install -g agentic-pm` puis `apm init`

### Support IDEs

| IDE | Format | Dossier |
|-----|--------|---------|
| Cursor | Markdown | `.cursor/commands` |
| Claude Code | Markdown | `.claude/commands` |
| GitHub Copilot | Markdown | `.github/prompts` |
| Windsurf | Markdown | `.windsurf/workflows` |
| Qwen Code | TOML | `.qwen/commands` |
| Gemini CLI | TOML | `.gemini/commands` |

### Phases du workflow

#### Setup Phase (obligatoire, linéaire)

1. **Context Synthesis & Discovery**
   - 4 Question Rounds : Vision → Technique → Process → Validation
   - Cycles itératifs obligatoires
   - Approval explicite avant Project Breakdown

2. **Project Breakdown & Plan Creation**
   - Domain Analysis → Phase Definition → Task Breakdown → Final Review
   - Chat-to-File (forced chain-of-thought)
   - Produit `Implementation_Plan.md`

3. **AI Review & Refinement** (optionnel)
   - Détecte task packing, pattern matching
   - Critique structurale

4. **Setup Completion**
   - User approve → `/apm-2-initiate-manager`

#### Task Loop Phase

1. **Manager Initialization**
   - Lit `Memory_Root.md` (premier session vs handover)
   - Lit guides + Implementation_Plan
   - User autorise avant assignation

2. **Task Assignment Prompt Creation**
   - Manager analyse tâche suivante
   - Construit Meta-Prompt avec contexte
   - Same-Agent vs Cross-Agent Dependencies
   - User copy-paste vers Implementation Agent

3. **Task Execution**
   - Multi-Step : confirmation à chaque checkpoint
   - Single-Step : atomique, un coup
   - Context scope serré

4. **Memory Logging & Review**
   - Implementation Agent → Memory Log
   - Final Task Report → User → Manager
   - Manager : Continue / Request Corrections / Update Plan

5. **Error Handling (Ad-Hoc Delegation)**
   - Blocage après 3 tentatives → Delegation Prompt
   - Ad-Hoc Agent (Research, Debug) → résout → retour

### Types d'agents APM

| Agent | Rôle | Contexte | Phase |
|-------|------|----------|-------|
| **Setup Agent** | Architecte | Vision complète, PRDs | Début projet |
| **Manager Agent** | Coordinateur | Plan, Memory Logs | Tout le projet |
| **Implementation Agent** | Builder | Task Assignment uniquement | Par assignation |
| **Ad-Hoc Agent** | Spécialiste temporaire | Contexte isolé | Debug, Research |

### Handover Procedures

- Trigger : ~80-90% contexte ou dégradation
- Entre tâches uniquement (jamais pendant exécution)
- Deux artefacts : Handover Prompt + Handover File
- Nouvel agent lit, résume, user vérifie

---

## 4. Synthèse comparative

| Aspect | cursor-agents | APM |
|--------|---------------|-----|
| **Focus** | Quality gates, spécialisation modèles | Gestion contexte, handover |
| **Agents** | 5 (SA, Security, Context, Dev, Docs) | 4 (Setup, Manager, Impl, Ad-Hoc) |
| **Mémoire** | Two-tier (docs + code) | Memory Logs, Handover File |
| **Tests** | 3 tiers, real API | Pas de spec dédiée |
| **Setup** | Manuel (find-replace) | `apm init` automatisé |
| **IDE** | Cursor, Gemini CLI, Qwen | 10+ IDEs supportés |

### Complémentarité

- **cursor-agents** : excellente pour quality gates, security, patterns Cursor
- **APM** : excellente pour projets longs, handover, gestion contexte
- **Docling** : combine les deux — Stage Gate (planning/inprogress/completed) + quality gates + validate-all

---

## 5. Recommandations pour Docling

1. **Enrichir les agents** avec les rôles cursor-agents (Context Specialist = Gemini CLI)
2. **Créer skill multi-agent-workflow** référençant process.md, backlog.md
3. **Règle senior-devops** : routine validate → review → docs
4. **Workflow unifié** : Stage Gate + Quality Gates + APM handover si projet long
5. **ai-library** : extraire le contenu réel d'awesome-ai-coding-tools (liens, descriptions)
