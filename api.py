"""
FastAPI — Docling Agent v3
Endpoints :
  POST /api/v1/invoices/process          → Extraction IA (upload unique)
  GET  /api/v1/invoices/status/{job_id}  → Statut job async
  GET  /api/v1/catalogue                 → Catalogue paginé (cursor)
  POST /api/v1/catalogue/batch           → Sauvegarde batch (depuis PWA validation)
  GET  /api/v1/catalogue/fournisseurs    → Liste fournisseurs distincts
  GET  /api/v1/stats                     → Stats dashboard
  GET  /api/v1/history                   → Historique factures
  GET  /api/v1/sync/status               → Statut dossier magique watchdog
  DELETE /api/v1/catalogue/reset         → Vider la base (admin)
"""

import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import sentry_sdk
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import Config
from backend.core.db_manager import DBManager
from backend.services.auth_service import create_token, verify_token, hash_password, verify_password
from backend.services.storage_service import StorageService
from backend.core.orchestrator import Orchestrator
from backend.schemas.invoice import BatchSaveRequest
from backend.services.watchdog_service import (
    get_watchdog_status,
    start_watchdog,
    stop_watchdog,
)

# ─── Sentry — error monitoring ────────────────────────────────────────────────
_SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if _SENTRY_DSN:
    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "production"),
        release=f"docling-agent@3.0.0",
    )


# ─── Auth dependencies ────────────────────────────────────────────────────────
async def get_current_user(authorization: str = Header(default="", alias="Authorization")) -> dict:
    """Extract and validate Bearer token from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    payload = verify_token(authorization[7:])
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    return payload


async def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    """Require authenticated user with admin role."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")
    return user

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Sémaphore pour limiter les extractions Gemini concurrentes (évite rate limit)
_extraction_semaphore = asyncio.Semaphore(3)

# Circuit-breaker Gemini : après N erreurs consécutives, marquer le job en erreur et passer au suivant
_GEMINI_CONSECUTIVE_ERRORS = 0
_GEMINI_CIRCUIT_BREAKER_THRESHOLD = 5


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage
    Config.validate()
    await DBManager.get_pool()
    await DBManager.run_migrations()
    loop = asyncio.get_event_loop()
    start_watchdog(Config.DEFAULT_MODEL, loop)
    logger.info("🚀 Docling Agent v3 démarré")
    yield
    # Arrêt
    stop_watchdog()
    await DBManager.close_pool()
    logger.info("🛑 Docling Agent v3 arrêté")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Docling Agent API",
    version="3.0.0",
    description="Extraction IA de factures BTP (CA/ES/FR) — Neon PostgreSQL",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 1 : Process facture (mode async avec job_id)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/api/v1/invoices/process")
async def process_invoice(
    background_tasks: BackgroundTasks,
    file:   UploadFile = File(...),
    model:  str        = Form(default="gemini-3-flash"),
    source: str        = Form(default="pc"),
    _user: dict        = Depends(get_current_user),
):
    """
    Upload + extraction IA.
    Retourne immédiatement un job_id (HTTP 202).
    Polling via GET /api/v1/invoices/status/{job_id}
    """
    job_id     = str(uuid.uuid4())
    file_bytes = await file.read()
    filename   = file.filename or "facture"

    MAX_UPLOAD = 50 * 1024 * 1024
    if len(file_bytes) > MAX_UPLOAD:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 50 Mo)")

    await DBManager.create_job(job_id, "processing")

    background_tasks.add_task(
        _run_extraction, job_id, file_bytes, filename, model, source
    )

    return JSONResponse(
        status_code=202,
        content={"job_id": job_id, "status": "processing"}
    )


async def _run_extraction(
    job_id: str, file_bytes: bytes, filename: str, model: str, source: str
):
    global _GEMINI_CONSECUTIVE_ERRORS
    async with _extraction_semaphore:
        try:
            result = await Orchestrator.process_file(
                file_bytes=file_bytes,
                filename=filename,
                model_id=model,
                source=source,
            )
            _GEMINI_CONSECUTIVE_ERRORS = 0  # Succès : reset du compteur
            await DBManager.update_job(
                job_id,
                "completed" if result["success"] else "error",
                result=result,
                error=result.get("error"),
            )
        except Exception as e:
            _GEMINI_CONSECUTIVE_ERRORS += 1
            circuit_triggered = _GEMINI_CONSECUTIVE_ERRORS >= _GEMINI_CIRCUIT_BREAKER_THRESHOLD
            if circuit_triggered:
                logger.warning(
                    f"Circuit-breaker Gemini : {_GEMINI_CONSECUTIVE_ERRORS} erreurs consécutives. "
                    "Job marqué en erreur, les autres jobs continuent."
                )
                _GEMINI_CONSECUTIVE_ERRORS = 0
            err_msg = str(e)
            if circuit_triggered:
                err_msg += f" (Gemini indisponible après {_GEMINI_CIRCUIT_BREAKER_THRESHOLD} échecs consécutifs)"
            await DBManager.update_job(
                job_id, "error", result=None, error=err_msg
            )


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 2 : Statut job
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/invoices/status/{job_id}")
async def get_job_status(job_id: str, _user: dict = Depends(get_current_user)):
    job = await DBManager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return job


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 3 : Catalogue paginé (cursor-based)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/catalogue")
async def get_catalogue(
    famille:      Optional[str] = None,
    fournisseur:  Optional[str] = None,
    search:       Optional[str] = None,
    limit:        int           = 50,
    cursor:       Optional[str] = None,
    _user: dict = Depends(get_current_user),
):
    """
    Catalogue avec pagination cursor.
    Recherche floue sur designation_raw (CA/ES) + designation_fr (FR) via pg_trgm.
    """
    try:
        result = await DBManager.get_catalogue(
            famille=famille,
            fournisseur=fournisseur,
            search=search,
            limit=min(limit, 200),
            cursor=cursor,
        )

        # Sérialiser les dates et Decimal pour JSON
        for p in result["products"]:
            for key, val in p.items():
                if hasattr(val, "isoformat"):
                    p[key] = val.isoformat()
                elif hasattr(val, "__float__"):
                    p[key] = float(val)

        return result

    except Exception as e:
        logger.error(f"Erreur get_catalogue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 4 : Sauvegarde batch (PWA → Validation → Save)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/api/v1/catalogue/batch")
async def save_batch(payload: BatchSaveRequest, _user: dict = Depends(get_current_user)):
    """
    Reçoit la liste de produits validés/corrigés par l'utilisateur
    depuis la ValidationPage PWA et les insère dans Neon.
    """
    try:
        nb_saved = await DBManager.upsert_products_batch(
            payload.produits,
            source=payload.source
        )
        return {"saved": nb_saved, "total": len(payload.produits)}
    except Exception as e:
        logger.error(f"Erreur batch save: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 5 : Fournisseurs distincts
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/catalogue/fournisseurs")
async def get_fournisseurs(_user: dict = Depends(get_current_user)):
    try:
        fournisseurs = await DBManager.get_fournisseurs()
        return {"fournisseurs": fournisseurs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 6 : Stats dashboard
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/stats")
async def get_stats(_user: dict = Depends(get_current_user)):
    try:
        return await DBManager.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 7 : Historique factures
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/history")
async def get_history(limit: int = 50, _user: dict = Depends(get_current_user)):
    try:
        rows = await DBManager.get_factures_history(limit=min(limit, 200))
        for r in rows:
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
                elif hasattr(v, "__float__"):
                    r[k] = float(v)
        return {"history": rows, "total": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 7b : URL PDF pré-signée (Storj)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/history/{facture_id}/pdf")
async def get_facture_pdf_url(facture_id: int, _user: dict = Depends(get_current_user)):
    """
    Retourne une URL pré-signée pour accéder au PDF.
    Nécessaire pour Storj où l'URL directe n'est pas accessible.
    """
    try:
        pool = await DBManager.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT pdf_url FROM factures WHERE id = $1", facture_id
            )
        if not row or not row["pdf_url"]:
            raise HTTPException(status_code=404, detail="PDF introuvable")
        pdf_url = row["pdf_url"]
        presigned = StorageService.get_presigned_url_from_pdf_url(pdf_url)
        if not presigned:
            raise HTTPException(status_code=500, detail="Impossible de générer l'URL")
        return {"url": presigned, "expires_in": 3600}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_facture_pdf_url: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 8 : Statut sync watchdog
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/sync/status")
async def get_sync_status(_user: dict = Depends(get_current_user)):
    """
    Retourne le statut du dossier magique (watchdog) pour la page Settings PWA.
    """
    return get_watchdog_status()


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 9 : Reset BDD (admin — à protéger en prod)
# ─────────────────────────────────────────────────────────────────────────────
@app.delete("/api/v1/catalogue/reset")
async def reset_catalogue(confirm: str = "", _admin: dict = Depends(get_admin_user)):
    if confirm != "SUPPRIMER_TOUT":
        raise HTTPException(
            status_code=400,
            detail="Passer ?confirm=SUPPRIMER_TOUT pour confirmer"
        )
    await DBManager.truncate_products()
    return {"message": "Catalogue vidé", "produits_restants": 0}






# ---------------------------------------------------------------------------
# ENDPOINT 11 : Historique de prix d'un produit
# ---------------------------------------------------------------------------
@app.get("/api/v1/catalogue/price-history/{product_id}")
async def get_price_history(product_id: int, _user: dict = Depends(get_current_user)):
    """Retourne l'historique des prix pour un produit."""
    try:
        pool = await DBManager.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT prix_ht, prix_brut, remise_pct, recorded_at
                FROM prix_historique
                WHERE produit_id = $1
                ORDER BY recorded_at DESC
                LIMIT 20
            """, product_id)
            result = []
            for r in rows:
                d = dict(r)
                for k, v in d.items():
                    if hasattr(v, "isoformat"):
                        d[k] = v.isoformat()
                    elif hasattr(v, "__float__"):
                        d[k] = float(v)
                result.append(d)
            return {"history": result, "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ---------------------------------------------------------------------------
# ENDPOINT 10 : Comparateur de prix fournisseurs
# ---------------------------------------------------------------------------
@app.get("/api/v1/catalogue/compare")
async def compare_prices(search: str = "", with_history: bool = True, _user: dict = Depends(get_current_user)):
    """
    Compare les prix d'un produit entre fournisseurs.
    Retourne les produits similaires tries par prix croissant.
    with_history=true : enrichit avec l'historique prix_historique pour graphiques.
    """
    if not search or len(search.strip()) < 2:
        raise HTTPException(status_code=400, detail="Recherche trop courte (min 2 car.)")
    try:
        rows = await DBManager.compare_prices(search.strip())
        for r in rows:
            for k, v in list(r.items()):
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
                elif hasattr(v, "__float__"):
                    r[k] = float(v)
            if with_history and r.get("id"):
                hist = await DBManager.get_price_history_by_product_id(r["id"])
                for h in hist:
                    for k, v in list(h.items()):
                        if hasattr(v, "isoformat"):
                            h[k] = v.isoformat()
                        elif hasattr(v, "__float__"):
                            h[k] = float(v)
                r["price_history"] = hist
        return {"results": rows, "search": search.strip(), "count": len(rows)}
    except Exception as e:
        logger.error(f"Erreur compare_prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# AUTH ENDPOINTS (Phase 4.3 - Multi-utilisateur)
# ---------------------------------------------------------------------------
@app.post("/api/v1/auth/register")
async def register(email: str = Form(...), password: str = Form(...), name: str = Form(default="")):
    """Inscription nouvel utilisateur."""
    pool = await DBManager.get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
        if existing:
            raise HTTPException(status_code=409, detail="Email deja utilise")
        pw_hash = hash_password(password)
        row = await conn.fetchrow(
            "INSERT INTO users (email, password_hash, display_name) VALUES ($1, $2, $3) RETURNING id, role",
            email, pw_hash, name or email.split("@")[0]
        )
        token = create_token(row["id"], email, row["role"])
        return {"token": token, "user_id": row["id"], "email": email}


@app.post("/api/v1/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """Connexion utilisateur."""
    pool = await DBManager.get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, email, password_hash, role, display_name FROM users WHERE email = $1",
            email
        )
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        token = create_token(user["id"], user["email"], user["role"])
        return {
            "token": token,
            "user_id": user["id"],
            "email": user["email"],
            "name": user["display_name"],
            "role": user["role"],
        }


@app.get("/api/v1/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Retourne l'utilisateur connecté depuis le token Bearer."""
    return {"user_id": user["sub"], "email": user["email"], "role": user["role"]}
# ─── Racine ───────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Docling Agent v3 API is running",
        "docs": "/docs",
        "version": "3.0.0"
    }


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
