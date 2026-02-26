# Rapport d'Expert — Docling Agent

*Analyse technique, concurrentielle et stratégique — Février 2026*

> **Note :** Certains points (ex. S3 Storj) ont pu être implémentés depuis la rédaction du rapport. Vérifier l'état actuel du code.

## 1. Synthèse exécutive

| Dimension | Verdict | Score |
|-----------|---------|-------|
| Stack technique | Solide pour un MVP. Deux risques critiques en production. | 7/10 |
| Positionnement marché | Créneau réel, non adressé. Proposition de valeur claire. | 9/10 |
| Maturité produit | Fonctionnel mais des trous fonctionnels bloquants. | 6/10 |
| Urgence réglementaire | Facturation électronique obligatoire sept. 2026 = opportunité stratégique | **Critique** |
| Potentiel de croissance | Écosystème BTP + base communautaire = effet réseau puissant | 8/10 |

**Conclusion :** Docling occupe un créneau unique : extraction IA de lignes de factures fournisseurs BTP multilingues (CA/ES/FR) pour constituer une base de prix réutilisable. Aucun concurrent identifié ne fait exactement cela.

---

## 2. Risques critiques à traiter

### 2.1 BackgroundTasks sans persistance

**Problème :** FastAPI BackgroundTasks n'offre aucune persistance ni garantie d'exécution. Si le backend redémarre pendant un traitement (déploiement, crash, timeout), le job est **perdu silencieusement**. Le client croit que sa facture est en cours — elle ne sera jamais traitée.

**Solutions :**
- **Court terme (1 jour)** : Persister l'état des jobs dans Neon (table `jobs`: job_id, status, result, created_at, updated_at). Polling inchangé.
- **Moyen terme (1 semaine)** : Migrer vers Celery + Redis ou ARQ (async). Render supporte Redis.
- **Production** : Render Background Workers avec job queue.

### 2.2 Stockage S3 Storj non implémenté

**Problème :** Le bouton "Voir PDF" dans l'Historique est inutilisable. Les factures originales ne sont pas archivées. Trou fonctionnel visible dès la première semaine.

**Effort estimé :** 2-3 heures. boto3 est là, l'endpoint S3 Storj est compatible AWS SDK.

---

## 3. Choix du modèle IA — Gemini Flash

| Modèle | Précision doc. | Coût relatif | Recommandation |
|--------|----------------|--------------|----------------|
| Gemini 3 Flash (actuel) | Très bonne | 0,075$/M | ✅ Garder |
| Gemini 3 Pro | Excellente | ~2,50$/M | Cas complexes |
| GPT-4.1 Mini | Bonne | 0,40$/M | Alternative viable |
| Claude Sonnet 4.x | Excellente | ~3$/M | Trop cher |

**Recommandation :** Intégrer une option de fallback vers GPT-4.1 mini ou DeepSeek V3 si Gemini est indisponible.

**Point d'attention :** Rate limit Gemini Flash réduit (~1/3 vs génération précédente). Le sémaphore à 3 est bien calibré — surveiller les 429 en production.

---

## 4. Dette technique frontend

| Fichier | Problème | Impact | Effort |
|---------|----------|--------|--------|
| CompareModal.jsx, ValidationPage.jsx | Index comme `key` dans `.map()` | Bugs de rendu sur listes longues | 1h |
| HistoryPage, SettingsPage | Dépendances useEffect manquantes | Stale closures, rerenders inutiles | 2h |
| useStore.js | `_idCounter` global, `queueStats` non mémorisé | Performance dégradée à >50 items | 3h |
| Build | Chunks > 500 Ko | Chargement initial lent sur mobile 3G | 4h (code-split) |

---

## 5. Analyse concurrentielle

### Marché OCR/IA factures 2026

- Coût manuel : 12,88 à 19,83 €/facture
- Coût avec IA : 2,36 €/facture
- Acteurs : Koncile, Klippa, Nanonets, Rossum, Docsumo, Parseur

**Point clé :** Aucun n'extrait des lignes produits pour une base de prix matériaux. Docling est unique.

### Marché logiciels BTP France

- 500 000 entreprises BTP en France
- **Avantage Docling :** BatiChiffrage propose 80 000 prix génériques nationaux. Docling constitue les VRAIS prix payés par l'artisan à SES fournisseurs (BigMat, Discor, Guerin Roses). Infiniment plus précis pour chiffrer.

### Douleurs clients concurrents

| Douleur | Fréquence | Docling résout ? |
|---------|-----------|------------------|
| Trop cher pour petits artisans | 🔴 Très fréquent | ✅ Oui (coût API transparent) |
| Pas de scan factures fournisseurs | 🔴 Fréquent | ✅ Oui (core feature) |
| Trop complexe | 🟠 Fréquent | ✅ 5 écrans simples |
| Filigrane / pub version gratuite | 🟠 Fréquent | ✅ Absent |
| Pas de mode hors ligne chantier | 🔴 Très fréquent | ❌ Non implémenté |
| Précision OCR insuffisante | 🟡 Modéré | ✅ Gemini Vision > 95% |
| Pas de comparaison prix fournisseurs | 🟠 Fréquent | ⚠️ Prévu (CompareModal) |

---

## 6. Opportunité réglementaire — Facturation électronique 2026

**Calendrier officiel :**
- **1er septembre 2026** : Toutes les entreprises doivent pouvoir RECEVOIR des factures électroniques (Factur-X, UBL, CII)
- **1er septembre 2026** : Grandes entreprises et ETI doivent ÉMETTRE
- **1er septembre 2027** : PME, TPE et micro-entreprises doivent ÉMETTRE

**Implication :** Docling doit ingérer des fichiers Factur-X (PDF + XML embarqué). La bonne nouvelle : Gemini Vision lit le PDF. Il suffit d'extraire aussi le XML embarqué pour une précision quasi-parfaite sans IA — les données sont déjà structurées.

**Opportunité :** Se positionner comme Opérateur de Dématérialisation (OD) connecté à une PDP (Pennylane, Evoliz, Qonto — 101 certifiées en janv. 2026).

---

## 7. Roadmap recommandée

### Sprint 1 — Urgences immédiates (1 semaine)

| # | Tâche | Effort | Pourquoi urgent |
|---|-------|--------|-----------------|
| 1 | Persister les jobs en base Neon (table jobs) | 4h | Perte de données si crash backend |
| 2 | Implémenter storage_service.py S3 Storj | 3h | Bouton "Voir PDF" cassé |
| 3 | Fixer les clés index dans CompareModal et ValidationPage | 1h | Bugs silencieux sur listes |
| 4 | Ajouter circuit-breaker Gemini (après N erreurs consécutives) | 4h | File bloquée si Gemini down |

### Sprint 2-3 — Priorités hautes (1 mois)

| # | Tâche | Source | Impact |
|---|-------|--------|--------|
| 5 | Mode offline PWA : file IndexedDB + sync au retour | Douleur #1 artisans | Utilisation sur chantier |
| 6 | Support Factur-X : extraction XML embarqué | Obligation légale sept. 2026 | Précision quasi-parfaite |
| 7 | TVA, remise globale, numéro auto dans DevisPage | Analyse UI + Obat | Devis PDF professionnel |
| 8 | Migration SDK google-genai (async natif) | Audit backend | Code simplifié |

### Q2-Q3 2026 — Croissance stratégique

| # | Fonctionnalité | Modèle | Potentiel |
|---|----------------|--------|-----------|
| 9 | Base communautaire de prix géolocalisés | Freemium | Effet réseau, moat |
| 10 | Intégration PDP partenaire (Qonto/Pennylane) | Partenariat API | Conformité 2026 clé en main |
| 11 | Gemini Batch API pour watchdog | -50% coût | Watchdog rentable gros volumes |
| 12 | Comparateur prix fournisseurs avancé (graphiques) | Table prix_historique existe | Fidélisation |

---

## 8. Ce qu'il faut éviter

- **Signature électronique en interne** : coûteux (conformité eIDAS). Déléguer via Yousign/DocuSign (~0,10€/signature).
- **Bibliothèque de prix génériques** : l'avantage Docling = prix RÉELS de l'artisan, pas des prix théoriques.
- **Uvicorn multi-workers** tant que `_jobs` est en mémoire : chaque worker a sa propre instance, le polling retournerait 404. Résoudre d'abord la persistance en base.

---

## 9. SWOT

| Forces ✅ | Faiblesses ❌ |
|-----------|---------------|
| Cas d'usage unique : catalogue prix depuis factures réelles | BackgroundTasks sans persistance |
| Stack moderne (FastAPI, Neon, Gemini, PWA) | Storj S3 non implémenté |
| 104 tests passés — rare à ce stade | Aucun mode offline |
| Multilingue CA/ES/FR nativement | TVA et remise absents dans devis |
| Transparence coût API par facture | Clés instables dans listes React |
| Watchdog dossier magique = zéro friction | Pas de circuit-breaker Gemini |

| Opportunités 🚀 | Menaces ⚠️ |
|-----------------|------------|
| Facturation électronique sept. 2026 = données structurées gratuites | Google peut changer pricing/rate limits Gemini |
| 500k entreprises BTP FR, 80% sur Excel | Costructor (80k clients) pourrait ajouter scan IA |
| Base communautaire = effet réseau | Obat (4,9/5, leader) a les moyens d'intégrer GPT-4o |
| Gemini Batch API : -50% coût | BatiChiffrage (80k prix) standard ancré |
| Niche hispano-catalane non adressée | Réforme PDP complexifie l'écosystème |

---

## 10. Note finale par dimension

| Dimension | Note | Commentaire |
|-----------|------|-------------|
| Originalité du concept | 9/10 | Vide de marché réel |
| Architecture technique | 7/10 | Solide mais 2 risques critiques |
| Couverture fonctionnelle MVP | 6/10 | Core OK mais devis trop léger, PDF cassé |
| Alignement terrain BTP | 8/10 | Watchdog, multilingue, familles BTP = bien compris |
| Préparation production | 5/10 | Jobs mémoire, S3 absent = pas prêt pour scale |
| Potentiel 12 mois | 8/10 | Conformité 2026 + offline + base communautaire |

---

## 11. Améliorations UX détaillées (par écran)

### Scanner
- Message quand file vide
- Indicateur progression globale plus visible
- Vibration/son confirmation mobile

### Catalogue
- Tri par prix, date, fournisseur
- Alertes changement de prix

### Priorité basse (backlog)
- Historique des prix (graphiques, table `prix_historique` existe)
- Bibliothèque de prix (tarifs de référence type Batichiffrage)
- Favoris produits
- Recherche/filtres Historique (date, statut, fournisseur)

### Backend (pistes futures)
- **aiometer** : rate limiting plus fin que le sémaphore actuel
- **Tests E2E** : Playwright ou Cypress pour tests navigateur

---

## 12. Contexte écosystème BTP

Docling/INVOIX fait partie d'un écosystème plus large :
1. Secrétaire IA (qualification appels)
2. Annuaires clients intelligents
3. Réseau B2B Artisans
4. **INVOIX OCR + Base communautaire** ← ce projet
5. Entreprises de route
6. Uber Matos (livraison matériel)
7. Évacuation déchets
8. Annuaire Pro BTP
9. Allez-Market
10. Promotions fournisseurs

Docling est le cœur catalogue + extraction. Les autres produits s'appuient sur ce socle.

---

**Conclusion d'expert :** Docling Agent a la bonne idée au bon moment. Le calendrier réglementaire français (facturation électronique sept. 2026) va forcer 500 000 artisans BTP à se moderniser. Aucun outil existant ne fait ce que fait Docling. Les deux chantiers techniques à traiter immédiatement (persistance jobs + S3) sont rapides à implémenter et non-négociables avant tout déploiement terrain.

---

*Source : Rapport d'expert indépendant — Février 2026*
