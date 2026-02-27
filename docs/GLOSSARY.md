# Glossaire — Docling

Termes clés du projet (métier BTP, technique, IA).

---

## Métier BTP

| Terme | Définition |
|-------|-------------|
| **BTP** | Bâtiment et Travaux Publics |
| **Devis** | Document chiffré proposé au client avant travaux |
| **Facture fournisseur** | Document émis par un fournisseur (BigMat, Discor, etc.) |
| **Famille BTP** | Catégorie produit : Maçonnerie, Plomberie, Carrelage, Électricité, etc. |
| **Base de prix** | Catalogue de produits avec prix unitaires pour chiffrage |
| **IVA / TVA** | Impôt sur la valeur ajoutée (21 % en Espagne/Catalogne) |

---

## Technique Docling

| Terme | Définition |
|-------|-------------|
| **Orchestrator** | Pipeline backend : prétraitement → Gemini → validation → DB |
| **Dossier magique** | Dossier surveillé (watchdog) pour dépôt automatique de factures |
| **Upsert** | Insert ou update selon clé (désignation + user_id) |
| **Batch save** | Enregistrement groupé des produits validés |
| **PWA** | Progressive Web App — installable, offline-ready |

---

## IA & Services

| Terme | Définition |
|-------|-------------|
| **Gemini 3 Flash** | Modèle Google (vision multimodale) pour extraction factures |
| **CLAHE** | Contraste adaptatif (OpenCV) pour améliorer photos |
| **Confidence score** | high/low — fiabilité arithmétique d'une ligne extraite |
| **Agent Skill** | Format agentskills.io — instructions pour agents IA |

---

## Infrastructure

| Terme | Définition |
|-------|-------------|
| **Neon** | PostgreSQL serverless (cloud) |
| **Pooler** | PgBouncer — connexions poolées (URL `-pooler`) |
| **Render** | Hébergement backend (Procfile) |
| **Netlify** | Hébergement frontend (build `dist/`) |
| **Storj** | Stockage S3-compatible (archivage PDF) |
