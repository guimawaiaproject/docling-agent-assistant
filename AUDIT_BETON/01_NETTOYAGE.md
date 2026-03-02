# 🧹 01 — NETTOYAGE PROJET 2026
# Exécuté le 1er mars 2026 — Phase 01 Audit Bêton Docling

---

## RAPPORT D'EXÉCUTION

### PHASE N1 — FICHIERS PARASITES

| Catégorie | Trouvés | Action | Justification |
|-----------|---------|--------|---------------|
| Anciens audits | AUDIT_BETON/, .cursor/PROMPT AUDIT/, .cursor/commands/audit-* | **GARDER** | Rapports et prompts actifs |
| Fichiers vides | 0 significatif | — | — |
| __pycache__ / .pyc | backend/, tests/, migrations/ | **NETTOYER** | Déjà dans .gitignore, régénérés à l'exécution |
| Lockfiles concurrents | package-lock.json + pnpm-lock.yaml | **🟠 CORRIGER** | Un seul gestionnaire (choisir pnpm) |
| .env committé | 0 | ✅ | — |
| dist/ committé | 0 | ✅ | — |

### PHASE N2 — DÉPENDANCES

**Backend (requirements.txt)** :
| Package | Version | Statut 2026 |
|---------|---------|-------------|
| fastapi | 0.115.0 | ✅ |
| pydantic | 2.9.2 | ✅ v2 |
| asyncpg | 0.31.0 | ✅ |
| httpx | >=0.27.0 | ✅ |
| PyJWT | 2.10.1 | ✅ |
| argon2-cffi | 25.1.0 | ✅ |
| boto3 | 1.40.61 | ⚪ sync (aiobotocore pour async) |
| ruff | (dev pyproject) | ✅ |

**Frontend (package.json)** :
| Package | Statut 2026 |
|---------|-------------|
| react | 19.2.4 ✅ |
| react-router-dom | 7.13.1 ✅ |
| eslint | 9.x (legacy → Biome) |
| axios | Présent (TanStack Query recommandé) |
| zustand | 5.0.11 ✅ |
| tailwindcss | 3.4.17 (v4 recommandé) |

### PHASE N3 — CONFIGS

| Config | Présent | Action |
|--------|---------|--------|
| pyproject.toml | ✅ | Ruff, pytest configurés |
| [tool.ruff] | ✅ | OK |
| eslint.config.js | ✅ | ESLint flat config |
| biome.json | ❌ | Migrer ESLint+Prettier → Biome |
| .prettierrc | ❌ | — |

### PHASE N4 — .gitignore

✅ Complet : __pycache__, .env, .cursor/, dist/, .pytest_cache/, .ruff_cache/, node_modules/

### GATE N — NETTOYAGE

| Critère | Status |
|---------|--------|
| Build OK | À vérifier (pnpm build) |
| Import backend OK | À vérifier |
| Un seul lockfile | ❌ FAIL — package-lock.json + pnpm-lock.yaml |
| .gitignore complet | ✅ PASS |

**ACTION REQUISE** : Supprimer `docling-pwa/package-lock.json` pour n'utiliser que pnpm.

---

## BILAN

| Catégorie | Trouvés | Supprimés | Gardés |
|-----------|---------|-----------|--------|
| Lockfiles concurrents | 2 | 0 | 1 à garder (pnpm) |
| Configs legacy | ESLint | 0 | Migrer vers Biome (backlog) |
| __pycache__ | ~20 | Nettoyables | .gitignore OK |

**STATUS GATE N** : ⚠️ CONDITIONNEL — Corriger lockfiles avant PASS
**→ Si lockfiles corrigés : continuer vers 02_CARTOGRAPHIE.md**
