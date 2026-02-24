# 🛡️ Docling Agent — Catalogue BTP Intelligent (Édition Premium)

> **Application d'extraction automatisée de factures fournisseurs** pour le secteur BTP (Bâtiment & Travaux Publics).
> Transforme des factures PDF/photo en un catalogue de prix structuré, consultable et stocké en toute sécurité localement.

---

## 📌 Présentation

**Docling Agent** est un assistant IA métier taillé pour les factures de matériaux de construction. Il s'appuie exclusivement sur **Google Gemini 3 Flash** (vision multimodale et exécution de code mathématique) pour extraire instantanément le contenu de factures multilingues (Catalan/Espagnol) et le normaliser en français.

### Cas d'usage principal

Un chef de chantier BTP reçoit des lourdes factures de fournisseurs espagnols/catalans (BigMat, etc.).
Il les télécharge en lot → l'application traite toutes les factures en tâche de fond (FastAPI BackgroundTasks), extrait chaque ligne produit, traduit, classe par famille, calcule le prix TTC, et alimente un catalogue interactif local.

### Fonctionnalités clés de la version Premium

- 🧠 **Vision IA Intégrale** — Analyse directe de PDF et photos (JPG, PNG, WebP) par Gemini 3 Flash sans OCR externe, avec un préprocesseur OpenCV intégré pour lisser les photos mobiles de mauvaise qualité.
- 🚀 **Traitement Asynchrone (Anti-Timeout)** — Envoi de lots de fichiers avec gestion par File d'Attente (BackgroundTasks) et Polling intelligent de l'interface graphique.
- 📁 **Le Dossier Magique (Type OneDrive)** — Traitement en arrière-plan transparent (`watchdog`). Déposez vos PDF dans un dossier et la base se met à jour toute seule.
- ⚡ **Cache Interface (Zéro Latence)** — Utilisation experte de `@st.cache_data` (Streamlit) pour rendre la navigation dans le catalogue instantanée avec purge intelligente à l'édition.
- 🌐 **Traduction & Normalisation** — Catalan/Espagnol → Français et classement standardisé (familles BTP).
- 📦 **Catalogue Interactif & Upsert** — Dédoublonnage robuste avec écrasement automatique des anciens prix (SQLite local) et éditeur data-grid cliquable.
- 🔍 **Recherche & Filtres** — Par fournisseur, famille, mot-clé en temps réel.
- 📊 **Export Tableur** — CSV et Excel nativement gérés.

---

## ⚡ Pipeline d'extraction

```
📸 Photo / PDF facture
    ↓
🧠 Gemini 3 Flash (Extraction structurée + traduction FR + classification BTP + Auto-Check Mathématique)
    ↓
✅ Validation Pydantic (Schémas stricts, calcul automatique de TVA/IVA)
    ↓
🗄️ SQLite (Dédoublonnage intelligent [fournisseur + désignation_raw], upsert prix)
    ↓
📊 Catalogue interactif avec Cache RAM Memoire (Streamlit)
```

### Flux détaillé (Backend Asynchrone)

1. Envoi REST vers `/api/v1/invoices/process`. L'API répond par un `job_id` immédiatement (Statut 202 HTTP).
2. L'interface "ping" (polling) la route `/api/v1/invoices/status/{job_id}` une fois par seconde.
3. Le backend convertit automatiquement l'image source en WebP pour alléger la taille (Image-Shrinker).
4. **Extraction IA** multimodal via Gemini au format strict JSON.
5. **Parsing JSON** via Pydantic pour correction mathématique (`prix_remise_ht` * `1.21` IVA).
6. **Upsert SQLite Local** : on ajoute un nouveau produit ou l'on remet à jour le prix d'un article BTP existant.

---

## 🏗️ Architecture

Architecture 3 Tiers (Clean Architecture) orientée données métier :

```
docling-agent-assistant/
│
├── app.py                              # 🖥️  Frontend Streamlit (UI Vibe, Cache RAM, Polling asynchrone)
├── api.py                              # ⚙️  Routeur FastAPI (Asynchrone + BackgroundTasks Jobs)
│
├── backend/
│   ├── core/
│   │   ├── config.py                   # 🔐  Validation de l'environnement (clés API)
│   │   ├── db_manager.py              # 🗄️  Contrôleur SQLite Thread-Safe
│   │   ├── orchestrator.py            # 🎯  Chef d'atelier IA & Routage Image Preprocessor
│   │   └── monitoring.py              # ⏱️  Calculateur de performances temps réel
│   │
│   ├── schemas/
│   │   └── invoice.py                 # 📐  Définition Pydantic ("Le Moule de la facture") avec gestion du Confidence Score
│   │
│   └── services/
│       ├── gemini_service.py          # 🧠  Connecteur Google Gemini 3 Flash
│       └── image_preprocessor.py      # 🖼️  Nettoyeur de Photos Mobiles OpenCV
│
├── data_cache.db                       # 💾  Base de données locale (Autocréée)
├── .env                                # 🔑  Variables (GEMINI_API_KEY)
├── requirements.txt                    # 📦  Dépendances minimales Python
└── run_local.bat                       # 🚀  Lanceur "Clé-en-main" (Lance l'API cachée + Ouvre le web)
```

*(Note : Tout interfaçage OCR.space, Google Drive, ou Google Sheets a été formellement banni de la version Premium afin de garantir un délai de réseau infaillible et une souveraineté de la donnée)*.

---

## 📐 Modèles de données (Pydantic Schemas)

### `Product` — Ligne produit facture

```python
class Product(BaseModel):
    fournisseur: str          # "BigMat", "Punto Madera", etc.
    designation_raw: str      # Nom original (Catalan/Espagnol)
    designation_fr: str       # Traduction française
    famille: str              # Classification BTP
    unite: str                # "sac", "kg", "m²", "ml", "unité", etc.
    prix_brut_ht: float       # Prix unitaire avant remise
    remise_pct: float | None  # Pourcentage de remise
    prix_remise_ht: float     # Prix unitaire après remise HT
    prix_ttc_iva21: float     # Prix TTC avec IVA 21% (auto-calculé si 0)
    confidence: str           # "high" ou "low" (Vérification arithmétique de l'IA)
```

**Auto-calcul Intégré :** S'assure que tout tarif remisé renvoie forcément le prix facturé en calculant `prix_ttc_iva21 = prix_remise_ht × 1.21`.

---

## 🗄️ Base de données (SQLite)

### Logique anti-doublon (Upsert)

- **Clé Unique de fusion** : `(designation_raw, fournisseur)`
- Si l'article provenant d'un même devis BigMat s'appelle pareil, l'IA considère que c'est le même, et vient écraser son prix à la date la plus récente.
- Les DataFrames retournées (`get_catalogue`) re-mappent proprement les valeurs Nulles (`NaN`) en variables `None` pour garantir aux Endpoints de FastAPI une serialisation JSON vierge d'Erreur 500.

---

## 🧠 L'Intelligence (Gemini 3 Flash)

### Configuration Optimale
- Le prompt charge l'IA d'intervenir en tant qu'**Expert Comptable BTP**.
- **Format** de sortie contraint : `application/json` (déterministe, zéro bla-bla).
- **Température** : `0.1` (Factuelle).

### Gestion de la Rate Limit "Auto-Heal"
Un retry backend gère intelligemment si l'API Google vous adresse un "STOP" temporaire :
```
Tentative n°1 → Code 429 RESOURCE_EXHAUSTED → Délai dynamique de Xs (indiqué par Google)
Tentative n°2 → Rattrapée et succès sans crash !
```

---

## 🚀 Installation & Utilisation V2

```bash
# 1. Cloner le repo localement
git clone <repo-url>
cd docling-agent-assistant

# 2. Créer l'environnement virtuel (Optionnel si vous savez ce que vous faites)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Installer les librairies minimales et premium
pip install -r requirements.txt

# 4. Assigner le Cerveau (.env)
cp .env.example .env
# Remplissez strictement GEMINI_API_KEY=AI...

# 5. Lancer l'application D'UN CLIC
run_local.bat
# (Cela coupera tout serveur fantôme résiduel sur les ports, remontera le uvicorn API, et allumera Streamlit).
```

---

## 📁 Le "Dossier Magique" (Synchronisation Auto)

Si l'application tourne, elle écoute en permanence le dossier local défini par la variable `.env` `WATCHDOG_FOLDER` (par défaut : dossier `Docling_Factures` à la racine).

1. Glissez-déposez n'importe quelle facture PDF/JPG depuis votre ordinateur ou mobile vers ce dossier (partagé).
2. L'application la capte instantanément (< 2 secondes).
3. Gemini l'analyse en arrière-plan sans bloquer personne.
4. L'application déplace le PDF réussi vers le sous-dossier `/Traitees` (ou `/Erreurs` en cas de corruption).
5. Le tableau Streamlit est mis à jour en direct !

---

## 🔌 Tuto intégration HTTP (BackgroundTasks)

Si vous souhaitez brancher une application Mobile à cette API :
La route n'est plus bloquante. Voici le nouveau flux asynchrone 2026 :

```python
import time
import requests

# 1. POSTER LA FACTURE
res = requests.post("http://localhost:8000/api/v1/invoices/process", files={"file": mon_fichier})
# Réponse immédiate -> status 202 Accepted
job_id = res.json()["job_id"]

# 2. ATTENDRE LE RESULTAT (POLLING)
while True:
    time.sleep(1)
    status_res = requests.get(f"http://localhost:8000/api/v1/invoices/status/{job_id}")
    etape = status_res.json()
    if etape["status"] == "completed":
        print("BINGO :", etape["result"]["products_added"])
        break
    elif etape["status"] == "error":
        print("Dommage :", etape["error"])
        break
```

---

## 📝 Licence
MIT — Usage libre. Développé pour centraliser les chantiers Franco-Espagnols.
