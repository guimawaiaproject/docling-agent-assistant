# Analyse des 5 fenêtres — Docling Agent

Pour chaque écran : contenu actuel, comparaison avec les apps existantes, avis personnel, améliorations proposées et guide d'utilisation.

---

## 1. SCANNER

### Ce qu'il y a actuellement

- **Bouton principal** : « Photographier une Facture » — ouvre la caméra pour prendre une photo.
- **Zone d'upload** : glisser-déposer ou sélection de fichiers PDF/images.
- **Deux boutons** :
  - « Parcourir les fichiers » — sélection de fichiers un par un.
  - « Sélectionner un dossier » — parcourt un dossier et ses sous-dossiers pour récupérer tous les PDF.
- **Zone de liste** : affiche les fichiers en attente et leur statut (en attente, en cours, terminé, erreur).
- **Boutons d'action** : « Lancer » pour traiter la file, « Poubelle » pour vider la file.

### Améliorations proposées

1. **Message quand la file est vide** : « Aucun fichier en attente. Glissez des PDF ou ajoutez un dossier. »
2. **Indicateur de progression globale** : barre « X / Y fichiers traités » plus visible.
3. **Raccourci** : « Sélectionner un dossier » plus visible quand il y a beaucoup de PDF à traiter.
4. **Retour** : vibration ou son de confirmation sur mobile quand un traitement est terminé.

---

## 2. CATALOGUE

### Ce qu'il y a actuellement

- **Titre** : « Catalogue » avec nombre total de produits.
- **Recherche** : barre de recherche.
- **Filtres** : par famille (Armature, Plomberie, etc.) et par fournisseur.
- **Statistiques prix** : Min, Moyenne, Max.
- **Boutons d'action** : Export CSV, Export Excel.
- **Vue** : tableau ou cartes.

### Améliorations proposées

1. **Comparaison de prix** : comparer deux produits similaires (déjà prévu avec `CompareModal`).
2. **Tri** : tri par prix, date, fournisseur.
3. **Favoris** : marquer des produits souvent utilisés.
4. **Alertes** : alerter si un prix change beaucoup par rapport à l'historique.

---

## 3. DEVIS

### Ce qu'il y a actuellement

- **Champs** : « Mon Entreprise BTP » et « Nom du client ».
- **Zone « Produits sélectionnés »** : liste, quantités, total HT, génération PDF.
- **Recherche** : « Chercher un produit… ».

### Améliorations proposées

1. **Zone « Mon Devis »** : toujours visible, même vide, avec « Ajoutez des produits ci-dessous ».
2. **TVA** : champ pour taux de TVA (ex. 20 %) et total TTC.
3. **Remise globale** : pourcentage ou montant sur le total.
4. **Client** : liste de clients récents ou suggestions.
5. **Brouillon** : sauvegarder un devis sans le finaliser.
6. **Numéro de devis** : numérotation automatique (ex. DEV-2026-001).

---

## 4. HISTORIQUE

### Ce qu'il y a actuellement

- **Statistiques** : nombre de factures, nombre de produits, coût API.
- **Graphique** : répartition par famille.
- **Liste** : pour chaque facture — nom, statut, produits extraits, modèle IA, coût, actions.

### Améliorations proposées

1. **Recherche** : par nom de fichier ou fournisseur.
2. **Filtres** : par date (7 jours, 30 jours, personnalisé), par statut.
3. **Tri** : par date, par coût, par nombre de produits.
4. **Détails** : cliquer sur une facture pour voir les produits extraits.
5. **Graphique coût** : évolution du coût API dans le temps.

---

## 5. RÉGLAGES

### Ce qu'il y a actuellement

- **Connexion API** : statut, bouton « Tester ».
- **Modèle IA** : Gemini 3 Flash, 3.1 Pro, 2.5 Flash.
- **Dossier magique** : statut, dossier surveillé.
- **À propos** : version, technologies.

### Améliorations proposées

1. **Dossier magique** : explication courte « Surveille le dossier X et traite automatiquement les nouveaux PDF ».
2. **Chemin du dossier** : afficher le chemin complet.
3. **Aide** : lien « En savoir plus » ou FAQ.
4. **Thème** : option clair/sombre.
5. **Notifications** : activer/désactiver les notifications.

---

## Synthèse globale

| Écran | Maturité | Priorité d'amélioration |
|-------|----------|--------------------------|
| **Scanner** | ✅ Bonne | Message quand vide, progression plus visible |
| **Catalogue** | ✅ Bonne | Comparaison, tri, favoris |
| **Devis** | ✅ Bonne | TVA, remise, brouillon, zone « Mon Devis » toujours visible |
| **Historique** | ✅ Bonne | Recherche, filtres, export |
| **Réglages** | ✅ Bonne | Explication du dossier magique, lien vers la doc |
