# 🤖 PROMPTS DE CORRECTION — AUDIT DOCLING AGENT V3
## Tous les prompts pour corriger les problèmes détectés dans les 2 audits

---

# ⚡ SPRINT 0 — BLOQUANTS PROD (à faire AVANT TOUT)

---

## PROMPT 1 — Isolation multi-tenant (user_id) 🔴 CRITIQUE

```
Tu es un expert backend Python/PostgreSQL. 

Dans le projet Docling Agent (repo: https://github.com/guimawaiaproject/docling-agent-assistant.git), les tables `produits` et `factures` n'ont PAS de colonne `user_id`. Tous les utilisateurs voient les mêmes données.

**Fais exactement ceci :**

1. Dans `backend/schema_neon.sql` : Ajoute `user_id INTEGER REFERENCES users(id) ON DELETE CASCADE` aux tables `produits` et `factures`.

2. Crée une migration Alembic dans `backend/alembic/versions/` :
   - Ajoute `user_id` nullable (NULL = données legacy)
   - Crée un index sur `user_id` pour chaque table

3. Dans `backend/core/db_manager.py` :
   - Toutes les méthodes SELECT doivent avoir un paramètre `user_id` et filtrer par `WHERE user_id = :user_id`
   - Toutes les méthodes INSERT doivent inclure `user_id`
   - Cherche toutes les occurrences de `SELECT * FROM produits` et `SELECT * FROM factures` et ajoute le filtre

4. Dans `backend/api.py` (ou les routes) :
   - Extrais `user_id` depuis le JWT token (`current_user.id`) et passe-le à chaque appel db_manager

Montre-moi le code modifié pour chaque fichier. Commence par la migration Alembic.
```

---

## PROMPT 2 — _safe_float pour éviter les crashs 🔴 CRITIQUE

```
Dans le fichier `backend/core/db_manager.py`, il y a du code qui fait `float(product.get("prix_brut_ht") or 0)`. 

Si l'IA Gemini retourne "N/A" ou une chaîne de texte, ça plante avec ValueError.

**Fais ceci :**

1. Ajoute cette fonction utilitaire en haut du fichier (après les imports) :

```python
def _safe_float(val, default: float = 0.0) -> float:
    """Convertit une valeur en float sans planter si invalide."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default
```

2. Remplace TOUTES les occurrences de `float(product.get(...)` par `_safe_float(product.get(...))` dans tout le fichier db_manager.py.

3. Aussi remplacer les patterns comme `float(... or 0)` par `_safe_float(...)`.

Montre-moi toutes les lignes modifiées avec leur contexte (5 lignes avant/après).
```

---

## PROMPT 3 — VITE_API_URL obligatoire en prod 🔴 CRITIQUE

```
Dans `docling-pwa/src/config/api.js`, si VITE_API_URL n'est pas défini en production, le code utilise '' comme fallback et affiche un console.warn. Ça fait que les requêtes vont au mauvais endroit.

**Modifie le fichier ainsi :**

```javascript
const _env = import.meta.env.VITE_API_URL;

// En production, VITE_API_URL est OBLIGATOIRE
if (import.meta.env.PROD && !_env) {
  throw new Error(
    '❌ VITE_API_URL est requis en production. Ajoutez-le dans vos variables d\'environnement.'
  );
}

export const API_BASE_URL = _env || '';
```

Montre-moi le fichier complet modifié.
```

---

# 🔒 SPRINT 1 — SÉCURITÉ & FIABILITÉ

---

## PROMPT 4 — Échapper les wildcards ILIKE

```
Dans `backend/core/db_manager.py`, les paramètres de recherche utilisés dans les requêtes ILIKE ne sont pas échappés. Un utilisateur peut taper "%" pour matcher tous les produits.

**Ajoute cette fonction et utilise-la :**

```python
def _escape_ilike(term: str) -> str:
    """Échappe les caractères spéciaux PostgreSQL ILIKE."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
```

Ensuite, cherche toutes les lignes avec `ILIKE` dans db_manager.py et applique `_escape_ilike()` sur le paramètre avant de l'utiliser.

Exemple :
```python
# Avant
search_term = f"%{term}%"

# Après  
search_term = f"%{_escape_ilike(term)}%"
```

Montre-moi chaque ligne modifiée.
```

---

## PROMPT 5 — Ajouter CSP, HSTS, X-Frame-Options

```
L'application Docling Agent n'a aucun header de sécurité HTTP. Elle est vulnérable aux attaques XSS et clickjacking.

**Fais les 2 choses suivantes :**

1. Dans `docling-pwa/index.html`, ajoute dans le `<head>` :
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https:;">
<meta http-equiv="X-Frame-Options" content="DENY">
```

2. Dans `backend/api.py` (FastAPI), ajoute le middleware de sécurité :
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Après la création de l'app FastAPI :
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

Montre-moi le code complet modifié pour les 2 fichiers.
```

---

## PROMPT 6 — serialize_row : ne pas modifier in-place

```
Dans `backend/utils/serializers.py`, la fonction `serialize_row` modifie le dictionnaire directement (in-place). Si le même objet est réutilisé ailleurs, les données peuvent être corrompues.

**Remplace la fonction par cette version qui retourne une copie :**

```python
def serialize_row(row: dict) -> dict:
    """Sérialise une ligne de DB sans modifier l'original."""
    return {k: _serialize_val(v) for k, v in row.items()}
```

Montre-moi le fichier serializers.py complet modifié, en t'assurant que `_serialize_val` est toujours définie.
```

---

## PROMPT 7 — Envoyer `source` depuis ValidationPage

```
Dans `docling-pwa/src/pages/ValidationPage.jsx`, la fonction `handleValidate` envoie les produits au backend sans inclure le champ `source`. Du coup, les scans mobile sont enregistrés comme "pc" dans les statistiques.

**Modifie `handleValidate` pour inclure la source :**

Cherche comment ScanPage.jsx détermine la source (probablement avec une fonction `getSource()` ou en détectant si l'appareil est mobile).

Ajoute la même logique dans ValidationPage.jsx :
```javascript
const payload = {
  produits: products,
  source: /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'pc'
};
```

Montre-moi la fonction handleValidate complète modifiée.
```

---

## PROMPT 8 — CI : security scan + coverage gate

```
Dans `.github/workflows/ci.yml`, il n'y a pas de vérification de sécurité des dépendances ni de seuil minimum de couverture des tests.

**Ajoute ces étapes dans le workflow CI :**

1. Pour le backend Python, après les tests existants :
```yaml
- name: Security audit Python
  run: |
    pip install pip-audit --break-system-packages
    pip-audit --requirement requirements.txt

- name: Tests avec couverture
  run: |
    pytest --cov=backend --cov-report=xml --cov-fail-under=60
```

2. Pour le frontend, après npm install :
```yaml
- name: Security audit npm
  run: npm audit --audit-level=high

- name: Tests frontend avec couverture
  run: npm run test:coverage -- --coverage.thresholds.lines=60
```

Montre-moi le fichier ci.yml complet avec ces ajouts correctement intégrés.
```

---

# 🎨 SPRINT 2 — UX & CORRECTIONS INTERFACE

---

## PROMPT 9 — Empty states avec CTA (Catalogue + Historique)

```
Dans l'application Docling (React + Tailwind), les pages Catalogue et Historique affichent "Aucun produit trouvé" sans aucun bouton pour guider l'utilisateur.

**Modifie les 2 fichiers :**

1. Dans `docling-pwa/src/pages/CataloguePage.jsx`, trouve le bloc qui affiche l'empty state (cherche "Aucun produit") et remplace-le par :

```jsx
<div className="flex flex-col items-center justify-center py-20 gap-4">
  <Package className="w-16 h-16 text-slate-600" />
  <h3 className="text-xl font-semibold text-slate-300">Votre catalogue est vide</h3>
  <p className="text-slate-500 text-center max-w-sm">
    Scannez une facture pour commencer à construire votre catalogue de produits.
  </p>
  <button
    onClick={() => navigate('/scan')}
    className="mt-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium transition-colors"
  >
    📷 Scanner une facture
  </button>
</div>
```

2. Fais la même chose dans `docling-pwa/src/pages/HistoryPage.jsx` avec le message "Aucune facture traitée".

Montre-moi les 2 composants empty state modifiés avec leur contexte complet.
```

---

## PROMPT 10 — Dropzone clickable (noClick: false)

```
Dans `docling-pwa/src/pages/ScanPage.jsx`, la dropzone a l'option `noClick: true` ce qui empêche l'utilisateur d'ouvrir le sélecteur de fichiers en cliquant sur la zone.

C'est contre-intuitif : l'utilisateur s'attend à pouvoir cliquer pour choisir un fichier.

**Cherche la ligne avec `noClick: true` et change-la en `noClick: false`** (ou supprime-la, false est la valeur par défaut).

Montre-moi la section useDropzone complète modifiée.
```

---

## PROMPT 11 — AUTH_REQUIRED : documenter et sécuriser

```
Dans `docling-pwa/src/config/features.js`, `AUTH_REQUIRED` est à `false` par défaut. En production multi-utilisateur, oublier de le passer à `true` serait une faille majeure.

**Modifie le fichier ainsi :**

```javascript
export const features = {
  // AUTH_REQUIRED doit TOUJOURS être true en production.
  // Pour le développement local uniquement, peut être mis à false.
  AUTH_REQUIRED: import.meta.env.VITE_AUTH_REQUIRED !== 'false',
  // ... autres features
};
```

Ainsi :
- En prod (où VITE_AUTH_REQUIRED n'est pas défini) → `true` automatiquement
- Pour désactiver en dev → mettre VITE_AUTH_REQUIRED=false dans .env.local

Ajoute aussi dans `.env.example` :
```
# Mettre à 'false' UNIQUEMENT en développement local
VITE_AUTH_REQUIRED=true
```

Montre-moi les fichiers modifiés.
```

---

## PROMPT 12 — Option vide dans select Famille (Validation)

```
Dans `docling-pwa/src/pages/ValidationPage.jsx`, le select pour choisir la famille d'un produit n'a pas d'option vide. Si l'IA n'a pas détecté de famille, la première option est sélectionnée par défaut, ce qui crée de mauvaises données.

**Trouve le select `famille` et ajoute une option vide en premier :**

```jsx
<select value={product.famille || ''} onChange={...}>
  <option value="">— Choisir une famille —</option>
  {FAMILLES.map(f => (
    <option key={f} value={f}>{f}</option>
  ))}
</select>
```

Montre-moi le composant select complet modifié avec son contexte.
```

---

## PROMPT 13 — workbox-window et vitest dans les bonnes dépendances

```
Dans `docling-pwa/package.json` :
1. `workbox-window` est dans les dépendances mais n'est jamais importé dans le code. Supprime-le de `dependencies`.
2. `vitest` est dans `dependencies` au lieu de `devDependencies`. Déplace-le.

**Montre-moi le package.json modifié** avec ces 2 corrections. Après modification, explique la commande npm à lancer pour nettoyer le node_modules.
```

---

## PROMPT 14 — Confirmation avant clearQueue (éviter pertes accidentelles)

```
Dans `docling-pwa/src/pages/ScanPage.jsx`, le bouton qui vide la file d'attente (clearQueue) supprime tout sans demander confirmation. L'utilisateur peut perdre tous ses fichiers en attente par erreur.

**Ajoute une confirmation avant clearQueue :**

```jsx
const handleClearQueue = () => {
  const count = pendingFiles.length; // ou la variable qui compte les fichiers
  if (window.confirm(`Vider la file ? ${count} fichier(s) seront annulés.`)) {
    clearQueue();
  }
};
```

Et remplace tous les appels directs à `clearQueue()` par `handleClearQueue()` dans le composant.

Montre-moi le code modifié.
```

---

# 📱 SPRINT 3 — PERFORMANCE & POLISH MOBILE

---

## PROMPT 15 — Retry avec exponential backoff sur apiClient

```
Dans `docling-pwa/src/services/apiClient.js`, si la connexion réseau est instable, les requêtes échouent immédiatement sans réessayer.

**Ajoute un intercepteur de retry avec backoff exponentiel :**

```javascript
// Intercepteur de réponse avec retry
let retryCount = 0;
const MAX_RETRIES = 3;

apiClient.interceptors.response.use(
  response => {
    retryCount = 0;
    return response;
  },
  async error => {
    const isNetworkError = !error.response;
    const isRetryable = error.response?.status >= 500;
    
    if ((isNetworkError || isRetryable) && retryCount < MAX_RETRIES) {
      retryCount++;
      const delay = Math.pow(2, retryCount) * 1000; // 2s, 4s, 8s
      await new Promise(resolve => setTimeout(resolve, delay));
      return apiClient(error.config);
    }
    
    retryCount = 0;
    return Promise.reject(error);
  }
);
```

Intègre ce code dans le fichier apiClient.js existant. Montre-moi le fichier complet.
```

---

## PROMPT 16 — Vue cartes par défaut sur mobile (Catalogue)

```
Dans `docling-pwa/src/pages/CataloguePage.jsx`, la vue tableau a une largeur minimale de 800px ce qui oblige les utilisateurs mobile à scroller horizontalement. C'est pénible pour un chef de chantier.

**Modifie l'état initial de la vue pour détecter le mobile :**

```javascript
// Remplace :
const [viewMode, setViewMode] = useState('table');

// Par :
const [viewMode, setViewMode] = useState(
  window.innerWidth < 640 ? 'cards' : 'table'
);
```

Montre-moi la ligne modifiée avec son contexte (10 lignes avant/après).
```

---

## PROMPT 17 — Toast avec action "Voir le catalogue" (Scan)

```
Dans `docling-pwa/src/pages/ScanPage.jsx`, après un scan réussi, le toast de succès n'a pas de bouton d'action. L'utilisateur doit naviguer manuellement.

**Modifie le toast de succès pour inclure une action :**

```javascript
// Cherche le toast.success après le batch et remplace-le par :
toast.success(`${successCount} fichier(s) traité(s) — ${productCount} produits ajoutés`, {
  duration: 5000,
  action: {
    label: 'Voir le catalogue',
    onClick: () => navigate('/catalogue')
  }
});
```

Montre-moi toutes les occurrences de `toast.success` dans ScanPage.jsx et les modifications correspondantes.
```

---

## PROMPT 18 — Flux batch cohérent avec flux caméra

```
Dans `docling-pwa/src/pages/ScanPage.jsx`, le flux caméra redirige automatiquement vers /validation après le scan, mais le flux batch (upload de fichiers) ne le fait pas. L'utilisateur reste sur /scan sans savoir quoi faire.

**Après la fin du batch (tous les fichiers traités avec succès), affiche une modal ou un bloc d'action :**

```jsx
{batchFinished && (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <div className="bg-slate-800 rounded-2xl p-8 max-w-sm mx-4 text-center">
      <div className="text-4xl mb-4">✅</div>
      <h3 className="text-xl font-bold text-white mb-2">Traitement terminé !</h3>
      <p className="text-slate-400 mb-6">{productCount} produits ajoutés</p>
      <div className="flex gap-3">
        <button onClick={() => navigate('/validation')} className="flex-1 py-3 bg-emerald-600 text-white rounded-xl">
          Valider les produits
        </button>
        <button onClick={() => navigate('/catalogue')} className="flex-1 py-3 bg-slate-700 text-white rounded-xl">
          Voir le catalogue
        </button>
      </div>
    </div>
  </div>
)}
```

Intègre ceci dans le composant ScanPage.jsx. Montre-moi la section modifiée complète.
```

---

## PROMPT 19 — Command palette cmd+K

```
Dans l'application Docling (React), il n'y a pas de command palette. Les power users ne peuvent pas naviguer rapidement.

**Crée un composant CommandPalette.jsx dans `docling-pwa/src/components/` :**

```jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const COMMANDS = [
  { id: 'scan', label: 'Nouveau scan', icon: '📷', path: '/scan' },
  { id: 'catalogue', label: 'Voir le catalogue', icon: '📚', path: '/catalogue' },
  { id: 'devis', label: 'Créer un devis', icon: '📝', path: '/devis' },
  { id: 'history', label: 'Historique des factures', icon: '🕐', path: '/history' },
  { id: 'settings', label: 'Réglages', icon: '⚙️', path: '/settings' },
];

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(prev => !prev);
        setQuery('');
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const filtered = COMMANDS.filter(c =>
    c.label.toLowerCase().includes(query.toLowerCase())
  );

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-start justify-center pt-20 px-4" onClick={() => setOpen(false)}>
      <div className="bg-slate-800 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden" onClick={e => e.stopPropagation()}>
        <input
          autoFocus
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Rechercher une action..."
          className="w-full px-4 py-4 bg-transparent text-white placeholder-slate-500 outline-none border-b border-slate-700 text-lg"
        />
        <div className="max-h-64 overflow-y-auto">
          {filtered.map(cmd => (
            <button
              key={cmd.id}
              onClick={() => { navigate(cmd.path); setOpen(false); }}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-slate-700 text-left transition-colors"
            >
              <span className="text-xl">{cmd.icon}</span>
              <span className="text-white">{cmd.label}</span>
            </button>
          ))}
          {filtered.length === 0 && (
            <p className="px-4 py-8 text-slate-500 text-center">Aucune action trouvée</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

Ensuite, importe et utilise ce composant dans App.jsx pour qu'il soit disponible partout.

Montre-moi le composant complet + la modification d'App.jsx.
```

---

## PROMPT 20 — Sauvegarde brouillon devis (localStorage)

```
Dans `docling-pwa/src/pages/DevisPage.jsx`, si l'utilisateur quitte la page, tout le devis en cours est perdu.

**Ajoute une sauvegarde automatique du brouillon :**

```javascript
// Au chargement, restaure le brouillon
useEffect(() => {
  const draft = localStorage.getItem('devis_draft');
  if (draft) {
    try {
      const { entreprise, client, selectedProducts, remise, tvaRate, notes } = JSON.parse(draft);
      setEntreprise(entreprise || '');
      setClient(client || {});
      setSelectedProducts(selectedProducts || []);
      setRemise(remise || 0);
      // ... restaure les autres champs
    } catch (e) {
      localStorage.removeItem('devis_draft');
    }
  }
}, []);

// À chaque modification, sauvegarde le brouillon (debounced)
useEffect(() => {
  const timer = setTimeout(() => {
    localStorage.setItem('devis_draft', JSON.stringify({
      entreprise, client, selectedProducts, remise, tvaRate
    }));
  }, 1000);
  return () => clearTimeout(timer);
}, [entreprise, client, selectedProducts, remise, tvaRate]);

// Après génération du PDF, efface le brouillon
const handleGenerate = () => {
  // ... code existant
  localStorage.removeItem('devis_draft');
};
```

Intègre ce code dans DevisPage.jsx. Montre-moi les useEffect modifiés/ajoutés + un bouton "Effacer le brouillon" discret.
```

---

## PROMPT 21 — Unifier Alembic et run_migrations

```
Dans `backend/core/db_manager.py`, la fonction `run_migrations()` exécute des ALTER TABLE et CREATE TABLE directement, en parallèle d'Alembic. Les deux systèmes peuvent entrer en conflit et créer des incohérences.

**Analyse le code et fais ceci :**

1. Identifie toutes les opérations dans `run_migrations()` (ALTER TABLE, CREATE TABLE, etc.)
2. Pour chacune, vérifie si elle existe déjà dans un fichier Alembic dans `backend/alembic/versions/`
3. Si elle n'existe pas dans Alembic : crée une migration Alembic correspondante
4. Une fois toutes les opérations dans Alembic, remplace `run_migrations()` par :

```python
async def run_migrations(self):
    """Toutes les migrations sont gérées par Alembic. Ne rien faire ici."""
    logger.info("Migrations gérées par Alembic - run_migrations() désactivé")
    pass
```

5. Documente dans un commentaire : "Pour lancer les migrations : alembic upgrade head"

Montre-moi la liste des opérations trouvées dans run_migrations() et les nouvelles migrations Alembic correspondantes.
```

---

## PROMPT 22 — TVA multi-taux par ligne (Devis)

```
Dans `docling-pwa/src/pages/DevisPage.jsx`, il n'y a qu'un seul taux TVA pour tout le devis. En BTP, on a souvent : 20% matériaux, 10% travaux, 5.5% rénovation.

**Modifie le devis pour permettre la TVA par ligne :**

1. Dans `selectedProducts`, chaque produit doit avoir son propre `tvaRate` (défaut : le taux global actuel)

2. Au moment d'ajouter un produit, ajoute un sélecteur TVA :
```jsx
<select 
  value={product.tvaRate || defaultTvaRate}
  onChange={e => updateProductTva(product.id, parseFloat(e.target.value))}
  className="text-sm bg-slate-700 rounded px-2 py-1"
>
  <option value="0.055">5.5%</option>
  <option value="0.1">10%</option>
  <option value="0.2">20%</option>
</select>
```

3. Le calcul du total TTC doit utiliser le taux de chaque ligne :
```javascript
const totalTTC = selectedProducts.reduce((sum, p) => {
  const ht = p.prix * p.quantite;
  return sum + ht * (1 + (p.tvaRate ?? defaultTvaRate));
}, 0);
```

4. Le PDF généré doit afficher la TVA par ligne.

Montre-moi les sections modifiées de DevisPage.jsx.
```

---

## PROMPT 23 — Badge confidence et diff dans ValidationPage

```
Dans `docling-pwa/src/pages/ValidationPage.jsx`, seuls les champs "low confidence" sont mis en évidence avec une bordure amber. Les champs "medium" ne sont pas marqués, et on ne voit pas ce qui a été modifié manuellement.

**Ajoute ces améliorations :**

1. Badge de confiance coloré sur chaque ligne :
```jsx
const ConfidenceBadge = ({ confidence }) => {
  const config = {
    high: { color: 'bg-emerald-900 text-emerald-300', label: '✓ Haute' },
    medium: { color: 'bg-amber-900 text-amber-300', label: '~ Moyenne' },
    low: { color: 'bg-red-900 text-red-300', label: '! Faible' },
  };
  const c = config[confidence] || config.medium;
  return <span className={`text-xs px-2 py-0.5 rounded-full ${c.color}`}>{c.label}</span>;
};
```

2. Tracking des modifications :
```javascript
// Dans le state initial, stocker les valeurs originales de l'IA
const [originalValues] = useState(() => 
  products.reduce((acc, p) => ({ ...acc, [p.id]: { ...p } }), {})
);

// Fonction pour détecter si un champ a été modifié
const isModified = (productId, field) => 
  originalValues[productId]?.[field] !== currentProduct[field];
```

3. Bordure bleue sur les champs modifiés manuellement.

Montre-moi le code complet de ces 3 améliorations intégré dans ValidationPage.jsx.
```

---

## PROMPT 24 — Export RGPD + bouton dans Settings

```
L'application Docling n'a pas d'export des données utilisateur (obligation RGPD).

**Fais ceci :**

1. Backend — Ajoute un endpoint dans `backend/api.py` :
```python
@app.get("/api/export/my-data")
async def export_my_data(current_user = Depends(get_current_user)):
    """Export RGPD : toutes les données de l'utilisateur."""
    produits = await db.get_all_products(user_id=current_user.id)
    factures = await db.get_all_factures(user_id=current_user.id)
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "user": {"id": current_user.id, "email": current_user.email},
        "produits": produits,
        "factures": factures,
    }
    
    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f"attachment; filename=mes-donnees-{current_user.id}.json"}
    )
```

2. Frontend — Dans `docling-pwa/src/pages/SettingsPage.jsx`, ajoute une section "Mes données" avec un bouton :
```jsx
<button
  onClick={async () => {
    const data = await apiClient.get('/api/export/my-data');
    const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mes-donnees-docling.json';
    a.click();
  }}
  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg"
>
  📥 Exporter mes données (RGPD)
</button>
```

Montre-moi les 2 fichiers modifiés.
```

---

## PROMPT 25 — Amélioration page Settings (paramètres manquants)

```
La page Settings de Docling est très limitée. Beaucoup de paramètres importants sont absents.

**Ajoute ces sections dans `docling-pwa/src/pages/SettingsPage.jsx` :**

1. Section "Mon entreprise" :
   - Nom de l'entreprise (utilisé dans les devis PDF)
   - Adresse
   - Logo (upload image, converti en base64 et stocké en localStorage)

2. Section "Préférences devis" :
   - TVA par défaut (select 5.5% / 10% / 20%)
   - Format numérotation (input texte, ex: "DEV-{YYYY}-{NNN}")
   - Mentions légales (textarea)

3. Section "Compte" :
   - Modifier le mot de passe (appel API)

Utilise localStorage pour persister les paramètres entreprise/devis côté client, et une API pour le mot de passe.

Montre-moi le composant SettingsPage.jsx avec ces 3 sections ajoutées.
```

---

# 🚀 SPRINT 4 — SCALABILITÉ & EXCELLENCE

---

## PROMPT 26 — Pipeline CI/CD avec déploiement automatique

```
Dans `.github/workflows/ci.yml`, il n'y a pas de déploiement automatique. Chaque déploiement est manuel, ce qui risque des erreurs.

**Crée un nouveau workflow `.github/workflows/deploy.yml` :**

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy backend
        # Adapte selon ton hébergeur (Railway, Render, Fly.io, etc.)
        # Exemple Render :
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_URL }}

  deploy-frontend:
    runs-on: ubuntu-latest
    environment: production
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v4
      
      - name: Build frontend
        run: |
          cd docling-pwa
          npm ci
          npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
          VITE_AUTH_REQUIRED: 'true'
      
      - name: Deploy to Vercel/Netlify
        # Adapte selon ton hébergeur
        run: echo "Déployer le dossier dist/"
```

Adapte ce template selon l'hébergeur utilisé (Railway, Render, Fly.io, Vercel, etc.). Montre-moi le workflow complet adapté.
```

---

## PROMPT 27 — httpOnly cookies pour JWT (sécurité avancée)

```
Dans `docling-pwa/src/services/apiClient.js`, le token JWT est stocké dans localStorage. Si un script malveillant est injecté (XSS), il peut voler le token.

**Migre vers des httpOnly cookies :**

1. Backend `backend/api.py` — Login : retourne le token dans un cookie httpOnly :
```python
from fastapi.responses import JSONResponse

@app.post("/api/auth/login")
async def login(data: LoginSchema):
    # ... vérification existante ...
    token = create_jwt_token(user.id)
    
    response = JSONResponse(content={"user": {"id": user.id, "email": user.email}})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=86400  # 24h
    )
    return response
```

2. Backend — Middleware auth : lire le token depuis le cookie :
```python
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401)
    # ... décoder JWT existant ...
```

3. Frontend — Retire `Authorization: Bearer` des headers, active `withCredentials` :
```javascript
apiClient.defaults.withCredentials = true;
// Supprime la lecture/écriture localStorage pour le token
```

Montre-moi les fichiers backend et frontend modifiés.
```

---

## PROMPT 28 — Web Vitals monitoring

```
L'application Docling n'a pas de monitoring des performances (LCP, INP, CLS). Si quelque chose ralentit, personne ne le sait.

**Ajoute le monitoring Web Vitals :**

1. Installe la dépendance :
```bash
cd docling-pwa && npm install web-vitals
```

2. Crée `docling-pwa/src/utils/vitals.js` :
```javascript
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals';

function sendToAnalytics({ name, value, rating, id }) {
  // En prod : envoyer à ton backend ou Sentry
  if (import.meta.env.PROD) {
    console.log(`[Web Vitals] ${name}: ${Math.round(value)} (${rating})`);
    // Optionnel : fetch('/api/vitals', { method: 'POST', body: JSON.stringify({ name, value, rating }) })
  }
}

export function measureWebVitals() {
  onCLS(sendToAnalytics);
  onINP(sendToAnalytics);
  onLCP(sendToAnalytics);
  onFCP(sendToAnalytics);
  onTTFB(sendToAnalytics);
}
```

3. Dans `docling-pwa/src/main.jsx`, appelle `measureWebVitals()` au démarrage.

Montre-moi les 3 modifications (package.json, nouveau fichier vitals.js, main.jsx).
```

---

# 📋 RÉCAPITULATIF — ORDRE D'EXÉCUTION RECOMMANDÉ

```
## Comment utiliser ces prompts

Copie chaque prompt dans Claude (ou ton IA préférée) en donnant le contexte du projet.
Commence TOUJOURS par donner ce contexte avant chaque prompt :

---
**CONTEXTE :** Je travaille sur le projet Docling Agent v3, une PWA React + FastAPI Python
pour l'extraction de factures BTP via IA (Gemini).
Repo : https://github.com/guimawaiaproject/docling-agent-assistant.git
Stack : React 18, Tailwind CSS, FastAPI, PostgreSQL (Neon), JWT auth, Gemini API
---

## Ordre recommandé :

### 🔴 Faire ABSOLUMENT en premier (avant prod multi-user) :
1. Prompt 1 — user_id multi-tenant
2. Prompt 2 — _safe_float
3. Prompt 3 — VITE_API_URL obligatoire

### 🟠 Semaine 1 :
4. Prompt 4 — Échapper ILIKE
5. Prompt 5 — Headers sécurité
6. Prompt 6 — serialize_row copie
7. Prompt 7 — source ValidationPage
8. Prompt 8 — CI security + coverage
9. Prompt 10 — Dropzone clickable
10. Prompt 12 — Option vide Famille
11. Prompt 14 — Confirmation clearQueue

### 🟡 Semaine 2 :
12. Prompt 9 — Empty states CTA
13. Prompt 11 — AUTH_REQUIRED sécurisé
14. Prompt 13 — workbox-window + vitest
15. Prompt 16 — Mobile vue cartes
16. Prompt 17 — Toast avec action
17. Prompt 18 — Flux batch cohérent
18. Prompt 20 — Brouillon devis
19. Prompt 24 — Export RGPD
20. Prompt 25 — Settings manquants

### 🔵 Semaine 3+ :
21. Prompt 15 — Retry backoff
22. Prompt 19 — Command palette
23. Prompt 21 — Unifier Alembic
24. Prompt 22 — TVA multi-taux
25. Prompt 23 — Badges confidence
26. Prompt 26 — CI/CD deploy auto
27. Prompt 27 — httpOnly cookies
28. Prompt 28 — Web Vitals
```
