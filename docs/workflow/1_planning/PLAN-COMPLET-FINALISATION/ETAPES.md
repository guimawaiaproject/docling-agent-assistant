# Étapes — Exécution pas à pas

Guide exécutable. Chaque étape = une action. Ne pas sauter d'étape.

---

## Phase 0 — Optimiser les agents (cursor-senior-2026)

### Étape 0.1
1. Ouvrir `cursor-senior-2026/.cursor/agents/react-specialist.md`
2. Ajouter section "Anti-patterns", "Checklist validation", "Erreurs courantes"
3. Sauvegarder

### Étape 0.2
1. Ouvrir `cursor-senior-2026/.cursor/agents/python-specialist.md`
2. Ajouter sections idem
3. Sauvegarder

### Étape 0.3
1. Ouvrir `cursor-senior-2026/.cursor/agents/fastapi-specialist.md`
2. Ajouter sections idem
3. Sauvegarder

### Étape 0.4
1. Ouvrir `cursor-senior-2026/.cursor/agents/vue-specialist.md`, `typescript-specialist.md`, `migration-2to3.md`
2. Ajouter sections idem (adaptées)
3. Sauvegarder

### Étape 0.5
- [ ] Vérifier AGENTS.md cursor-senior-2026 à jour
- [ ] Commit : `git commit -m "feat(agents): enrichir specialists avec anti-patterns et checklists"`

---

## Phase 1 — Baseline Docling

### Étape 1.1
```bash
cd docling
git status
git add -A
git commit -m "chore: baseline avant plan finalisation"
```

### Étape 1.2
```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts/validate_all.ps1

# Linux/Mac
make validate-all
```
- [ ] Tous les tests verts. Si échec → corriger avant de continuer.

### Étape 1.3
Créer `docs/workflow/2_inprogress/BASELINE-2026.md` avec :
- Date
- Résultat validate-all (OK/échec)
- Liste fonctionnalités vérifiées

---

## Phase 2 — Sprint 1

### Étape 2.1 — Jobs
- [ ] Vérifier : extraction → redémarrage API → status job accessible
- [ ] Si OK : rien à faire. Si KO : implémenter persistance.

### Étape 2.2 — Clés React
1. **Checkpoint** : `git commit -m "checkpoint: avant fix clés React"`
2. Ouvrir `docling-pwa/src/components/CompareModal.jsx`
3. Remplacer toute key instable par id stable
4. Répéter pour ValidationPage, ScanPage
5. **validate-all**
6. Commit si vert

### Étape 2.3 — Storage S3
- [ ] Tester bouton "Voir PDF" sur HistoryPage
- [ ] Si cassé : corriger storage_service + orchestrator

### Étape 2.4 — Circuit-breaker
- [ ] Vérifier implémentation existante
- [ ] Test manuel : clé Gemini invalide → job error après N tentatives

---

## Phase 3 — Sprint 2 (après Sprint 1 terminé)

Pour chaque feature (offline, Factur-X, DevisPage) :
1. Créer spec + design dans `1_planning/<feature>/`
2. Valider spec
3. Déplacer en `2_inprogress/<feature>/`
4. Implémenter
5. validate-all après chaque sous-tâche
6. Déplacer en `3_completed/<feature>/` avec summary.md

---

## Règle d'or

**Ne jamais dire "c'est fait" sans validate-all vert.**
