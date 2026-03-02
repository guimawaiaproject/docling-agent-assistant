# Améliorations Fondations, Stabilité, Monitoring & Robustesse

**Statut** : Backlog
**Date** : 2 mars 2026
**Source** : Analyse sectorielle complète du projet Docling (Audit Bêton, api.py, backend, frontend, CI/CD)

---

## Vue d'ensemble

Ce document agrège toutes les améliorations à apporter au projet, organisées en quatre secteurs :

| Secteur | Objectif | Priorité |
|---------|----------|----------|
| **1. Fondations** | Sécuriser le cœur de l'application | 🔴 Critique |
| **2. Stabilité & Performance** | Rendre l'app "industrielle" | 🟠 Haute |
| **3. Fondations de Monitoring** | Immédiat — visibilité opérationnelle | 🟠 Haute |
| **4. Robustesse et Surveillance** | Résilience, alertes, observabilité | 🟡 Moyenne |

---

# 1. LES FONDATIONS — Sécuriser le Cœur de l'Application

## 1.1 CVE et dépendances vulnérables (BLOQUEUR)

**Référence** : AUDIT_BETON/06_SECURITE.md — Score A06 : 55/100

### Backend (pip)

| Package | CVE | Sévérité | Action |
|---------|-----|----------|--------|
| cryptography | PYSEC-2023-254, GHSA-* | Haute | `pip install -U cryptography>=46.0.5` |
| filelock | CVE-2025-68146 | Haute | `pip install -U filelock>=3.20.1` |
| werkzeug | CVE-2025-66221, CVE-2026-* | Moyenne/Haute | `pip install -U werkzeug>=3.1.6` |
| wheel | CVE-2026-24049 | Haute | `pip install -U wheel>=0.46.2` |
| fastapi | CVE-2024-24762 (ReDoS multipart) | Moyenne | Déjà 0.115.0 — vérifier fix |

**Commande** : `pip-audit` après chaque mise à jour.

### Frontend (npm)

| Package | CVE | Sévérité | Action |
|---------|-----|----------|--------|
| serialize-javascript | GHSA-5c6j-r48x-rmvq (RCE) | Haute | Mettre à jour vite-plugin-pwa@0.19.8+ |
| vite-plugin-pwa | via workbox-build | Haute | Mettre à jour ou remplacer |
| esbuild / vite | GHSA-67mh-4wv8-2f99 | Modérée | `vite@7.3.1` si disponible |

**Commande** : `npm audit` après chaque mise à jour.

---

## 1.2 Authentification et cookies

| ID | Problème | Fichier | Fix |
|----|----------|---------|-----|
| S-003 | SameSite=Lax au lieu de Strict | api.py:459 | `samesite="strict"` (ou garder "lax" si redirect login cross-domain) |
| S-004 | Lockout après échecs login non implémenté | auth_service.py | Compteur échecs par email/IP, lockout 15 min après 5 échecs |
| S-006 | Auth failures en niveau debug | auth_service.py:55 | `logger.warning("Token invalide ou payload malformé")` |
| S-007 | Pas de refresh token | — | JWT 24h — envisager refresh token ou session courte (1h) + refresh |

---

## 1.3 Validation et configuration

| ID | Problème | Fichier | Fix |
|----|----------|---------|-----|
| S-005 | Validation chemin WATCHDOG_FOLDER | config.py | Valider que path résolu est sous répertoire autorisé (pas /etc, pas traversal) |
| B-003 | Body JSON non validé (community prefs) | api.py | Schéma Pydantic pour `community_consent`, `zone_geo` |
| B-002 | ILIKE sans _escape_like (community stats) | community_service.py | Appliquer `_escape_like()` sur paramètre fournisseur |

---

## 1.4 Headers et CORS

| Élément | Statut | Action |
|---------|--------|--------|
| X-Content-Type-Options | ✅ nosniff | — |
| X-Frame-Options | ✅ DENY | — |
| HSTS | ✅ En prod | — |
| Content-Security-Policy | 🟡 Meta CSP PWA uniquement | Ajouter header CSP sur API si exposition publique |
| docs/redoc | ⚠️ Activés par défaut | Désactiver en prod : `docs_url=None` si `ENVIRONMENT=production` |

---

# 2. STABILITÉ & PERFORMANCE — Rendre l'App "Industrielle"

## 2.1 Backend — Requêtes et I/O

| ID | Problème | Fichier | Fix |
|----|----------|---------|-----|
| P-001 | N+1 insert_anonymous_price | orchestrator.py:127-136 | Batch `INSERT ... VALUES (...), (...), ...` au lieu de N requêtes |
| P-002 | COUNT(*) catalogue à chaque requête | db_manager.py | Estimation pg_stat ou cache court (30s) pour total |
| P-003 | get_fournisseurs sans pagination | db_manager.py | LIMIT 500 ou pagination cursor |
| P-004 | export_my_data charge tout en mémoire | db_manager.py | Pagination ou streaming JSON (LIMIT 50000) |
| P-005 | StorageService boto3 sans timeout | storage_service.py | `Config=botocore.config.Config(connect_timeout=30, read_timeout=60)` |

---

## 2.2 Backend — Rate limiting

| Endpoint | Limite actuelle | Action |
|----------|-----------------|--------|
| /api/v1/auth/register | 5/min | ✅ |
| /api/v1/auth/login | 5/min | ✅ |
| /api/v1/invoices/process | 20/min | ✅ |
| /api/v1/sync/status | 30/min | ✅ |
| /api/vitals | Aucune | Ajouter rate limit (ex. 60/min) |
| /api/v1/catalogue, /history, etc. | Aucune | Envisager rate limit global par IP (ex. 300/min) |

---

## 2.3 Frontend — Bundle et chargement

| ID | Problème | Fichier | Fix |
|----|----------|---------|-----|
| P-006 | excel-gen 917 kB import statique | CataloguePage.jsx | `const exportExcel = async () => { const ExcelJS = (await import('exceljs')).default; ... }` |
| P-007 | Spline 3D ~4 MB (react-spline + physics) | SplineScene | Feature flag ou scène allégée pour mobile ; lazy déjà OK |
| P-008 | pdf-gen, charts | — | Acceptable ; déjà en manualChunks |

---

## 2.4 Architecture API

| Problème | Fix |
|----------|-----|
| api.py monolithique ~620 lignes | Modulariser en APIRouter (invoices, catalogue, auth, community, misc) |
| DBManager singleton | Injection via `Depends(get_pool)` + `get_db_manager` |
| Exceptions dispersées | `DoclingException`, `JobNotFoundError` + `@app.exception_handler` centralisés |
| Pas de response_model | Schémas Pydantic pour toutes les réponses (catalogue, batch, stats, etc.) |

---

# 3. FONDATIONS DE MONITORING — Immédiat

## 3.1 Sentry — Activation et configuration

**État** : Projets Sentry non créés (docs/SENTRY-CONFIG.md)

| Action | Priorité |
|--------|----------|
| Créer projet docling-api (Python/FastAPI) sur Sentry | 🔴 |
| Créer projet docling-pwa (React) sur Sentry | 🔴 |
| Configurer SENTRY_DSN (backend) et VITE_SENTRY_DSN (frontend) dans .env et Render/Netlify | 🔴 |
| Vérifier que ErrorBoundary + reactErrorHandler remontent bien les erreurs | 🟠 |
| Configurer upload source maps (Vite) pour stack traces lisibles | 🟡 |

---

## 3.2 Health check — Enrichissement

**État actuel** : `/health` vérifie DB via `SELECT 1`

| Amélioration | Description |
|--------------|-------------|
| Health détaillé | Ajouter `GET /health/detailed` avec : db, pool_size, watchdog_status, sentry_configured |
| Latence DB | Mesurer temps de `SELECT 1` et l'inclure dans la réponse |
| Readiness vs Liveness | Séparer `/health/live` (process up) et `/health/ready` (DB + services) pour Kubernetes/Render |
| Script health_check.py | Ajouter vérification Storj (optionnel) si configuré |

---

## 3.3 Logging structuré

| Problème | Fix |
|----------|-----|
| Format texte libre | Passer à JSON structuré : `{"timestamp":"...","level":"INFO","request_id":"...","msg":"..."}` |
| request_id | Déjà injecté — s'assurer qu'il est dans chaque log (via middleware ou contextvars) |
| Niveau auth | `logger.debug` → `logger.warning` pour token invalide (S-006) |
| Données sensibles | Vérifier qu'aucun password/token/secret n'est loggé |

---

## 3.4 Web Vitals et métriques frontend

| Élément | Statut | Action |
|---------|--------|--------|
| reportWebVitals.js | ✅ Envoi sendBeacon vers /api/vitals | — |
| POST /api/vitals | ✅ Reçoit CLS, LCP, FCP, etc. | Ajouter rate limit ; persister en BDD ou envoyer à Sentry/analytics |
| Dashboard | ❌ Absent | Envisager Sentry Performance ou dashboard custom pour LCP, FCP |

---

# 4. ROBUSTESSE ET SURVEILLANCE

## 4.1 Résilience backend

| Composant | État | Amélioration |
|-----------|------|--------------|
| Circuit breaker Gemini | ✅ _GeminiCircuitBreaker(threshold=5) | — |
| Sémaphore extraction | ✅ Semaphore(3) | — |
| Pool asyncpg | ✅ min 2, max 10, command_timeout 60s | Ajouter `max_inactive_connection_lifetime` pour éviter connexions stale |
| boto3 | ❌ Pas de timeout | Configurer connect_timeout, read_timeout |
| Retry Gemini | ✅ Retry avec backoff | — |

---

## 4.2 Résilience frontend

| Composant | État | Amélioration |
|-----------|------|--------------|
| apiClient retry | ✅ 3 retries, backoff 500*2^n pour 5xx/network | — |
| ErrorBoundary | ✅ Sentry.captureException | — |
| OfflineBanner | ✅ Affiche fichiers en attente | Vérifier que offlineQueue existe et fonctionne |
| 401 → redirect /login | ✅ Interceptor axios | — |

---

## 4.3 Surveillance et alertes

| Besoin | Solution | Priorité |
|--------|----------|----------|
| Erreurs 5xx | Sentry (si DSN) | 🔴 |
| Health check externe | UptimeRobot, Better Uptime, ou cron Render | 🟠 |
| Latence API | Sentry Performance (traces_sample_rate) | 🟠 |
| Logs agrégés | Render logs, ou Papertrail/Logtail si volume | 🟡 |
| Alertes Slack/email | Sentry Alerts + intégration | 🟡 |

---

## 4.4 CI/CD et déploiement

| Élément | État | Amélioration |
|---------|------|--------------|
| pip-audit | ❌ Non exécuté en CI | Ajouter étape `pip-audit` dans tests.yml / ci.yml |
| npm audit | ❌ Non exécuté en CI | Ajouter `npm audit --audit-level=high` (fail si high) |
| Health après deploy | ✅ curl /health dans CI | — |
| Variables Render | SENTRY_DSN, DATABASE_URL, etc. | Vérifier que SENTRY_DSN est bien défini en prod |
| ENVIRONMENT=production | À vérifier | S'assurer que Render définit ENVIRONMENT=production |

---

# 5. PLAN D'ACTION PRIORISÉ

## Phase 1 — Bloqueurs (avant tout déploiement)

1. **CVE pip** : `pip install -U cryptography filelock werkzeug wheel` + `pip-audit`
2. **CVE npm** : `npm update vite-plugin-pwa` (ou version fixée) + `npm audit`
3. **Sentry** : Créer projets, configurer DSN backend + frontend

## Phase 2 — Court terme (cette session / semaine)

4. **Auth** : logger.warning pour token invalide ; SameSite=strict si possible
5. **Performance** : Batch insert_anonymous_price ; timeout boto3
6. **Health** : Endpoint /health/ready détaillé
7. **CI** : pip-audit et npm audit dans workflows

## Phase 3 — Moyen terme (sprint)

8. **Export** : LIMIT ou pagination sur export_my_data
9. **Fournisseurs** : Pagination ou LIMIT 500
10. **Lazy-load exceljs** : Dynamic import au clic Export
11. **Lockout login** : 5 échecs → lockout 15 min
12. **Modularisation API** : APIRouter, DI DBManager

## Phase 4 — Backlog

13. Validation WATCHDOG_FOLDER
14. Rate limit /api/vitals
15. Logging structuré JSON
16. Dashboard Web Vitals
17. Désactiver /docs en prod

---

# 6. RÉFÉRENCES

- [AUDIT_BETON/06_SECURITE.md](../../AUDIT_BETON/06_SECURITE.md)
- [AUDIT_BETON/09_PERFORMANCE.md](../../AUDIT_BETON/09_PERFORMANCE.md)
- [AUDIT_BETON/10_RAPPORT_FINAL.md](../../AUDIT_BETON/10_RAPPORT_FINAL.md)
- [docs/SENTRY-CONFIG.md](../../SENTRY-CONFIG.md)
- [docs/workflow/0_backlog/FASTAPI-BEST-PRACTICES-AMELIORATIONS.md](FASTAPI-BEST-PRACTICES-AMELIORATIONS.md)
