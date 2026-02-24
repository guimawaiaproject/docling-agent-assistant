# 📖 CAHIER DES CHARGES : Docling Agent BTP (Édition Premium)

## 1. Description du Projet
L'objectif est d'avoir une application métier "clé en main" pour fluidifier, automatiser et centraliser l'extraction des données issues de factures de chantier (BTP) complexes, souvent dans des langues étrangères (Catalan/Espagnol), en numérisant la tarification vers un référentiel central.

---

## 2. Architecture Technique (La fondation)
Le projet repose sur 3 piliers intangibles et locaux, pour garantir la **vitesse**, la **sécurité**, et **l'indépendance** technologique.

*   **Le Cerveau (IA)** : **Google Gemini 2.5 Flash**. Seule et unique IA du projet (Vision OCR + Analyse sémantique).
    *   👉 *Fichier Responsable : `backend/services/gemini_service.py`*
*   **Le Moteur (API Backend)** : **FastAPI (Python)**. Une API REST ultra-rapide traitant les fichiers en parallèle.
    *   👉 *Fichier Responsable : `api.py`*
*   **L'Interface Client (Frontend)** : **Streamlit**. Application web vitrine locale (Design Premium, jauges en temps réel).
    *   👉 *Fichier Responsable : `app.py`*
*   **Le Stockage (Base de Données)** : **SQLite (Local)**. Base de données relationnelle ultra-rapide gérant les upserts et les requêtes SQL (Fichier `data_cache.db`).
    *   👉 *Fichier Responsable : `backend/core/db_manager.py`*
*   **La Configuration** : Variables d'environnement pour stocker intelligemment les clés API (`.env`).
    *   👉 *Fichier Responsable : `backend/core/config.py`*

---

## 3. Fonctionnalités Principales (Les "Features")

### 3.1. Le Traitement Haute Vitesse (L'Usine)
*   **Agressivité Parallèle (Le Turbo)** : Envoi simultané (ThreadPool) de multiples factures pour accélerer le traitement global.
    *   👉 *Déclenché dans : `app.py` (Barre de paramètres latérale et boucle d'envoi)*
*   **Le Chef d'Orchestre (Pipeline)** : Logique de Hachage du fichier -> Vérification si déjà traité -> Extraction IA -> Sauvegarde DB.
    *   👉 *Fichier Responsable : `backend/core/orchestrator.py`*
*   **Optimisation Réseau (Image-Shrinker)** : Compression automatique des factures scannées en format WebP (très léger) avant l'envoi vers Google pour décupler la rapidité de transfert et réduire les coûts tokens.
    *   👉 *Fichier Responsable : `app.py` (fonction `optimize_image`)*
*   **Tableau de Bord Économique & Vitesse** : Compteur de documents par seconde et estimation exacte du coût API Google.
    *   👉 *Affichage : `app.py`*
    *   👉 *Calcul Backend (Temps de traitement) : `backend/core/monitoring.py`*

### 3.2. L'Extraction IA Spécialisée BTP
Le prompt "Expert-Comptable" dicte à Gemini 2.5 Flash comment agir.
*   **Missions exactes de l'IA** :
    1.  Extraire : Fournisseur, N° de Facture, Date de facture.
    2.  Extraire Lignes : Nom original, Traduction Française, Unité, Prix Brut, Remise, Prix Net, Prix TTC.
    3.  Classer automatiquement l'article dans une des grandes familles BTP (Ciment, Gros œuvre, Électricité...).
    *   👉 *Fichier Responsable : `backend/services/gemini_service.py` (Variable `EXTRACTION_PROMPT`)*

### 3.3. Le Catalogue Centralisé (Le Cœur du Trésor)
*   **Logique de Fusion "Upsert"** : Si l'IA trouve un doublon exact ("Designation Originale" du même "Fournisseur"), alors le nouveau prix vient écraser l'ancien. Sinon, l'article est inséré comme nouveau produit.
    *   👉 *Fichier Responsable : `backend/core/db_manager.py` (Méthode `upsert_product`)*
*   **L'Éditeur Interactif (Tableau Magique)** : Le catalogue affiché n'est pas qu'un visuel. Il est dynamique. Double-cliquer modifie une case, "Entrée" sauvegarde la correction dans la base SQLite en appelant l'API.
    *   👉 *Création de la grille visuelle : `app.py` (Composant `st.data_editor`)*
    *   👉 *Route de point d'entrée pour recevoir les modifications : `api.py` (Endpoint `PUT /api/v1/products/{product_id}`)*
*   **Statistiques (Le compteur du Haut)** : Ramène en permanence le nombre de factures traitées et d'articles distincts.
    *   👉 *Fichier Responsable : `backend/core/db_manager.py` (Méthode `get_stats`)*

---

## 4. Nomenclature et Référentiel des Fichiers Strictement Nécessaires
L'application BTP Premium se compose d'une architecture épurée. Voici les seuls fichiers qui doivent constituer ce projet final et leurs utilités respectives.

### 🏠 Racine du projet
*   📄 **`app.py`** : L'interface graphique (Frontend). Affiche votre tableau de bord interactif, la jauge Turbo, vos compteurs de statistiques et gère l'envoi des factures vers le Backend.
*   📄 **`api.py`** : Le routeur central (Backend). Expose les points d'accès (serveur Uvicorn/FastAPI) que l'interface Streamlit va appeler pour parler avec l'Intelligence Artificielle et la base de données.
*   📄 **`requirements.txt`** : Le carnet de santé Python. Liste exclusivement les librairies requises (`streamlit`, `fastapi`, `google-genai`, `pandas`, `pydantic`). C'est le passeport d'installation.
*   📄 **`run_local.bat`** : Le bouton de démarrage (Lanceur). Allume silencieusement l'API en arrière-plan et ouvre l'interface utilisateur web d'un simple double-clic sous Windows.
*   📄 **`.env`** : Fichier caché de sécurité. Stocke uniquement vos secrets informatiques, comme la `GEMINI_API_KEY`. (Ne doit jamais être partagé sous peine de piratage).
*   📄 **`data_cache.db`** : (Généré automatiquement par le projet au 1er lancement) La base de données SQLite physique contenant votre catalogue complet et l'historique interactif.

### 🧠 Cœur du système (`backend/core/`)
*   📄 **`config.py`** : Le contrôleur d'environnement. Sécurise le chargement du `.env` et stoppe l'application immédiatement si la clé Gemini manque avant d'autoriser le démarrage.
*   📄 **`db_manager.py`** : Le bibliothécaire (SQLite). Gère la création des tables et encaisse toute la logique anti-doublon (Upsert) pour mettre à jour les prix instantanément depuis la base de données SQLite.
*   📄 **`orchestrator.py`** : Le grand chef d'atelier de production. C'est lui qui dirige la chaîne de montage en connectant les composants : "Prendre le fichier -> Vérifier en base s'il est connu -> Envoyer à l'IA -> Enregistrer les nouveaux tarifs en base".
*   📄 **`monitoring.py`** : L'inspecteur des temps. Chronomètre à la microseconde près le temps passé par l'IA (requis pour le calcul d'affichage de la vitesse en doc/sec) et prépare le journal d'erreurs en cas de pépin (Sentry).

### 🛠️ Services Intelligents (`backend/services/`)
*   📄 **`gemini_service.py`** : L'interprète technique IA. C'est l'un des fichiers les plus critiques. Il porte le "Mega-Prompt" BTP (instructions de comportement). Il lit l'image de la facture, l'envoie valider au modèle `gemini-2.5-flash`, et force l'IA à lui fournir un tableau stérile formaté correctement (sans invention ni délire asymétrique).

### 📐 Schémas Standards (`backend/schemas/`)
*   📄 **`invoice.py`** : Le moule industriel (définitions Pydantic). Il impose au système ce qu'est un "Produit Extractible BTP" (champs obligatoires : Fournisseur, Prix, Unité, Remise) et ce qu'indique un "Résultat de facture", garantissant que le service ne casse pas le tableau.
