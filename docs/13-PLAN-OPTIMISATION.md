# Plan d'optimisation — Docling Agent

*Plan chronologique avec tests de vérification à chaque implémentation — Fév. 2026*

---

## Vue d'ensemble

Ce document regroupe les actions d'amélioration identifiées dans les audits (05, 06, 10, 12) en sprints exécutables, avec une checklist de vérification après chaque étape.

---

## Sprint 1 — Urgences immédiates (1 semaine)

### 1.1 Persister les jobs en base Neon

| Élément | Détail |
|---------|--------|
| **Problème** | BackgroundTasks sans persistance : jobs perdus si crash/redémarrage |
| **Solution** | Table `jobs` en Neon (job_id, status, result, created_at, updated_at) |
| **Effort** | 4h |

**Tests de vérification :**
- [ ] Table `jobs` créée dans `schema_neon.sql`
- [ ] `api.py` écrit/ lit dans la table au lieu de `_jobs` en mémoire
- [ ] Polling `/api/v1/invoices/status/{job_id}` fonctionne après redémarrage backend
- [ ] Test : lancer extraction → redémarrer API → vérifier que le job est toujours accessible

---

### 1.2 Implémenter storage_service.py S3 Storj

| Élément | Détail |
|---------|--------|
| **Problème** | Bouton "Voir PDF" cassé, factures non archivées |
| **Solution** | `storage_service.py` upload S3 + intégration orchestrator + colonne `pdf_url` |
| **Effort** | 3h |

**Tests de vérification :**
- [ ] `storage_service.py` upload un PDF vers Storj et retourne l'URL
- [ ] `orchestrator.py` appelle l'upload après extraction réussie
- [ ] Colonne `pdf_url` dans schema + db_manager
- [ ] Endpoint `/api/v1/history` renvoie `pdf_url` pour chaque facture
- [ ] Bouton "Voir PDF" ouvre le document

---

### 1.3 Fixer les clés React (CompareModal, ValidationPage, ScanPage)

| Élément | Détail |
|---------|--------|
| **Problème** | Index comme `key` dans `.map()` → bugs de rendu sur listes longues |
| **Solution** | Remplacer par identifiants stables (`item.id`, `p.id` ou combinaison unique) |
| **Effort** | 1h |

**Tests de vérification :**
- [ ] CompareModal.jsx : aucune `key={index}` dans les `.map()`
- [ ] ValidationPage.jsx : idem
- [ ] ScanPage.jsx : idem (utiliser `item.id` si existe)
- [ ] `npm run lint` sans erreur
- [ ] Test manuel : ajouter/supprimer des items, vérifier pas de glitch visuel

---

### 1.4 Circuit-breaker Gemini

| Élément | Détail |
|---------|--------|
| **Problème** | File bloquée si Gemini down pendant longtemps |
| **Solution** | Après N erreurs consécutives (ex. 5), marquer le job en erreur et passer au suivant |
| **Effort** | 4h |

**Tests de vérification :**
- [ ] `gemini_service.py` ou `orchestrator.py` : compteur d'erreurs consécutives
- [ ] Après N échecs : job marqué `error`, message explicite
- [ ] Les autres jobs dans la file continuent d'être traités
- [ ] Test : simuler Gemini indisponible (clé invalide) → vérifier comportement

---

## Sprint 2 — Priorités hautes (2 semaines)

### 2.1 Mode offline PWA (IndexedDB + sync)

| Élément | Détail |
|---------|--------|
| **Problème** | Pas de scan sur chantier sans connexion |
| **Solution** | File d'attente IndexedDB, sync au retour connexion |
| **Effort** | 1-2 semaines |

**Tests de vérification :**
- [ ] Fichiers scannés en offline stockés en IndexedDB
- [ ] Au retour connexion : upload automatique vers l'API
- [ ] Indicateur visuel "hors ligne" / "synchronisation en cours"
- [ ] Test : couper réseau → scanner 2-3 factures → rétablir → vérifier sync

---

### 2.2 Support Factur-X (extraction XML embarqué)

| Élément | Détail |
|---------|--------|
| **Problème** | Conformité facturation électronique obligatoire sept. 2026 |
| **Solution** | Extraire XML embarqué des PDF Factur-X pour précision quasi-parfaite sans IA |
| **Effort** | 1 semaine |

**Tests de vérification :**
- [ ] Détection PDF Factur-X (XML embarqué)
- [ ] Extraction des lignes produits depuis le XML
- [ ] Fallback Gemini si pas Factur-X
- [ ] Test avec facture Factur-X réelle

---

### 2.3 TVA, remise globale, numéro auto dans DevisPage

| Élément | Détail |
|---------|--------|
| **Problème** | Devis PDF trop léger (pas de TVA, remise, numérotation) |
| **Solution** | Champs TVA (%), remise globale, numéro auto (DEV-2026-001) |
| **Effort** | 4-6h |

**Tests de vérification :**
- [ ] Champ TVA modifiable, total TTC calculé
- [ ] Champ remise (% ou montant)
- [ ] Numéro de devis auto-incrémenté
- [ ] PDF généré contient toutes les infos

---

## Sprint 3+ — Moyen terme

### 3.1 Migration SDK google-genai (async natif)

| Élément | Détail |
|---------|--------|
| **Problème** | `asyncio.to_thread()` pour contourner le SDK synchrone |
| **Solution** | Migrer vers `google-genai` avec `client.aio.models.generate_content()` |
| **Effort** | 1 semaine |

**Tests de vérification :**
- [ ] Tous les tests pytest passent
- [ ] Extraction fonctionne en production
- [ ] Suppression du code `asyncio.to_thread()` pour Gemini

---

### 3.2 Comparateur prix fournisseurs avancé

| Élément | Détail |
|---------|--------|
| **Problème** | CompareModal basique |
| **Solution** | Graphiques évolution prix (table `prix_historique` existe) |
| **Effort** | 1 semaine |

**Tests de vérification :**
- [ ] Comparaison 2+ fournisseurs pour un même produit
- [ ] Graphique évolution temporelle si données disponibles

---

### 3.3 Base communautaire de prix géolocalisés

| Élément | Détail |
|---------|--------|
| **Problème** | Effet réseau, moat concurrentiel |
| **Solution** | Partage de prix entre artisans (anonymisé, géolocalisé) |
| **Effort** | 2-4 semaines |

**Tests de vérification :**
- [ ] Modèle Freemium défini
- [ ] API partage/consultation prix
- [ ] Consentement utilisateur (RGPD)

---

## Checklist globale par implémentation

Pour chaque tâche du plan :

1. **Avant** : Lire la doc associée (05, 06, 10, 12)
2. **Pendant** : Suivre les bonnes pratiques (DRY, tests)
3. **Après** : Cocher les tests de vérification
4. **Mettre à jour** : 10-NOTES-AUDIT.md si nouveaux points d'attention

---

## Références

- [05-AUDIT-BACKEND.md](05-AUDIT-BACKEND.md) — Optimisations backend
- [06-AUDIT-FRONTEND.md](06-AUDIT-FRONTEND.md) — Dette technique frontend
- [10-NOTES-AUDIT.md](10-NOTES-AUDIT.md) — Points d'attention, prochaines étapes
- [12-EXPERT-REPORT.md](12-EXPERT-REPORT.md) — Rapport expert, SWOT, roadmap détaillée

---

*Document créé lors de la réorganisation docs/ — Fév. 2026*
