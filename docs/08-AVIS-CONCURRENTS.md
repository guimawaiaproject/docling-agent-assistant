# Avis clients des concurrents — Points manquants relevés

*Recherche web réalisée sur CamScanner, Adobe Scan, Expensify, QuickBooks, Obat, Costructor et logiciels BTP (2024-2026). À intégrer ou consulter avec [07-ANALYSE-UI.md](07-ANALYSE-UI.md).*

---

## Ce que les utilisateurs reprochent aux concurrents

| Concurrent | Problèmes signalés |
|------------|--------------------|
| **CamScanner** | Publicités, filigrane sur la version gratuite, pas d'OCR en gratuit, cloud limité. Les utilisateurs cherchent des alternatives sans pub. |
| **Adobe Scan** | Coût de l'abonnement. Beaucoup d'utilisateurs se tournent vers des solutions gratuites (Google Drive, Microsoft Lens). |
| **Expensify** | Version gratuite : seulement 10 scans par mois. ~6 % d'avis négatifs (1-2 étoiles). |
| **QuickBooks** | Pas de scan de factures natif. Limite de 90 jours pour connecter les écritures. |
| **Obat (BTP)** | Prix élevés (25 à 79 €/mois). |
| **Logiciels BTP** | Complexité pour les petits artisans. Manque de version gratuite ou d'essai long. |

---

## Ce que les utilisateurs attendent (attentes clients)

### Pour le scan / extraction
- **Mode hors ligne** : pouvoir scanner sur chantier sans connexion, puis synchroniser plus tard (Veryfi, Smart Invoice Extract le proposent).
- **Pas de filigrane** : documents propres sans marque sur les PDF.
- **Précision** : taux de reconnaissance > 90 % (référence : ONexpense).
- **Multilingue** : factures en catalan, espagnol, français (déjà présent dans Docling).
- **Traitement par lot** : upload groupé, pas seulement fichier par fichier (Docling le fait déjà).

### Pour le catalogue
- **Comparaison fournisseurs** : comme BâtiCOMPARE, TARIFEO — comparer les prix d'un même produit chez plusieurs fournisseurs.
- **Historique des prix** : voir l'évolution des prix dans le temps (Docling a `prix_historique` en base).
- **Bibliothèque de prix** : accès à des tarifs de référence (Batichiffrage chez Obat).

### Pour les devis / factures
- **Signature électronique** : demandée par les artisans (Obat, Costructor le proposent).
- **Conformité 2026** : facturation électronique obligatoire en France (sept. 2026 grandes entreprises, sept. 2027 PME) — format structuré, pas seulement PDF par email.
- **Suivi des paiements** : alertes impayés, rappels.
- **Gain de temps** : 2-3 min par devis au lieu de 20-30 min (objectif des artisans).
- **Mentions légales** : TVA, mentions obligatoires générées automatiquement.

### Pour l'usage terrain
- **Accès mobile et hors ligne** : travailler depuis le chantier.
- **Simplicité** : interface intuitive pour des utilisateurs peu à l'aise avec l'informatique.
- **Version gratuite** : essai ou plan gratuit pour les petits volumes (Costructor : 0 €, 15 €/mois).

---

## Points où Docling est déjà en avance

- ✅ Extraction multilingue (CA/ES/FR).
- ✅ Sélection de dossier récursive.
- ✅ Transparence sur le coût API.
- ✅ Dossier magique (automatisation).
- ✅ Catalogue alimenté par les factures scannées.
- ✅ Export CSV/Excel.
- ✅ Choix du modèle IA (vitesse vs précision).

---

## Points à prioriser selon les avis clients

| Priorité | Fonctionnalité | Source |
|----------|----------------|--------|
| 🔴 Haute | Mode hors ligne (scan + file d'attente, sync au retour) | Veryfi, Smart Invoice Extract, attentes artisans |
| 🔴 Haute | Conformité facturation électronique 2026 | Obligation légale France |
| 🟠 Moyenne | Signature électronique sur devis | Obat, Costructor, artisans |
| 🟠 Moyenne | Comparaison de prix entre fournisseurs | BâtiCOMPARE, TARIFEO |
| 🟠 Moyenne | Suivi des paiements / alertes impayés | Artisans BTP |
| 🟡 Basse | Historique des prix (graphiques) | Catalogue BTP |
| 🟡 Basse | Bibliothèque de prix de référence | Obat Batichiffrage |

---

*Document complémentaire à [07-ANALYSE-UI.md](07-ANALYSE-UI.md) — Fév. 2026*
