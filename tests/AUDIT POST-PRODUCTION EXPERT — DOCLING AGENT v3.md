---

# AUDIT POST-PRODUCTION EXPERT — DOCLING AGENT v3

**Projet** : Docling Agent — Extraction de factures BTP par IA (Gemini)  
**Stack** : FastAPI + React 19/Vite PWA + PostgreSQL Neon + Google Gemini  
**Date** : 25 février 2026

---

## 1. CODE MORT & INUTILISE

---

**[CODE MORT] — 🟠 MAJEUR**  
📍 Localisation : `backend/services/image_preprocessor.py` lignes 7, 9  
🔍 Problème : `import io` et `import tempfile` ne sont jamais utilisés  
⚠️ Impact : Pollution du namespace, confusion pour les nouveaux développeurs  
✅ Solution : Supprimer ces deux imports

---

**[CODE MORT] — 🟠 MAJEUR**  
📍 Localisation : `backend/services/gemini_service.py` ligne 13  
🔍 Problème : `import time` inutilisé (le retry utilise `asyncio.sleep`)  
⚠️ Impact : Confusion — laisse croire qu'il y a du code bloquant  
✅ Solution : Supprimer `import time`

---

**[CODE MORT] — 🟡 MINEUR**  
📍 Localisation : `backend/core/orchestrator.py` lignes 12-13  
🔍 Problème : `import mimetypes` et `from typing import Optional` ne sont jamais utilisés  
✅ Solution : Supprimer

---

**[CODE MORT] — 🟠 MAJEUR**  
📍 Localisation : `backend/core/db_manager.py` ligne ~477  
🔍 Problème : La méthode `get_price_history(designation, fournisseur)` n'est appelée nulle part dans le projet. Seule `get_price_history_by_product_id` est utilisée.  
✅ Solution : Supprimer ou marquer comme deprecated

---

**[CODE MORT] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/services/imageService.js`  
🔍 Problème : `compressBatch` est exportée mais jamais importée dans aucun fichier  
✅ Solution : Supprimer

---

**[CODE MORT] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/services/offlineQueue.js`  
🔍 Problème : `isOnline()` et `registerBackgroundSync()` sont exportées mais jamais importées  
✅ Solution : Supprimer

---

**[CODE MORT] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx`  
🔍 Problème : `const [compareSearch] = useState('')` — pas de setter, la valeur reste toujours `''`. Le prop `initialSearch={compareSearch}` passe toujours une chaîne vide  
✅ Solution : Supprimer l'état ou implémenter le setter

---

**[CODE MORT] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/pages/SettingsPage.jsx`  
🔍 Problème : Import `WifiOff` inutilisé  
✅ Solution : Supprimer

---

**[CODE MORT] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx` lignes ~109-118  
🔍 Problème : Le code de style XLSX (header styling) est mort — la lib `xlsx` community edition n'applique pas `cell.s`  
✅ Solution : Supprimer le code de style ou migrer vers `exceljs`

---

## 2. DEPENDANCES & PACKAGES

---

**[DEPS] — 🟠 MAJEUR**  
📍 Localisation : `requirements.txt`  
🔍 Problème : `Pillow==10.4.0` est listé mais **jamais importé** dans aucun fichier Python  
✅ Solution : Supprimer ou justifier la dépendance

---

**[DEPS] — 🟠 MAJEUR**  
📍 Localisation : `requirements.txt`  
🔍 Problème : Versions non pinées (`asyncpg>=0.30.0`, `google-genai>=1.0.0`, `boto3>=1.35.0`, `factur-x>=3.0.0`, `pytest>=8.0.0`, `requests>=2.28.0`). Les builds ne sont pas reproductibles  
⚠️ Impact : Un `pip install` en prod peut tirer une version incompatible  
✅ Solution : Piner toutes les versions exactes. Utiliser `pip-compile` (pip-tools) pour générer un lock file

---

**[DEPS] — 🟠 MAJEUR**  
📍 Localisation : `requirements.txt`  
🔍 Problème : `requests` est une dépendance de test seulement mais listée avec les dépendances de production  
✅ Solution : Créer un `requirements-dev.txt` séparé avec `pytest`, `pytest-asyncio`, `requests`

---

**[DEPS] — 🟠 MAJEUR**  
📍 Localisation : `requirements.txt`  
🔍 Problème : `lxml` est importée directement par `facturx_extractor.py` mais n'est pas listée explicitement (dépendance transitive de `factur-x`). Si `factur-x` change sa dépendance, le code casse  
✅ Solution : Ajouter `lxml` explicitement

---

**[DEPS] — 🔴 CRITIQUE**  
📍 Localisation : `docling-pwa/package.json`  
🔍 Problème : **TOUTES** les devDependencies sont dans `dependencies` : eslint, @eslint/js, eslint-plugin-*, @types/react, @types/react-dom, @vitejs/plugin-react, @vitejs/plugin-basic-ssl, postcss, autoprefixer, vite, vite-plugin-pwa. Il n'y a **aucune section `devDependencies`**  
⚠️ Impact : Le bundle de production inclut des outils de dev, image Docker plus lourde  
✅ Solution : Déplacer tous les outils de build/lint dans `devDependencies`

---

**[DEPS] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/package.json`  
🔍 Problème : `@types/react` et `@types/react-dom` installés mais c'est un projet JavaScript (pas TypeScript)  
✅ Solution : Supprimer ces packages

---

## 3. APPELS API & INTEGRATIONS EXTERNES

---

**[API] — 🔴 CRITIQUE**  
📍 Localisation : `docling-pwa/src/pages/ScanPage.jsx`  
🔍 Problème : Le polling (`while(true)`) dans `processItem()` et `handleCameraFile()` n'a **aucun AbortController**. Si l'utilisateur quitte la page pendant le polling, les boucles continuent en arrière-plan  
⚠️ Impact : Memory leak, mises à jour de state sur composant démonté, warnings React, consommation réseau inutile  
✅ Solution :

```javascript
useEffect(() => {
  const controller = new AbortController();
  // passer controller.signal aux appels axios
  return () => controller.abort();
}, []);
```

---

**[API] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/config/api.js` ligne 1  
🔍 Problème : Le fallback `http://localhost:8000` sera utilisé en production si `VITE_API_URL` n'est pas défini. Les requêtes partiront dans le vide  
✅ Solution :

```javascript
export const API_BASE_URL = import.meta.env.VITE_API_URL 
  || (import.meta.env.DEV ? 'http://localhost:8000' : (() => { throw new Error('VITE_API_URL requis en production') })())
```

---

**[API] — 🟠 MAJEUR**  
📍 Localisation : Tous les fichiers pages (`ScanPage`, `CataloguePage`, `DevisPage`, `HistoryPage`, `SettingsPage`, `CompareModal`)  
🔍 Problème : Pas d'instance Axios partagée. Chaque fichier crée ses propres appels sans intercepteur global pour les erreurs 401/403, timeout, retry  
✅ Solution : Créer un `src/services/apiClient.js` avec intercepteurs :

```javascript
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});
apiClient.interceptors.response.use(null, (error) => {
  if (error.response?.status === 401) { /* redirect login */ }
  return Promise.reject(error);
});
```

---

**[API] — 🟠 MAJEUR**  
📍 Localisation : `api.py` lignes 378-386  
🔍 Problème : **N+1 query** dans `compare_prices` — pour chaque résultat de comparaison (jusqu'à 20), une requête SQL séparée (`get_price_history_by_product_id`) est exécutée  
⚠️ Impact : 20 requêtes SQL au lieu d'une seule avec `WHERE produit_id IN (...)`  
✅ Solution : Batch query avec `WHERE produit_id = ANY($1::int[])` sur tous les IDs collectés

---

**[API] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/components/CompareModal.jsx`  
🔍 Problème : `doSearch()` fait un appel axios sans AbortController. Si l'utilisateur tape vite, les requêtes s'empilent (race condition) et la dernière réponse affichée peut ne pas correspondre au dernier terme cherché  
✅ Solution : AbortController + debounce

---

**[API] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/pages/HistoryPage.jsx`  
🔍 Problème : Mélange `fetch()` et `axios` dans le même flux (`handleRescan`). `fetch(facture.pdf_url)` suivi de `axios.post(ENDPOINTS.process)`  
✅ Solution : Uniformiser sur axios

---

## 4. SECURITE

---

**[SECU] — 🔴 CRITIQUE**  
📍 Localisation : `api.py` lignes 311-323  
🔍 Problème : L'endpoint `DELETE /api/v1/catalogue/reset` n'exige l'authentification **que si** le header `authorization` commence par `Bearer`. Si on ne passe rien, le check auth est **sauté** et seul `confirm=SUPPRIMER_TOUT` suffit. **N'importe qui peut vider la base**  
✅ Solution :

```python
@app.delete("/api/v1/catalogue/reset")
async def reset_catalogue(confirm: str = "", authorization: str = Header("")):
    payload = verify_token(authorization.removeprefix("Bearer ").strip())
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")
    if confirm != "SUPPRIMER_TOUT":
        raise HTTPException(status_code=400, detail="Confirmation requise")
    await DBManager.truncate_products()
    return {"message": "Catalogue vidé"}
```

---

**[SECU] — 🔴 CRITIQUE**  
📍 Localisation : `api.py` ligne 312, 435  
🔍 Problème : `authorization: str = ""` est interprété par FastAPI comme un **query parameter**, pas un header HTTP. Les tokens JWT sont exposés dans les URLs, access logs, historique navigateur, proxys  
✅ Solution : Utiliser `from fastapi import Header` et `authorization: str = Header("")`

---

**[SECU] — 🔴 CRITIQUE**  
📍 Localisation : `backend/services/auth_service.py`  
🔍 Problème : **Implémentation JWT entièrement maison** (encode/decode/sign manuels). Le padding base64, la comparaison de signatures, la gestion des edge cases sont des opérations critiques qui doivent être déléguées à une bibliothèque auditée  
⚠️ Impact : Vulnérabilité potentielle à des attaques timing, algorithm confusion, ou parsing incorrect  
✅ Solution : Remplacer par `PyJWT` ou `python-jose[cryptography]`

---

**[SECU] — 🔴 CRITIQUE**  
📍 Localisation : `backend/services/auth_service.py` ligne 18  
🔍 Problème : `JWT_SECRET = os.getenv("JWT_SECRET", "docling-dev-secret-change-in-prod")` — si la variable d'env n'est pas définie, **n'importe qui connaissant le code source peut forger des tokens admin**  
✅ Solution : Aucun fallback. Lever une exception au démarrage si `JWT_SECRET` n'est pas défini :

```python
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET non défini — impossible de démarrer")
```

---

**[SECU] — 🔴 CRITIQUE**  
📍 Localisation : `api.py` — tous les endpoints métier  
🔍 Problème : Les endpoints `/api/v1/catalogue`, `/api/v1/stats`, `/api/v1/history`, `/api/v1/invoices/process` sont **entièrement publics**. Aucun middleware d'authentification  
⚠️ Impact : N'importe qui avec l'URL de l'API peut lire les données, injecter des produits, consommer le quota Gemini  
✅ Solution : Ajouter un middleware FastAPI `Depends(get_current_user)` sur les routes protégées

---

**[SECU] — 🟠 MAJEUR**  
📍 Localisation : `api.py` lignes 90-107  
🔍 Problème : Le fichier uploadé est lu **entièrement en mémoire** (`await file.read()`) avant la vérification de taille. Un fichier de 500 Mo sera chargé en RAM avant d'être rejeté. Aucune validation de type MIME  
✅ Solution : Lire par chunks avec limite, valider le Content-Type et l'extension :

```python
MAX_UPLOAD = 50 * 1024 * 1024
chunks = []
size = 0
async for chunk in file:
    size += len(chunk)
    if size > MAX_UPLOAD:
        raise HTTPException(413, "Fichier trop volumineux")
    chunks.append(chunk)
file_bytes = b"".join(chunks)
```

---

**[SECU] — 🟠 MAJEUR**  
📍 Localisation : `backend/services/facturx_extractor.py` ligne 64  
🔍 Problème : `etree.fromstring(xml_bytes)` sans protection XXE (XML External Entity). Un PDF malicieux avec un XML Factur-X crafté pourrait lire des fichiers serveur ou déclencher un SSRF  
✅ Solution :

```python
parser = etree.XMLParser(resolve_entities=False, no_network=True)
root = etree.fromstring(xml_bytes, parser=parser)
```

---

**[SECU] — 🟠 MAJEUR**  
📍 Localisation : `api.py` lignes 78-83  
🔍 Problème : CORS `allow_methods=["*"]` et `allow_headers=["*"]` en production  
✅ Solution : Restreindre aux méthodes nécessaires : `["GET", "POST", "DELETE", "OPTIONS"]` et headers : `["Authorization", "Content-Type"]`

---

**[SECU] — 🟠 MAJEUR**  
📍 Localisation : `api.py` — endpoints auth  
🔍 Problème : Aucun rate limiting sur `/api/v1/auth/register` et `/api/v1/auth/login`. Vulnérable au brute-force  
✅ Solution : Ajouter `slowapi` ou un middleware de rate limiting

---

**[SECU] — 🟠 MAJEUR**  
📍 Localisation : `api.py` lignes 202, 225, 265, etc.  
🔍 Problème : `raise HTTPException(status_code=500, detail=str(e))` — expose les détails d'erreur interne (noms de tables, messages SQL)  
✅ Solution : Logger l'erreur détaillée, retourner un message générique :

```python
except Exception as e:
    logger.error("Erreur get_catalogue: %s", e, exc_info=True)
    raise HTTPException(status_code=500, detail="Erreur interne du serveur")
```

---

**[SECU] — 🟠 MAJEUR**  
📍 Localisation : `backend/services/auth_service.py` ligne 79  
🔍 Problème : PBKDF2 avec 100 000 itérations. En 2026, OWASP recommande **600 000+ itérations** pour PBKDF2-SHA256, ou idéalement `argon2id`  
✅ Solution : Migrer vers `argon2-cffi`

---

**[SECU] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx` — export CSV  
🔍 Problème : Les données utilisateur sont insérées dans le CSV sans protection contre l'injection de formules Excel (`=CMD(...)`, `+`, `-`, `@`). Un fournisseur malveillant pourrait injecter une formule  
✅ Solution : Préfixer les cellules commençant par `=`, `+`, `-`, `@` avec un apostrophe `'`

---

**[SECU] — 🟡 MINEUR**  
📍 Localisation : `backend/core/config.py` ligne 54  
🔍 Problème : `os.getenv("PWA_URL", "")` ajoute une chaîne vide à ALLOWED_ORIGINS si non défini  
✅ Solution : Filtrer les valeurs vides :

```python
ALLOWED_ORIGINS = [o for o in [...] if o]
```

---

## 5. PERFORMANCE

---

**[PERF] — 🔴 CRITIQUE**  
📍 Localisation : `docling-pwa/src/App.jsx`  
🔍 Problème : **Aucun lazy loading**. Les 6 pages sont importées statiquement. `recharts`, `xlsx`, `jspdf`, `jspdf-autotable`, `framer-motion` sont chargés dans le bundle initial. Estimation : **>500 Ko gzippé**  
✅ Solution :

```javascript
const ScanPage = React.lazy(() => import('./pages/ScanPage'));
const CataloguePage = React.lazy(() => import('./pages/CataloguePage'));
// etc.
// Dans Routes: <Suspense fallback={<LoadingSpinner />}><ScanPage /></Suspense>
```

---

**[PERF] — 🟠 MAJEUR**  
📍 Localisation : `backend/core/orchestrator.py` lignes 87-103  
🔍 Problème : L'upload S3 et la sauvegarde BDD sont exécutés **séquentiellement** alors qu'ils sont indépendants  
✅ Solution :

```python
nb_saved, pdf_url = await asyncio.gather(
    DBManager.upsert_products_batch(products_dicts, source=source),
    asyncio.to_thread(StorageService.upload_file, file_bytes, filename, content_type=mime_type),
)
```

---

**[PERF] — 🟠 MAJEUR**  
📍 Localisation : `backend/core/db_manager.py` lignes 173-178  
🔍 Problème : Batch INSERT exécuté un produit à la fois dans une boucle `for`. Avec 50 produits, c'est 50 round-trips SQL  
✅ Solution : Utiliser `executemany` ou `COPY` pour les lots, ou construire un seul `INSERT ... VALUES (...), (...), ...`

---

**[PERF] — 🟠 MAJEUR**  
📍 Localisation : `api.py` — 5 endpoints différents  
🔍 Problème : Le pattern de sérialisation date/Decimal est copié-collé dans **5 endpoints** :

```python
for k, v in r.items():
    if hasattr(v, "isoformat"):
        r[k] = v.isoformat()
    elif hasattr(v, "__float__"):
        r[k] = float(v)
```

⚠️ Impact : Violation DRY massive, maintenance coûteuse  
✅ Solution : Extraire en utilitaire :

```python
def serialize_row(row: dict) -> dict:
    return {k: v.isoformat() if hasattr(v, 'isoformat') else float(v) if hasattr(v, '__float__') else v for k, v in row.items()}
```

---

**[PERF] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/services/offlineQueue.js`  
🔍 Problème : `getPendingCount()` charge TOUS les items IndexedDB (avec leurs ArrayBuffer de fichiers) juste pour `.length`. Devrait utiliser `objectStore.count()`  
✅ Solution : Utiliser `IDBObjectStore.count()` directement

---

**[PERF] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/pages/ScanPage.jsx`  
🔍 Problème : `URL.createObjectURL(file)` sans jamais appeler `URL.revokeObjectURL()` — fuite mémoire  
✅ Solution : Révoquer dans le cleanup du useEffect ou quand l'URL n'est plus nécessaire

---

## 6. ARCHITECTURE & STRUCTURE

---

**[ARCHI] — 🟠 MAJEUR**  
📍 Localisation : `api.py` lignes 279-282, 333-345  
🔍 Problème : Les endpoints `get_facture_pdf_url` et `get_price_history` exécutent du SQL directement dans le controller au lieu de passer par `DBManager`  
⚠️ Impact : Contournement de la couche d'abstraction, impossible à mocker pour les tests  
✅ Solution : Ajouter ces méthodes dans `DBManager`

---

**[ARCHI] — 🟠 MAJEUR**  
📍 Localisation : `api.py` lignes 49-50  
🔍 Problème : Variables globales mutables `_GEMINI_CONSECUTIVE_ERRORS` et `_GEMINI_CIRCUIT_BREAKER_THRESHOLD` ne sont pas thread-safe avec `asyncio.Semaphore(3)` permettant 3 tâches concurrentes  
✅ Solution : Utiliser `asyncio.Lock()` pour protéger les incrémentations/décrémentations, ou encapsuler dans une classe CircuitBreaker

---

**[ARCHI] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/pages/ValidationPage.jsx` et `CataloguePage.jsx`  
🔍 Problème : La constante `FAMILLES` est définie **deux fois** avec des valeurs différentes (CataloguePage inclut "Electricité", pas ValidationPage)  
✅ Solution : Centraliser dans un fichier `src/constants.js`

---

**[ARCHI] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/store/useStore.js`  
🔍 Problème : `get queueStats()` — un getter JS natif dans un store Zustand ne crée **pas** de souscription réactive. Les composants qui lisent `queueStats` ne se re-rendront pas quand les valeurs changent  
✅ Solution : Convertir en selecteur externe ou en fonction calculée

---

**[ARCHI] — 🟡 MINEUR**  
📍 Localisation : `backend/core/db_manager.py` ligne 23  
🔍 Problème : `DATABASE_URL` est définie en global ET dans `Config`. Deux sources de vérité  
✅ Solution : Utiliser uniquement `Config.DATABASE_URL`

---

**[ARCHI] — 🟡 MINEUR**  
📍 Localisation : `backend/core/config.py`  
🔍 Problème : Toutes les valeurs Config sont évaluées à l'import module. Impossible de surcharger pour les tests sans `unittest.mock.patch`  
✅ Solution : Utiliser `pydantic_settings.BaseSettings` pour une config injectable et testable

---

**[ARCHI] — 🟡 MINEUR**  
📍 Localisation : `backend/services/gemini_service.py` ligne 183  
🔍 Problème : `await __import__("asyncio").sleep(wait)` — hack `__import__` au lieu d'un import propre  
✅ Solution : Ajouter `import asyncio` en haut du fichier

---

## 7. TESTS & QUALITE

---

**[TESTS] — 🔴 CRITIQUE**  
📍 Localisation : `tests/test_schemas.py` ligne ~125  
🔍 Problème : Le test `test_default_source` attend `"mobile"` mais le modèle définit `source: str = "pc"`. **Ce test échoue systématiquement**  
✅ Solution : Corriger l'assertion à `"pc"` ou corriger le modèle

---

**[TESTS] — 🟠 MAJEUR**  
📍 Localisation : `.github/workflows/ci.yml`  
🔍 Problème : Le job `backend-test` n'a **aucun service PostgreSQL**. Les tests d'intégration DB échouent obligatoirement en CI  
✅ Solution : Ajouter un service PostgreSQL dans le workflow :

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_PASSWORD: test
    ports:
      - 5432:5432
```

---

**[TESTS] — 🟠 MAJEUR**  
📍 Localisation : `tests/conftest.py` lignes 5-8  
🔍 Problème : La fixture `event_loop` est dépréciée depuis `pytest-asyncio >= 0.23`  
✅ Solution : Supprimer la fixture et configurer `asyncio_mode = "auto"` dans `pyproject.toml`

---

**[TESTS] — 🟠 MAJEUR**  
📍 Localisation : Projet global  
🔍 Problème : **Aucun test frontend**. Pas de tests unitaires React, pas de tests d'intégration, pas de tests E2E  
✅ Solution : Ajouter `vitest` + `@testing-library/react` pour les tests unitaires, `Playwright` pour les E2E

---

**[TESTS] — 🟡 MINEUR**  
📍 Localisation : CI pipeline  
🔍 Problème : Pas de linting (ni backend ruff/flake8, ni frontend eslint) dans le CI  
✅ Solution : Ajouter des jobs de lint dans le CI

---

## 8. BASE DE DONNEES & DATA LAYER

---

**[DB] — 🟠 MAJEUR**  
📍 Localisation : `backend/schema_neon.sql` ligne 27  
🔍 Problème : `produits.fournisseur` est un `VARCHAR(200)` libre sans clé étrangère vers `fournisseurs`. La table `fournisseurs` existe mais n'est pas référencée. Incohérences de données garanties  
✅ Solution : Ajouter `REFERENCES fournisseurs(nom)` ou migrer vers une FK sur `fournisseurs.id`

---

**[DB] — 🟠 MAJEUR**  
📍 Localisation : `backend/schema_neon.sql`  
🔍 Problème : Pas de contraintes `CHECK` sur les colonnes `status`/`role`/`confidence`/`source`. N'importe quelle valeur peut être insérée  
✅ Solution :

```sql
ALTER TABLE jobs ADD CONSTRAINT chk_jobs_status CHECK (status IN ('processing', 'completed', 'error'));
ALTER TABLE users ADD CONSTRAINT chk_users_role CHECK (role IN ('user', 'admin'));
ALTER TABLE produits ADD CONSTRAINT chk_produits_confidence CHECK (confidence IN ('high', 'low'));
```

---

**[DB] — 🟠 MAJEUR**  
📍 Localisation : `backend/schema_neon.sql`  
🔍 Problème : Script SQL monolithique sans outil de migration versionné. Pas de rollback possible, pas de tracking des migrations appliquées  
✅ Solution : Migrer vers Alembic (SQLAlchemy) ou `yoyo-migrations`

---

**[DB] — 🟠 MAJEUR**  
📍 Localisation : `backend/core/db_manager.py` lignes 194-195  
🔍 Problème : Les erreurs d'insertion dans `prix_historique` sont **silencieusement ignorées** (`except Exception: pass`). Perte de données d'historique sans trace  
✅ Solution : Logger l'erreur au minimum :

```python
except Exception as e:
    logger.warning("Erreur insertion prix_historique: %s", e)
```

---

**[DB] — 🟡 MINEUR**  
📍 Localisation : `backend/schema_neon.sql` — table `users`  
🔍 Problème : La colonne `password_hash` est en `TEXT` sans contrainte de longueur minimale. Pas de contrainte `CHECK (email ~* '^.+@.+\..+$')` sur l'email  
✅ Solution : Ajouter des contraintes de validation

---

## 9. DEVOPS & CONFIGURATION

---

**[DEVOPS] — 🔴 CRITIQUE**  
📍 Localisation : `api.py` lignes 453-456  
🔍 Problème : Le `/health` retourne toujours `{"status": "ok"}` même si la base de données est down. Le load balancer Render ne détectera jamais une panne Neon  
✅ Solution :

```python
@app.get("/health")
async def health():
    try:
        pool = await DBManager.get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ok", "db": "connected", "version": "3.0.0"}
    except Exception:
        raise HTTPException(503, detail="Database unreachable")
```

---

**[DEVOPS] — 🔴 CRITIQUE**  
📍 Localisation : `run_local.bat` lignes 13-14  
🔍 Problème : `taskkill /F /IM python.exe /T` et `taskkill /F /IM node.exe /T` tuent **TOUS** les processus Python et Node du système, pas seulement ceux du projet  
⚠️ Impact : Destruction d'autres projets en cours d'exécution  
✅ Solution : Utiliser des fichiers PID ou tuer par port spécifique

---

**[DEVOPS] — 🟠 MAJEUR**  
📍 Localisation : `.gitignore`  
🔍 Problème : `node_modules/` n'est **pas listé** dans le `.gitignore` racine. Le `git status` montre des fichiers node_modules trackés  
✅ Solution : Ajouter `node_modules/` au `.gitignore` racine et `git rm -r --cached docling-pwa/node_modules`

---

**[DEVOPS] — 🟠 MAJEUR**  
📍 Localisation : Projet global  
🔍 Problème : Le `docker-compose.yml` a été **supprimé** (`D docker-compose.yml` dans git status). Impossible de démarrer l'environnement de dev complet (API + DB + PWA) en une commande  
✅ Solution : Recréer un `docker-compose.yml` avec les services `api`, `postgres`, `pwa`

---

**[DEVOPS] — 🟠 MAJEUR**  
📍 Localisation : `Dockerfile`  
🔍 Problème : Pas de `HEALTHCHECK` Docker, pas de `.dockerignore` détecté (les PDFs, tests, node_modules sont copiés dans l'image)  
✅ Solution : Créer un `.dockerignore` et ajouter un `HEALTHCHECK`

---

**[DEVOPS] — 🟠 MAJEUR**  
📍 Localisation : `.env.example`  
🔍 Problème : `JWT_SECRET` est commenté et présenté comme optionnel (`# JWT_SECRET=change-this-to-a-long-random-string`). En réalité, sans lui, la valeur par défaut hardcodée est utilisée  
✅ Solution : Le rendre obligatoire dans `.env.example` et dans le code

---

**[DEVOPS] — 🟡 MINEUR**  
📍 Localisation : Projet global  
🔍 Problème : Aucun monitoring (Sentry, Prometheus), aucun alerting, aucune métrique métier  
✅ Solution : Intégrer Sentry pour le error tracking au minimum

---

**[DEVOPS] — 🟡 MINEUR**  
📍 Localisation : `run_local.bat`  
🔍 Problème : Script Windows uniquement. Aucun équivalent Linux/Mac  
✅ Solution : Ajouter un `run_local.sh` ou un `Makefile`

---

## 10. ACCESSIBILITE & UX TECHNIQUE

---

**[A11Y] — 🔴 CRITIQUE**  
📍 Localisation : `docling-pwa/src/components/CompareModal.jsx` et `ValidationPage.jsx` (lightbox)  
🔍 Problème : Les modals n'ont pas de `role="dialog"`, pas d'`aria-modal="true"`, pas de focus trap, pas de fermeture par `Escape`  
⚠️ Impact : Inaccessible pour les utilisateurs de lecteurs d'écran et navigation clavier  
✅ Solution : Utiliser `@radix-ui/react-dialog` ou implémenter manuellement role, aria-modal, focus trap, et keydown Escape

---

**[A11Y] — 🟠 MAJEUR**  
📍 Localisation : Tous les fichiers pages  
🔍 Problème : Les boutons icon-only (Trash2, Plus, Minus, Camera, etc.) n'ont **aucun `aria-label`**. Invisibles pour les lecteurs d'écran  
✅ Solution : Ajouter `aria-label="Supprimer"`, `aria-label="Ajouter"`, etc.

---

**[A11Y] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/pages/DevisPage.jsx`, `ValidationPage.jsx`  
🔍 Problème : Les inputs utilisent `placeholder` au lieu de `<label>`. Le placeholder disparaît à la saisie, l'utilisateur perd le contexte  
✅ Solution : Ajouter des `<label htmlFor="...">` associés

---

**[A11Y] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx`  
🔍 Problème : La vue "tableau" utilise des `<div>` avec flex au lieu de `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<td>`. Les lecteurs d'écran ne comprennent pas la structure tabulaire  
✅ Solution : Utiliser un vrai `<table>` HTML sémantique

---

**[A11Y] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/main.jsx`  
🔍 Problème : Pas d'`ErrorBoundary` global. Une erreur JS dans un composant crash toute l'app sans message utilisateur  
✅ Solution : Ajouter un `ErrorBoundary` avec un fallback UI

---

## 11. INTERNATIONALISATION & LOCALISATION

---

**[I18N] — 🟠 MAJEUR**  
📍 Localisation : Tous les fichiers frontend  
🔍 Problème : Tous les textes sont hardcodés en français (avec parfois des accents manquants dans `DevisPage.jsx`). Aucun système i18n  
⚠️ Impact : Si le projet doit être multilingue un jour, refactoring massif nécessaire  
✅ Solution : Si monolingue assumé, documenter cette décision. Sinon, intégrer `react-i18next`

---

**[I18N] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/src/pages/ValidationPage.jsx` ligne ~  
🔍 Problème : TVA hardcodée à 21% (`* 1.21`). Le taux varie selon le pays (5.5%/10%/20% en France, 21% en Belgique, 21% en Espagne)  
✅ Solution : Externaliser en configuration ou constante paramétrable

---

**[I18N] — 🟡 MINEUR**  
📍 Localisation : `docling-pwa/src/pages/DevisPage.jsx`  
🔍 Problème : Caractères accentués manquants dans l'UI ("Generez" au lieu de "Générez", "selectionnes" au lieu de "sélectionnés")  
✅ Solution : Corriger les accents

---

## 12. DOCUMENTATION & MAINTENABILITE

---

**[DOC] — 🟠 MAJEUR**  
📍 Localisation : `README.md`  
🔍 Problème : Le README principal fait 15 lignes. Pas d'instructions d'installation détaillées, pas de prérequis, pas de variables d'env expliquées  
✅ Solution : README complet avec : prérequis, installation, configuration .env, démarrage local, architecture, déploiement

---

**[DOC] — 🟠 MAJEUR**  
📍 Localisation : `docling-pwa/README.md`  
🔍 Problème : 6 lignes. Aucune instruction de setup (`npm install`, `npm run dev`), pas de variables d'env documentées  
✅ Solution : Documenter le setup complet

---

**[DOC] — 🟡 MINEUR**  
📍 Localisation : Projet global  
🔍 Problème : Pas de CHANGELOG, pas de CONTRIBUTING.md, pas de LICENSE  
✅ Solution : Créer ces fichiers standard

---

**[DOC] — 🔵 INFO**  
📍 Localisation : `docs/` (13 fichiers markdown)  
🔍 Problème : Bonne base documentaire existante, mais dispersée et potentiellement obsolète  
✅ Solution : Auditer la cohérence docs/ vs code actuel

---

## BUG CONFIRME

---

**[BUG] — 🔴 CRITIQUE**  
📍 Localisation : `backend/schemas/invoice.py` lignes 44-46  
🔍 Problème : Division par zéro si `remise_pct == 100` :

```python
ecart = abs(self.prix_remise_ht - computed) / computed  # computed = 0 si remise = 100%
```

✅ Solution : Guard clause `if computed == 0`

---

## TABLEAU RECAPITULATIF

| # | Catégorie | Sévérité | Fichier | Statut |
|---|-----------|----------|---------|--------|
| 1 | Sécurité | 🔴 CRITIQUE | `api.py:311` | DELETE sans auth obligatoire |
| 2 | Sécurité | 🔴 CRITIQUE | `api.py:312,435` | Token en query param |
| 3 | Sécurité | 🔴 CRITIQUE | `auth_service.py` | JWT maison |
| 4 | Sécurité | 🔴 CRITIQUE | `auth_service.py:18` | JWT_SECRET hardcodé |
| 5 | Sécurité | 🔴 CRITIQUE | `api.py` (global) | Endpoints métier sans auth |
| 6 | Bug | 🔴 CRITIQUE | `invoice.py:45` | Division par zéro |
| 7 | DevOps | 🔴 CRITIQUE | `api.py:453` | Health check ne vérifie pas la DB |
| 8 | DevOps | 🔴 CRITIQUE | `run_local.bat:13-14` | taskkill tue tous les processus |
| 9 | Performance | 🔴 CRITIQUE | `App.jsx` | Pas de lazy loading (bundle >500Ko) |
| 10 | Tests | 🔴 CRITIQUE | `test_schemas.py:125` | Test avec assertion incorrecte |
| 11 | A11y | 🔴 CRITIQUE | `CompareModal.jsx` | Modal sans accessibilité |
| 12 | Sécurité | 🟠 MAJEUR | `api.py:90` | Upload lu en RAM sans limite |
| 13 | Sécurité | 🟠 MAJEUR | `facturx_extractor.py:64` | XXE vulnerability |
| 14 | Sécurité | 🟠 MAJEUR | `api.py:78` | CORS trop permissif |
| 15 | Sécurité | 🟠 MAJEUR | `api.py` | Pas de rate limiting auth |
| 16 | Sécurité | 🟠 MAJEUR | `api.py` | Erreurs internes exposées |
| 17 | Sécurité | 🟠 MAJEUR | `auth_service.py:79` | PBKDF2 itérations insuffisantes |
| 18 | Sécurité | 🟠 MAJEUR | `CataloguePage.jsx` | CSV injection |
| 19 | Perf | 🟠 MAJEUR | `api.py:378` | N+1 query compare_prices |
| 20 | Perf | 🟠 MAJEUR | `orchestrator.py:87` | Pipeline sériel BDD+S3 |
| 21 | Perf | 🟠 MAJEUR | `db_manager.py:173` | Batch INSERT un par un |
| 22 | DRY | 🟠 MAJEUR | `api.py` x5 | Sérialisation copié-collée |
| 23 | Archi | 🟠 MAJEUR | `api.py:279` | SQL dans le controller |
| 24 | Archi | 🟠 MAJEUR | `useStore.js` | getter non-réactif Zustand |
| 25 | Archi | 🟠 MAJEUR | `Validation/Catalogue` | FAMILLES dupliqué |
| 26 | API | 🟠 MAJEUR | `ScanPage.jsx` | Polling sans AbortController |
| 27 | API | 🟠 MAJEUR | `config/api.js` | Fallback localhost en prod |
| 28 | API | 🟠 MAJEUR | 6 fichiers | Pas d'instance axios partagée |
| 29 | DB | 🟠 MAJEUR | `schema_neon.sql:27` | FK fournisseur manquante |
| 30 | DB | 🟠 MAJEUR | `schema_neon.sql` | Pas de CHECK constraints |
| 31 | DB | 🟠 MAJEUR | `schema_neon.sql` | Pas de migrations versionnées |
| 32 | DB | 🟠 MAJEUR | `db_manager.py:194` | Erreur silencieuse prix_historique |
| 33 | Deps | 🔴 CRITIQUE | `package.json` | Tout en dependencies |
| 34 | Deps | 🟠 MAJEUR | `requirements.txt` | Versions non pinées |
| 35 | Tests | 🟠 MAJEUR | CI | Pas de PostgreSQL en CI |
| 36 | Tests | 🟠 MAJEUR | Projet | Aucun test frontend |
| 37 | DevOps | 🟠 MAJEUR | `.gitignore` | node_modules non ignoré |
| 38 | DevOps | 🟠 MAJEUR | Projet | docker-compose supprimé |
| 39 | A11y | 🟠 MAJEUR | Global | Boutons icon-only sans aria-label |
| 40 | A11y | 🟠 MAJEUR | Global | Inputs sans labels |
| 41 | I18n | 🟠 MAJEUR | Global | TVA 21% hardcodée |
| 42 | Doc | 🟠 MAJEUR | README.md | Documentation insuffisante |

---

## SCORE DE SANTE GLOBAL

```
🏥 SCORE SANTÉ : 31/100
```

| Domaine | Score | Détails |
|---------|-------|---------|
| **Sécurité** | 4/20 | JWT maison, endpoints publics, XXE, pas de rate limiting, CORS ouvert, token en query param |
| **Performance** | 9/20 | Pas de lazy loading, N+1 queries, pipeline sériel, INSERT en boucle |
| **Maintenabilité** | 8/20 | DRY violations x5, SQL dans controllers, config non injectable, code mort partout |
| **Qualité code** | 6/20 | Bug division/0, getter Zustand cassé, test qui échoue, race conditions |
| **Tests** | 4/20 | Test incorrect, CI sans DB, zéro test frontend, fixture dépréciée |

---

## PRIORITES IMMEDIATES (Top 5 — à corriger MAINTENANT)

1. **Sécuriser l'endpoint DELETE `/api/v1/catalogue/reset`** — n'importe qui peut vider la base. Utiliser `Header()` FastAPI et rendre l'auth obligatoire.

2. **Remplacer le JWT maison par PyJWT** — la crypto faite maison est le risque #1. Supprimer le fallback de `JWT_SECRET` et lever une exception au démarrage si absent.

3. **Ajouter l'authentification sur tous les endpoints métier** — actuellement l'API entière est publique. Créer un `Depends(get_current_user)` et l'appliquer.

4. **Protéger contre XXE dans `facturx_extractor.py`** — un PDF malicieux peut lire les fichiers du serveur. Ajouter `XMLParser(resolve_entities=False, no_network=True)`.

5. **Ajouter `React.lazy()` sur toutes les pages** — le bundle initial charge recharts+xlsx+jspdf inutilement. Impact direct sur le LCP et l'expérience premier chargement.

---

Ce projet a une **bonne base fonctionnelle** et une architecture modulaire correcte, mais il n'est **pas prêt pour la production** en l'état. Les 5 failles critiques de sécurité doivent être corrigées avant tout déploiement public. La dette technique est significative mais gérable en 2-3 sprints si priorisée correctement.