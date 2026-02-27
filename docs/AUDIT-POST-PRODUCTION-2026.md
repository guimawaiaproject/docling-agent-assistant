# 🧠 AUDIT POST-PRODUCTION EXPERT SENIOR 2026 — Docling Agent v3

**Projet** : Docling Agent — Extraction de factures BTP par IA (Gemini)
**Stack** : FastAPI + React 19/Vite PWA + PostgreSQL Neon + Google Gemini
**Date** : 26 février 2026

---

## 1. 🧟 CODE MORT & INUTILISÉ

---

**[CODE MORT] — 🟠 MAJEUR**
📍 Localisation : `docling-pwa/package.json` ligne 34
🔍 Problème : `workbox-window` est une dépendance directe mais **jamais importée** dans le code source. Le plugin `vite-plugin-pwa` gère le service worker en interne.
⚠️ Impact : Bundle inutile, confusion sur l'usage
✅ Solution : Supprimer `workbox-window` des dependencies

---

**[CODE MORT] — 🟡 MINEUR**
📍 Localisation : `docling-pwa/src/config/api.js`
🔍 Problème : L'endpoint `price-history` existe côté API (`/api/v1/catalogue/price-history/{product_id}`) mais **n'est pas exposé** dans `ENDPOINTS`. Le frontend n'y accède jamais directement (l'historique est fourni par `compare` avec `with_history=true`).
⚠️ Impact : Endpoint orphelin côté frontend
✅ Solution : Ajouter `priceHistory: (id) => \`${API_BASE_URL}/api/v1/catalogue/price-history/${id}\`` si usage prévu, sinon documenter

---

**[CODE MORT] — 🟡 MINEUR**
📍 Localisation : `docling-pwa/src/config/api.js`
🔍 Problème : L'endpoint `reset` (DELETE `/api/v1/catalogue/reset`) n'est pas dans `ENDPOINTS`. La page Settings n'expose pas de bouton reset admin.
⚠️ Impact : Endpoint admin non accessible depuis la PWA
✅ Solution : Soit ajouter l'endpoint + UI admin protégée, soit documenter comme API-only

---

## 2. 📦 DÉPENDANCES & PACKAGES

---

**[DEPS] — 🔴 CRITIQUE**
📍 Localisation : `docling-pwa/package.json`
🔍 Problème : **xlsx** (SheetJS) a 2 CVE actives :
- GHSA-4r6h-8v6p-xvw6 (Prototype Pollution)
- GHSA-5pgg-2g8v-p4x9 (ReDoS)

`npm audit` signale : *No fix available*
⚠️ Impact : Vulnérabilités de sécurité en production
✅ Solution : Migrer vers **exceljs** ou **xlsx-js-style** (fork maintenu), ou valider/sanitiser strictement les fichiers Excel uploadés

---

**[DEPS] — 🟠 MAJEUR**
📍 Localisation : `docling-pwa/package.json`
🔍 Problème : **esbuild** (via Vite) vulnérable GHSA-67mh-4wv8-2f99 (moderate) — requêtes arbitraires au dev server
⚠️ Impact : Risque en dev uniquement ; fix via `npm audit fix --force` installe Vite 7 (breaking)
✅ Solution : Suivre les mises à jour Vite ; en dev, ne pas exposer le serveur sur le réseau public

---

**[DEPS] — 🟠 MAJEUR**
📍 Localisation : `docling-pwa/package.json`
🔍 Problème : **vitest** est dans `dependencies` au lieu de `devDependencies`.
⚠️ Impact : Bundle de production potentiellement alourdi
✅ Solution : Déplacer `vitest`, `@vitest/coverage-v8`, `@testing-library/*`, `jsdom`, `axios-mock-adapter` dans `devDependencies`

---

**[DEPS] — 🟡 MINEUR**
📍 Localisation : `requirements.txt`
🔍 Problème : `Pillow` n'est pas listé — `opencv-python-headless` peut inclure des dépendances image. Vérifier si Pillow est utilisé ailleurs.
✅ Solution : Si `Pillow` n'est pas importé, ne pas l'ajouter. L'audit précédent mentionnait Pillow inutilisé — confirmé absent du `requirements.txt` actuel.

---

## 3. 🌐 APPELS API & INTÉGRATIONS EXTERNES

---

**[API] — 🔴 CRITIQUE**
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx` lignes 125–139
🔍 Problème : Le catalogue est récupéré **sans paramètres** (`limit`, `cursor`, `famille`, `fournisseur`, `search`). L'API retourne par défaut **50 produits maximum**. Le filtrage est fait **côté client** sur ces 50 produits.
⚠️ Impact : Si catalogue > 50 produits, les utilisateurs ne voient qu'une fraction. Pagination inexistante.
✅ Solution : Passer les filtres à l'API et implémenter la pagination cursor :

```javascript
const [cursor, setCursor] = useState(null)
const fetchCatalogue = useCallback(async () => {
  setLoading(true)
  try {
    const params = { limit: 100 }
    if (cursor) params.cursor = cursor
    if (famille !== 'Toutes') params.famille = famille
    if (fournisseur !== 'Tous') params.fournisseur = fournisseur
    if (search.trim()) params.search = search.trim()
    const [catRes, fournRes] = await Promise.all([
      apiClient.get(ENDPOINTS.catalogue, { params }),
      apiClient.get(ENDPOINTS.fournisseurs),
    ])
    const data = catRes.data
    setAllProducts(prev => cursor ? [...prev, ...(data.products || [])] : (data.products || []))
    setCursor(data.next_cursor)
    setHasMore(data.has_more ?? false)
    setFournisseurs(fournRes.data.fournisseurs || [])
  } catch { toast.error('Impossible de charger le catalogue') }
  finally { setLoading(false) }
}, [cursor, famille, fournisseur, search])
```

---

**[API] — 🟠 MAJEUR**
📍 Localisation : `docling-pwa/src/config/api.js` lignes 3–10
🔍 Problème : Si `VITE_API_URL` n'est pas défini en production, `resolveBaseURL()` retourne `''` (URL relative). Le `console.warn` est présent mais le fallback peut être incorrect selon le déploiement (Netlify, sous-domaine, etc.).
⚠️ Impact : Requêtes API vers la mauvaise origine en production
✅ Solution : Faire échouer le build si `VITE_API_URL` n'est pas défini en prod :

```javascript
if (import.meta.env.PROD && !_env) {
  throw new Error('VITE_API_URL must be set for production build')
}
```

---

**[API] — 🟡 MINEUR**
📍 Localisation : `docling-pwa/src/pages/CompareModal.jsx` ligne 75
🔍 Problème : L'appel `ENDPOINTS.compare` ne passe pas `with_history`. Par défaut l'API renvoie `with_history=true`, donc OK.
✅ Solution : Pas de changement requis ; documenter si besoin.

---

## 4. 🔐 SÉCURITÉ

---

**[SÉCURITÉ] — 🔴 CRITIQUE**
📍 Localisation : `docling-pwa/src` — **aucune page de login/register**
🔍 Problème : L'API exige un token Bearer pour presque tous les endpoints. La PWA n'a **aucune page de connexion ou d'inscription**. Le token doit être injecté manuellement (localStorage) ou via un script externe.
⚠️ Impact : **Impossible pour un utilisateur final de se connecter.** L'application est inutilisable en production multi-utilisateur.
✅ Solution : Créer une page Login/Register (ou une route protégée avec redirection vers login si 401) :

```jsx
// Exemple : pages/LoginPage.jsx
// - Formulaire email/password
// - POST /api/v1/auth/login
// - Stocker token dans localStorage
// - Rediriger vers /scan
// App.jsx : route /login, ProtectedRoute qui vérifie token et redirige si absent
```

---

**[SÉCURITÉ] — 🟠 MAJEUR**
📍 Localisation : `docling-pwa/src/services/apiClient.js` ligne 10
🔍 Problème : Token JWT stocké dans **localStorage**. Vulnérable en cas de XSS.
⚠️ Impact : Vol de session si un script malveillant injecte du code
✅ Solution : Privilégier `httpOnly` cookies côté backend (si possible). Sinon, minimiser la surface XSS (pas de `dangerouslySetInnerHTML`, validation CSP stricte).

---

**[SÉCURITÉ] — 🟠 MAJEUR**
📍 Localisation : `docling-pwa/vite.config.js` lignes 29–64
🔍 Problème : Le cache Workbox pour `/api/v1/catalogue`, `/api/v1/stats`, `/api/v1/history` stocke les réponses par URL. Les requêtes avec `Authorization: Bearer <token>` peuvent être partagées si le cache ne distingue pas les utilisateurs.
⚠️ Impact : Données d'un utilisateur potentiellement servies à un autre (cache key = URL uniquement)
✅ Solution : Exclure les endpoints authentifiés du cache, ou configurer Workbox pour inclure les headers dans la clé de cache (si supporté).

---

**[SÉCURITÉ] — 🟡 MINEUR**
📍 Localisation : `.env.example` ligne 26
🔍 Problème : `JWT_SECRET=change-this-to-a-long-random-string` — valeur par défaut faible si le fichier est copié sans modification.
✅ Solution : `Config.validate()` exige déjà `JWT_SECRET` non vide. S'assurer que le README insiste sur `openssl rand -hex 32`.

---

## 5. ⚡ PERFORMANCE

---

**[PERF] — 🟠 MAJEUR**
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx`
🔍 Problème : Filtrage et tri effectués **côté client** sur tout le tableau. Avec 50+ produits, le `useMemo` recalcule à chaque changement de `search`, `famille`, `fournisseur`, `sortKey`, `sortDir`.
⚠️ Impact : Re-renders inutiles si le catalogue grossit
✅ Solution : Déjà partiellement atténué par la virtualisation (react-virtual). Déplacer le filtrage côté API (voir section API).

---

**[PERF] — 🟡 MINEUR**
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx`
🔍 Problème : `fetchCatalogue` appelé sans `limit` — le backend limite à 200 max. Pour un catalogue de 1000 produits, 5 appels seraient nécessaires avec pagination.
✅ Solution : Implémenter le chargement progressif (cursor) comme décrit en section API.

---

## 6. 🏗️ ARCHITECTURE & STRUCTURE

---

**[ARCHI] — 🟠 MAJEUR**
📍 Localisation : `api.py` lignes 368–391, 424–443
🔍 Problème : `register`, `login` et `get_price_history` exécutent du **SQL direct** dans le controller au lieu de passer par `DBManager` ou un service dédié.
⚠️ Impact : Violation de la séparation des responsabilités, logique dupliquée, tests plus difficiles
✅ Solution : Créer `AuthService.register()`, `AuthService.login()` et `DBManager.get_price_history()` ; appeler depuis les routes.

---

**[ARCHI] — 🟡 MINEUR**
📍 Localisation : `backend/core/config.py`
🔍 Problème : La classe `Config` utilise des attributs de classe statiques qui sont **copiés au chargement** depuis `_settings`. Si `_settings` change (reload), `Config` ne reflète pas les changements.
⚠️ Impact : Edge case en dev avec hot-reload
✅ Solution : Utiliser `@property` ou accéder directement à `_settings` si besoin de valeurs dynamiques.

---

## 7. 🧪 TESTS & QUALITÉ

---

**[TESTS] — 🟠 MAJEUR**
📍 Localisation : `requirements-dev.txt`
🔍 Problème : `psycopg2-binary` et `httpx` ne sont pas listés. Les tests d'intégration (`conftest.py`, `test_database.py`) utilisent `psycopg2` et `httpx`.
⚠️ Impact : `pip install -r requirements-dev.txt` ne suffit pas pour lancer tous les tests
✅ Solution : `tests/requirements-test.txt` existe et contient les bonnes dépendances. Documenter : `pip install -r tests/requirements-test.txt` pour les tests complets ou merger dans `requirements-dev.txt`.

---

**[TESTS] — 🟡 MINEUR**
📍 Localisation : `docling-pwa/vitest.config.js`
🔍 Problème : Fichier vide ou minimal — à vérifier si la config est correcte pour les tests.
✅ Solution : S'assurer que `jsdom` est bien configuré pour les tests React.

---

## 8. 🗃️ BASE DE DONNÉES & DATA LAYER

---

**[DB] — 🟡 MINEUR**
📍 Localisation : `backend/core/db_manager.py` lignes 107–154
🔍 Problème : `run_migrations()` exécute des `ALTER TABLE` et `CREATE TABLE IF NOT EXISTS` dans le code applicatif au lieu d'Alembic.
⚠️ Impact : Migrations non versionnées, risque de drift entre environnements
✅ Solution : Déplacer ces migrations dans un fichier Alembic dédié (ex. `a004_add_pdf_url_etc.py`).

---

**[DB] — 🟡 MINEUR**
📍 Localisation : `migrations/versions/a001_baseline_schema.py`
🔍 Problème : La table `fournisseurs` est créée mais **jamais utilisée** par le code. Les fournisseurs sont stockés comme `VARCHAR` dans `produits.fournisseur`.
✅ Solution : Soit ajouter une FK vers `fournisseurs`, soit supprimer la table si elle n'est pas prévue.

---

## 9. 🚀 DEVOPS & CONFIGURATION

---

**[DEVOPS] — 🟡 MINEUR**
📍 Localisation : `.github/workflows/ci.yml`
🔍 Problème : Le job `backend-test` utilise `pytest tests/` mais les tests d'intégration nécessitent `psycopg2` et une DB. Le fichier `requirements-dev.txt` n'inclut pas `psycopg2-binary`.
⚠️ Impact : Les tests peuvent échouer ou être skippés en CI
✅ Solution : Ajouter `pip install -r tests/requirements-test.txt` ou inclure `psycopg2-binary` dans les dépendances de test du workflow.

---

**[DEVOPS] — 🟡 MINEUR**
📍 Localisation : `Dockerfile`
🔍 Problème : Pas de `USER` non-root avant la ligne 17 — en fait `useradd` et `USER appuser` sont présents. ✅ Correct
✅ Solution : Aucune.

---

## 10. ♿ ACCESSIBILITÉ & UX TECHNIQUE

---

**[A11Y] — 🟡 MINEUR**
📍 Localisation : `docling-pwa/src/components/CompareModal.jsx`
🔍 Problème : Le modal a `aria-modal="true"` et `aria-labelledby` — bon.
✅ Solution : Vérifier le focus trap (déjà présent avec Tab). Les graphiques Recharts sont peu accessibles (pas de texte alternatif).

---

**[A11Y] — 🟡 MINEUR**
📍 Localisation : `docling-pwa/src/pages/CataloguePage.jsx`
🔍 Problème : Les icônes `SortAsc`/`SortDesc` n'ont pas d'`aria-label` explicite.
✅ Solution : Ajouter `aria-label="Tri ascendant"` / `aria-label="Tri descendant"` sur les icônes de tri.

---

## 11. 🌍 INTERNATIONALISATION & LOCALISATION

---

**[I18N] — 🟡 MINEUR**
📍 Localisation : Projet entier
🔍 Problème : Textes hardcodés en français. Pas de système i18n.
⚠️ Impact : Extension difficile vers CA/ES si le marché cible l'exige
✅ Solution : Pour l'instant acceptable si le projet est mono-langue FR. Ajouter `react-i18next` ou équivalent si multi-langue prévu.

---

## 12. 📝 DOCUMENTATION & MAINTENABILITÉ

---

**[DOC] — 🟡 MINEUR**
📍 Localisation : `README.md`
🔍 Problème : Les instructions sont claires. Le README mentionne `requirements-dev.txt` mais pas `tests/requirements-test.txt` pour les tests complets.
✅ Solution : Ajouter une section "Tests complets" avec `pip install -r tests/requirements-test.txt`.

---

## 📊 TABLEAU RÉCAPITULATIF

| # | Catégorie | Sévérité | Fichier / Zone | Statut |
|---|-----------|----------|----------------|--------|
| 1 | Sécurité | 🔴 CRITIQUE | Pas de page Login | À corriger |
| 2 | API | 🔴 CRITIQUE | CataloguePage pagination | À corriger |
| 3 | Dépendances | 🔴 CRITIQUE | xlsx CVE | À corriger |
| 4 | Sécurité | 🟠 MAJEUR | localStorage JWT | À corriger |
| 5 | Sécurité | 🟠 MAJEUR | Cache Workbox API auth | À corriger |
| 6 | API | 🟠 MAJEUR | VITE_API_URL prod | À corriger |
| 7 | Dépendances | 🟠 MAJEUR | workbox-window inutile | À corriger |
| 8 | Dépendances | 🟠 MAJEUR | vitest en dependencies | À corriger |
| 9 | Architecture | 🟠 MAJEUR | SQL dans routes | À corriger |
| 10 | Tests | 🟠 MAJEUR | requirements-test | À corriger |
| 11 | Code mort | 🟠 MAJEUR | workbox-window | À corriger |
| 12 | DB | 🟡 MINEUR | run_migrations vs Alembic | À planifier |
| 13 | A11y | 🟡 MINEUR | Labels tri | À planifier |
| 14 | Doc | 🟡 MINEUR | requirements-test | À planifier |

---

## 🏥 SCORE SANTÉ : 62/100

- **Sécurité** : 8/20
- **Performance** : 12/20
- **Maintenabilité** : 14/20
- **Qualité code** : 14/20
- **Tests** : 14/20

---

## 🚀 PRIORITÉS IMMÉDIATES (À corriger MAINTENANT)

1. **Créer une page Login/Register** — Sans elle, l’application est inutilisable en production multi-utilisateur.
2. **Corriger la pagination du catalogue** — Passer les filtres à l’API et gérer le cursor pour afficher tous les produits.
3. **Remplacer xlsx** — Migrer vers exceljs ou une alternative sans CVE connues.
4. **Exclure les endpoints authentifiés du cache Workbox** — Éviter le partage de données entre utilisateurs.
5. **Vérifier VITE_API_URL en production** — Faire échouer le build si absent pour éviter les requêtes vers une mauvaise origine.

---

*Audit réalisé le 26 février 2026 — Docling Agent v3*
