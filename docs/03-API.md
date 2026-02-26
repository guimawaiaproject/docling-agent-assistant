# API — Docling Agent

## Endpoints

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/v1/invoices/process` | Upload facture → extraction IA (async, retourne job_id) |
| GET | `/api/v1/invoices/status/{job_id}` | Polling statut du job |
| GET | `/api/v1/catalogue` | Catalogue paginé (cursor) avec recherche floue pg_trgm |
| POST | `/api/v1/catalogue/batch` | Sauvegarde batch produits validés depuis la PWA |
| GET | `/api/v1/catalogue/fournisseurs` | Liste fournisseurs distincts |
| GET | `/api/v1/stats` | Statistiques dashboard |
| GET | `/api/v1/history` | Historique factures traitées |
| GET | `/api/v1/sync/status` | Statut watchdog (dossier magique) |
| DELETE | `/api/v1/catalogue/reset` | Vider la base (admin, JWT requis) |
| GET | `/health` | Health check |

---

## POST /api/v1/invoices/process

**Body (multipart/form-data) :**
- `file` : fichier PDF ou image (obligatoire)
- `model` : modèle IA (défaut : gemini-3-flash-preview)
- `source` : pc | mobile | watchdog (défaut : pc)

**Réponse :** 202 Accepted
```json
{
  "job_id": "uuid",
  "status": "processing"
}
```

---

## GET /api/v1/invoices/status/{job_id}

**Réponse :**
```json
{
  "status": "completed",
  "result": {
    "success": true,
    "products": [...],
    "products_added": 5,
    "filename": "..."
  }
}
```

---

## GET /api/v1/catalogue

**Query params :**
- `famille` : filtre par famille
- `fournisseur` : filtre par fournisseur
- `search` : recherche floue (pg_trgm)
- `limit` : nombre de résultats (défaut 50)
- `cursor` : pagination cursor-based

---

## Schémas Pydantic (Product)

```python
{
  "fournisseur": str,
  "designation_raw": str,
  "designation_fr": str,
  "famille": str,
  "unite": str,
  "prix_brut_ht": float,
  "remise_pct": float,
  "prix_remise_ht": float,
  "prix_ttc_iva21": float,
  "numero_facture": str | None,
  "date_facture": str | None,
  "confidence": "high" | "low"
}
```

---

## Limites

- **Upload** : max 50 Mo par fichier
- **CORS** : `Config.ALLOWED_ORIGINS`, pas `*`
- **Reset** : protégé par JWT admin
