# Guide des services et réglages — Docling Agent

**Version simplifiée pour les non-développeurs**

---

## 🧩 Les 6 services du backend

### 1. **L’intelligence artificielle (Gemini)**
**Rôle** : Lit les factures (PDF ou photos) et en extrait les produits (nom, prix, fournisseur, etc.).

**Détails** :
- Utilise l’IA Google Gemini
- Comprend le catalan, l’espagnol et le français
- 3 modèles possibles : Flash (rapide), Pro (plus précis), 2.5 Flash (stable)

---

### 2. **La base de données (Neon)**
**Rôle** : Stocke tout ce que l’app enregistre : produits, factures, historique.

**Détails** :
- Base PostgreSQL hébergée sur Neon (cloud)
- Conserve le catalogue produits, l’historique des factures et les statistiques

---

### 3. **Le stockage cloud (Storj)**
**Rôle** : Enregistre les PDF des factures dans le cloud pour pouvoir les consulter plus tard.

**Détails** :
- Compatible S3 (Storj, R2, MinIO)
- Optionnel : si non configuré, les factures sont traitées mais pas archivées en ligne

---

### 4. **Le dossier magique (Watchdog)**
**Rôle** : Surveille un dossier sur ton PC. Dès qu’un PDF ou une image y est déposé, il est traité automatiquement.

**Détails** :
- Dossier par défaut : `Docling_Factures`
- Les fichiers traités vont dans `Traitees`, les erreurs dans `Erreurs`
- Peut être désactivé si tu préfères tout faire via l’app

---

### 5. **Le prétraitement des images**
**Rôle** : Améliore les photos de factures (contraste, netteté) avant de les envoyer à l’IA.

**Détails** :
- Utilisé uniquement pour les photos (pas les PDF)
- Utilise OpenCV

---

### 6. **L’authentification (JWT)**
**Rôle** : Gère la connexion des utilisateurs (login, mots de passe, droits).

**Détails** :
- Préparé pour une utilisation multi-utilisateurs
- Protège certaines actions (ex. vider le catalogue)

---

## ⚙️ Les réglages (fichier .env)

### Obligatoires

| Réglage | À quoi ça sert |
|--------|----------------|
| **GEMINI_API_KEY** | Clé pour utiliser l’IA Google. À créer sur [aistudio.google.com](https://aistudio.google.com). |
| **DATABASE_URL** | Adresse de ta base de données Neon. Format : `postgresql://user:motdepasse@serveur.neon.tech/nom_base?sslmode=require` |

---

### Optionnels

| Réglage | À quoi ça sert | Valeur par défaut |
|--------|----------------|-------------------|
| **DEFAULT_AI_MODEL** | Modèle d’IA utilisé par défaut | `gemini-3-flash-preview` |
| **WATCHDOG_FOLDER** | Dossier surveillé pour le traitement automatique | `./Docling_Factures` |
| **WATCHDOG_ENABLED** | Activer ou désactiver le dossier magique | `true` |
| **STORJ_BUCKET** | Nom du « compartiment » cloud pour les PDF | `docling-factures` |
| **STORJ_ACCESS_KEY** | Clé d’accès au stockage cloud | (vide = stockage désactivé) |
| **STORJ_SECRET_KEY** | Mot de passe secret du stockage cloud | (vide = stockage désactivé) |
| **STORJ_ENDPOINT** | Adresse du service de stockage | `https://gateway.storjshare.io` |
| **PWA_URL** | Adresse de ton app en ligne (ex. Netlify) | (vide) |
| **JWT_SECRET** | Clé secrète pour les connexions utilisateurs | (valeur par défaut en dev) |
| **JWT_EXPIRY_HOURS** | Durée de validité d’une session (en heures) | `24` |

---

## 📋 Résumé visuel

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCLING AGENT BACKEND                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📤 Tu envoies une facture (app ou dossier magique)        │
│                          │                                  │
│                          ▼                                  │
│   🖼️ Prétraitement image (si photo)                         │
│                          │                                  │
│                          ▼                                  │
│   🤖 IA Gemini → extrait les produits                       │
│                          │                                  │
│                          ▼                                  │
│   💾 Base de données Neon → enregistre les produits          │
│                          │                                  │
│                          ▼                                  │
│   ☁️ Stockage cloud (optionnel) → archive le PDF            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Que configurer selon ton usage ?

| Cas d’usage | À configurer |
|-------------|--------------|
| **Test rapide** | GEMINI_API_KEY + DATABASE_URL |
| **Usage quotidien** | Idem + éventuellement le stockage cloud |
| **Dossier magique** | WATCHDOG_FOLDER (ou laisser par défaut) |
| **App en ligne** | PWA_URL + JWT_SECRET (pour la prod) |
