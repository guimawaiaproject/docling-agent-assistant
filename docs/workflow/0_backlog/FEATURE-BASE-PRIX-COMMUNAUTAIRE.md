# Base de données communautaire — Prix anonymes FR/ES

**Statut** : Idée / Backlog  
**Priorité** : Moyenne  
**Contexte** : Projet Docling FR/ES (BTP, factures fournisseurs)

---

## Objectif

Collecter anonymement les prix pour créer un service à valeur ajoutée : statistiques de prix moyens par zone et par produit, utiles pour les artisans BTP.

---

## Schéma proposé (validé)

### Table `prix_anonymes`

| Colonne      | Type        | Description |
|-------------|-------------|-------------|
| produit_hash | TEXT       | SHA256(salt + designation_normalisee + fournisseur) |
| fournisseur  | VARCHAR(200) | BigMat, Leroy Merlin, Punto Madera, etc. |
| zone_geo     | VARCHAR(10)  | "FR-34", "ES-08" (pays + 2 chiffres CP) |
| pays         | CHAR(2)      | "FR" \| "ES" |
| prix_ht      | NUMERIC(10,4) | Prix unitaire HT |
| date_facture | DATE         | Date de la facture |
| created_at   | TIMESTAMPTZ  | Horodatage insertion |

- Pas d'identifiant utilisateur
- Hash salé côté serveur (secret dans .env)
- Zone = 2 premiers chiffres code postal (département FR, province ES)

### Préférences utilisateur

- `community_consent` : booléen (partage anonyme activé)
- `zone_geo` : "FR-34" | "ES-08" | etc.
- Stockage : table `user_preferences` ou champ sur `users`

---

## Mécanisme de consentement

1. **SettingsPage** : case à cocher « Partager anonymement mes prix pour aider la communauté »
2. **Sélecteur zone** : dropdown départements FR (01-95) + provinces ES (01-52)
3. **Backend** : stocker en base (pas localStorage) pour persistance et conformité RGPD

---

## Collecte des données

1. **Orchestrator** : après extraction réussie, si `community_consent` activé
2. **Tâche asynchrone** : insertion dans `prix_anonymes` sans bloquer le flux
3. **Hash** : `SHA256(SECRET + designation_normalisee + fournisseur)`
4. **Normalisation** : minuscules, trim, suppression accents pour regroupement

---

## Endpoint `/api/v1/community/stats`

- Agrégats : prix moyen, min, max par (produit_hash, zone_geo, fournisseur)
- **k-anonymité** : ne publier que si COUNT(*) >= 5 contributeurs
- Paramètres : `zone`, `pays`, `fournisseur`, `search` (sur designation via lookup)

---

## Page CommunityStats (frontend)

- Carte FR/ES avec heatmap ou markers par zone
- Graphiques : évolution prix, comparaison fournisseurs
- Filtres : zone, famille produit, fournisseur

---

## Sécurité & RGPD

- [x] Consentement explicite opt-in
- [x] Pas d'user_id, hash irréversible (avec salt)
- [x] Zone = département/province (pas code postal complet)
- [x] k-anonymité sur les stats publiées
- [ ] Politique de confidentialité à mettre à jour

---

## Références

- Analyse initiale : session agent 2026-02-28
- Bonnes pratiques : ICO case study, k-anonymity
- Structure géo : France 2 premiers CP = département, Espagne = province
