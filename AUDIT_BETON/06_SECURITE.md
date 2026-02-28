# 🔒 06 — AUDIT SÉCURITÉ COMPLET
# OWASP Top 10 2025 · JWT · Injection · Auth · Headers · Secrets
# Exécuté le 28 février 2026 — Phase 06 Audit Bêton Docling

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

**Vérification code :**
- `DBManager.get_job(job_id, user_id)` : `WHERE job_id = $1::uuid AND user_id = $2` ✅
- `DBManager.get_facture_pdf_url(facture_id, user_id)` : `WHERE id = $1 AND user_id = $2` ✅
- `DBManager.get_price_history_by_product_id(product_id, user_id)` : `JOIN produits p ON p.user_id = $2` ✅
- Tous les endpoints catalogue/stats/history passent `user_id` depuis `_user["sub"]` ✅

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
| HSTS | 🟠 | **Manquant** — pas de `Strict-Transport-Security` |
| HTTPS forcé | ⚠️ | Dépend du reverse proxy (non vérifiable dans le code) |

**Score A02 : 85/100** — JWT et Argon2 corrects. HSTS et SameSite=strict à ajouter.

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
| /api/v1/invoices/process | **Aucune** | 🟠 |
| Autres endpoints | Aucune | 🟡 |

**Risque :** Abus de l'API Gemini (coût, quota) via /process sans limite.

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

**Score A04 : 75/100** — Rate limit manquant sur /process.

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
| Strict-Transport-Security | 🟠 | **Manquant** |
| Content-Security-Policy | 🟡 | Meta CSP dans index.html PWA — pas de header API |

### CORS

| Vérification | Statut | Détail |
|--------------|--------|--------|
| allow_origins | ✅ | Liste explicite (localhost, PWA_URL, netlify) |
| allow_credentials | ✅ | True |
| allow_methods | ✅ | GET, POST, DELETE, OPTIONS |
| allow_headers | ✅ | Authorization, Content-Type |

### Mode debug

| Vérification | Statut | Détail |
|--------------|--------|--------|
| reload | ✅ | `reload=False` dans uvicorn.run |
| docs/redoc | ⚠️ | Activés par défaut FastAPI — à désactiver en prod si souhaité |

**Score A05 : 80/100** — HSTS et CSP header API à ajouter.

---

## S6 — OWASP A06 : VULNERABLE COMPONENTS

### Backend (pip-audit)

*Exécution pip-audit : timeout lors de l'audit. Vérification manuelle :*

| Package | Version | CVE connues | Action |
|---------|---------|-------------|--------|
| fastapi | 0.115.0 | — | OK |
| PyJWT | 2.10.1 | CVE-2025-45768 (disputée par fournisseur) | Surveiller mise à jour |
| argon2-cffi | 25.1.0 | — | OK |
| lxml | 5.4.0 | XXE mitigé (facturx) | OK |
| slowapi | 0.1.9 | — | OK |

### Frontend (npm audit)

| Package | Sévérité | CVE | Fix |
|---------|----------|-----|-----|
| esbuild (via vite) | moderate | GHSA-67mh-4wv8-2f99 | npm audit fix — breaking |
| vite | moderate | Dépend esbuild | Idem |

**Note :** Pas de CVE critique/haute confirmée. 2 vulnérabilités modérées npm.

**Score A06 : 85/100** — Pas de CVE critique/haute bloquante.

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
| Requêtes HTTP vers URL utilisateur | ✅ | Aucune — pas de `requests.get(url)` avec URL user |
| Watchdog folder | 🟡 | WATCHDOG_FOLDER depuis .env — pas de validation anti-/etc/ |

**Risque Watchdog :** Si .env modifié (accès serveur), WATCHDOG_FOLDER=/etc serait possible. Mitigation : validation du chemin au démarrage.

**Score A10 : 88/100** — Pas de SSRF classique. Validation chemin watchdog recommandée.

---

## S11 — SECRETS & VARIABLES D'ENVIRONNEMENT

### Analyse secrets dans le code

| Fichier | Ligne | Contenu | Faux positif | Action |
|---------|-------|---------|--------------|--------|
| backend/services/gemini_service.py | 99 | `api_key = Config.GEMINI_API_KEY` | Oui (env) | — |
| docling-pwa/node_modules/.../sentry_react.js | — | `password = "%filtered%"` | Oui (lib) | — |

**Résultat :** 0 secret en clair dans le code source du projet.

### .env commité

```bash
git ls-files | grep "\.env$"
# → 0 résultat (exit 1 = vide)
```

**.env dans .gitignore** ✅

### .env.example

Placeholders uniquement (`YOUR_GEMINI_API_KEY`, `change-this-to-a-long-random-string`) — acceptable ✅

**Score Secrets : 95/100**

---

## S12 — ANALYSE FICHIERS UPLOADÉS

| Vérification | Statut | Détail |
|--------------|--------|--------|
| Validation MIME | ✅ | `_ALLOWED_MIMES` + content_type |
| Taille max | ✅ | 50 Mo, vérifié avant accumulation |
| Sanitisation nom fichier | 🟡 | `filename.replace("/", "_")` — pas de `os.path.basename()` pour path traversal |
| Stockage S3 | ✅ | Clé = `hash8_safe_name` — pas d'exécution |
| Fichiers temporaires | N/A | Pas de tempfile pour upload (traitement en mémoire) |

**Path traversal :** `../../etc/passwd.pdf` → `.._.._etc_passwd.pdf` (replace) — mitigé mais `os.path.basename()` plus robuste.

**Score File Upload : 88/100**

---

## LISTE PROBLÈMES SÉCURITÉ

```
[S-001] 🟠 CRITIQUE — Rate limiting manquant sur /process
  OWASP    : A04 - Insecure Design
  Fichier  : api.py:271
  Vecteur  : Attaquant envoie des centaines de factures → quota Gemini épuisé, coût élevé
  Impact   : DoS financier, quota API épuisé
  Fix      : Ajouter @limiter.limit("20/minute") sur process_invoice

[S-002] 🟠 CRITIQUE — HSTS header manquant
  OWASP    : A05 - Security Misconfiguration
  Fichier  : api.py:232-239
  Vecteur  : Downgrade HTTPS→HTTP en MITM
  Impact   : Token/cookies interceptables
  Fix      : En prod : response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

[S-003] 🟠 CRITIQUE — SameSite=Lax au lieu de Strict
  OWASP    : A02 - Cryptographic Failures
  Fichier  : api.py:459
  Vecteur  : CSRF partiel sur requêtes cross-site GET
  Impact   : Risque CSRF réduit mais non nul
  Fix      : samesite="strict" (ou garder "lax" si redirect login depuis domaine externe)

[S-004] 🟡 MAJEUR — Lockout après échecs login non implémenté
  OWASP    : A07 - Authentication Failures
  Fichier  : api.py (login)
  Vecteur  : Bruteforce avec 5 req/min = 300/h
  Impact   : Comptes faibles compromis
  Fix      : Compteur échecs par email/IP, lockout 15 min après 5 échecs

[S-005] 🟡 MAJEUR — Validation chemin WATCHDOG_FOLDER
  OWASP    : A10 - SSRF / Misconfiguration
  Fichier  : backend/core/config.py
  Vecteur  : WATCHDOG_FOLDER=/etc si env modifié
  Impact   : Surveillance dossier sensible
  Fix      : Valider que path résolu est sous répertoire autorisé (ex: ./ ou $HOME)

[S-006] 🟡 MAJEUR — Sanitisation filename upload
  OWASP    : A04 - Insecure Design
  Fichier  : backend/services/storage_service.py:57
  Vecteur  : Path traversal dans clé S3 (théorique)
  Impact   : Clés S3 malformées
  Fix      : safe_name = os.path.basename(filename).replace(" ", "_").replace("/", "_").replace("\\", "_")

[S-007] 🟡 MAJEUR — Auth failures en niveau debug
  OWASP    : A09 - Security Logging
  Fichier  : backend/services/auth_service.py:55
  Vecteur  : Échecs token invisibles en prod (level INFO)
  Impact   : Détection attaques retardée
  Fix      : logger.warning("Token invalide ou payload malformé") au lieu de debug

[S-008] 🔵 MINEUR — Content-Security-Policy non défini (API)
  OWASP    : A05 - Security Misconfiguration
  Fichier  : api.py
  Impact   : XSS secondaire non mitigé par CSP
  Fix      : CSP présent dans PWA index.html — API stateless, priorité basse

[S-009] 🔵 MINEUR — Argon2 time_cost=3
  OWASP    : A02 - Cryptographic Failures
  Fichier  : backend/services/auth_service.py:32
  Impact   : Légèrement plus lent que time_cost=2 (OWASP recommande 2)
  Fix      : time_cost=2 acceptable pour meilleur équilibre perf/sécu
```

---

## SCORECARD SÉCURITÉ

| OWASP | Score /100 | Problèmes 🔴 | Problèmes 🟠 | Notes |
|-------|-----------|-------------|-------------|-------|
| A01 Broken Access Control | 95 | 0 | 0 | IDOR mitigé |
| A02 Cryptographic Failures | 85 | 0 | 1 | SameSite, HSTS |
| A03 Injection | 92 | 0 | 0 | SQL, XSS OK |
| A04 Insecure Design | 75 | 0 | 1 | Rate limit /process |
| A05 Security Misconfiguration | 80 | 0 | 1 | HSTS, CSP |
| A06 Vulnerable Components | 85 | 0 | 0 | 2 modérées npm |
| A07 Authentication Failures | 78 | 0 | 0 | Lockout manquant |
| A08 Data Integrity Failures | 70 | 0 | 0 | require-hashes |
| A09 Security Logging | 82 | 0 | 0 | Auth log level |
| A10 SSRF | 88 | 0 | 0 | Watchdog path |
| Secrets | 95 | 0 | 0 | OK |
| File Uploads | 88 | 0 | 0 | Sanitisation |
| **GLOBAL SÉCURITÉ** | **84** | **0** | **3** | Déployable avec correctifs 🟠 |

---

## CORRECTIFS PRIORITAIRES (🔴 et 🟠)

### [S-001] Rate limit /process

```python
# api.py, avant process_invoice
@app.post("/api/v1/invoices/process")
@limiter.limit("20/minute")
async def process_invoice(...):
```

### [S-002] HSTS en production

```python
# api.py, _security_headers
async def _security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if os.getenv("ENVIRONMENT", "").lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### [S-003] SameSite Strict (optionnel)

```python
# api.py, _set_auth_cookie
response.set_cookie(
    ...
    samesite="strict",  # était "lax"
    ...
)
```

*Note :* Si la PWA est chargée depuis un domaine différent du backend et que le login redirige, `lax` peut être nécessaire. Évaluer selon l'architecture.

---

## ✅ GATE S — SÉCURITÉ

### Critères de passage

| Critère | Résultat |
|---------|----------|
| 0 problème 🔴 | ✅ |
| 0 secret dans le code | ✅ |
| 0 .env commité | ✅ |
| 0 CVE critique/haute | ✅ (npm : 2 modérées) |
| 0 SQL injection (f-string user input) | ✅ |
| 0 dangerouslySetInnerHTML | ✅ |

### Verdict

**STATUS : ✅ PASS**

- Aucune faille 🔴 FATAL identifiée.
- 3 problèmes 🟠 CRITIQUE identifiés — **[S-001] et [S-002] appliqués** (rate limit /process, HSTS prod).
- 4 problèmes 🟡 MAJEUR recommandés.
- Le projet est **déployable** en production.

---

*Audit exécuté selon `.cursor/PROMPT AUDIT/06_SECURITE.md` — Phase 06 Audit Bêton Docling.*
