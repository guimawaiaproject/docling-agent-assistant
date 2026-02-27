# Plan complet A à Z — Finalisation Docling

Plan détaillé avec agents spécialisés et outils à invoquer pour chaque tâche.

---

## Inventaire des ressources

### Agents (cursor-senior-2026 + Docling)

| Agent | Commande | Usage |
|-------|----------|-------|
| System Architect | `/plan` | Spec, design, décomposition |
| Feature Developer | `/dev` | Implémentation générique |
| Backend Specialist | `/backend` | API, DB, services |
| Frontend Specialist | `/frontend` | UI, composants |
| React Specialist | `/react` | Composants React, hooks |
| Python Specialist | `/python` | Code Python, async |
| FastAPI Specialist | `/fastapi` | Endpoints, Pydantic |
| Security Reviewer | `/review` | Auth, endpoints critiques |
| Test Architect | `/test` | Stratégie, génération tests |
| Context Specialist | @context-specialist | Analyse codebase |
| Docs Writer | @docs-writer | Documentation |
| Migration Assistant | @migration-assistant | Migrations Alembic |

### Skills (à activer)

| Skill | Projet | Quand |
|-------|--------|-------|
| docling-factures | Docling | Extraction, API, pipeline |
| neon-postgres | Docling | DB, migrations |
| git-checkpoint | cursor-senior | Avant modifs |
| verification-before-completion | cursor-senior | Avant "c'est fait" |
| multi-agent-workflow | Docling | Coordination |

### Scripts (Docling)

| Script | Usage |
|--------|-------|
| `scripts/validate_all.ps1` | Lint + tests + skills (Windows) |
| `scripts/validate_all.sh` | Idem (Linux/Mac) |
| `scripts/health_check.py` | Health API + DB |
| `scripts/validate_env.py` | Variables .env |
| `scripts/validate_skills.py` | Format SKILL.md |
| `scripts/review.sh` | Ruff + gito |

### Scripts (cursor-senior-2026)

| Script | Usage |
|--------|-------|
| `scripts/git-checkpoint.sh` | Commit avant modifs |
| `scripts/pre-modif-check.sh` | État git avant modif |
| `scripts/verify-before-completion.sh` | Vérification avant fin |
| `scripts/project-profile.sh` | Profil projet |
| `scripts/context-builder.sh` | Fichiers pertinents |

### Commandes Make (Docling)

| Cible | Usage |
|-------|-------|
| `make validate-all` | Validation complète |
| `make routine` | health-check + validate-all |
| `make review` | Revue code |
| `make validate-skills` | Valider skills |
| `make health-check` | API + DB |
| `make migrate` | alembic upgrade head |

### Prompts (cursor-senior-2026)

| Fichier | Usage |
|---------|-------|
| `docs/prompts/SESSION-START.md` | Début session |
| `docs/prompts/EXECUTION-PRE.md` | Checklist avant modif |
| `docs/prompts/EXECUTION-POST.md` | Checklist après modif |
| `docs/prompts/AUDIT-SECURITY.md` | Audit sécurité |

---

## Phase 0 — Préparation (cursor-senior-2026)

**Objectif** : S'assurer que les agents sont optimisés et que le framework est prêt.

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 0.1 | - | - | `/checkpoint` ou `git-checkpoint.sh` | Checkpoint git avant modification |
| 0.2 | - | - | Lire react-specialist.md | Vérifier anti-patterns, checklist présents |
| 0.3 | - | - | Idem pour python, fastapi, vue, typescript, migration-2to3 | Tous agents enrichis |
| 0.4 | - | - | `git commit` | Commit Phase 0 |

---

## Phase 1 — Baseline Docling

**Objectif** : Établir une baseline stable avant toute modification.

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 1.1 | - | - | `/checkpoint` ou `scripts/git-checkpoint.sh` | Checkpoint git |
| 1.2 | - | - | `make routine` ou `scripts/validate_all.ps1` | Validation complète |
| 1.3 | - | - | `scripts/health_check.py` | Vérifier API + DB |
| 1.4 | Docs Writer | @docs-writer | [BASELINE-2026.md](../../2_inprogress/BASELINE-2026.md) | Remplir baseline avec résultats |
| 1.5 | - | - | `git commit -m "chore: baseline avant plan finalisation"` | Commit baseline |

---

## Phase 2 — Sprint 1 (urgences)

### 2.1 Jobs persistés

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 2.1.1 | - | - | `/checkpoint` | Checkpoint avant |
| 2.1.2 | Backend Specialist | `/backend` | Skill `docling-factures` | Vérifier DBManager.create_job, get_job |
| 2.1.3 | - | - | Test manuel : extraction → redémarrage API → GET status | Vérifier persistance |
| 2.1.4 | - | - | `make validate-all` | Validation |
| 2.1.5 | - | - | `git commit` | Si OK |

### 2.2 Fixer clés React

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 2.2.1 | - | - | `/checkpoint` | Checkpoint |
| 2.2.2 | React Specialist | `/react` | CompareModal, ValidationPage, ScanPage | Remplacer key instable par id stable |
| 2.2.3 | - | - | Skill `verification-before-completion` | Avant de terminer |
| 2.2.4 | - | - | `make validate-all` | Validation |
| 2.2.5 | - | - | `git commit -m "fix: clés React stables"` | Commit |

### 2.3 Storage S3

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 2.3.1 | - | - | `/checkpoint` | Checkpoint |
| 2.3.2 | Python Specialist | `/python` | storage_service.py | Vérifier/corriger upload S3 |
| 2.3.3 | FastAPI Specialist | `/fastapi` | orchestrator.py, api.py | Intégration upload après extraction |
| 2.3.4 | - | - | `make validate-all` | Validation |
| 2.3.5 | - | - | Test manuel : bouton "Voir PDF" | Vérifier |

### 2.4 Circuit-breaker Gemini

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 2.4.1 | - | - | `/checkpoint` | Checkpoint |
| 2.4.2 | Python Specialist | `/python` | api.py (_GeminiCircuitBreaker) | Vérifier implémentation |
| 2.4.3 | - | - | Test : clé Gemini invalide → job error après N tentatives | Vérifier |
| 2.4.4 | - | - | `make validate-all` | Validation |

---

## Phase 3 — Sprint 2 (priorités hautes)

**Règle** : Spec avant code. Pour chaque feature : créer dossier `1_planning/<feature>/` avec spec + design.

### 3.1 Mode offline PWA (IndexedDB)

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 3.1.1 | System Architect | `/plan` | offline-pwa/ | Créer spec.md, design.md |
| 3.1.2 | - | - | STAGE_GATE_PROMPT_PLAN | Valider spec |
| 3.1.3 | - | - | Déplacer en 2_inprogress/offline-pwa/ | Prêt à coder |
| 3.1.4 | Frontend Specialist | `/frontend` | IndexedDB, Service Worker | Implémenter file d'attente |
| 3.1.5 | React Specialist | `/react` | Composants offline, indicateur sync | UI |
| 3.1.6 | - | - | `make validate-all` après chaque sous-tâche | Validation incrémentale |
| 3.1.7 | Docs Writer | @docs-writer | summary.md | Déplacer en 3_completed/ |

### 3.2 Support Factur-X

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 3.2.1 | System Architect | `/plan` | factur-x/ | spec.md, design.md |
| 3.2.2 | Python Specialist | `/python` | facturx_extractor.py | Détection/extraction XML |
| 3.2.3 | Backend Specialist | `/backend` | orchestrator.py | Intégration fallback Gemini |
| 3.2.4 | - | - | Skill docling-factures | Vérifier pipeline |
| 3.2.5 | - | - | `make validate-all` | Validation |

### 3.3 DevisPage : TVA, remise, numéro auto

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 3.3.1 | System Architect | `/plan` | devis-tva/ | spec courte |
| 3.3.2 | React Specialist | `/react` | DevisPage.jsx | Champs TVA, remise, numéro DEV-2026-XXX |
| 3.3.3 | - | - | devisGenerator.js | Calcul total TTC |
| 3.3.4 | - | - | `make validate-all` | Validation |

---

## Phase 4 — Sprint 3+ (optionnel)

### 4.1 Migration SDK google-genai async

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 4.1.1 | Python Specialist | `/python` | gemini_service.py | Migrer vers client.aio |
| 4.1.2 | - | - | Supprimer asyncio.to_thread() | Validation |
| 4.1.3 | - | - | `make validate-all` | Validation |

### 4.2 Comparateur prix avancé

| Étape | Agent | Commande | Outil | Action |
|-------|-------|----------|-------|--------|
| 4.2.1 | System Architect | `/plan` | spec + design | Graphiques évolution |
| 4.2.2 | React Specialist | `/react` | CompareModal | UI avancée |
| 4.2.3 | Backend Specialist | `/backend` | Table prix_historique | API |

---

## Règles anti-régression (chaque tâche)

- **Avant** : /checkpoint, lire fichiers, spec si nouvelle feature
- **Pendant** : Une chose à la fois, agent spécialisé, pas de cleanup en passant
- **Après** : verification-before-completion, make validate-all, cocher tests

---

## Ordre d'exécution recommandé

1. **Phase 0** : cursor-senior-2026 (agents déjà optimisés)
2. **Phase 1** : Baseline Docling
3. **Phase 2** : Sprint 1 (2.1 → 2.2 → 2.3 → 2.4)
4. **Phase 3** : Sprint 2 (3.1 → 3.2 → 3.3)
5. **Phase 4** : Optionnel

---

## Références

- [spec.md](spec.md)
- [ETAPES.md](ETAPES.md)
- [13-PLAN-OPTIMISATION.md](../../13-PLAN-OPTIMISATION.md)
- [AGENTS.md](../../../../AGENTS.md)
