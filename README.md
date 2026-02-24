# 🛡️ Docling Agent — Catalogue BTP Intelligent

> **Application d'extraction automatisée de factures fournisseurs** pour le secteur BTP (Bâtiment & Travaux Publics).
> Transforme des factures PDF/photo en un catalogue de prix structuré, consultable et synchronisé dans le cloud.

---

## 📌 Présentation

**Docling Agent** est un assistant IA spécialisé dans le traitement de factures de matériaux de construction. Il utilise **Google Gemini 2.0 Flash** pour extraire automatiquement les données de factures multilingues (Catalan/Espagnol) et les traduit en français.

### Cas d'usage principal

Un chef de chantier BTP reçoit des factures de fournisseurs espagnols/catalans (BigMat, etc.).
Il les scanne ou les photographie → l'app extrait chaque ligne produit, traduit en français, classe par famille, calcule le prix TTC, et alimente un catalogue centralisé.

### Fonctionnalités clés

- 🧠 **Extraction IA multimodale** — PDF, photos (JPG, PNG, WebP, HEIC)
- 🌐 **Traduction automatique** — Catalan/Espagnol → Français
- 📦 **Catalogue de prix** — Dédoublonnage intelligent, mise à jour automatique des prix
- 🔍 **Recherche & Filtres** — Par fournisseur, famille, mot-clé
- 📊 **Export Excel** — Téléchargement du catalogue complet
- ☁️ **Synchronisation cloud** — Google Drive (archivage) + Google Sheets (catalogue partagé)
- ⚡ **OCR.space hybride** — Pré-extraction OCR pour réduire la consommation tokens Gemini de 90%
- 🔄 **Cache intelligent** — Détection de doublons par hash SHA-256
- 📈 **Suivi quota API** — Gauge visuelle de consommation Gemini

---

## ⚡ Pipeline d'extraction

```
📸 Photo / PDF facture
    ↓
📝 [OPTIONNEL] OCR.space (extraction texte brut — réduit tokens Gemini de 90%)
    ↓
🧠 Gemini 2.0 Flash (extraction structurée + traduction FR + classification BTP)
    ↓
✅ Validation Pydantic (schémas stricts, calcul auto TTC)
    ↓
🗄️ SQLite (dédoublonnage par [fournisseur + désignation], upsert prix)
    ↓
☁️ Google Drive + Sheets (archivage & sync cloud)
    ↓
📊 Catalogue consultable + Export Excel
```

### Flux détaillé

1. **Hash SHA-256** du fichier → vérification cache (évite le retraitement)
2. **Détection MIME** automatique (PDF, JPG, PNG, WebP, HEIC)
3. **Extraction IA** via Gemini 2.0 Flash :
   - Mode multimodal : envoi direct du fichier binaire
   - Mode texte : envoi du texte pré-OCR (si OCR.space configuré)
4. **Parsing JSON strict** de la réponse Gemini → validation Pydantic
5. **Upsert produit** en base SQLite : ajout ou mise à jour prix
6. **Enregistrement facture** pour traçabilité

---

## 🏗️ Architecture

```
docling-agent-assistant/
│
├── app.py                              # 🖥️  Interface Streamlit (UI principale)
│
├── backend/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                   # ⚙️  Configuration (pydantic-settings + .env)
│   │   ├── db_manager.py              # 🗄️  SQLite thread-safe — catalogue produits + factures
│   │   └── orchestrator.py            # 🎯  Pipeline d'extraction (hash → cache → Gemini → DB)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── invoice.py                 # 📐  Modèles Pydantic (Product, InvoiceResult, ProcessingResult)
│   │
│   └── services/
│       ├── __init__.py
│       ├── gemini_service.py          # 🧠  Extraction IA multimodale (Gemini 2.0 Flash)
│       ├── ocr_space_service.py       # 📝  OCR.space — extraction texte brut pré-Gemini
│       ├── google_drive_service.py    # ☁️  Archivage Drive (Année/Trimestre/Mois)
│       └── google_sheets_service.py   # 📊  Sync catalogue → Google Sheets
│
├── tests/                              # 🧪  26 tests pytest (100% pass)
│   ├── backend/
│   │   ├── core/
│   │   │   ├── test_config.py         # Tests configuration
│   │   │   ├── test_db_manager.py     # Tests base de données
│   │   │   └── test_orchestrator.py   # Tests pipeline
│   │   ├── services/
│   │   │   ├── test_gemini_service.py
│   │   │   ├── test_google_drive_service.py
│   │   │   ├── test_google_sheets_service.py
│   │   │   └── test_ocr_space_service.py
│   │   └── integration/
│   │       ├── test_invoice_schemas.py
│   │       └── test_pipeline_complete.py
│   └── frontend/
│       └── test_streamlit_app.py
│
├── .env                                # 🔐  Variables d'environnement (clés API)
├── .env.example                        # 📋  Template de configuration
├── .github/workflows/tests.yml        # 🔁  CI GitHub Actions
├── requirements.txt                    # 📦  Dépendances Python
├── pyproject.toml                      # 🔧  Metadata projet + config pytest/ruff
└── pytest.ini                          # 🧪  Config pytest
```

---

## 📐 Modèles de données (Pydantic Schemas)

### `Product` — Ligne produit facture

```python
class Product(BaseModel):
    fournisseur: str          # "BigMat", "Punto Madera", etc.
    designation_raw: str      # Nom original (Catalan/Espagnol)
    designation_fr: str       # Traduction française
    famille: str              # Classification BTP (voir liste ci-dessous)
    unite: str                # "sac", "kg", "m²", "ml", "unité", etc.
    prix_brut_ht: float       # Prix unitaire avant remise
    remise_pct: float | None  # Pourcentage de remise
    prix_remise_ht: float     # Prix unitaire après remise HT
    prix_ttc_iva21: float     # Prix TTC avec IVA 21% (auto-calculé si absent)
```

**Calcul automatique :** Si `prix_ttc_iva21 == 0` et `prix_remise_ht > 0`, alors `prix_ttc_iva21 = prix_remise_ht × 1.21`.

### `InvoiceResult` — Facture complète

```python
class InvoiceResult(BaseModel):
    numero_facture: str       # "F2024-001"
    date_facture: str         # "15/03/2024" (format JJ/MM/AAAA)
    fournisseur: str          # "BigMat"
    products: List[Product]   # Liste de toutes les lignes produit
```

### `ProcessingResult` — Résultat de traitement

```python
class ProcessingResult(BaseModel):
    invoice: InvoiceResult
    file_hash: str            # SHA-256 du fichier source
    products_added: int       # Nombre de nouveaux produits
    products_updated: int     # Nombre de prix mis à jour
    was_cached: bool          # True = facture déjà traitée
```

### Familles de produits BTP

| Famille | Exemples |
|---|---|
| Ciment | Portland, prompt, colle ciment |
| Gros œuvre | Parpaings, briques, linteaux |
| Armature | Fer à béton, treillis soudé |
| Quincaillerie | Vis, boulons, fixations |
| Maçonnerie | Mortier, colle, enduit |
| Ragréage | Autolissant, fibre |
| Finition | Peinture, vernis, lasure |
| Cloison | Placo, rails, montants |
| Plâtre | Plâtre, enduit plâtre |
| Granulat | Sable, gravier, concassé |
| Isolation | Laine de verre, XPS |
| Étanchéité | Membrane, bitume |
| Plomberie | Tubes, raccords, vannes |
| Électricité | Câbles, gaines, disjoncteurs |
| Outillage | Disques, lames, EPI |
| Logistique | Transport, location |
| Évacuation | Regards, tubes PVC |
| Colle | Colle carrelage, silicone |
| Additif | Adjuvants, fibres |

---

## 🗄️ Base de données SQLite

### Table `products`

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fournisseur TEXT NOT NULL,
    designation_raw TEXT NOT NULL,         -- Clé de dédoublonnage
    designation_fr TEXT,
    famille TEXT,
    unite TEXT,
    prix_brut_ht REAL DEFAULT 0.0,
    remise_pct REAL,
    prix_remise_ht REAL DEFAULT 0.0,
    prix_ttc_iva21 REAL DEFAULT 0.0,
    numero_facture TEXT,
    date_facture TEXT,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(designation_raw, fournisseur)   -- Contrainte unicité
);
```

### Table `invoices`

```sql
CREATE TABLE invoices (
    file_hash TEXT PRIMARY KEY,           -- SHA-256 du fichier
    filename TEXT NOT NULL,
    fournisseur TEXT,
    numero_facture TEXT,
    date_facture TEXT,
    nb_products INTEGER DEFAULT 0,
    processed_at TIMESTAMP NOT NULL
);
```

### Logique d'upsert

- **Clé unique** : `(designation_raw, fournisseur)`
- Si le produit existe déjà → mise à jour du prix (= "updated")
- Si le produit est nouveau → insertion (= "added")
- **Thread-safe** : toutes les opérations utilisent un `threading.Lock`

---

## 🧠 Service Gemini (Extraction IA)

### Configuration

- **Modèle** : `gemini-2.0-flash`
- **SDK** : `google-genai` (SDK officiel v1+)
- **Température** : `0.1` (réponses déterministes)
- **Format de sortie** : `application/json` (JSON strict)

### Prompt d'extraction

Le prompt demande à Gemini de jouer le rôle d'un **expert comptable BTP** et d'extraire :
- Métadonnées facture (numéro, date, fournisseur)
- Toutes les lignes produit avec traduction FR et classification famille

### Retry automatique (Rate Limit)

```
Tentative 1 → 429 RESOURCE_EXHAUSTED → attente 5s
Tentative 2 → 429 RESOURCE_EXHAUSTED → attente 15s
Tentative 3 → 429 RESOURCE_EXHAUSTED → attente 45s
→ Échec final après 3 retries
```

Le délai est extrait dynamiquement du message d'erreur (`retry in Xs`).

### Deux modes d'extraction

| Mode | Méthode | Input | Tokens | Quand l'utiliser |
|---|---|---|---|---|
| **Multimodal** | `extract_invoice(file_bytes, mime_type)` | Fichier binaire (PDF/image) | Élevé (~5K-50K) | Par défaut |
| **Texte** | `extract_from_text(ocr_text)` | Texte pré-OCR | Faible (~500-2K) | Avec OCR.space |

---

## 📝 Service OCR.space (Optionnel)

### Objectif

Réduire de **90% les tokens Gemini** en envoyant du texte brut au lieu de fichiers binaires.

### Configuration

- **API** : `https://api.ocr.space/parse/image`
- **Engine** : OCR Engine 2 (meilleur pour les tableaux)
- **Langue** : Espagnol (spa) par défaut
- **Format** : Base64 encoded
- **Options** : `isTable=True`, `scale=True`, `detectOrientation=True`

### Pipeline hybride

```
1. Si OCR_SPACE_API_KEY configuré :
   → OCR.space extrait le texte brut
   → Gemini structure le texte en JSON (mode texte, ~10x moins de tokens)

2. Si OCR_SPACE_API_KEY absent ou OCR échoue :
   → Gemini reçoit le fichier binaire directement (mode multimodal)
```

---

## ☁️ Services Google Cloud (Optionnels)

### Google Drive — Archivage automatique

Structure de dossiers créée automatiquement :
```
📁 Racine Drive
├── 📁 2024
│   ├── 📁 T1
│   │   ├── 📁 01-Janvier
│   │   ├── 📁 02-Février
│   │   └── 📁 03-Mars
│   ├── 📁 T2
│   └── ...
```

### Google Sheets — Catalogue synchronisé

Colonnes du spreadsheet :

| Colonne | Champ DB | Description |
|---|---|---|
| Fournisseur | `fournisseur` | BigMat, Punto Madera, etc. |
| Désignation (Català) | `designation_raw` | Nom original catalan/espagnol |
| Désignation (FR) | `designation_fr` | Traduction française |
| Famille | `famille` | Ciment, Finition, Cloison... |
| Unité | `unite` | sac, kg, m², ml... |
| P.U. Brut HT | `prix_brut_ht` | Prix avant remise |
| Remise % | `remise_pct` | Pourcentage de remise |
| P.U. Remisé HT | `prix_remise_ht` | Prix après remise |
| P.U. IVA 21% | `prix_ttc_iva21` | Prix TTC espagnol |
| N° Facture | `numero_facture` | Traçabilité |
| Date Facture | `date_facture` | Date du document |

---

## 🖥️ Interface Streamlit (app.py)

### Onglets

1. **📤 Traiter des factures** — Upload multi-fichiers (PDF, JPG, PNG, WebP), barre de progression, résultats en temps réel
2. **📦 Catalogue** — Tableau filtrable par fournisseur/famille/recherche, export Excel
3. **ℹ️ À propos** — Documentation intégrée

### Sidebar

- 🔑 Saisie clé API Gemini (stockée en session)
- 📊 Statistiques DB (produits, factures, familles)
- ⚡ Gauge quota API Gemini (usage/jour, restant, total cumulé)
- 🗑️ Bouton reset base (double-clic sécurité)

---

## 🚀 Installation

```bash
# 1. Cloner
git clone <repo-url>
cd docling-agent-assistant

# 2. Environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env avec vos clés API

# 5. Lancer
streamlit run app.py
```

---

## 📋 Configuration (.env)

```env
# === OBLIGATOIRE ===
GEMINI_API_KEY=votre_cle_gemini_api

# === OPTIONNEL — Réduction tokens (économie ~90%) ===
OCR_SPACE_API_KEY=votre_cle_ocr_space

# === OPTIONNEL — Google Cloud (archivage + sync) ===
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_DRIVE_FOLDER_ID=id_dossier_racine_drive
GOOGLE_SHEET_ID=id_spreadsheet_google
```

### Obtenir les clés

| Service | URL | Plan gratuit |
|---|---|---|
| Gemini API | [aistudio.google.com](https://aistudio.google.com) | 1500 requêtes/jour |
| OCR.space | [ocr.space](https://ocr.space/ocrapi) | 25000 requêtes/mois |
| Google Cloud | [console.cloud.google.com](https://console.cloud.google.com) | Service account requis |

---

## 📦 Dépendances

```
# Core
google-genai>=1.0       # SDK Gemini officiel
pandas>=2.0             # DataFrames
streamlit==1.38.0       # Interface web
openpyxl>=3.1           # Export Excel
pydantic>=2.0           # Validation données
pydantic-settings>=2.0  # Configuration .env
pillow>=10.0            # Traitement images
python-dotenv>=1.0      # Chargement .env
requests                # Appels HTTP (OCR.space)

# Google Cloud (optionnel)
google-api-python-client>=2.0
google-auth>=2.0

# Dev
pytest>=8.0
pytest-mock>=3.0
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Tests par module
pytest tests/backend/core/ -v              # Config, DB, Pipeline
pytest tests/backend/services/ -v          # Gemini, OCR, Drive, Sheets
pytest tests/backend/integration/ -v       # Schémas + pipeline complet
pytest tests/frontend/ -v                  # Interface Streamlit
```

### Couverture des tests (26 tests, 100% pass)

| Fichier | Tests | Couverture |
|---|---|---|
| `test_config.py` | 3 | Config valide, clé vide, clé placeholder |
| `test_db_manager.py` | 5 | Init tables, upsert add/update, save invoice, erreur SQLite |
| `test_orchestrator.py` | 3 | Pipeline succès, cache hit, extraction vide |
| `test_gemini_service.py` | 4 | Extraction OK, JSON invalide, rate limit, mode texte |
| `test_google_drive_service.py` | 2 | Upload OK, erreur API |
| `test_google_sheets_service.py` | 2 | Sync OK, erreur API |
| `test_ocr_space_service.py` | 3 | Extraction OK, erreur serveur, timeout |
| `test_invoice_schemas.py` | 2 | Calcul TTC auto, TTC explicite |
| `test_pipeline_complete.py` | 1 | Pipeline intégration complète (DB réelle) |
| `test_streamlit_app.py` | 1 | Boot Streamlit headless sans crash |

---

## 🔌 API — Guide d'intégration pour app mobile

### Point d'entrée principal

```python
from backend.core.config import get_config
from backend.core.db_manager import DBManager
from backend.core.orchestrator import ExtractionOrchestrator

# Initialiser
config = get_config()
db = DBManager(config.db_path)
orchestrator = ExtractionOrchestrator(config=config, db_manager=db)

# Traiter une facture
result = orchestrator.process_file(
    file_bytes=b"...",          # Contenu binaire du fichier
    filename="facture.pdf",     # Nom avec extension
    on_status=print             # Callback progression (optionnel)
)

# Résultat
print(result.products_added)    # 5
print(result.products_updated)  # 2
print(result.was_cached)        # False
print(result.invoice.numero_facture)  # "F2024-001"
```

### Accéder au catalogue

```python
# DataFrame pandas complet
df = db.get_catalogue()

# Statistiques
stats = db.get_stats()
# {"products": 150, "invoices": 23, "families": 12}

# Vérifier si une facture existe déjà
is_dupe = db.is_invoice_processed(DBManager.compute_file_hash(file_bytes))
```

### Utiliser Gemini directement

```python
from backend.services.gemini_service import GeminiService

gemini = GeminiService(config)

# Mode multimodal (PDF/image)
result = gemini.extract_invoice(file_bytes, "application/pdf")

# Mode texte (pré-OCR)
result = gemini.extract_from_text("BIGMAT\nCiment 25kg ... 8.50€")
```

### Format JSON attendu par Gemini

```json
{
  "numero_facture": "F2024-001",
  "date_facture": "15/03/2024",
  "fournisseur": "BigMat",
  "products": [
    {
      "fournisseur": "BigMat",
      "designation_raw": "Ciment Portland CEM II 25kg",
      "designation_fr": "Ciment Portland CEM II 25kg",
      "famille": "Ciment",
      "unite": "sac",
      "prix_brut_ht": 10.50,
      "remise_pct": 15.0,
      "prix_remise_ht": 8.93,
      "prix_ttc_iva21": 10.80
    }
  ]
}
```

---

## 🔒 Sécurité

- **Clés API** : stockées dans `.env` (jamais committé — voir `.gitignore`)
- **Base de données** : locale (SQLite), pas de données sensibles en cloud sauf si Google Cloud activé
- **Thread-safety** : `threading.Lock` sur toutes les opérations DB
- **Validation** : Pydantic v2 strict sur toutes les entrées/sorties
- **Rate limiting** : retry automatique avec backoff exponentiel

---

## 🗺️ Roadmap — Améliorations possibles

### Court terme
- [ ] Ajout de plus de fournisseurs BTP (Leroy Merlin, Point P, etc.)
- [ ] Support multi-pages PDF (actuellement page unique)
- [ ] Historique des prix par produit (graphique temporel)
- [ ] Comparateur de prix entre fournisseurs

### Moyen terme
- [ ] **API REST** (FastAPI) pour intégration mobile
- [ ] **App mobile** Flutter/React Native connectée à l'API
- [ ] **Notifications** push quand un prix baisse
- [ ] **OCR offline** (Tesseract) pour les zones sans internet

### Long terme
- [ ] **Prédiction de prix** par ML (tendances saisonnières)
- [ ] **Marketplace** — comparaison multi-fournisseurs automatisée
- [ ] **Intégration ERP** (Sage, EBP, Batigest)

---

## 📝 Licence

MIT — Usage libre, commercial inclus.

---

## 👤 Contact

Projet développé pour la gestion de chantiers BTP en Catalogne/Espagne.
