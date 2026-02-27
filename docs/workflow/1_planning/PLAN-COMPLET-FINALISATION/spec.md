# Spec — Plan complet finalisation Docling

---

## Phase 0 — Optimiser les agents (cursor-senior-2026)

**Objectif** : Enrichir les agents spécialisés pour qu'ils ne cassent pas le projet.

### Étape 0.1 — React Specialist

| Action | Détail |
|--------|--------|
| Fichier | `cursor-senior-2026/.cursor/agents/react-specialist.md` |
| Ajouts | Anti-patterns, checklist validation, erreurs courantes, références |

**Contenu à ajouter :**
- Anti-patterns : useEffect sans deps, props drilling, objets inline dans JSX
- Checklist : pas de console.log, props typées, lint vert
- Erreurs courantes : key={index}, dépendances useEffect manquantes
- Référence : react.dev

### Étape 0.2 — Python Specialist

| Action | Détail |
|--------|--------|
| Fichier | `cursor-senior-2026/.cursor/agents/python-specialist.md` |
| Ajouts | Anti-patterns, checklist, erreurs courantes |

**Contenu à ajouter :**
- Anti-patterns : bare except, print en prod, sync bloquant pour I/O
- Checklist : mypy/ruff vert, pas de any
- Erreurs courantes : oubli await, fuite de connexions

### Étape 0.3 — FastAPI Specialist

| Action | Détail |
|--------|--------|
| Fichier | `cursor-senior-2026/.cursor/agents/fastapi-specialist.md` |
| Ajouts | Anti-patterns, checklist, erreurs courantes |

### Étape 0.4 — Autres agents (Vue, TypeScript, Migration 2to3)

Même structure : anti-patterns + checklist + erreurs courantes.

### Validation Phase 0

- [ ] Tous les agents modifiés
- [ ] AGENTS.md à jour
- [ ] Pas de régression sur cursor-senior-2026

---

## Phase 1 — Préparer Docling (baseline)

**Objectif** : Établir une baseline stable avant toute modification.

### Étape 1.1 — Checkpoint git

```bash
git add -A && git status
git commit -m "chore: baseline avant plan finalisation"
```

### Étape 1.2 — Validation baseline

```bash
make validate-all   # ou scripts/validate_all.ps1 sur Windows
```

- [ ] Lint backend (ruff) vert
- [ ] Lint frontend (eslint) vert
- [ ] Tests backend (pytest) verts
- [ ] Tests frontend (vitest) verts
- [ ] validate-skills vert

### Étape 1.3 — Documenter l'état actuel

Créer `docs/workflow/2_inprogress/BASELINE-2026.md` :
- Liste des tests qui passent
- Fonctionnalités vérifiées manuellement (scan, validation, catalogue, devis)

---

## Phase 2 — Sprint 1 (urgences)

**Règle** : Une tâche à la fois. Checkpoint avant chaque tâche. validate-all après.

### Étape 2.1 — Vérifier jobs persistés

| Statut | Les jobs sont déjà en base (DBManager.create_job, get_job) |
| Action | Vérifier que le test "redémarrage API" passe |
| Checkpoint | `git commit -m "verify: jobs persistence OK"` |

**Tests :**
- [ ] Lancer extraction → redémarrer API → GET status/{job_id} retourne le job

### Étape 2.2 — Fixer clés React

| Fichiers | CompareModal, ValidationPage, ScanPage |
| Problème | key={index} ou key instable |
| Solution | Utiliser id stable (item.id, p.id, ou hash unique) |
| Agent | @react ou /react |

**Checklist :**
- [ ] CompareModal : key sans index
- [ ] ValidationPage : key stable (p._key ?? p.id)
- [ ] ScanPage : key stable
- [ ] make validate-all vert

### Étape 2.3 — Vérifier storage S3

| Statut | storage_service.py existe, orchestrator l'appelle |
| Action | Vérifier bouton "Voir PDF" fonctionne |
| Si cassé | Corriger selon 13-PLAN-OPTIMISATION 1.2 |

### Étape 2.4 — Vérifier circuit-breaker Gemini

| Statut | Implémenté dans api.py |
| Action | Vérifier comportement (5 erreurs → job error) |

---

## Phase 3 — Sprint 2 (priorités hautes)

**Spec avant code** : Pour chaque feature, créer un dossier dans `1_planning/` avec spec.md + design.md, puis déplacer en `2_inprogress/`.

### 3.1 — Mode offline PWA (IndexedDB)

- Créer `1_planning/offline-pwa/spec.md`
- Créer `1_planning/offline-pwa/design.md`
- Valider avec System Architect
- Déplacer en `2_inprogress/offline-pwa/`
- Implémenter par petits incréments

### 3.2 — Support Factur-X

- Spec + design
- Détection PDF Factur-X
- Extraction XML
- Fallback Gemini

### 3.3 — DevisPage : TVA, remise, numéro auto

- Spec courte (4-6h)
- Champs TVA, remise, numéro DEV-2026-XXX

---

## Phase 4 — Sprint 3+ (optionnel)

- Migration SDK google-genai async
- Comparateur prix avancé
- Base communautaire (long terme)

---

## Checklist anti-régression (à chaque tâche)

| Avant | Pendant | Après |
|-------|--------|-------|
| Checkpoint git | Une chose à la fois | make validate-all |
| Lire fichiers concernés | Pas de cleanup en passant | Cocher tests de vérification |
| Spec si nouvelle feature | Réutiliser l'existant | Mettre à jour implementation_notes |

---

## En cas de régression

1. `git diff` pour identifier le changement
2. `git checkout -- <fichier>` ou `git revert` si commit déjà fait
3. Réappliquer le changement en plus petit
4. Valider après chaque micro-changement
