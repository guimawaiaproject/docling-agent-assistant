# Spec — Base prix communautaire

**Référence** : [FEATURE-BASE-PRIX-COMMUNAUTAIRE.md](../../0_backlog/FEATURE-BASE-PRIX-COMMUNAUTAIRE.md)

## 1. Schéma base de données

### Table `prix_anonymes`

```sql
CREATE TABLE prix_anonymes (
    id           SERIAL PRIMARY KEY,
    produit_hash TEXT NOT NULL,
    fournisseur  VARCHAR(200) NOT NULL,
    zone_geo     VARCHAR(10) NOT NULL,
    pays         CHAR(2) NOT NULL,
    prix_ht      NUMERIC(10,4) NOT NULL,
    date_facture DATE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prix_anonymes_hash_zone ON prix_anonymes(produit_hash, zone_geo);
CREATE INDEX idx_prix_anonymes_fournisseur ON prix_anonymes(fournisseur);
```

### Table `users` — colonnes consentement

- `community_consent` BOOLEAN DEFAULT FALSE
- `zone_geo` VARCHAR(10) (ex: FR-34, ES-08)

## 2. Endpoint `/api/v1/community/stats`

**Méthode** : GET
**Paramètres** : `zone`, `pays`, `fournisseur`, `search`
**Règles** : k-anonymité (COUNT >= 5 contributeurs par agrégat)

**Réponse** :
```json
{
  "stats": [
    {
      "produit_hash": "...",
      "designation_sample": "Ciment 42.5R",
      "fournisseur": "BigMat",
      "zone_geo": "FR-34",
      "prix_moyen": 12.50,
      "prix_min": 11.00,
      "prix_max": 14.00,
      "nb_contributions": 12
    }
  ]
}
```

## 3. Collecte

- **Trigger** : après extraction réussie (orchestrator)
- **Condition** : `user.community_consent = true` et `user.zone_geo` défini
- **Hash** : `SHA256(COMMUNITY_SALT + designation_normalisee + fournisseur)`
- **Insertion** : asynchrone, non bloquante

## 4. Frontend

- **SettingsPage** : case « Partager anonymement mes prix » + sélecteur zone
- **Stockage** : API PATCH `/api/v1/users/me/preferences`
