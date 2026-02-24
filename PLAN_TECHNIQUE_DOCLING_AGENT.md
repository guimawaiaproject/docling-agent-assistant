# PLAN TECHNIQUE — DOCLING AGENT ASSISTANT v3
## Prompt Engineer pour Google Antigravity / Gemini 3 Flash

---

## CONTEXTE DU PROJET EXISTANT

**Repo GitHub :** https://github.com/guimawaiaproject/docling-agent-assistant

**Stack actuelle :**
- Frontend : Streamlit (app.py)
- Backend : FastAPI (api.py) — localhost:8000
- IA : Google Gemini 2.5 Flash (gemini_service.py)
- BDD : SQLite local → migré PostgreSQL Neon (db_manager.py)
- Orchestration : orchestrator.py + BackgroundTasks FastAPI
- Schémas : Pydantic (backend/schemas/invoice.py)
- Nouveau Watchdog PC : Script compagnon transparent (pc_sync.exe) avec envoi HTTP vers backend Cloud
- Docker : Dockerfile + docker-compose.yml
- CI/CD : .github/workflows/

**Données actuelles :**
- 241 produits en base
- Fournisseurs BTP franco-espagnols/catalans (BigMat, Discor, etc.)
- Champs : fournisseur, designation_raw (Català/ES), designation_fr, famille BTP, unité, prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21, n°facture, date_facture
- Clé unique anti-doublon : (designation_raw, fournisseur)
- Export CSV + Excel fonctionnel

**Objectif final (Format distribution "Utilisateur Lambda") :**
Application Cloud usage solo, structurée pour être installée très facilement par l'utilisateur final :
1. Sur PC (Le Compagnon) : L'utilisateur lance un simple exécutable `pc_sync.exe` configuré. Il glisse-dépose un PDF facture dans un dossier local → extraction auto vers le cloud → catalogue.
2. Sur mobile (La PWA Cloud) : L'utilisateur installe la PWA depuis son navigateur → photo facture → extraction → validation → catalogue.
3. Base de données cloud (Neon) intégrée de manière transparente, accessible de partout (PC et Mobile).
4. Futur module : génération de devis depuis le catalogue.

---

## PILIER 1 — UPGRADE IA (gemini_service.py)

### 1.1 — Migration Gemini 2.5 Flash → Gemini 3 Flash

**Fichier cible :** `backend/services/gemini_service.py`

```python
# AVANT
MODEL_NAME = "gemini-2.5-flash-preview"

# APRÈS
MODEL_NAME = "gemini-3-flash"
```

**Dépendance :** Mettre à jour `requirements.txt`
```
google-generativeai>=0.8.0
```

---

### 1.2 — Activer Code Execution (Agentic Vision)

Gemini 3 Flash peut maintenant vérifier son propre travail arithmétiquement.
Modifier la configuration du modèle dans `gemini_service.py` :

```python
import google.generativeai as genai

model = genai.GenerativeModel(
    model_name="gemini-3-flash",
    tools="code_execution",  # Active la vérification arithmétique
    generation_config=genai.GenerationConfig(
        temperature=0.1,
        response_mime_type="application/json"
    )
)
```

**Objectif :** Le modèle recalcule `prix_remise_ht * 1.21` et compare avec `prix_ttc_iva21` extrait. Si différence > 2% → flag `confidence: "low"` dans le JSON retourné.

---

### 1.3 — Améliorer le prompt système dans gemini_service.py

**Prompt actuel :** Expert comptable BTP, extraction JSON.

**Nouveau prompt à implémenter :**

```python
SYSTEM_PROMPT = """
Tu es un expert comptable BTP spécialisé dans les factures franco-espagnoles et catalanes.

MISSION : Extraire TOUTES les lignes produit de cette facture et retourner un JSON valide.

RÈGLES STRICTES :
1. Extraire chaque ligne produit individuellement, même si la facture en contient 50+
2. Traduire designation_raw (Català/Español) → designation_fr (Français professionnel BTP)
3. Classifier famille parmi : Armature, Cloison, Climatisation, Plomberie, Électricité,
   Menuiserie, Couverture, Carrelage, Isolation, Peinture, Outillage, Consommable, Autre
4. Vérifier : prix_remise_ht = prix_brut_ht * (1 - remise_pct/100)
5. Vérifier : prix_ttc_iva21 = prix_remise_ht * 1.21
6. Si une vérification échoue → ajouter "confidence": "low" sur la ligne concernée
7. Si un champ est illisible → mettre null, jamais inventer

FORMAT JSON OBLIGATOIRE :
{
  "fournisseur": "string",
  "numero_facture": "string",
  "date_facture": "DD/MM/YYYY",
  "produits": [
    {
      "designation_raw": "string",
      "designation_fr": "string",
      "famille": "string",
      "unite": "string (sac|kg|m²|ml|unité|litre|rouleau)",
      "prix_brut_ht": float,
      "remise_pct": float,
      "prix_remise_ht": float,
      "prix_ttc_iva21": float,
      "confidence": "high|low"
    }
  ],
  "total_ht": float,
  "total_ttc": float
}

Retourne UNIQUEMENT le JSON, sans markdown, sans commentaire.
"""
```

---

### 1.4 — Ajouter prétraitement image (pour photos mobiles floues)

**Nouveau fichier :** `backend/services/image_preprocessor.py`

```python
import cv2
import numpy as np
from PIL import Image
import io

def preprocess_invoice_image(image_bytes: bytes) -> bytes:
    """
    Améliore la qualité d'une photo de facture mobile avant envoi à Gemini.
    - Correction contraste
    - Débruitage
    - Conversion WebP optimisé
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Débruitage
    img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # Amélioration contraste CLAHE
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    img = cv2.merge((l, a, b))
    img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)

    # Encode WebP qualité 85
    _, buffer = cv2.imencode('.webp', img, [cv2.IMWRITE_WEBP_QUALITY, 85])
    return buffer.tobytes()
```

**Intégration dans orchestrator.py :**
```python
from backend.services.image_preprocessor import preprocess_invoice_image

# Avant l'appel Gemini, si le fichier est une image (JPG/PNG/WebP) :
if file_extension in ['.jpg', '.jpeg', '.png', '.webp']:
    file_bytes = preprocess_invoice_image(file_bytes)
```

**Dépendance à ajouter dans requirements.txt :**
```
opencv-python-headless>=4.9.0
Pillow>=10.0.0
```

---

## PILIER 2 — BASE DE DONNÉES (Neon PostgreSQL)

### 2.1 — Neon reste le meilleur choix (verdict confirmé 2026)

Neon est serverless, scale-to-zero, PostgreSQL natif, acquis par Databricks pour ~1Md$.
Supabase = overkill (auth/storage inutiles pour usage solo).
Turso = SQLite distribué, schéma différent, migration complexe.

**→ Garder Neon, optimiser le schéma.**

---

### 2.2 — Migration schéma SQLite → PostgreSQL Neon optimisé

**Fichier cible :** `backend/core/db_manager.py`

**Schéma SQL complet à appliquer sur Neon :**

```sql
-- Extension vectorielle pour futur module devis IA
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- Recherche textuelle rapide

-- Table fournisseurs
CREATE TABLE IF NOT EXISTS fournisseurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) UNIQUE NOT NULL,
    pays VARCHAR(50) DEFAULT 'ES',
    langue VARCHAR(20) DEFAULT 'ca', -- ca=catalan, es=espagnol, fr=français
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table produits (remplace la table SQLite actuelle)
CREATE TABLE IF NOT EXISTS produits (
    id SERIAL PRIMARY KEY,
    fournisseur_id INTEGER REFERENCES fournisseurs(id),
    fournisseur VARCHAR(200) NOT NULL, -- dénormalisé pour perf
    designation_raw TEXT NOT NULL,
    designation_fr TEXT NOT NULL,
    famille VARCHAR(100),
    unite VARCHAR(50),
    prix_brut_ht NUMERIC(10,4),
    remise_pct NUMERIC(5,2) DEFAULT 0,
    prix_remise_ht NUMERIC(10,4),
    prix_ttc_iva21 NUMERIC(10,4),
    numero_facture VARCHAR(100),
    date_facture DATE,
    confidence VARCHAR(10) DEFAULT 'high',
    -- Vecteur pour recherche sémantique future (module devis)
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Clé unique anti-doublon (identique à l'actuel SQLite)
    UNIQUE(designation_raw, fournisseur)
);

-- Table factures (historique des fichiers traités)
CREATE TABLE IF NOT EXISTS factures (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500),
    storage_url TEXT, -- URL Storj/cloud future
    statut VARCHAR(20) DEFAULT 'traite', -- traite|erreur|en_cours
    nb_produits_extraits INTEGER DEFAULT 0,
    cout_api_usd NUMERIC(8,6) DEFAULT 0,
    source VARCHAR(20) DEFAULT 'pc', -- pc|mobile
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index performances
CREATE INDEX IF NOT EXISTS idx_produits_famille ON produits(famille);
CREATE INDEX IF NOT EXISTS idx_produits_fournisseur ON produits(fournisseur);
CREATE INDEX IF NOT EXISTS idx_produits_designation_trgm
    ON produits USING GIN (designation_fr gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_produits_updated ON produits(updated_at DESC);
```

---

### 2.3 — Réécrire db_manager.py avec asyncpg (performances)

**Fichier :** `backend/core/db_manager.py`

```python
import asyncpg
import os
from typing import Optional
import logging

DATABASE_URL = os.getenv("DATABASE_URL")  # URL Neon depuis .env

class DBManager:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
        return cls._pool

    @classmethod
    async def upsert_product(cls, product: dict) -> bool:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO produits
                    (fournisseur, designation_raw, designation_fr, famille, unite,
                     prix_brut_ht, remise_pct, prix_remise_ht, prix_ttc_iva21,
                     numero_facture, date_facture, confidence)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
                ON CONFLICT (designation_raw, fournisseur)
                DO UPDATE SET
                    designation_fr = EXCLUDED.designation_fr,
                    famille = EXCLUDED.famille,
                    prix_brut_ht = EXCLUDED.prix_brut_ht,
                    remise_pct = EXCLUDED.remise_pct,
                    prix_remise_ht = EXCLUDED.prix_remise_ht,
                    prix_ttc_iva21 = EXCLUDED.prix_ttc_iva21,
                    updated_at = NOW()
            """,
            product['fournisseur'], product['designation_raw'],
            product['designation_fr'], product['famille'],
            product['unite'], product['prix_brut_ht'],
            product['remise_pct'], product['prix_remise_ht'],
            product['prix_ttc_iva21'], product['numero_facture'],
            product['date_facture'], product.get('confidence', 'high'))
        return True

    @classmethod
    async def get_catalogue(cls, famille=None, fournisseur=None, search=None) -> list:
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            query = """
                SELECT * FROM produits
                WHERE ($1::text IS NULL OR famille = $1)
                AND ($2::text IS NULL OR fournisseur ILIKE $2)
                AND ($3::text IS NULL OR designation_fr ILIKE $3)
                ORDER BY updated_at DESC
            """
            rows = await conn.fetch(
                query, famille,
                f"%{fournisseur}%" if fournisseur else None,
                f"%{search}%" if search else None
            )
            return [dict(r) for r in rows]
```

**Dépendance :**
```
asyncpg>=0.29.0
```

---

### 2.4 — Variables d'environnement (.env)

```env
# Neon PostgreSQL
DATABASE_URL=postgresql://user:password@ep-xxx.eu-west-1.aws.neon.tech/neondb?sslmode=require

# Gemini
GEMINI_API_KEY=AIza...

# Storage futur (optionnel phase 2)
STORJ_ACCESS_KEY=
STORJ_SECRET_KEY=
STORJ_BUCKET=docling-factures
```

---
## PILIER 3 — PWA (Progressive Web App) — REMPLACE STREAMLIT

### 3.1 — Stratégie : Vite + React + PWA

**Pourquoi PWA et pas Flutter/React Native :**
- Pas d'app store → installation directe depuis navigateur mobile (Chrome/Safari)
- Un seul codebase pour PC et mobile
- Accès caméra natif via `MediaDevices API` (Chrome Android + Safari iOS 16.4+)
- Déployable gratuitement sur Netlify
- Remplace complètement Streamlit (plus rapide, responsive, offline-ready)
- Antigravity + Gemini génère du React/JSX facilement

**Résultat final :** URL unique `https://docling-agent.netlify.app`
- PC : catalogue + drag-and-drop PDF
- Mobile : "Ajouter à l'écran d'accueil" → icône app, accès caméra natif

---

### 3.2 — Structure projet PWA

```
docling-pwa/
├── public/
│   ├── manifest.json              # Config PWA (icône, nom, couleurs)
│   └── icons/                     # icon-192.png, icon-512.png
├── src/
│   ├── main.jsx
│   ├── App.jsx                    # Router + layout
│   ├── config/
│   │   └── api.js                 # URL FastAPI Railway
│   ├── services/
│   │   ├── apiService.js          # Appels axios vers FastAPI
│   │   └── imageService.js        # Compression WebP avant upload
│   ├── components/
│   │   └── Navbar.jsx             # Navigation bas (mobile) / haut (PC)
│   └── pages/
│       ├── ScanPage.jsx           # Caméra + upload + polling
│       ├── ValidationPage.jsx     # Vérification données extraites
│       └── CataloguePage.jsx      # Liste produits + filtres
├── vite.config.js
├── package.json
└── netlify.toml
```

---

### 3.3 — package.json

```json
{
  "name": "docling-pwa",
  "private": true,
  "version": "3.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.22.0",
    "axios": "^1.6.7"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.1.4",
    "vite-plugin-pwa": "^0.19.2",
    "workbox-window": "^7.0.0",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35"
  }
}
```

---

### 3.4 — vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/*.png'],
      manifest: {
        name: 'Docling Agent BTP',
        short_name: 'Docling',
        description: 'Scanner de factures fournisseurs BTP',
        theme_color: '#1a1a2e',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        runtimeCaching: [{
          urlPattern: /\/api\/v1\/catalogue/,
          handler: 'StaleWhileRevalidate',
          options: { cacheName: 'catalogue-cache', expiration: { maxAgeSeconds: 3600 } }
        }]
      }
    })
  ],
  server: {
    https: true,   // OBLIGATOIRE pour accès caméra en dev local
    host: true     // Accessible depuis mobile sur même réseau WiFi
  }
})
```

---

### 3.5 — config/api.js

```javascript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const ENDPOINTS = {
  process:   `${API_BASE_URL}/api/v1/invoices/process`,
  status:    (jobId) => `${API_BASE_URL}/api/v1/invoices/status/${jobId}`,
  catalogue: `${API_BASE_URL}/api/v1/catalogue`,
  batch:     `${API_BASE_URL}/api/v1/catalogue/batch`,
}
```

**`.env.local` (dev) :**
```
VITE_API_URL=http://localhost:8000
```

**`.env.production` (Netlify) :**
```
VITE_API_URL=https://docling-agent-xxxx.railway.app
```

---

### 3.6 — services/imageService.js

```javascript
/**
 * Compresse image capturée en WebP avant upload FastAPI.
 * Réduit taille 70-80% sans perte visible sur factures.
 */
export async function compressToWebP(imageFile, quality = 0.85) {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const img = new Image()
    const url = URL.createObjectURL(imageFile)

    img.onload = () => {
      const maxSize = 2000
      let { width, height } = img
      if (width > maxSize || height > maxSize) {
        const ratio = Math.min(maxSize / width, maxSize / height)
        width = Math.round(width * ratio)
        height = Math.round(height * ratio)
      }
      canvas.width = width
      canvas.height = height
      canvas.getContext('2d').drawImage(img, 0, 0, width, height)
      canvas.toBlob(
        (blob) => { URL.revokeObjectURL(url); resolve(new File([blob], 'facture.webp', { type: 'image/webp' })) },
        'image/webp', quality
      )
    }
    img.src = url
  })
}
```

---

### 3.7 — pages/ScanPage.jsx

```jsx
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ENDPOINTS } from '../config/api'
import { compressToWebP } from '../services/imageService'

export default function ScanPage() {
  const navigate = useNavigate()
  const inputRef = useRef()
  const [status, setStatus] = useState('idle')
  const [progress, setProgress] = useState('')

  const handleFile = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setStatus('uploading')
    setProgress('Compression en cours...')
    const toUpload = file.type.startsWith('image/') ? await compressToWebP(file) : file
    setProgress('Envoi vers le serveur...')
    await uploadAndPoll(toUpload, file)
  }

  const uploadAndPoll = async (file, originalFile) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await axios.post(ENDPOINTS.process, formData)
    const jobId = data.job_id
    setStatus('processing')
    setProgress('Gemini analyse la facture...')
    const interval = setInterval(async () => {
      const { data: s } = await axios.get(ENDPOINTS.status(jobId))
      if (s.status === 'completed') {
        clearInterval(interval)
        navigate('/validation', { state: { result: s.result, fileUrl: URL.createObjectURL(originalFile) } })
      } else if (s.status === 'error') {
        clearInterval(interval)
        setStatus('error')
        setProgress(`Erreur : ${s.error}`)
      }
    }, 1500)
  }

  const openCamera = () => {
    inputRef.current.accept = 'image/*'
    inputRef.current.setAttribute('capture', 'environment')
    inputRef.current.click()
  }

  const openFile = () => {
    inputRef.current.accept = '.pdf,image/*'
    inputRef.current.removeAttribute('capture')
    inputRef.current.click()
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 gap-6 pb-24">
      <h1 className="text-2xl font-bold text-gray-800">Scanner une facture</h1>
      <button onClick={openCamera}
        className="w-full max-w-sm py-6 bg-green-600 text-white rounded-2xl text-xl font-semibold shadow-lg active:scale-95 transition-transform">
        📷 Prendre en photo
      </button>
      <button onClick={openFile}
        className="w-full max-w-sm py-4 bg-blue-600 text-white rounded-2xl text-lg font-semibold shadow active:scale-95 transition-transform">
        📄 Choisir PDF / fichier
      </button>
      <input ref={inputRef} type="file" className="hidden" onChange={handleFile} />
      {status !== 'idle' && (
        <div className="flex flex-col items-center gap-3 mt-4">
          {status === 'processing' && <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />}
          <p className="text-gray-600 text-center">{progress}</p>
        </div>
      )}
    </div>
  )
}
```

---

### 3.8 — pages/ValidationPage.jsx

```jsx
import { useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import axios from 'axios'
import { ENDPOINTS } from '../config/api'

const FAMILLES = ['Armature','Cloison','Climatisation','Plomberie','Électricité',
  'Menuiserie','Couverture','Carrelage','Isolation','Peinture','Outillage','Consommable','Autre']

export default function ValidationPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [products, setProducts] = useState(state.result.produits)

  const update = (i, field, val) =>
    setProducts(prev => prev.map((p, idx) => idx === i ? { ...p, [field]: val } : p))

  const handleValidate = async () => {
    await axios.post(ENDPOINTS.batch, { produits: products })
    navigate('/catalogue')
  }

  return (
    <div className="p-4 pb-24">
      <h1 className="text-xl font-bold mb-3">Vérification — {products.length} produits</h1>
      {state.fileUrl && <img src={state.fileUrl} alt="Facture" className="w-full max-h-48 object-contain rounded-xl mb-4 border" />}
      <div className="space-y-3">
        {products.map((p, i) => (
          <div key={i} className={`p-3 rounded-xl border-2 ${p.confidence === 'low' ? 'border-orange-400 bg-orange-50' : 'border-gray-200 bg-white'}`}>
            {p.confidence === 'low' && <span className="text-xs bg-orange-500 text-white px-2 py-0.5 rounded-full mb-2 inline-block">⚠️ Vérifier</span>}
            <input value={p.designation_fr} onChange={e => update(i, 'designation_fr', e.target.value)}
              className="w-full font-medium border-b mb-2 pb-1 focus:outline-none focus:border-blue-500 bg-transparent" />
            <div className="grid grid-cols-2 gap-2 text-sm">
              <select value={p.famille} onChange={e => update(i, 'famille', e.target.value)} className="border rounded-lg p-1">
                {FAMILLES.map(f => <option key={f}>{f}</option>)}
              </select>
              <input type="number" value={p.prix_remise_ht} onChange={e => update(i, 'prix_remise_ht', parseFloat(e.target.value))}
                className="border rounded-lg p-1" placeholder="Prix HT" />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              TTC IVA21%: <strong>{(p.prix_remise_ht * 1.21).toFixed(4)} €</strong> | {p.unite} | {p.fournisseur}
            </p>
          </div>
        ))}
      </div>
      <button onClick={handleValidate}
        className="w-full mt-6 py-4 bg-green-600 text-white rounded-2xl text-lg font-semibold sticky bottom-20">
        ✅ Valider et enregistrer ({products.length} produits)
      </button>
    </div>
  )
}
```

---

### 3.9 — pages/CataloguePage.jsx

```jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import { ENDPOINTS } from '../config/api'

const FAMILLES = ['Toutes','Armature','Cloison','Climatisation','Plomberie',
  'Électricité','Menuiserie','Couverture','Carrelage','Isolation','Peinture','Outillage','Consommable','Autre']

export default function CataloguePage() {
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState('')
  const [famille, setFamille] = useState('Toutes')
  const [loading, setLoading] = useState(true)

  useEffect(() => { fetchCatalogue() }, [search, famille])

  const fetchCatalogue = async () => {
    setLoading(true)
    const params = {}
    if (search) params.search = search
    if (famille !== 'Toutes') params.famille = famille
    const { data } = await axios.get(ENDPOINTS.catalogue, { params })
    setProducts(data)
    setLoading(false)
  }

  return (
    <div className="p-4 pb-24">
      <h1 className="text-xl font-bold mb-4">📦 Catalogue ({products.length})</h1>
      <input value={search} onChange={e => setSearch(e.target.value)}
        placeholder="Rechercher ciment, treillis..."
        className="w-full border rounded-xl p-3 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-400" />
      <select value={famille} onChange={e => setFamille(e.target.value)}
        className="w-full border rounded-xl p-3 mb-4">
        {FAMILLES.map(f => <option key={f}>{f}</option>)}
      </select>
      {loading
        ? <div className="flex justify-center pt-10"><div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>
        : <div className="space-y-2">
            {products.map((p) => (
              <div key={p.id} className="p-3 border rounded-xl bg-white shadow-sm">
                <div className="flex justify-between items-start">
                  <p className="font-medium text-sm flex-1 pr-2">{p.designation_fr}</p>
                  <span className="text-green-700 font-bold text-sm whitespace-nowrap">{p.prix_remise_ht} €/{p.unite}</span>
                </div>
                <div className="flex gap-2 mt-1">
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{p.famille}</span>
                  <span className="text-xs text-gray-400">{p.fournisseur}</span>
                </div>
              </div>
            ))}
          </div>
      }
    </div>
  )
}
```

---

### 3.10 — components/Navbar.jsx

```jsx
import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-3 z-50 shadow-lg">
      <NavLink to="/scan" className={({ isActive }) =>
        `flex flex-col items-center ${isActive ? 'text-green-600' : 'text-gray-400'}`}>
        <span className="text-2xl">📷</span>
        <span className="text-xs mt-0.5">Scanner</span>
      </NavLink>
      <NavLink to="/catalogue" className={({ isActive }) =>
        `flex flex-col items-center ${isActive ? 'text-blue-600' : 'text-gray-400'}`}>
        <span className="text-2xl">📦</span>
        <span className="text-xs mt-0.5">Catalogue</span>
      </NavLink>
    </nav>
  )
}
```

---

### 3.11 — netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "20"
```

---

### 3.12 — Déploiement Netlify

```bash
npm install -g netlify-cli
npm run build
netlify deploy --prod --dir=dist

# Sur Netlify Dashboard → Environment variables :
# VITE_API_URL = https://docling-agent-xxxx.railway.app
```

**Sur mobile :** Chrome → ouvrir URL → menu ⋮ → "Ajouter à l'écran d'accueil" → installée comme vraie app.

---

## PILIER 4 — COMPAGNON PC (SYNCHRONISATION DOSSIER LAMBDA)

Pour offrir une expérience "Grand Public" sous PC (Windows/Mac) : l'utilisateur dépose juste un fichier dans un dossier, et le système s'occupe du reste.

### 4.1 — Le script Watchdog Local (`pc_sync.py`)
Ce script indépendant tourne sur le PC de l'utilisateur. Il surveille un dossier local (ex: `C:\\Docling_Factures\\A_Traiter`). Dès qu'un PDF est glissé, il fait une requête POST HTTPS directement vers l'API Railway, puis déplace le fichier dans `Docling_Factures\\Traitees`.

**Script (`backend/pc_sync.py`) :**
```python
import time
import os
import shutil
import httpx
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

API_URL = "https://docling-agent-xxxx.railway.app/api/v1/invoices/process"
BASE_DIR = os.path.join(os.path.expanduser("~"), "Docling_Factures")
FOLDER_TO_WATCH = os.path.join(BASE_DIR, "A_Traiter")
FOLDER_DONE = os.path.join(BASE_DIR, "Traitees")

os.makedirs(FOLDER_TO_WATCH, exist_ok=True)
os.makedirs(FOLDER_DONE, exist_ok=True)

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            print(f"📄 Nouveau fichier détecté : {event.src_path}")
            time.sleep(2) # Attendre la fin de copie fichier
            try:
                with open(event.src_path, "rb") as f:
                    response = httpx.post(API_URL, files={"file": f}, timeout=120.0)
                if response.status_code == 200:
                    print("✅ Fichier envoyé et traité avec succès !")
                    shutil.move(event.src_path, os.path.join(FOLDER_DONE, os.path.basename(event.src_path)))
                else:
                    print("❌ Erreur de traitement API", response.text)
            except Exception as e:
                print(f"⚠️ Erreur de connexion : {e}")

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(PDFHandler(), FOLDER_TO_WATCH, recursive=False)
    observer.start()
    print(f"👁️ Surveillance active sur : {FOLDER_TO_WATCH}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

### 4.2 — Création de l'exécutable "Lambda" (PyInstaller)
Pour rendre l'installation triviale pour l'utilisateur final, nous figeons `pc_sync.py` en un simple fichier `.exe`.
```bash
pip install pyinstaller watchdog httpx
pyinstaller --onefile --noconsole pc_sync.py
```
**Résultat :** On livre `pc_sync.exe` à l'utilisateur. Il double-clique, ça crée son arborescence de dossiers locale automatiquement, et il n'a plus qu'à glisser ses fichiers. Tout part magiquement dans le Cloud (Railway → Neon).

---

## PILIER 5 — DÉPLOIEMENT BACKEND (FastAPI → Railway)

### 5.1 — Déployer api.py sur Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway variables set GEMINI_API_KEY=AIza...
railway variables set DATABASE_URL=postgresql://...
railway up
# → URL : https://docling-agent-xxxx.railway.app
```

**Modifier api.py :**
```python
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
```

---

### 5.2 — CORS dans api.py (obligatoire pour PWA Netlify)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://docling-agent.netlify.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 5.3 — Procfile (Railway)

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

---

### 5.4 — Nouvel endpoint POST /api/v1/catalogue/batch dans api.py

```python
@app.post("/api/v1/catalogue/batch")
async def save_products_batch(payload: dict):
    produits = payload.get("produits", [])
    saved = 0
    for product in produits:
        await DBManager.upsert_product(product)
        saved += 1
    return {"saved": saved}
```

---

## ORDRE D'EXÉCUTION POUR ANTIGRAVITY

```text
TÂCHE 1 — gemini_service.py
  → model = "gemini-3-flash"
  → tools = "code_execution"
  → Remplacer prompt système (section 1.3)

TÂCHE 2 — image_preprocessor.py
  → Créer backend/services/image_preprocessor.py (section 1.4)
  → Intégrer dans orchestrator.py avant appel Gemini

TÂCHE 3 — Schéma SQL Neon
  → Exécuter SQL section 2.2 dans Neon console
  → Vérifier 241 produits existants intacts

TÂCHE 4 — db_manager.py
  → Réécrire avec asyncpg (section 2.3)
  → Tester upsert + get_catalogue

TÂCHE 5 — api.py & Railway (Pilier 5)
  → Ajouter CORS, Port dynamique, Endpoint batch, et Procfile (sections 5.1 à 5.4)
  → Déployer sur Railway & Tester l'accessibilité externe (HTTPS)

TÂCHE 6 — Compagnon PC Watchdog (Pilier 4)
  → Créer le script backend/pc_sync.py avec URL Railway en dur
  → Convertir en pc_sync.exe via PyInstaller
  → Tester le glisser-déposer sur le PC local

TÂCHE 7 — Créer PWA React (Pilier 3)
  → npm create vite@latest docling-pwa -- --template react
  → Développer l'interface et la lier à l'API Railway
  → Tester en local

TÂCHE 8 — Déploiement Netlify
  → npm run build && netlify deploy --prod --dir=dist
  → Tester mobile complet : Photo → Extraction Cloud → Catalogue
```

---

## CHECKLIST FINALE

- [ ] `gemini-3-flash` actif avec l'outil de code_execution
- [ ] Nouveau prompt intégré avec calcul du confidence score
- [ ] `image_preprocessor.py` terminé et branché sur l'orchestrateur
- [ ] Base de données Neon PostgreSQL provisionnée avec vecteurs/trgm
- [ ] `db_manager.py` migré sur asyncpg
- [ ] API FastAPI déployée publiquement sur Railway (CORS activé)
- [ ] Compagnon PC (`pc_sync.py`) développé
- [ ] Exécutable de distribution simple `pc_sync.exe` généré
- [ ] Interface Frontend (PWA Vite/React) terminée
- [ ] PWA hébergée et déployée sur Netlify (HTTPS)
- [ ] Validation du flux global "Utilisateur Lambda" : Scan Mobile + Dépôt PC
