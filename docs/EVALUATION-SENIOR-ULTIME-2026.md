# 🏆 ÉVALUATION SENIOR ULTIME EXHAUSTIVE
# Docling Agent v3 — Tous les fronts simultanément
# Standard : Staff Engineer / Principal Architect 2026

**Date :** 26 février 2026
**Méthode :** Lecture exhaustive du code source, vérification des audits précédents, analyse delta

---

## RÉSULTAT PAR AXE

### AXE 1 — SÉCURITÉ : 52/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 1.1 Auth & Authz | 12/20 | Isolation multi-tenant cassée (produits/factures partagés) |
| 1.2 Validation inputs | 12/15 | Longueur OK sur register/login. Pas de validation min password |
| 1.3 Injection & XSS | 11/15 | ILIKE wildcards non échappés. Pas de CSP |
| 1.4 Cryptographie | 8/10 | Argon2id, JWT HS256. Pas de rotation token |
| 1.5 Config & Secrets | 7/10 | JWT_SECRET validé. .env.example valeur faible |
| 1.6 Dépendances | 6/10 | esbuild CVE. xlsx→exceljs migré ✅ |
| 1.7 Infrastructure | 5/10 | Pas de CSP, HSTS, X-Frame-Options. Docker non-root ✅ |
| 1.8 OWASP Top 10 | 3/10 | A01 Broken Access Control majeur |

**Problèmes détectés :**

[PROBLÈME 1.1] — 🔴 CRITIQUE
📍 Fichier : `backend/schema_neon.sql`, `backend/core/db_manager.py`
🔍 Problème : Les tables `produits` et `factures` n'ont **pas de colonne user_id**. Tous les utilisateurs authentifiés voient le même catalogue et le même historique.
⚠️ Impact : Fuite de données entre utilisateurs. Multi-tenant impossible.
✅ Solution : Ajouter `user_id INTEGER REFERENCES users(id)` à produits et factures. Migrer les données existantes. Filtrer toutes les requêtes par user_id.

[PROBLÈME 1.2] — 🟠 MAJEUR
📍 Fichier : `backend/core/db_manager.py` lignes 236-251
🔍 Problème : Les paramètres `search` et `fournisseur` passés à ILIKE contiennent `%` et `_` sans échappement. Un utilisateur peut injecter `%` pour matcher tout.
⚠️ Impact : Recherche qui retourne plus de résultats que prévu.
✅ Solution : `term.replace("%", "\\%").replace("_", "\\_")` avant utilisation dans ILIKE.

[PROBLÈME 1.3] — 🟠 MAJEUR
📍 Fichier : `docling-pwa/index.html`
🔍 Problème : Aucun Content-Security-Policy, X-Frame-Options, ou HSTS défini.
⚠️ Impact : Vulnérable aux attaques XSS, clickjacking.
✅ Solution : Ajouter meta CSP ou headers via serveur. `X-Frame-Options: DENY`, `Strict-Transport-Security`.

[PROBLÈME 1.4] — 🟡 MINEUR
📍 Fichier : `docling-pwa/package.json`
🔍 Problème : `workbox-window` en dépendance directe mais jamais importé. `vitest` en dependencies au lieu de devDependencies.
⚠️ Impact : Bundle alourdi. Confusion.
✅ Solution : Supprimer workbox-window. Déplacer vitest en devDependencies.

[PROBLÈME 1.5] — 🟡 MINEUR
📍 Fichier : `docling-pwa/src/services/apiClient.js`
🔍 Problème : Token JWT stocké dans localStorage. Vulnérable en cas de XSS.
⚠️ Impact : Vol de session si script malveillant injecté.
✅ Solution : Privilégier httpOnly cookies côté backend. Minimiser surface XSS (CSP stricte).

---

### AXE 2 — ARCHITECTURE & CODE QUALITY : 68/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 2.1 Séparation responsabilités | 16/20 | API → Service → DB correct. Orchestrator propre |
| 2.2 SOLID | 14/20 | SRP globalement respecté. DIP partiel |
| 2.3 Code mort & duplication | 10/15 | workbox-window inutilisé. serializers modifie in-place |
| 2.4 Gestion erreurs | 12/15 | Erreurs propagées. Pas d'erreurs silencieuses |
| 2.5 Maintenabilité | 13/15 | Nommage cohérent. Config centralisée |
| 2.6 Patterns | 13/15 | Async/await cohérent. ErrorBoundary présent |

**Problèmes détectés :**

[PROBLÈME 2.1] — 🟠 MAJEUR
📍 Fichier : `backend/core/db_manager.py` lignes 72-75
🔍 Problème : `_upsert_params` utilise `float(product.get("prix_brut_ht") or 0)`. Si Gemini retourne `"N/A"` ou une chaîne non numérique, `float("N/A")` lève ValueError.
⚠️ Impact : Crash lors du batch save si produit mal formé.
✅ Solution : Créer `_safe_float(val, default=0.0)` avec try/except. Utiliser partout.

[PROBLÈME 2.2] — 🟠 MAJEUR
📍 Fichier : `backend/utils/serializers.py` lignes 7-17
🔍 Problème : `serialize_row` modifie le dict **in-place**. Risque de mutation partagée si objet réutilisé.
⚠️ Impact : Données corrompues en cas de cache ou réutilisation.
✅ Solution : `def serialize_row(row): return {k: _serialize_val(v) for k, v in row.items()}` (copie).

[PROBLÈME 2.3] — 🟡 MINEUR
📍 Fichier : `docling-pwa/src/pages/ValidationPage.jsx` ligne 39
🔍 Problème : `handleValidate` envoie `{ produits: products }` sans le champ `source`. Le backend utilise `source: "pc"` par défaut. Les produits scannés en mobile sont enregistrés comme "pc".
⚠️ Impact : Statistiques source incorrectes.
✅ Solution : Ajouter `source: getSource()` (comme ScanPage) dans le payload.

---

### AXE 3 — UX/UI : 58/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 3.1 Cohérence visuelle | 12/15 | Design system cohérent. Tailwind uniforme |
| 3.2 Navigation & IA | 8/15 | Pas de command palette. Pas de breadcrumbs |
| 3.3 États & feedback | 10/20 | Empty states sans CTA. Pas de skeleton loader |
| 3.4 Formulaires | 12/15 | Labels, validation. Autofocus partiel |
| 3.5 Mobile & responsive | 10/15 | Bottom nav. Touch targets corrects |
| 3.6 Accessibilité | 8/10 | ARIA partiel. Focus visible |
| 3.7 Onboarding | 5/10 | Aucun onboarding. Pas de tooltips |

**Problèmes détectés :**

[PROBLÈME 3.1] — 🟠 FRICTION
📍 Fichier : `docling-pwa/src/pages/CataloguePage.jsx` lignes 363-367
🔍 Problème : Empty state "Aucun produit trouvé" sans CTA pour scanner.
⚠️ Impact : Utilisateur ne sait pas qu'il doit d'abord scanner des factures.
✅ Solution : "Votre catalogue est vide. Scannez une facture pour commencer." + bouton "Scanner" → /scan.

[PROBLÈME 3.2] — 🟠 FRICTION
📍 Fichier : `docling-pwa/src/pages/HistoryPage.jsx` lignes 159-164
🔍 Problème : Empty state "Aucune facture traitée pour l'instant" sans CTA.
⚠️ Impact : Même problème — pas de guidance.
✅ Solution : "Aucune facture encore. Scannez votre première facture." + CTA vers /scan.

[PROBLÈME 3.3] — 🟠 FRICTION
📍 Fichier : `docling-pwa/src/pages/ScanPage.jsx` ligne 218
🔍 Problème : `noClick: true` sur useDropzone. Le clic sur la zone n'ouvre pas le sélecteur de fichiers.
⚠️ Impact : Découvrabilité réduite. L'utilisateur doit trouver "Parcourir les fichiers".
✅ Solution : `noClick: false` pour que le clic ouvre le picker.

[PROBLÈME 3.4] — 🟡 POLISH
📍 Fichier : Global
🔍 Problème : Pas de command palette (cmd+K). Pas de breadcrumbs sur pages profondes.
⚠️ Impact : Power users frustrés. Perte de repères.
✅ Solution : Implémenter cmd+K avec "Nouveau scan", "Aller au catalogue", etc. Breadcrumb sur Validation, Devis.

---

### AXE 4 — PERFORMANCE : 72/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 4.1 Web Vitals | 16/25 | Pas de mesure LCP/INP/CLS. Bundle non audité |
| 4.2 Backend | 18/25 | Index présents. Pas de N+1. Pool OK. Pas de cache statique |
| 4.3 Frontend | 19/25 | Code splitting par route. Virtualisation catalogue. exceljs |
| 4.4 Réseau | 19/25 | Pagination cursor. AbortController. Pas de retry backoff |

**Problèmes détectés :**

[PROBLÈME 4.1] — 🟡 MINEUR
📍 Fichier : `docling-pwa/`
🔍 Problème : Pas de mesure Web Vitals (LCP, INP, CLS) en production.
⚠️ Impact : Impossible de détecter les régressions UX.
✅ Solution : Intégrer web-vitals ou Sentry Performance. Dashboard Lighthouse CI.

[PROBLÈME 4.2] — 🟡 MINEUR
📍 Fichier : `docling-pwa/src/services/apiClient.js`
🔍 Problème : Pas de retry avec exponential backoff sur erreurs réseau.
⚠️ Impact : Échec immédiat sur instabilité réseau.
✅ Solution : axios-retry ou interceptor avec retry(3, backoff).

---

### AXE 5 — TESTS & QUALITÉ : 55/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 5.1 Couverture | 12/25 | Pas de % enforce. Tests E2E présents |
| 5.2 Qualité tests | 14/25 | Faker, fixtures réelles. Pas de sleep |
| 5.3 Types de tests | 14/25 | Unit, intégration, E2E, security. Pas de perf |
| 5.4 CI Quality Gates | 15/25 | Lint, test, build. Pas de coverage min. Pas de npm/pip audit |

**Problèmes détectés :**

[PROBLÈME 5.1] — 🟠 MAJEUR
📍 Fichier : `.github/workflows/ci.yml`
🔍 Problème : Pas de quality gate sur la couverture. Pas de `npm audit` ni `pip-audit` dans le pipeline.
⚠️ Impact : Vulnérabilités et régressions de couverture non détectées.
✅ Solution : Ajouter `pytest --cov --cov-fail-under=60`. `npm audit --audit-level=high`. `pip-audit`.

[PROBLÈME 5.2] — 🟡 MINEUR
📍 Fichier : `docling-pwa/`
🔍 Problème : Vitest configuré mais couverture non exécutée en CI.
⚠️ Impact : Tests frontend optionnels.
✅ Solution : Ajouter job `npm run test:coverage` dans CI. Fail si coverage < seuil.

---

### AXE 6 — DEVOPS & OBSERVABILITÉ : 58/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 6.1 CI/CD | 14/25 | Lint, test, build. Pas de deploy auto. Pas de feature flags |
| 6.2 Monitoring | 12/25 | Sentry optionnel. Pas d'uptime. Pas de dashboard |
| 6.3 Logging | 14/25 | Logs structurés. Pas de request_id. Niveaux corrects |
| 6.4 Infrastructure | 18/25 | Health check. Graceful shutdown. Docker non-root. Backup non documenté |

**Problèmes détectés :**

[PROBLÈME 6.1] — 🟠 MAJEUR
📍 Fichier : `.github/workflows/ci.yml`
🔍 Problème : Pas de déploiement automatique. Pas de staging/prod séparés dans le workflow.
⚠️ Impact : Déploiement manuel. Risque d'erreur.
✅ Solution : Ajouter workflow deploy sur push main. Environnements staging/prod.

[PROBLÈME 6.2] — 🟡 MINEUR
📍 Fichier : `api.py`
🔍 Problème : Sentry initialisé si DSN présent, mais pas obligatoire. Pas de métriques métier (scans/jour).
⚠️ Impact : Monitoring incomplet en prod.
✅ Solution : Rendre SENTRY_DSN obligatoire en prod. Ajouter métriques custom.

---

### AXE 7 — DONNÉES & FIABILITÉ : 48/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 7.1 Intégrité | 10/25 | Pas de user_id. Contraintes OK. Migrations mixtes |
| 7.2 Cohérence | 12/25 | Types cohérents. Enums partiels. Decimal utilisé |
| 7.3 Cas limites | 12/25 | float() crash. Gemini mal formé partiellement géré |
| 7.4 Migrations | 14/25 | Alembic + run_migrations inline. Downgrade présent |

**Problèmes détectés :**

[PROBLÈME 7.1] — 🔴 CRITIQUE
📍 Fichier : `backend/schema_neon.sql`, `backend/core/db_manager.py`
🔍 Problème : `produits` et `factures` sans user_id. Données partagées entre tous les utilisateurs.
⚠️ Impact : Impossible d'isoler les données par utilisateur. Multi-tenant cassé.
✅ Solution : Migration Alembic ajoutant user_id. Rétrocompatibilité : user_id NULL = données legacy. Nouveaux inserts avec user_id.

[PROBLÈME 7.2] — 🟠 MAJEUR
📍 Fichier : `backend/core/db_manager.py`
🔍 Problème : `run_migrations()` dans lifespan exécute des ALTER/CREATE en parallèle d'Alembic. Drift possible.
⚠️ Impact : Schéma code vs schéma DB peut diverger.
✅ Solution : Unifier : soit tout via Alembic, soit tout via run_migrations. Documenter la stratégie.

---

### AXE 8 — PRODUCT & BUSINESS LOGIC : 70/100

**Sous-scores :**

| Domaine | Score | Points négatifs |
|---------|-------|-----------------|
| 8.1 Complétude | 16/25 | Login/Register ✅. Auth feature flag. Pas de dead-ends |
| 8.2 Valeur utilisateur | 17/25 | Scan→Validation→Catalogue fonctionnel. Onboarding manquant |
| 8.3 Robustesse métier | 18/25 | TVA, remises. Calculs corrects. Export Excel/CSV/PDF |
| 8.4 Scalabilité business | 19/25 | Pagination. Limit 500 Devis. Multi-tenant à implémenter |

**Problèmes détectés :**

[PROBLÈME 8.1] — 🟠 MAJEUR
📍 Fichier : `docling-pwa/src/config/features.js`
🔍 Problème : `AUTH_REQUIRED` par défaut false. L'app peut être utilisée sans login.
⚠️ Impact : En prod multi-utilisateur, risque de laisser AUTH_REQUIRED=false par erreur.
✅ Solution : En prod, exiger AUTH_REQUIRED=true. Ou inverser : AUTH_OPTIONAL pour désactiver.

[PROBLÈME 8.2] — 🟡 MINEUR
📍 Fichier : `docling-pwa/src/config/api.js`
🔍 Problème : Si VITE_API_URL non défini en prod, fallback `''` avec console.warn. Build peut passer.
⚠️ Impact : Requêtes API vers mauvaise origine.
✅ Solution : `if (import.meta.env.PROD && !_env) throw new Error('VITE_API_URL requis')`.

---

## SCORECARD GLOBAL

| Axe | Domaine | Score /100 | Niveau |
|-----|---------|------------|--------|
| 1 | Sécurité | 52 | 🟠 |
| 2 | Architecture | 68 | 🟡 |
| 3 | UX/UI | 58 | 🟠 |
| 4 | Performance | 72 | 🟡 |
| 5 | Tests | 55 | 🟠 |
| 6 | DevOps | 58 | 🟠 |
| 7 | Données | 48 | 🟠 |
| 8 | Product | 70 | 🟡 |
| | **GLOBAL** | **60/100** | 🟠 |

Légende : 🔴 <50 | 🟠 50-69 | 🟡 70-84 | 🟢 85+

---

## LISTE EXHAUSTIVE DES PROBLÈMES (tri par sévérité)

| # | Axe | Sévérité | Fichier | Problème | Effort |
|---|-----|----------|---------|----------|--------|
| 1 | Sécu/Data | 🔴 | schema_neon.sql, db_manager | produits/factures sans user_id — données partagées | XL |
| 2 | Sécu | 🟠 | db_manager | ILIKE wildcards % _ non échappés | S |
| 3 | Sécu | 🟠 | index.html | Pas de CSP, HSTS, X-Frame-Options | M |
| 4 | Data | 🟠 | db_manager | float() crash si Gemini retourne "N/A" | S |
| 5 | Archi | 🟠 | serializers.py | serialize_row modifie in-place | S |
| 6 | UX | 🟠 | CataloguePage, HistoryPage | Empty states sans CTA | S |
| 7 | UX | 🟠 | ScanPage | noClick: true sur dropzone | XS |
| 8 | Product | 🟠 | api.js | VITE_API_URL non validé en prod | S |
| 9 | Product | 🟠 | features.js | AUTH_REQUIRED false par défaut | S |
| 10 | UX | 🟠 | ValidationPage | source non envoyé au batch | S |
| 11 | Tests | 🟠 | ci.yml | Pas de coverage gate, npm/pip audit | M |
| 12 | DevOps | 🟠 | ci.yml | Pas de deploy auto | L |
| 13 | Data | 🟠 | db_manager | run_migrations + Alembic mélangés | M |
| 14 | Sécu | 🟡 | package.json | workbox-window inutilisé, vitest en deps | XS |
| 15 | Sécu | 🟡 | apiClient | Token localStorage (XSS) | M |
| 16 | UX | 🟡 | Global | Pas de command palette, breadcrumbs | M |
| 17 | Perf | 🟡 | apiClient | Pas de retry backoff | S |
| 18 | Perf | 🟡 | docling-pwa | Pas de Web Vitals | M |

---

## ROADMAP DE CORRECTION PRIORISÉE

### SPRINT 0 — BLOQUANTS PROD (avant tout déploiement multi-utilisateur)

1. **Isolation multi-tenant** : Ajouter user_id à produits et factures. Migrer. Filtrer toutes les requêtes. (XL)
2. **VITE_API_URL** : Faire échouer le build si non défini en prod. (S)
3. **_safe_float** : Protéger db_manager contre valeurs non numériques. (S)

### SPRINT 1 — SÉCURITÉ & FIABILITÉ (semaine 1)

4. Échapper % et _ dans ILIKE (db_manager). (S)
5. Ajouter CSP, X-Frame-Options, HSTS. (M)
6. serialize_row : retourner copie au lieu de modifier in-place. (S)
7. ValidationPage : envoyer source dans le payload batch. (S)
8. CI : npm audit, pip-audit, coverage gate. (M)

### SPRINT 2 — UX & COMPLÉTUDE (semaine 2)

9. Empty states Catalogue + History avec CTA "Scanner". (S)
10. noClick: false sur dropzone. (XS)
11. AUTH_REQUIRED : documenter et sécuriser la config prod. (S)
12. workbox-window : supprimer. vitest → devDependencies. (XS)

### SPRINT 3 — PERFORMANCE & POLISH (semaine 3)

13. Retry avec exponential backoff sur apiClient. (S)
14. Web Vitals monitoring. (M)
15. Command palette (cmd+K). (M)

### SPRINT 4 — SCALABILITÉ & EXCELLENCE (semaine 4+)

16. Deploy automatique staging/prod. (L)
17. Migrations : unifier Alembic vs run_migrations. (M)
18. httpOnly cookies pour JWT (si possible). (M)

---

## VERDICT FINAL

**L'app est-elle prête pour la production ?** **CONDITIONNEL**

**Pourquoi :**
- En mode **single-tenant** (un seul utilisateur, AUTH_REQUIRED=false) : l'app est utilisable. Les correctifs post-audits (pagination, Settings total_processed, Workbox sans cache API, facturx division par zéro, login/register) ont été appliqués.
- En mode **multi-utilisateur** : **inacceptable**. Les données (catalogue, historique, stats) sont partagées entre tous les utilisateurs. Aucune isolation.

**Ce qui est bien fait (top 5) :**
1. Auth moderne : Argon2id, JWT, rehash PBKDF2→Argon2id, validation email/password.
2. Pagination cursor sur le catalogue avec load more et filtres API.
3. Jobs isolés par user_id. Rate limiting sur auth. Docker non-root.
4. Migration xlsx→exceljs (CVE corrigées). Workbox sans cache API.
5. Structure backend propre : Orchestrator, DBManager, services séparés.

**Ce qui est critique à corriger (top 5) :**
1. Isolation multi-tenant : user_id sur produits et factures.
2. _safe_float dans db_manager pour éviter les crashs.
3. VITE_API_URL obligatoire en prod.
4. Empty states avec CTA pour l'onboarding.
5. CI : security scan et coverage gate.

**Estimation pour atteindre 90/100 global :** 4-6 semaines (1 dev full-time) en suivant la roadmap.
