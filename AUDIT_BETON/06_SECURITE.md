# 🔒 06 — AUDIT SÉCURITÉ COMPLET
# OWASP Top 10 2025 · JWT · Injection · Auth · Headers · Secrets
# Exécuté le 1er mars 2026 — Phase 06 Audit Bêton Docling

---

## VÉRIFICATIONS (1er mars 2026)

| Critère | Statut |
|---------|--------|
| SQL injection (f-string + input) | ✅ Aucune — params $1,$2 |
| dangerouslySetInnerHTML | ✅ 0 (frontend) |
| Secrets dans code | À vérifier (grep) |
| pip-audit | À exécuter dans venv projet |

---

## PRINCIPE

```
La sécurité ne se suppose pas. Elle se prouve.
Pour chaque vecteur d'attaque :
  → Tenter l'attaque mentalement
  → Vérifier le code qui devrait bloquer l'attaque
  → Si le code n'existe pas ou est insuffisant → 🔴 FATAL

Un seul problème 🔴 de sécurité = produit non déployable.
```

---

## S1 — OWASP A01 : BROKEN ACCESS CONTROL

### Test 1 : IDOR (Insecure Direct Object Reference)

| Endpoint | {id} dans URL | WHERE user_id | Source user_id | IDOR possible | Sévérité |
|----------|--------------|---------------|----------------|---------------|---------|
| GET /api/v1/catalogue | Non | OUI | Token | Non | ✅ |
| GET /api/v1/invoices/status/{job_id} | OUI | OUI | Token | Non | ✅ |
| GET /api/v1/history/{facture_id}/pdf | OUI | OUI | Token | Non | ✅ |
| GET /api/v1/catalogue/price-history/{product_id} | OUI | OUI (JOIN) | Token | Non | ✅ |
| DELETE /api/v1/catalogue/reset | Non | OUI | Token (admin) | Non | ✅ |
| POST /api/v1/catalogue/batch | Non | OUI | Token | Non | ✅ |
| GET /api/v1/catalogue/compare | Non | OUI | Token | Non | ✅ |
| GET /api/v1/export/my-data | Non | OUI | Token | Non | ✅ |

**Vérification code :**
- `DBManager.get_job(job_id, user_id)` : `WHERE job_id = $1::uuid AND user_id = $2` ✅
- `DBManager.get_facture_pdf_url(facture_id, user_id)` : `WHERE id = $1 AND user_id = $2` (si user_id non None) ✅
- `DBManager.get_price_history_by_product_id(product_id, user_id)` : `JOIN produits p ON p.user_id = $2` ✅
- Tous les endpoints catalogue/stats/history passent `user_id` depuis `_user["sub"]` ✅
- **Edge case** : `get_facture_pdf_url` et `get_price_history` sans filtre user_id si `user_id=None` — cas théorique (token invalide) ; en pratique `create_token` fournit toujours `sub` ✅

### Test 2 : Élévation de privilèges

- `get_admin_user` vérifie `user.get("role") != "admin"` → 403 ✅
- Endpoint `/api/v1/catalogue/reset` protégé par `Depends(get_admin_user)` ✅
- Pas de routes admin non documentées (grep admin/superuser) ✅

**Score A01 : 95/100** — Isolation multi-tenant correcte, IDOR mitigé.

---

## S2 — OWASP A02 : CRYPTOGRAPHIC FAILURES

### JWT

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Algorithme hardcodé | ✅ | `JWT_ALGORITHM = "HS256"`, `algorithms=[JWT_ALGORITHM]` dans verify_token |
| JWT_SECRET ≥ 32 chars | ✅ | `Config.validate()` : `len(JWT_SECRET) < 32` → exit |
| Expiration (exp) | ✅ | `exp: now + JWT_EXPIRY` (24h par défaut) |
| Données sensibles payload | ✅ | sub, email, role — pas de password |

### Passwords (Argon2)

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Argon2id | ✅ | `PasswordHasher` (argon2-cffi, argon2id par défaut) |
| Paramètres | ⚠️ | `time_cost=3, memory_cost=65536, parallelism=2` — OWASP recommande time_cost=2 |
| Rehash legacy | ✅ | PBKDF2 → Argon2id silencieux au login |

### Cookies

| Vérification | Statut | Détail |
|--------------|--------|--------|
| HttpOnly | ✅ | `httponly=True` |
| Secure (prod) | ✅ | `secure=is_prod` (ENVIRONMENT=production) |
| SameSite | 🟠 | `samesite="lax"` — recommandation OWASP : `strict` |

### Données en transit

| Vérification | Statut | Détail |
|--------------|--------|--------|
| HSTS | ✅ | `Strict-Transport-Security` en prod (api.py:252-253) |
| HTTPS forcé | ⚠️ | Dépend du reverse proxy (non vérifiable dans le code) |

**Score A02 : 88/100** — JWT et Argon2 corrects. SameSite=strict recommandé.

---

## S3 — OWASP A03 : INJECTION

### SQL Injection

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Requêtes paramétrées | ✅ | asyncpg avec `$1`, `$2`… partout |
| ILIKE échappé | ✅ | `_escape_like()` + `ESCAPE E'\\\\'` |
| f-string avec user input | ✅ | f-strings pour structure (conditions), valeurs en params — pas de concaténation directe |

**Test mental :** Input `'; DROP TABLE products; --` → passé en `$1` → traité comme string littérale ✅

### Prompt Injection (Gemini)

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Contenu facture dans prompt | ⚠️ | PDF/image passé via `Part.from_bytes` — contenu OCR dans le flux |
| response_schema strict | ✅ | JSON schema avec types/required — limite la surface d'attaque |
| Prompt système séparé | ✅ | `system_instruction=SYSTEM_PROMPT` distinct du contenu |
| Risque | 🟡 | Facture malveillante (texte dans image) pourrait tenter injection — impact limité par schema |

### XSS (Frontend)

| Vérification | Statut | Détail |
|--------------|--------|--------|
| dangerouslySetInnerHTML | ✅ | 0 occurrence dans docling-pwa/src/ |
| Contenu utilisateur échappé | ✅ | React échappe par défaut |

**Score A03 : 92/100** — SQL et XSS bien protégés. Prompt injection risque théorique faible.

---

## S4 — OWASP A04 : INSECURE DESIGN

### Rate limiting

| Endpoint | Limite | Statut |
|----------|--------|--------|
| /api/v1/auth/register | 5/minute | ✅ |
| /api/v1/auth/login | 5/minute | ✅ |
| /api/v1/invoices/process | 20/minute | ✅ |
| /api/v1/sync/status | 30/minute | ✅ |
| Autres endpoints | Aucune | 🟡 |

### Circuit breaker

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Gemini circuit breaker | ✅ | `_GeminiCircuitBreaker(threshold=5)` |
| Sémaphore extraction | ✅ | `_extraction_semaphore = asyncio.Semaphore(3)` |

### Upload de fichiers

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Taille max | ✅ | 50 Mo (`_MAX_UPLOAD_BYTES`) |
| Type MIME vérifié | ✅ | `_ALLOWED_MIMES` + `file.content_type` |
| Extension vérifiée | ✅ | `_ALLOWED_EXTENSIONS` |
| Lecture par chunks | ✅ | 256 Ko par chunk, rejet si > 50 Mo total |

**Score A04 : 90/100** — Rate limit /process appliqué.

---

## S5 — OWASP A05 : SECURITY MISCONFIGURATION

### Headers de sécurité

| Header | Statut | Détail |
|--------|--------|--------|
| X-Content-Type-Options | ✅ | `nosniff` |
| X-Frame-Options | ✅ | `DENY` |
| X-XSS-Protection | ✅ | `1; mode=block` |
| Referrer-Policy | ✅ | `strict-origin-when-cross-origin` |
| Permissions-Policy | ✅ | `geolocation=(), microphone=(), camera=()` |
| Strict-Transport-Security | ✅ | En prod : `max-age=31536000; includeSubDomains` |
| Content-Security-Policy | 🟡 | Meta CSP dans index.html PWA — pas de header API |

### CORS

| Vérification | Statut | Détail |
|--------------|--------|--------|
| allow_origins | ✅ | Liste explicite (localhost, PWA_URL, netlify) |
| allow_credentials | ✅ | True |
| allow_methods | ✅ | GET, POST, DELETE, OPTIONS, PATCH |
| allow_headers | ✅ | Authorization, Content-Type, X-Requested-With |

### Mode debug

| Vérification | Statut | Détail |
|--------------|--------|--------|
| reload | ✅ | `reload=False` dans uvicorn.run |
| docs/redoc | ⚠️ | Activés par défaut FastAPI — à désactiver en prod si souhaité |

**Score A05 : 88/100** — HSTS en prod ✅. CSP header API optionnel.

---

## S6 — OWASP A06 : VULNERABLE COMPONENTS

### Backend (pip-audit — exécution 1er mars 2026)

| Package | Version | CVE | Sévérité | Fix version | Action |
|---------|---------|-----|----------|-------------|--------|
| cryptography | 41.0.4 | PYSEC-2023-254, PYSEC-2024-225, GHSA-3ww4-gg4f-jr7f, GHSA-9v9h-cgj8-h64p, GHSA-h4gh-qq45-vh27, GHSA-r6ph-v2qm-q3c2 | Haute | 46.0.5 | 🔴 Mettre à jour |
| fastapi | 0.104.1 | CVE-2024-24762 (ReDoS multipart) | Moyenne | 0.109.1 | 🟠 Mettre à jour |
| filelock | 3.20.0 | CVE-2025-68146 (TOCTOU symlink) | Haute | 3.20.1 | 🔴 Mettre à jour |
| werkzeug | 3.1.3 | CVE-2025-66221, CVE-2026-21860, CVE-2026-27199 (Windows device names) | Moyenne/Haute | 3.1.6 | 🔴 Mettre à jour |
| wheel | 0.45.1 | CVE-2026-24049 (path traversal chmod) | Haute | 0.46.2 | 🔴 Mettre à jour |
| ecdsa | 0.19.1 | CVE-2024-23342 (Minerva timing) | Moyenne | — | Pas de fix prévu |

### Frontend (npm audit — exécution 1er mars 2026)

| Package | Sévérité | CVE | Fix |
|---------|----------|-----|-----|
| serialize-javascript | **high** | GHSA-5c6j-r48x-rmvq (RCE RegExp/Date) | vite-plugin-pwa 0.19.8 |
| vite-plugin-pwa | **high** | via workbox-build | 0.19.8 |
| workbox-build | **high** | via @rollup/plugin-terser | — |
| @rollup/plugin-terser | **high** | via serialize-javascript | — |
| esbuild | moderate | GHSA-67mh-4wv8-2f99 | vite 7.3.1 |
| vite | moderate | via esbuild | 7.3.1 |

**Résumé :** 4 vulnérabilités **haute** npm, 5+ **haute** pip. **🔴 GATE FAIL** sur CVE critique/haute.

**Score A06 : 55/100** — CVE haute bloquantes à corriger avant déploiement.

---

## S7 — OWASP A07 : AUTHENTICATION FAILURES

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Rate limit /login | ✅ | 5/minute |
| Lockout après N échecs | ❌ | Non implémenté |
| Token refresh | ❌ | Pas de refresh token (JWT 24h) |
| Session fixation | ✅ | Nouveau token à chaque login |
| Logout | ⚠️ | Suppression cookie uniquement — pas de blacklist token |
| Message erreur login | ✅ | "Email ou mot de passe incorrect" (générique) |

**Score A07 : 78/100** — Lockout et refresh token non implémentés.

---

## S8 — OWASP A08 : DATA INTEGRITY FAILURES

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Webhooks signature | N/A | Pas de webhooks |
| pip --require-hashes | ❌ | Non utilisé |
| package-lock.json | ✅ | Commitée (npm) |
| Secrets dans logs | ✅ | Aucun log de password/token/secret |

**Score A08 : 70/100** — require-hashes recommandé pour reproductibilité.

---

## S9 — OWASP A09 : SECURITY LOGGING & MONITORING

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Échecs auth loggés | ⚠️ | `logger.debug("Token invalide")` — niveau debug |
| Erreurs 5xx | ✅ | `logger.error(..., exc_info=True)` |
| Sentry | ✅ | Configuré si SENTRY_DSN |
| Données sensibles dans logs | ✅ | Aucun password/secret/token loggé |

**Score A09 : 82/100** — Échecs auth à logger en WARNING en prod.

---

## S10 — OWASP A10 : SERVER-SIDE REQUEST FORGERY (SSRF)

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Requêtes HTTP vers URL utilisateur | ✅ | Bytez/Gemini : URLs fixes — pas d'URL user |
| Watchdog folder | 🟡 | WATCHDOG_FOLDER depuis .env — pas de validation anti-/etc/ |

**Risque Watchdog :** Si .env modifié (accès serveur), WATCHDOG_FOLDER=/etc serait possible. Mitigation : validation du chemin au démarrage.

**Score A10 : 88/100** — Pas de SSRF classique. Validation chemin watchdog recommandée.

---

## S11 — SECRETS & VARIABLES D'ENVIRONNEMENT

### Analyse secrets dans le code

| Fichier | Ligne | Contenu | Faux positif | Action |
|---------|-------|---------|--------------|--------|
| backend/services/gemini_service.py | 99 | `api_key = Config.GEMINI_API_KEY` | Oui (env) | — |
| backend/services/storage_service.py | 31 | `aws_secret_access_key=Config.STORJ_SECRET_KEY` | Oui (env) | — |
| docling-pwa/src/services/apiClient.js | 35 | `localStorage.getItem('docling-token')` | Fallback Bearer | Cookie httpOnly prioritaire |

**Résultat :** 0 secret en clair dans le code source du projet.

### .env commité

```bash
git ls-files | grep "\.env$"
# → 0 résultat (exit 1 = vide)
```

**.env dans .gitignore** ✅

**Score Secrets : 95/100**

---

## S12 — ANALYSE FICHIERS UPLOADÉS

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Validation MIME | ✅ | `_ALLOWED_MIMES` + content_type |
| Taille max | ✅ | 50 Mo, vérifié avant accumulation |
| Sanitisation nom fichier | 🟡 | Pas de `os.path.basename()` pour path traversal |
| Stockage S3/Storj | ✅ | Clé hashée — pas d'exécution |
| Fichiers temporaires | N/A | Pas de tempfile pour upload (traitement en mémoire) |

**Score File Upload : 88/100**

---

## SCORECARD SÉCURITÉ

| OWASP | Score /100 | Problèmes 🔴 | Problèmes 🟠 | Notes |
|-------|-----------|-------------|-------------|-------|
| A01 Broken Access Control | 95 | 0 | 0 | IDOR mitigé |
| A02 Cryptographic Failures | 88 | 0 | 1 | SameSite |
| A03 Injection | 92 | 0 | 0 | SQL, XSS OK |
| A04 Insecure Design | 90 | 0 | 0 | Rate limit OK |
| A05 Security Misconfiguration | 88 | 0 | 0 | HSTS OK |
| A06 Vulnerable Components | **55** | **5+** | **2** | CVE haute pip + npm |
| A07 Authentication Failures | 78 | 0 | 0 | Lockout manquant |
| A08 Data Integrity Failures | 70 | 0 | 0 | require-hashes |
| A09 Security Logging | 82 | 0 | 0 | Auth log level |
| A10 SSRF | 88 | 0 | 0 | Watchdog path |
| Secrets | 95 | 0 | 0 | OK |
| File Uploads | 88 | 0 | 0 | Sanitisation |
| **GLOBAL SÉCURITÉ** | **78** | **5+** | **3** | **NON DÉPLOYABLE** — CVE haute |

---

## LISTE PROBLÈMES SÉCURITÉ

```
[S-001] 🔴 FATAL — CVE haute pip (cryptography, filelock, werkzeug, wheel)
  OWASP    : A06 - Vulnerable Components
  Vecteur  : Exploitation des vulnérabilités connues
  Impact   : DoS, déni de service, fuite de données
  Fix      : pip install -U cryptography filelock werkzeug wheel
             pip-audit après mise à jour

[S-002] 🔴 FATAL — CVE haute npm (serialize-javascript, vite-plugin-pwa)
  OWASP    : A06 - Vulnerable Components
  Vecteur  : RCE via RegExp.flags / Date.prototype (GHSA-5c6j-r48x-rmvq)
  Impact   : Exécution de code arbitraire côté build
  Fix      : npm update vite-plugin-pwa@0.19.8 (ou version fixée)
             npm audit après mise à jour

[S-003] 🟠 CRITIQUE — SameSite=Lax au lieu de Strict
  OWASP    : A02 - Cryptographic Failures
  Fichier  : api.py:459
  Vecteur  : CSRF partiel sur requêtes cross-site GET
  Fix      : samesite="strict" (ou garder "lax" si redirect login depuis domaine externe)

[S-004] 🟡 MAJEUR — Lockout après échecs login non implémenté
  OWASP    : A07 - Authentication Failures
  Vecteur  : Bruteforce avec 5 req/min = 300/h
  Fix      : Compteur échecs par email/IP, lockout 15 min après 5 échecs

[S-005] 🟡 MAJEUR — Validation chemin WATCHDOG_FOLDER
  OWASP    : A10 - SSRF / Misconfiguration
  Fichier  : backend/core/config.py
  Fix      : Valider que path résolu est sous répertoire autorisé

[S-006] 🟡 MAJEUR — Auth failures en niveau debug
  OWASP    : A09 - Security Logging
  Fichier  : backend/services/auth_service.py:55
  Fix      : logger.warning("Token invalide ou payload malformé")
```

---

## ✅ GATE S — SÉCURITÉ

### Critères de passage

| Critère | Résultat |
|---------|----------|
| 0 problème 🔴 | ❌ — CVE haute pip + npm |
| 0 secret dans le code | ✅ |
| 0 .env commité | ✅ |
| 0 CVE critique/haute | ❌ — 4 high npm, 5+ high pip |
| 0 SQL injection (f-string user input) | ✅ |
| 0 dangerouslySetInnerHTML | ✅ |

### Verdict

**STATUS : 🔴 FAIL**

- **5+ vulnérabilités haute** identifiées (pip + npm).
- Le projet **n'est pas déployable** en production tant que les CVE haute ne sont pas corrigées.
- Actions prioritaires :
  1. `pip install -U cryptography filelock werkzeug` (versions fix)
  2. `npm update vite-plugin-pwa` ou migration vers version sans vulnérabilité
  3. Relancer `pip-audit` et `npm audit` — viser 0 critical, 0 high

---

*Audit exécuté selon `.cursor/PROMPT AUDIT/06_SECURITE.md` — Phase 06 Audit Bêton Docling — 1er mars 2026.*
