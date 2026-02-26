# Analyse des 5 fenêtres — Docling Agent

Pour chaque écran : contenu actuel, comparaison avec les apps existantes, avis personnel, améliorations proposées et guide d’utilisation.

---

## 1. SCANNER

### Ce qu’il y a actuellement

- **Bouton principal** : « Photographier une Facture » — ouvre la caméra pour prendre une photo.
- **Zone d’upload** : glisser-déposer ou sélection de fichiers PDF/images.
- **Deux boutons** :
  - « Parcourir les fichiers » — sélection de fichiers un par un.
  - « Sélectionner un dossier » — parcourt un dossier et ses sous-dossiers pour récupérer tous les PDF.
- **Zone de liste** : affiche les fichiers en attente et leur statut (en attente, en cours, terminé, erreur).
- **Boutons d’action** : « Lancer » pour traiter la file, « Poubelle » pour vider la file.

### Comparaison avec les apps existantes

| App | Similitude | Différence |
|-----|-------------|------------|
| **CamScanner, Adobe Scan** | Photo + scan | Pas de traitement IA des produits |
| **Expensify, QuickBooks** | Scan de factures | Pas de sélection de dossier récursive |
| **Docling** | — | Scan + extraction produits + dossier magique |

### Avis personnel

- Points forts : bouton caméra, sélection de dossier, file de traitement claire.
- Points à améliorer : zone vide quand aucun fichier, pas de retour visuel immédiat après le clic sur « Lancer ».

### Améliorations proposées

1. **Message quand la file est vide** : « Aucun fichier en attente. Glissez des PDF ou ajoutez un dossier. »
2. **Indicateur de progression globale** : barre « X / Y fichiers traités » plus visible.
3. **Raccourci** : « Sélectionner un dossier » plus visible quand il y a beaucoup de PDF à traiter.
4. **Retour** : vibration ou son de confirmation sur mobile quand un traitement est terminé.

### Guide d’utilisation

1. **Photo** : cliquer sur « Photographier une Facture » → prendre la photo → l’app traite automatiquement.
2. **Fichiers** : glisser-déposer des PDF/images ou cliquer sur « Parcourir les fichiers ».
3. **Dossier** : cliquer sur « Sélectionner un dossier » → choisir un dossier → tous les PDF sont ajoutés.
4. **Lancer** : cliquer sur « Lancer » pour traiter la file.
5. **Suivi** : suivre les statuts (vert = OK, rouge = erreur).

---

## 2. CATALOGUE

### Ce qu’il y a actuellement

- **Titre** : « Catalogue » avec nombre total de produits.
- **Recherche** : barre de recherche.
- **Filtres** : par famille (Armature, Plomberie, etc.) et par fournisseur.
- **Statistiques prix** : Min, Moyenne, Max.
- **Boutons d’action** : Export CSV, Export Excel, autre action.
- **Vue** : tableau ou cartes.
- **Liste** : produit, fournisseur, famille, prix.

### Comparaison avec les apps existantes

| App | Similitude | Différence |
|-----|-------------|------------|
| **Excel, Google Sheets** | Tableau, filtres, export | Pas de scan automatique |
| **ERP de gestion** | Catalogue produits | Plus complexe |
| **Docling** | — | Catalogue simple, alimenté par extraction IA |

### Avis personnel

- Points forts : recherche, filtres, export CSV/Excel, statistiques prix.
- Points à améliorer : vue cartes sur mobile, comparaison de prix entre fournisseurs.

### Améliorations proposées

1. **Comparaison de prix** : comparer deux produits similaires (déjà prévu avec `CompareModal`).
2. **Tri** : tri par prix, date, fournisseur.
3. **Favoris** : marquer des produits souvent utilisés.
4. **Alertes** : alerter si un prix change beaucoup par rapport à l’historique.

### Guide d’utilisation

1. **Recherche** : taper un mot dans la barre de recherche.
2. **Filtres** : famille (ex. Plomberie) ou fournisseur (ex. Leroy Merlin).
3. **Export** : cliquer sur « Export CSV » ou « Export Excel » pour sauvegarder.
4. **Consultation** : parcourir la liste ou les cartes pour voir les produits et leurs prix.

---

## 3. DEVIS

### Ce qu’il y a actuellement

- **Champs** : « Mon Entreprise BTP » et « Nom du client ».
- **Zone « Produits sélectionnés »** (visible uniquement quand des produits sont ajoutés) :
  - Liste des produits sélectionnés.
  - Quantité (+/-).
  - Prix total par ligne.
  - Bouton supprimer.
  - Total HT.
  - Bouton « Générer le devis PDF ».
- **Recherche** : « Chercher un produit… ».
- **Liste** : produits du catalogue cliquables pour les ajouter au devis.

### Comparaison avec les apps existantes

| App | Similitude | Différence |
|-----|-------------|------------|
| **Devis.app, QuickBooks** | Devis + PDF | Pas de catalogue issu de factures |
| **Excel** | Calculs, totaux | Pas de génération PDF structurée |
| **Docling** | — | Devis basé sur catalogue produit des factures |

### Avis personnel

- Points forts : ajout simple, quantités, total HT, génération PDF.
- Points à améliorer : zone « Produits sélectionnés » peu visible avant le premier ajout, pas de TVA ni de remise globale.

### Améliorations proposées

1. **Zone « Mon Devis »** : toujours visible, même vide, avec « Ajoutez des produits ci-dessous ».
2. **TVA** : champ pour taux de TVA (ex. 20 %) et total TTC.
3. **Remise globale** : pourcentage ou montant sur le total.
4. **Client** : liste de clients récents ou suggestions.
5. **Brouillon** : sauvegarder un devis sans le finaliser.
6. **Numéro de devis** : numérotation automatique (ex. DEV-2026-001).

### Guide d’utilisation

1. **Infos** : « Mon Entreprise BTP » et « Nom du client ».
2. **Ajout** : cliquer sur un produit dans la liste pour l’ajouter au devis.
3. **Quantités** : utiliser + et - pour ajuster.
4. **Suppression** : cliquer sur la poubelle pour retirer un produit.
5. **Total** : vérifier le total HT.
6. **PDF** : cliquer sur « Générer le devis PDF » pour télécharger le document.

---

## 4. HISTORIQUE

### Ce qu’il y a actuellement

- **Titre** : « Historique — Audit trail des factures traitées ».
- **Bouton** : rafraîchir.
- **Statistiques** : nombre de factures, nombre de produits, coût API.
- **Graphique** : répartition par famille (Plomberie, Consommable, etc.).
- **Liste** : pour chaque facture :
  - Nom du fichier.
  - Statut (OK / erreur).
  - Nombre de produits extraits.
  - Modèle IA utilisé.
  - Coût par facture.
  - Date et heure.
  - Origine (PC, Mobile, Dossier).
  - Actions : « Voir PDF », « Re-scanner ».

### Comparaison avec les apps existantes

| App | Similitude | Différence |
|-----|-------------|------------|
| **Expensify, QuickBooks** | Historique de factures | Pas de coût API par document |
| **Cloud (AWS, etc.)** | Suivi des coûts | Pas de suivi par facture |
| **Docling** | — | Coût API visible par facture et par modèle |

### Avis personnel

- Points forts : transparence sur le coût API, répartition par famille, bouton « Re-scanner ».
- Points à améliorer : recherche, filtres par date, tri.

### Améliorations proposées

1. **Recherche** : par nom de fichier ou fournisseur.
2. **Filtres** : par date (7 jours, 30 jours, personnalisé), par statut.
3. **Tri** : par date, par coût, par nombre de produits.
4. **Détails** : cliquer sur une facture pour voir les produits extraits.
5. **Graphique coût** : évolution du coût API dans le temps.

### Guide d’utilisation

1. **Vue d’ensemble** : regarder les 3 cartes (factures, produits, coût API).
2. **Familles** : utiliser le graphique pour voir les types de produits les plus fréquents.
3. **Liste** : faire défiler pour voir chaque facture.
4. **Actions** : « Voir PDF » pour ouvrir le PDF, « Re-scanner » pour retraiter.
5. **Rafraîchir** : cliquer sur le bouton pour actualiser les données.

---

## 5. RÉGLAGES

### Ce qu’il y a actuellement

- **Connexion API** :
  - Statut : Non testé / Connecté / Déconnecté.
  - Bouton « Tester ».
  - Cartes : produits, infos, etc.
- **Modèle IA** :
  - Gemini 3 Flash (recommandé, rapide).
  - Gemini 3.1 Pro (précision).
  - Gemini 2.5 Flash (stable).
- **Dossier magique** :
  - Statut : actif ou inactif.
  - Dossier surveillé.
- **À propos** :
  - Version.
  - Technologies (FastAPI, Neon PostgreSQL).

### Comparaison avec les apps existantes

| App | Similitude | Différence |
|-----|-------------|------------|
| **Apps mobiles** | Paramètres, tests API | Peu montrent le modèle IA |
| **SaaS** | Choix de modèle | Pas de dossier magique |
| **Docling** | — | Choix de modèle IA + dossier magique |

### Avis personnel

- Points forts : test de connexion, choix du modèle IA, statut du dossier magique.
- Points à améliorer : expliquer le dossier magique, lien vers la doc.

### Améliorations proposées

1. **Dossier magique** : explication courte « Surveille le dossier X et traite automatiquement les nouveaux PDF ».
2. **Chemin du dossier** : afficher le chemin complet (ex. `C:\...\Docling_Factures`).
3. **Aide** : lien « En savoir plus » ou FAQ.
4. **Thème** : option clair/sombre.
5. **Notifications** : activer/désactiver les notifications.

### Guide d’utilisation

1. **Connexion** : cliquer sur « Tester » pour vérifier que l’app est bien connectée au serveur.
2. **Modèle IA** : choisir entre « Ultra-Rapide » (Flash), « Précision » (Pro) ou « Stable » (2.5 Flash).
3. **Dossier magique** : vérifier si le dossier est actif et quel dossier est surveillé.
4. **Infos** : consulter la version et les technologies utilisées.

---

## Synthèse globale

| Écran | Maturité | Priorité d’amélioration |
|-------|----------|--------------------------|
| **Scanner** | ✅ Bonne | Message quand vide, progression plus visible |
| **Catalogue** | ✅ Bonne | Comparaison, tri, favoris |
| **Devis** | ✅ Bonne | TVA, remise, brouillon, zone « Mon Devis » toujours visible |
| **Historique** | ✅ Bonne | Recherche, filtres, export |
| **Réglages** | ✅ Bonne | Explication du dossier magique, lien vers la doc |

---

*Document généré pour Docling Agent v3 — Guide d’analyse et d’amélioration.*

---

## Avis clients des concurrents

Voir le document complementaire **[08-AVIS-CONCURRENTS.md](08-AVIS-CONCURRENTS.md)** pour les points manquants releves aupres des concurrents (CamScanner, Expensify, Obat, etc.).
