# 🔍 AUDIT POST-PRODUCTION MANUEL ET EXHAUSTIF — Docling Agent v3

**Date** : 26 février 2026
**Périmètre** : backend/, docling-pwa/src/, api.py, requirements, migrations, CI, Docker, tests/
**Méthode** : Lecture ligne par ligne de chaque fichier — aucune supposition

---

## 1. LOGIQUE MÉTIER

---

**[LOGIQUE MÉTIER] — 🔴 CRITIQUE**
📍 Fichier : `backend/services/facturx_extractor.py` lignes 149-152
🔍 Problème : Division par zéro possible. Si `line_amount == 0` et `allowance == 0`, alors `(line_amount + allowance) == 0` et `remise_pct = round((allowance / (line_amount + allowance)) * 100, 2)` lève `ZeroDivisionError`.
⚠️ Impact : Crash lors de l'extraction Factur-X pour certaines factures avec montants à 0
✅ Solution :
```python
if allowance > 0 and (line_amount + allowance) > 0:
    remise_pct = round((allowance / (line_amount + allowance)) * 100, 2)
    prix_brut_ht = unit_price / (1 - remise_pct / 100) if remise_pct < 100 else unit_price
else:
    remise_pct = 0.0
```

---

**[LOGIQUE MÉTIER] — 🟠 MAJEUR**
📍 Fichier : `backend/core/db_manager.py` lignes 65-79
🔍 Problème : `_upsert_params` utilise `float()` sur des valeurs potentiellement non numériques. Si Gemini retourne `"N/A"` ou une chaîne pour `prix_brut_ht`, `float("N/A")` lève `ValueError`. Le `product.get("prix_brut_ht") or 0` ne protège pas contre les chaînes.
⚠️ Impact : Crash lors du batch save si un produit contient des données mal formées
✅ Solution :
```python
def _safe_float(val, default=0.0):
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default
# Puis utiliser _safe_float(product.get("prix_brut_ht")) etc.
```

---

**[LOGIQUE MÉTIER] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/pages/ValidationPage.jsx` lignes 36-48
🔍 Problème : `handleValidate` envoie `{ produits: products }` sans le champ `source`. Le backend `BatchSaveRequest` a `source: str = "pc"` par défaut, donc ça fonctionne, mais le flux caméra/watchdog envoie des produits avec `source: "mobile"` — cette info est perdue car le frontend ne transmet jamais `source`.
⚠️ Impact : Tous les produits validés manuellement sont enregistrés avec `source: "pc"` même s'ils viennent du mobile
✅ Solution : Ajouter `source: getSource()` ou stocker la source dans le store au moment de `setJobComplete`

---

**[LOGIQUE MÉTIER] — 🟡 MINEUR**
📍 Fichier : `backend/schemas/invoice.py` lignes 38-48
🔍 Problème : Le validateur `validate_and_compute` modifie `prix_remise_ht` si `prix_remise_ht == 0` et `prix_brut_ht > 0` et `remise_pct > 0`. Mais si l'utilisateur a intentionnellement mis 0 (produit gratuit), le calcul écrase avec `computed`.
⚠️ Impact : Cas limite rare — produit gratuit avec remise % pourrait être mal interprété
✅ Solution : Documenter ou ajouter une condition explicite pour `prix_remise_ht == 0` volontaire

---

**[LOGIQUE MÉTIER] — 🟡 MINEUR**
📍 Fichier : `docling-pwa/src/pages/DevisPage.jsx` lignes 66-68
🔍 Problème : `totalHT` utilise `parseFloat(s.prix_remise_ht) || 0` — correct. Mais `remiseGlobale` en mode `amount` (€) : `Math.min(remiseGlobale, totalHT)` — si l'utilisateur saisit une remise supérieure au total, elle est plafonnée. Pas de validation que `remiseGlobale >= 0`.
⚠️ Impact : Remise négative possible si l'utilisateur tape une valeur invalide
✅ Solution : `remiseGlobale = Math.max(0, parseFloat(remiseGlobale) || 0)` avant calcul

---

## 2. SÉCURITÉ APPROFONDIE

---

**[SÉCURITÉ] — 🔴 CRITIQUE**
📍 Fichier : `api.py` lignes 368-398
🔍 Problème : Les endpoints `register` et `login` n'exigent **pas** de token (correct), mais ils n'ont **aucune validation** sur la longueur de l'email, du mot de passe ou du nom. Un email de 1 Mo ou un password de 10 000 caractères peut être envoyé.
⚠️ Impact : DoS par payload massif, potentiel overflow en base
✅ Solution : Valider `len(email) <= 255`, `len(password) <= 128`, `len(name) <= 200` côté API (Pydantic ou Form)

---

**[SÉCURITÉ] — 🔴 CRITIQUE**
📍 Fichier : `api.py` ligne 408
🔍 Problème : `get_job_status(job_id)` — aucun contrôle que le job appartient à l'utilisateur connecté. Tout utilisateur authentifié peut interroger n'importe quel job_id (UUID) et voir le résultat (produits extraits, erreurs).
⚠️ Impact : Fuite de données entre utilisateurs en multi-tenant
✅ Solution : Ajouter une colonne `user_id` à la table `jobs` et filtrer `WHERE job_id = $1 AND user_id = $2`

---

**[SÉCURITÉ] — 🟠 MAJEUR**
📍 Fichier : `api.py` lignes 171-223
🔍 Problème : Le paramètre `model` dans `process_invoice` est accepté tel quel (`Form(default="gemini-3-flash-preview")`). Un client peut envoyer `model=../../etc/passwd` ou une valeur arbitraire. Le `model_id` est passé à `Orchestrator.process_file` puis à `GeminiService.get_or_create(model_id=model)` — qui utilise `Config.MODELS_DISPONIBLES.get(model_id, ...)`. Si la clé n'existe pas, il fallback sur gemini-2.5-flash. Pas de rejet explicite.
⚠️ Impact : Injection de modèle non prévu, coût API imprévisible
✅ Solution : Valider `if model not in Config.MODELS_DISPONIBLES: raise HTTPException(400, "Modèle invalide")`

---

**[SÉCURITÉ] — 🟠 MAJEUR**
📍 Fichier : `api.py` ligne 175
🔍 Problème : Le paramètre `source` accepte toute chaîne (`Form(default="pc")`). Les valeurs attendues sont `pc`, `mobile`, `watchdog`. La DB a une contrainte `ck_produits_source` mais l'upsert peut échouer si une valeur invalide est envoyée.
⚠️ Impact : Erreur 500 ou contournement de la contrainte selon l'ordre des opérations
✅ Solution : Valider `source in ("pc", "mobile", "watchdog")` avant traitement

---

**[SÉCURITÉ] — 🟠 MAJEUR**
📍 Fichier : `backend/core/db_manager.py` lignes 231-244
🔍 Problème : La requête `get_catalogue` construit du SQL dynamique avec `conditions.append(f"famille = ${idx}")` — les paramètres sont passés séparément, donc pas d'injection SQL directe. Mais `search` et `fournisseur` utilisent `ILIKE` avec `%{fournisseur}%` — si `fournisseur` contient `%` ou `_`, le comportement ILIKE peut être inattendu (wildcards).
⚠️ Impact : Recherche qui retourne plus de résultats que prévu (ex: `%` = tout)
✅ Solution : Échapper `%` et `_` dans les termes de recherche : `term.replace("%", "\\%").replace("_", "\\_")`

---

**[SÉCURITÉ] — 🟡 MINEUR**
📍 Fichier : `api.py` lignes 302-304
🔍 Problème : En cas d'exception dans `get_catalogue`, le message retourné est "Erreur interne du serveur" — générique. Mais `logger.error("Erreur get_catalogue", exc_info=True)` peut logger des détails (stack trace, requête SQL) dans Sentry ou les logs. Vérifier que les logs ne contiennent pas de données sensibles (tokens, mots de passe).
⚠️ Impact : Fuite d'info dans les logs en cas d'erreur
✅ Solution : Audit des logs — s'assurer qu'aucun payload utilisateur n'est loggé en clair

---

**[SÉCURITÉ] — 🟡 MINEUR**
📍 Fichier : `docling-pwa/src/services/apiClient.js` lignes 19-25
🔍 Problème : Sur 401, le client supprime le token et redirige vers `/login`. Mais si la page actuelle est `/login` ou `/register`, `window.location.pathname.startsWith('/login')` évite la redirection. Cependant, une redirection `window.location.href = '/login'` provoque un rechargement complet — perte de l'état en cours (ex: formulaire rempli).
⚠️ Impact : UX dégradée si token expire pendant une action
✅ Solution : Stocker `from` dans sessionStorage avant redirection pour pré-remplir après login

---

## 3. FLUX UTILISATEUR COMPLETS

---

**[FLUX] — 🔴 CRITIQUE**
📍 Fichier : `docling-pwa/src/pages/ScanPage.jsx` lignes 221-270
🔍 Problème : Si l'utilisateur ferme l'onglet pendant `processItem`, le job continue côté serveur (background_tasks). Le job_id n'est jamais récupéré par le client. Les produits sont bien insérés en BDD par l'orchestrator, mais le client ne le sait pas. Si l'utilisateur rouvre la page, il n'a aucun moyen de voir que le fichier a été traité.
⚠️ Impact : Utilisateur pense que le scan a échoué alors que les produits sont en base
✅ Solution : Au chargement de ScanPage, vérifier s'il y a des jobs "processing" récents pour cet utilisateur (nécessite user_id dans jobs) et proposer de reprendre le polling

---

**[FLUX] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/pages/ScanPage.jsx` lignes 266-269
🔍 Problème : En cas d'erreur, `updateItem(item.id, { status: 'error', ... })` est appelé. Mais si `err.name === 'CanceledError'` ou `ctrl.signal.aborted`, on fait `return` sans mettre à jour le statut. L'item reste en "processing" ou "uploading" indéfiniment.
⚠️ Impact : File d'attente avec des éléments bloqués visuellement
✅ Solution : Même en cas d'abort, appeler `updateItem(item.id, { status: 'pending', progress: 0 })` pour permettre un retry

---

**[FLUX] — 🟠 MAJEUR**
📍 Fichier : `backend/services/gemini_service.py` lignes 156-163
🔍 Problème : Si Gemini retourne un JSON mal formé, le regex `r"\{.*\}"` extrait le premier bloc. Mais si le JSON contient des produits avec des champs manquants, `Product(**p)` lève une exception, capturée par `logger.warning` et le produit est ignoré. Si **tous** les produits sont invalides, `produits_valides` est vide et on retourne un `InvoiceExtractionResult` avec 0 produits — pas d'erreur explicite.
⚠️ Impact : L'orchestrator reçoit `result.produits == []` et log "Aucun produit extrait" — l'utilisateur ne sait pas si c'est une facture vide ou un bug Gemini
✅ Solution : Si `len(produits_valides) < len(data.get("produits", []))`, logger le nombre de produits ignorés et inclure dans le message d'erreur

---

**[FLUX] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/store/useStore.js` lignes 56-76
🔍 Problème : `addToQueue` déduplique par `name__size`. Si l'utilisateur scanne le **même fichier deux fois** (même nom, même taille), il est ignoré. Mais si le fichier a été modifié (même nom, taille différente), il est ajouté. Pas de hash pour détecter le contenu identique.
⚠️ Impact : Doublons possibles si l'utilisateur renomme un fichier ou le modifie légèrement
✅ Solution : Pour l'instant acceptable. Pour une déduplication stricte, calculer un hash (SHA-256) du contenu — coûteux pour de gros fichiers

---

**[FLUX] — 🟡 MINEUR**
📍 Fichier : `docling-pwa/src/pages/ValidationPage.jsx` lignes 32-34
🔍 Problème : Si `products.length === 0`, redirection vers `/scan`. Mais si l'utilisateur arrive sur `/validation` via un lien direct (bookmark) après avoir vidé le store, il est redirigé. Le store Zustand est persisté avec `partialize: (state) => ({ selectedModel })` — les `extractedProducts` ne sont **pas** persistés. Donc au refresh, products est vide.
⚠️ Impact : Comportement attendu — pas de persistance des produits en cours de validation
✅ Solution : Documenter ou afficher un message "Session expirée, retour au scan" au lieu d'une redirection silencieuse

---

## 4. COHÉRENCE DES DONNÉES

---

**[DONNÉES] — 🔴 CRITIQUE**
📍 Fichier : `docling-pwa/src/pages/SettingsPage.jsx` ligne 186
🔍 Problème : Le frontend affiche `sync.files_processed` mais l'API `get_watchdog_status()` retourne `total_processed` (voir `watchdog_service.py` ligne 107). La clé `files_processed` n'existe pas.
⚠️ Impact : Le compteur "X fichiers traités" ne s'affiche jamais (toujours undefined/null)
✅ Solution : Remplacer `sync.files_processed` par `sync.total_processed`

---

**[DONNÉES] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/pages/DevisPage.jsx` lignes 20-31
🔍 Problème : `fetchProducts` appelle `apiClient.get(ENDPOINTS.catalogue)` **sans paramètres**. L'API retourne `{ products, next_cursor, has_more, total }` avec par défaut `limit=50`. Donc `data.products` contient au plus 50 produits. Pour un catalogue de 500 produits, la page Devis ne propose que les 50 premiers.
⚠️ Impact : Utilisateurs incapables d'ajouter des produits au devis s'ils ne sont pas dans les 50 premiers
✅ Solution : Implémenter un chargement paginé ou un paramètre `limit=500` (ou charger tout le catalogue en plusieurs appels)

---

**[DONNÉES] — 🟠 MAJEUR**
📍 Fichier : `backend/utils/serializers.py` lignes 7-17
🔍 Problème : `serialize_row` modifie le dict **in-place** (`row[k] = ...`). Si le même objet est passé à plusieurs reprises ou partagé, les mutations sont permanentes. Les appels `for p in result["products"]: serialize_row(p)` dans api.py modifient les objets avant de les retourner — correct. Mais si un middleware ou un cache réutilise ces objets, problème.
⚠️ Impact : Risque de mutation partagée en cas de réutilisation des objets
✅ Solution : Créer une copie avant modification : `row = dict(row); serialize_row(row); return row`

---

**[DONNÉES] — 🟡 MINEUR**
📍 Fichier : `docling-pwa/src/constants/categories.js` vs `backend/schemas/invoice.py`
🔍 Problème : `FAMILLES` côté frontend a "Électricité" (avec accent). Le schéma backend `FAMILLES_VALIDES` a "Electricite" (sans accent). Incohérence — si l'utilisateur sélectionne "Électricité" en validation, le backend le reçoit et le validateur le remplace par "Autre" car "Électricité" ∉ FAMILLES_VALIDES.
⚠️ Impact : Famille "Électricité" devient "Autre" à la sauvegarde
✅ Solution : Harmoniser — soit "Électricité" partout, soit "Electricite" partout (backend utilise Electricite dans le SYSTEM_PROMPT Gemini)

---

**[DONNÉES] — 🟡 MINEUR**
📍 Fichier : `backend/core/db_manager.py` lignes 72-76
🔍 Problème : Les prix sont stockés en `NUMERIC(10,4)` en base. Le code Python utilise `float()`. Les calculs financiers avec float peuvent avoir des erreurs d'arrondi (ex: 0.1 + 0.2 ≠ 0.3 en float).
⚠️ Impact : Arrondis incorrects sur de très gros catalogues ou calculs en chaîne
✅ Solution : Utiliser `Decimal` pour les calculs critiques côté Python, ou accepter l'approximation float pour ce use-case BTP

---

## 5. GESTION D'ERREURS

---

**[ERREURS] — 🔴 CRITIQUE**
📍 Fichier : `backend/core/db_manager.py` lignes 204-206
🔍 Problème : Dans `upsert_products_batch`, si une exception survient lors de l'insert dans `prix_historique`, elle est capturée par `except Exception as e: logger.warning(...)` et **ignorée**. L'upsert du produit principal a réussi, mais l'historique des prix n'est pas enregistré. L'utilisateur n'est pas informé.
⚠️ Impact : Données partielles — historique de prix incomplet sans traçabilité
✅ Solution : Soit propager l'erreur (rollback toute la transaction), soit retourner un indicateur `partial_success` avec le détail des échecs

---

**[ERREURS] — 🟠 MAJEUR**
📍 Fichier : `api.py` lignes 244-258
🔍 Problème : Dans `_run_extraction`, toute exception est capturée et le job est marqué "error". Mais le message `err_msg = str(e)` peut contenir des détails internes (chemins, stack). Si l'exception est une `RuntimeError` de Gemini avec un message technique, il est stocké dans `jobs.error` et renvoyé au client via `get_job_status`.
⚠️ Impact : Fuite d'information technique vers le client
✅ Solution : Sanitiser les messages d'erreur avant stockage — mapper les erreurs connues (rate limit, quota, invalid key) vers des messages utilisateur

---

**[ERREURS] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/pages/CataloguePage.jsx` lignes 176-178
🔍 Problème : `fetchCatalogue` en cas d'erreur : `toast.error('Impossible de charger le catalogue')` — message générique. L'erreur n'est pas loguée. Si c'est une 401 (token expiré), l'interceptor apiClient redirige vers login. Si c'est une 500, l'utilisateur ne sait pas si c'est réseau, serveur ou données.
⚠️ Impact : Debug difficile, UX pauvre
✅ Solution : Différencier 401, 403, 500, timeout — messages spécifiques ("Session expirée", "Serveur indisponible", etc.)

---

**[ERREURS] — 🟡 MINEUR**
📍 Fichier : `docling-pwa/src/services/offlineQueue.js` lignes 23-40
🔍 Problème : `enqueueUpload` ne gère pas le cas où `file.arrayBuffer()` échoue (fichier corrompu, trop gros). La Promise reject est propagée mais l'appelant (ScanPage) affiche `toast.error` avec `err.message`. Pas de gestion du quota IndexedDB (quota exceeded).
⚠️ Impact : En mode offline avec beaucoup de fichiers, IndexedDB peut saturer
✅ Solution : Capturer `QuotaExceededError` et afficher un message explicite "Espace de stockage insuffisant"

---

## 6. PERFORMANCE RÉELLE

---

**[PERF] — 🟠 MAJEUR**
📍 Fichier : `backend/core/db_manager.py` lignes 283-303
🔍 Problème : La requête `get_catalogue` exécute un `COUNT(*)` séparé pour le total à chaque appel. Sur un catalogue de 100k produits avec des filtres, le COUNT peut être lent. Pas d'index composite sur `(famille, fournisseur, updated_at)`.
⚠️ Impact : Temps de réponse catalogue qui dégrade avec la taille
✅ Solution : EXPLAIN ANALYZE sur la requête ; ajouter un index composite si nécessaire ; envisager un COUNT approximatif (ex: estimation) pour les gros catalogues

---

**[PERF] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/pages/CataloguePage.jsx` lignes 201-219
🔍 Problème : Le `useMemo` pour `filtered` dépend de `[allProducts, search, famille, fournisseur, sortKey, sortDir]`. Mais `search` est utilisé dans le useMemo alors que le filtrage par search est **côté API** (params.search). Le `filtered` trie et filtre côté client sur `allProducts` — qui est déjà filtré par l'API. Donc `search` dans les deps du useMemo est redondant si l'API gère search. En fait, l'API reçoit `params.search` — donc `allProducts` est déjà le résultat filtré. Le useMemo ne fait que le **tri** côté client. Les deps `search, famille, fournisseur` déclenchent un recalcul quand ces filtres changent — à ce moment-là, `fetchCatalogue` est rappelé (useEffect) et `allProducts` est remplacé. Donc le useMemo recalcule avec les nouveaux produits. OK. Mais le tri est fait côté client sur potentiellement des milliers de lignes — lourd.
⚠️ Impact : Re-renders et tri coûteux si catalogue > 1000 produits
✅ Solution : Déplacer le tri côté API (ORDER BY dynamique) pour éviter de trier tout le dataset en JS

---

**[PERF] — 🟡 MINEUR**
📍 Fichier : `docling-pwa/src/pages/ScanPage.jsx` lignes 117-146
🔍 Problème : `syncPendingUploads` traite les uploads **séquentiellement** (`for (const item of pending)`). Si 20 fichiers sont en attente, 20 requêtes POST sont envoyées une par une.
⚠️ Impact : Sync offline lente
✅ Solution : Paralléliser avec `Promise.all(pending.map(...))` en limitant la concurrence (ex: 3 en parallèle)

---

## 7. ÉTAT GLOBAL & SYNCHRONISATION

---

**[ÉTAT] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/store/useStore.js` lignes 114-118
🔍 Problème : Le store Zustand est persisté avec `partialize: (state) => ({ selectedModel })`. Les `extractedProducts`, `batchQueue`, `currentInvoice` ne sont **pas** persistés. Si l'utilisateur ouvre deux onglets, chaque onglet a son propre état en mémoire. Les actions dans l'onglet A ne sont pas visibles dans l'onglet B. Pas de synchronisation cross-tab.
⚠️ Impact : Incohérence si l'utilisateur travaille avec plusieurs onglets
✅ Solution : Utiliser `zustand/middleware` avec `persist` sur batchQueue pour les uploads en cours, ou afficher un avertissement "Ouvrir dans un seul onglet"

---

**[ÉTAT] — 🟠 MAJEUR**
📍 Fichier : `docling-pwa/src/pages/ScanPage.jsx` lignes 154-168
🔍 Problème : Au retour en ligne (`onOnline`), `syncPendingUploads` est appelé. Mais `syncPendingUploads` est dans les deps du useEffect. Si `syncPendingUploads` change (à cause de `selectedModel` ou `syncInProgress`), le useEffect se ré-exécute et ré-enregistre les listeners. Pas de problème majeur. Mais : si la sync échoue pour un fichier (ex: 401 token expiré), le fichier reste dans la queue IndexedDB. Au prochain `onOnline`, il sera retenté. Mais l'utilisateur a peut-être été déconnecté — le 401 va déclencher une redirection vers login, et la queue ne sera pas vidée.
⚠️ Impact : Boucle de sync échouée si token expiré pendant offline
✅ Solution : Sur 401 pendant sync, vider la queue ou afficher "Reconnectez-vous pour synchroniser"

---

**[ÉTAT] — 🟡 MINEUR**
📍 Fichier : `docling-pwa/src/pages/ValidationPage.jsx` lignes 36-48
🔍 Problème : Pas d'optimistic update. Au clic sur "Enregistrer", `setIsSaving(true)` puis `apiClient.post(...)`. Si succès, `clearJob()` et `navigate('/catalogue')`. Si erreur, `setIsSaving(false)` et toast. Pas de rollback nécessaire car on n'a pas modifié l'UI avant la réponse.
⚠️ Impact : Aucun — le flux est correct
✅ Solution : N/A

---

## 8. MIGRATIONS & SCHÉMA DB

---

**[MIGRATIONS] — 🔴 CRITIQUE**
📍 Fichier : `backend/core/db_manager.py` lignes 108-155
🔍 Problème : `run_migrations()` crée des tables (`prix_historique`, `users`, `jobs`) et des colonnes (`pdf_url`) **en dehors d'Alembic**. Les migrations Alembic (a001, a002, a003) créent aussi `prix_historique`, `users`, `jobs` dans a001. Donc on a deux sources de vérité. Si Alembic n'est jamais exécuté (ex: déploiement Docker sans `alembic upgrade head`), `run_migrations()` assure un minimum. Mais si on exécute Alembic puis l'app, `run_migrations()` ne fait que des `IF NOT EXISTS` — pas de conflit. Le vrai problème : **a003** ajoute une FK `produits.fournisseur -> fournisseurs(nom)`. Si `run_migrations()` est exécuté sans qu'Alembic a003 ait été appliqué, la table `produits` n'a pas la FK. L'app fonctionne. Puis quelqu'un run `alembic upgrade head` — a003 tente d'ajouter la FK. Si des produits ont des fournisseurs qui ne sont pas dans la table `fournisseurs`, l'INSERT ... ON CONFLICT de a003 les ajoute. OK. Mais le Dockerfile ne run pas Alembic. Le README dit de run `alembic upgrade head` manuellement. Donc l'ordre dépend du déploiement.
⚠️ Impact : Drift de schéma entre environnements, risque d'échec silencieux
✅ Solution : Unifier — soit tout via Alembic (et `run_migrations` ne fait que des vérifications), soit tout dans `run_migrations` et supprimer les doublons dans Alembic

---

**[MIGRATIONS] — 🟠 MAJEUR**
📍 Fichier : `migrations/versions/a003_add_fk_fournisseur.py`
🔍 Problème : La migration a003 ajoute une FK `produits.fournisseur -> fournisseurs(nom)`. Mais le code `db_manager._upsert_params` et `_UPSERT_SQL` utilisent `fournisseur` comme VARCHAR. La table `fournisseurs` a `nom VARCHAR(200) UNIQUE`. Si un produit a `fournisseur="BigMat"` et que `fournisseurs` n'a pas "BigMat", l'INSERT dans a003 l'ajoute. OK. Mais : le `schema_neon.sql` et `a001` créent `fournisseurs` avec `nom`. La table `produits` dans a001 n'a pas de FK. Donc en production actuelle, il est possible que la FK n'existe pas. Les tests conftest utilisent une DB de test — est-ce que a003 a été appliquée ?
⚠️ Impact : Incohérence si la FK existe en staging mais pas en prod
✅ Solution : Vérifier le schéma réel en prod avec `\d produits` et confirmer la présence de la FK

---

**[MIGRATIONS] — 🟡 MINEUR**
📍 Fichier : `backend/schema_neon.sql` vs `migrations/versions/a001_baseline_schema.py`
🔍 Problème : Le schéma SQL manuel et la migration a001 créent les mêmes tables. La table `factures` dans schema_neon a `statut` avec valeur par défaut 'traite'. La migration a001 aussi. Mais `schema_neon` a un commentaire `-- en_cours` dans les valeurs possibles. La contrainte `ck_produits_source` dans a002 limite `source` à pc, mobile, watchdog. Pas de contrainte sur `factures.statut`.
⚠️ Impact : Valeurs invalides possibles dans `factures.statut`
✅ Solution : Ajouter une contrainte CHECK sur `factures.statut` si nécessaire

---

## 9. PROBLÈMES ADDITIONNELS (hors axes)

---

**[TESTS] — 🟠 MAJEUR**
📍 Fichier : `tests/03_api/test_invoices.py`
🔍 Problème : Les tests `test_process_returns_202_and_job_id`, `test_process_file_too_large_413`, etc. utilisent `http_client` qui est **non authentifié**. L'endpoint `POST /api/v1/invoices/process` exige `Depends(get_current_user)`. Donc ces tests reçoivent **401 Unauthorized**, pas 202.
⚠️ Impact : Les tests échouent ou sont skippés
✅ Solution : Utiliser `authenticated_client` (fixture conftest) pour les tests process/status

---

**[CI] — 🟡 MINEUR**
📍 Fichier : `.github/workflows/ci.yml` lignes 35-42
🔍 Problème : `pip install -r requirements-dev.txt` — ce fichier n'inclut pas `psycopg2-binary`, `httpx`, `faker` nécessaires pour les tests d'intégration. Le conftest importe `httpx` et `faker`. Si requirements-dev ne les a pas, les tests échouent à l'import.
⚠️ Impact : CI peut échouer
✅ Solution : `pip install -r requirements-dev.txt -r tests/requirements-test.txt` ou merger les deps

---

**[DOCKER] — 🟡 MINEUR**
📍 Fichier : `docker-compose.yml` ligne 31
🔍 Problème : `DATABASE_URL` utilise `sslmode=disable` pour le Postgres local. En production Neon, `sslmode=require` est nécessaire. Le docker-compose est pour le dev local — correct.
✅ Solution : N/A — documenter que pour la prod, utiliser une URL Neon avec sslmode

---

## 📊 TABLEAU RÉCAPITULATIF COMPLET

| # | Catégorie | Sévérité | Fichier | Problème |
|---|-----------|---------|---------|----------|
| 1 | Logique métier | 🔴 | facturx_extractor.py | Division par zéro |
| 2 | Logique métier | 🟠 | db_manager.py | float() sur données non numériques |
| 3 | Logique métier | 🟠 | ValidationPage.jsx | source perdu au batch save |
| 4 | Sécurité | 🔴 | api.py | Pas de validation longueur email/password |
| 5 | Sécurité | 🔴 | api.py | Job status sans isolation utilisateur |
| 6 | Sécurité | 🟠 | api.py | Paramètre model non validé |
| 7 | Sécurité | 🟠 | api.py | Paramètre source non validé |
| 8 | Sécurité | 🟠 | db_manager.py | Wildcards % _ dans recherche |
| 9 | Flux | 🔴 | ScanPage.jsx | Fermeture onglet = perte de visibilité du job |
| 10 | Flux | 🟠 | ScanPage.jsx | Item reste "processing" après abort |
| 11 | Flux | 🟠 | gemini_service.py | Produits invalides ignorés silencieusement |
| 12 | Données | 🔴 | SettingsPage.jsx | files_processed vs total_processed |
| 13 | Données | 🟠 | DevisPage.jsx | Catalogue limité à 50 produits |
| 14 | Données | 🟡 | categories.js vs invoice.py | Électricité vs Electricite |
| 15 | Erreurs | 🔴 | db_manager.py | Erreur prix_historique avalée |
| 16 | Erreurs | 🟠 | api.py | Message d'erreur technique exposé |
| 17 | Perf | 🟠 | db_manager.py | COUNT(*) coûteux |
| 18 | Perf | 🟠 | CataloguePage.jsx | Tri côté client lourd |
| 19 | État | 🟠 | useStore.js | Pas de sync multi-onglets |
| 20 | État | 🟠 | ScanPage.jsx | Sync offline + 401 = boucle |
| 21 | Migrations | 🔴 | db_manager.py | Double système migrations |
| 22 | Migrations | 🟠 | a003 | FK fournisseur à vérifier |
| 23 | Tests | 🟠 | test_invoices.py | http_client non auth |
| 24 | CI | 🟡 | ci.yml | requirements-test manquant |

---

## 🏥 SCORE SANTÉ PAR DOMAINE

| Domaine | Score /100 | Commentaire |
|---------|------------|-------------|
| Logique métier | 72 | Cas limites (division par zéro, float) et source perdu |
| Sécurité | 58 | Isolation jobs, validation inputs, wildcards |
| Flux utilisateur | 65 | Fermeture onglet, abort, Gemini mal formé |
| Cohérence données | 70 | Mismatch total_processed, Devis 50 produits, familles |
| Gestion erreurs | 62 | Erreurs avalées, messages techniques exposés |
| Performance | 68 | COUNT, tri client, sync séquentielle |
| État & sync | 65 | Multi-onglets, offline+401 |
| Migrations & DB | 60 | Double système, FK à vérifier |
| **GLOBAL** | **65/100** | |

---

## 🚀 TOP 10 PRIORITÉS (ordre exact)

1. **Isolation des jobs par utilisateur** — Ajouter `user_id` à `jobs`, filtrer dans `get_job_status`. (Sécurité critique)
2. **Corriger `files_processed` → `total_processed`** — SettingsPage.jsx ligne 186. (Données, 1 ligne)
3. **Division par zéro Factur-X** — facturx_extractor.py guard `(line_amount + allowance) > 0`. (Logique critique)
4. **Validation des paramètres API** — model, source, longueur email/password dans register/login. (Sécurité)
5. **Erreur prix_historique non avalée** — db_manager : rollback ou rapport d'échec partiel. (Erreurs)
6. **DevisPage : charger tout le catalogue** — Pagination ou limit=500 pour la sélection produits. (Données)
7. **Tests process avec auth** — Remplacer http_client par authenticated_client dans test_invoices. (Tests)
8. **Unifier les migrations** — Migrer le contenu de run_migrations() vers Alembic. (DB)
9. **Sanitiser les messages d'erreur** — Ne pas exposer les détails techniques dans jobs.error. (Sécurité)
10. **Sync offline : gestion 401** — Sur token expiré pendant sync, vider la queue ou demander reconnexion. (Flux)

---

*Audit manuel exhaustif — 26 février 2026 — Docling Agent v3*
