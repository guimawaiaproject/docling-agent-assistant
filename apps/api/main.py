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
import json
import logging
import mimetypes
import os
import time
import uuid
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from core.config import Config
from core.db_manager import DBManager
from core.orchestrator import Orchestrator
from schemas.invoice import BatchSaveRequest
from services.auth_service import (
    create_token,
    hash_password,
    needs_rehash,
    validate_password,
    verify_password,
    verify_token,
)
from services.community_service import CommunityService
from services.storage_service import StorageService
from services.watchdog_service import (
    get_watchdog_status,
    start_watchdog,
    stop_watchdog,
)
from utils.serializers import serialize_row

# ─── Sentry — error monitoring ────────────────────────────────────────────────
_ENV = os.getenv("ENVIRONMENT", "production")
_SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if _SENTRY_DSN:
    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=_ENV,
        release="docling-agent@3.0.0",
    )
elif _ENV == "production":
    logging.getLogger(__name__).warning(
        "SENTRY_DSN non configuré en production — monitoring des erreurs désactivé"
    )


# ─── Rate limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─── Auth dependencies ────────────────────────────────────────────────────────
_GUEST_USER_ID: int | None = None  # Rempli au démarrage si FREE_ACCESS_MODE


async def get_current_user(
    request: Request,
    authorization: str = Header(default="", alias="Authorization"),
) -> dict:
    """Extract and validate token from Cookie or Authorization. Si FREE_ACCESS_MODE et pas de token → guest."""
    token = None
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    if not token:
        token = request.cookies.get("docling-token")

    if token:
        payload = verify_token(token)
        if payload:
            return payload

    # Accès free provisoire : pas de token → guest (si activé)
    if Config.FREE_ACCESS_MODE and _GUEST_USER_ID is not None:
        return {"sub": str(_GUEST_USER_ID), "email": "guest@free.provisional", "role": "user"}

    raise HTTPException(status_code=401, detail="Token manquant")


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


class _GeminiCircuitBreaker:
    """Thread-safe circuit breaker for Gemini API calls.
    Ouvre le circuit après N erreurs consécutives, cooldown 60s.
    """

    COOLDOWN_SEC = 60

    def __init__(self, threshold: int = 5):
        self._threshold = threshold
        self._consecutive_errors = 0
        self._open_until: float = 0.0
        self._lock = asyncio.Lock()

    def is_open(self) -> bool:
        """True si le circuit est ouvert (ne pas lancer d'extraction)."""
        return time.monotonic() < self._open_until

    async def record_success(self) -> None:
        async with self._lock:
            self._consecutive_errors = 0

    async def record_failure(self) -> bool:
        """Returns True if the circuit has tripped (threshold reached)."""
        async with self._lock:
            self._consecutive_errors += 1
            if self._consecutive_errors >= self._threshold:
                self._consecutive_errors = 0
                self._open_until = time.monotonic() + self.COOLDOWN_SEC
                return True
            return False

    @property
    def threshold(self) -> int:
        return self._threshold


_gemini_cb = _GeminiCircuitBreaker(threshold=5)


def _sanitize_job_error(err: Exception, tripped: bool = False) -> str:
    """Mappe les erreurs techniques vers des messages utilisateur sûrs."""
    msg = str(err).lower()
    if tripped:
        return "Service d'extraction temporairement indisponible. Réessayez dans quelques minutes."
    if "429" in msg or "resource_exhausted" in msg or "rate" in msg or "quota" in msg:
        return "Quota API dépassé. Réessayez plus tard."
    if "401" in msg or "403" in msg or "invalid" in msg and "key" in msg or "api_key" in msg:
        return "Clé API invalide ou inexistante."
    if "timeout" in msg or "timed out" in msg:
        return "Délai d'attente dépassé. Réessayez."
    return "Erreur lors de l'extraction. Réessayez ou contactez le support."


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _GUEST_USER_ID
    # Démarrage
    Config.validate()
    await DBManager.get_pool()
    await DBManager.run_migrations()

    # Accès free provisoire : créer ou récupérer l'utilisateur guest
    if Config.FREE_ACCESS_MODE:
        pool = await DBManager.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", "guest@free.provisional"
            )
            if not row:
                guest_hash = hash_password("guest-no-login-provisional")
                row = await conn.fetchrow(
                    """INSERT INTO users (email, password_hash, display_name, role)
                       VALUES ($1, $2, $3, $4) RETURNING id""",
                    "guest@free.provisional", guest_hash, "Invité (accès libre)", "user",
                )
            _GUEST_USER_ID = row["id"]
        logger.info("Accès free provisoire activé (guest user_id=%s)", _GUEST_USER_ID)

    loop = asyncio.get_running_loop()
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

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Trop de tentatives. Réessayez dans quelques instants."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    allow_credentials=True,
)


async def _security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if os.getenv("ENVIRONMENT", "").lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


app.middleware("http")(_security_headers)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Inject request_id (uuid[:8]), log request/response, add X-Request-ID header."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_id=%s method=%s path=%s status_code=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


# ─── Upload constants ─────────────────────────────────────────────────────────
_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 Mo
_ALLOWED_MIMES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
_ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
_CHUNK_SIZE = 256 * 1024  # 256 Ko


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 1 : Process facture (mode async avec job_id)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/api/v1/invoices/process")
@limiter.limit("20/minute")
async def process_invoice(
    request: Request,
    background_tasks: BackgroundTasks,
    file:   UploadFile = File(...),
    model:  str        = Form(default="gemini-3-flash-preview"),
    source: str        = Form(default="pc"),
    _user: dict        = Depends(get_current_user),
):
    """
    Upload + extraction IA.
    Retourne immédiatement un job_id (HTTP 202).
    Polling via GET /api/v1/invoices/status/{job_id}
    """
    if model not in Config.MODELS_DISPONIBLES:
        raise HTTPException(
            status_code=400,
            detail=f"Modèle invalide. Acceptés : {', '.join(sorted(Config.MODELS_DISPONIBLES))}",
        )
    if source not in ("pc", "mobile", "watchdog"):
        raise HTTPException(
            status_code=400,
            detail="Source invalide. Valeurs acceptées : pc, mobile, watchdog",
        )

    filename = file.filename or "facture"

    ext = os.path.splitext(filename)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Extension non autorisée. Acceptées : {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    declared_mime = file.content_type or mimetypes.guess_type(filename)[0] or ""
    if declared_mime not in _ALLOWED_MIMES:
        raise HTTPException(
            status_code=415,
            detail=f"Type MIME non autorisé ({declared_mime}). Acceptés : {', '.join(sorted(_ALLOWED_MIMES))}",
        )

    chunks: list[bytes] = []
    total_size = 0
    while True:
        chunk = await file.read(_CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > _MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 50 Mo)")
        chunks.append(chunk)

    file_bytes = b"".join(chunks)

    job_id = str(uuid.uuid4())
    user_id = int(_user["sub"]) if _user.get("sub") else None
    await DBManager.create_job(job_id, "processing", user_id=user_id)

    background_tasks.add_task(
        _run_extraction, job_id, file_bytes, filename, model, source, user_id
    )

    return JSONResponse(
        status_code=202,
        content={"job_id": job_id, "status": "processing"}
    )


async def _run_extraction(
    job_id: str,
    file_bytes: bytes,
    filename: str,
    model: str,
    source: str,
    user_id: int | None = None,
):
    if _gemini_cb.is_open():
        err_msg = _sanitize_job_error(Exception("circuit"), tripped=True)
        await DBManager.update_job(job_id, "error", result=None, error=err_msg)
        logger.warning("Circuit ouvert, extraction %s refusée", job_id)
        return

    fallback_model = "gemini-2.5-flash"

    async with _extraction_semaphore:
        try:
            result = await Orchestrator.process_file(
                file_bytes=file_bytes,
                filename=filename,
                model_id=model,
                source=source,
                user_id=user_id,
            )
            await _gemini_cb.record_success()
            await DBManager.update_job(
                job_id,
                "completed" if result["success"] else "error",
                result=result,
                error=result.get("error"),
            )
        except Exception as e:
            # Fallback vers modèle plus stable si échec du modèle principal
            if model != fallback_model and fallback_model in Config.MODELS_DISPONIBLES:
                try:
                    logger.info("Retry extraction %s avec fallback %s", filename, fallback_model)
                    result = await Orchestrator.process_file(
                        file_bytes=file_bytes,
                        filename=filename,
                        model_id=fallback_model,
                        source=source,
                        user_id=user_id,
                    )
                    await _gemini_cb.record_success()
                    await DBManager.update_job(
                        job_id,
                        "completed" if result["success"] else "error",
                        result=result,
                        error=result.get("error"),
                    )
                    return
                except Exception:
                    pass
            tripped = await _gemini_cb.record_failure()
            if tripped:
                logger.warning(
                    "Circuit-breaker Gemini : %d erreurs consecutives. "
                    "Job marque en erreur, les autres jobs continuent.",
                    _gemini_cb.threshold,
                )
            logger.error("Erreur extraction %s: %s", filename, e, exc_info=True)
            err_msg = _sanitize_job_error(e, tripped=tripped)
            await DBManager.update_job(
                job_id, "error", result=None, error=err_msg
            )


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 2 : Statut job
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/invoices/status/{job_id}")
async def get_job_status(job_id: str, _user: dict = Depends(get_current_user)):
    user_id = int(_user["sub"]) if _user.get("sub") else None
    job = await DBManager.get_job(job_id, user_id=user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return job


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 3 : Catalogue paginé (cursor-based)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/catalogue")
async def get_catalogue(
    famille:      str | None = None,
    fournisseur:  str | None = None,
    search:       str | None = None,
    limit:        int           = 50,
    cursor:       str | None = None,
    _user: dict = Depends(get_current_user),
):
    """
    Catalogue avec pagination cursor.
    Recherche floue sur designation_raw (CA/ES) + designation_fr (FR) via pg_trgm.
    """
    try:
        user_id = int(_user["sub"]) if _user.get("sub") else None
        result = await DBManager.get_catalogue(
            famille=famille,
            fournisseur=fournisseur,
            search=search,
            limit=min(limit, 200),
            cursor=cursor,
            user_id=user_id,
        )

        result["products"] = [serialize_row(p) for p in result["products"]]
        return result

    except Exception as err:
        logger.error("Erreur get_catalogue", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err


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
        user_id = int(_user["sub"]) if _user.get("sub") else None
        nb_saved, historique_failures = await DBManager.upsert_products_batch(
            payload.produits,
            source=payload.source,
            user_id=user_id,
        )
        resp = {"saved": nb_saved, "total": len(payload.produits)}
        if historique_failures > 0:
            resp["partial_success"] = True
            resp["historique_errors"] = historique_failures
        return resp
    except Exception as err:
        logger.error("Erreur batch save", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 5 : Fournisseurs distincts
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/catalogue/fournisseurs")
async def get_fournisseurs(_user: dict = Depends(get_current_user)):
    try:
        user_id = int(_user["sub"]) if _user.get("sub") else None
        fournisseurs = await DBManager.get_fournisseurs(user_id=user_id)
        return {"fournisseurs": fournisseurs}
    except Exception as err:
        logger.error("Erreur get_fournisseurs", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 6 : Stats dashboard
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/stats")
async def get_stats(_user: dict = Depends(get_current_user)):
    try:
        user_id = int(_user["sub"]) if _user.get("sub") else None
        return await DBManager.get_stats(user_id=user_id)
    except Exception as err:
        logger.error("Erreur get_stats", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 7 : Historique factures
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/history")
async def get_history(limit: int = 50, _user: dict = Depends(get_current_user)):
    try:
        user_id = int(_user["sub"]) if _user.get("sub") else None
        rows = await DBManager.get_factures_history(
            limit=min(limit, 200), user_id=user_id
        )
        return {"history": [serialize_row(r) for r in rows], "total": len(rows)}
    except Exception as err:
        logger.error("Erreur get_history", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err


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
        user_id = int(_user["sub"]) if _user.get("sub") else None
        pdf_url = await DBManager.get_facture_pdf_url(facture_id, user_id=user_id)
        if not pdf_url:
            raise HTTPException(status_code=404, detail="PDF introuvable")
        presigned = StorageService.get_presigned_url_from_pdf_url(pdf_url)
        if not presigned:
            raise HTTPException(status_code=500, detail="Impossible de générer l'URL")
        return {"url": presigned, "expires_in": 3600}
    except HTTPException:
        raise
    except Exception as err:
        logger.error("Erreur get_facture_pdf_url", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 8 : Statut sync watchdog
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/sync/status")
@limiter.limit("30/minute")
async def get_sync_status(request: Request, _user: dict = Depends(get_current_user)):
    """
    Retourne le statut du dossier magique (watchdog) pour la page Settings PWA.
    """
    return get_watchdog_status()


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT 9 : Reset BDD (admin — à protéger en prod)
# ─────────────────────────────────────────────────────────────────────────────
@app.delete("/api/v1/catalogue/reset")
async def reset_catalogue(
    confirm: str = "", _admin: dict = Depends(get_admin_user)
):
    if confirm != "SUPPRIMER_TOUT":
        raise HTTPException(
            status_code=400,
            detail="Passer ?confirm=SUPPRIMER_TOUT pour confirmer"
        )
    user_id = int(_admin["sub"]) if _admin.get("sub") else None
    await DBManager.truncate_products(user_id=user_id)
    return {"message": "Catalogue vidé", "produits_restants": 0}






# ---------------------------------------------------------------------------
# ENDPOINT 11 : Historique de prix d'un produit
# ---------------------------------------------------------------------------
@app.get("/api/v1/catalogue/price-history/{product_id}")
async def get_price_history(product_id: int, _user: dict = Depends(get_current_user)):
    """Retourne l'historique des prix pour un produit."""
    try:
        user_id = int(_user["sub"]) if _user.get("sub") else None
        rows = await DBManager.get_price_history_by_product_id(
            product_id, user_id=user_id
        )
        result = [serialize_row(dict(r)) for r in rows]
        return {"history": result, "product_id": product_id}
    except Exception as err:
        logger.error("Erreur get_price_history", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err
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
        user_id = int(_user["sub"]) if _user.get("sub") else None
        term = search.strip()
        if with_history:
            rows = await DBManager.compare_prices_with_history(term, user_id=user_id)
        else:
            rows = await DBManager.compare_prices(term, user_id=user_id)
        serialized = []
        for r in rows:
            d = dict(r)
            sr = serialize_row(d)
            sr["price_history"] = [serialize_row(h) for h in d.get("price_history", [])]
            serialized.append(sr)
        return {"results": serialized, "search": term, "count": len(rows)}
    except Exception as err:
        logger.error("Erreur compare_prices", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from err


# ---------------------------------------------------------------------------
# AUTH ENDPOINTS (Phase 4.3 - Multi-utilisateur)
# ---------------------------------------------------------------------------
@app.post("/api/v1/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, email: str = Form(...), password: str = Form(...), name: str = Form(default="")):
    """Inscription nouvel utilisateur."""
    ok, msg = validate_password(password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    if len(email) > 255:
        raise HTTPException(status_code=400, detail="Email trop long")
    if len(password) > 128:
        raise HTTPException(status_code=400, detail="Mot de passe trop long")
    if len(name) > 200:
        raise HTTPException(status_code=400, detail="Nom trop long")
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
        resp = JSONResponse(content={"user_id": row["id"], "email": email})
        _set_auth_cookie(resp, token)
        return resp


@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Connexion utilisateur. Rehash silencieux PBKDF2 → Argon2id si nécessaire."""
    if len(email) > 255:
        raise HTTPException(status_code=400, detail="Email trop long")
    if len(password) > 128:
        raise HTTPException(status_code=400, detail="Mot de passe trop long")
    pool = await DBManager.get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, email, password_hash, role, display_name FROM users WHERE email = $1",
            email
        )
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

        if needs_rehash(user["password_hash"]):
            new_hash = hash_password(password)
            await conn.execute(
                "UPDATE users SET password_hash = $1 WHERE id = $2",
                new_hash, user["id"],
            )
            logger.info("Rehash PBKDF2→Argon2id pour user_id=%s", user["id"])

        token = create_token(user["id"], user["email"], user["role"])
        resp = JSONResponse(content={
            "user_id": user["id"],
            "email": user["email"],
            "name": user["display_name"],
            "role": user["role"],
        })
        _set_auth_cookie(resp, token)
        return resp


def _set_auth_cookie(response: JSONResponse, token: str) -> None:
    """Set httpOnly JWT cookie. Secure in prod, SameSite=Lax."""
    is_prod = os.getenv("ENVIRONMENT", "").lower() == "production"
    response.set_cookie(
        key="docling-token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=24 * 3600,
        path="/",
    )


@app.post("/api/v1/auth/logout")
async def logout():
    """Déconnexion — supprime le cookie JWT."""
    resp = JSONResponse(content={"ok": True})
    resp.delete_cookie(key="docling-token", path="/")
    return resp


@app.get("/api/v1/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Retourne l'utilisateur connecté depuis le token Bearer."""
    user_id = int(user["sub"]) if user.get("sub") else None
    consent, zone_geo = await DBManager.get_user_community_prefs(user_id) if user_id else (False, None)
    return {
        "user_id": user["sub"],
        "email": user["email"],
        "role": user["role"],
        "community_consent": consent,
        "zone_geo": zone_geo,
    }


@app.patch("/api/v1/community/preferences")
async def update_community_preferences(
    request: Request,
    _user: dict = Depends(get_current_user),
):
    """Met à jour le consentement et la zone pour la base prix communautaire."""
    user_id = int(_user["sub"]) if _user.get("sub") else None
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID manquant")
    try:
        body = await request.json()
    except Exception:
        body = {}
    community_consent = body.get("community_consent")
    zone_geo = body.get("zone_geo")
    await DBManager.update_user_community_prefs(user_id, community_consent, zone_geo)
    return {"ok": True}


@app.get("/api/v1/community/stats")
async def get_community_stats(
    zone: str | None = None,
    pays: str | None = None,
    fournisseur: str | None = None,
    limit: int = 50,
    _user: dict = Depends(get_current_user),
):
    """Stats agrégées base prix communautaire (k-anonymité >= 5)."""
    stats = await CommunityService.get_stats(
        zone=zone, pays=pays, fournisseur=fournisseur, limit=limit
    )
    return {"stats": stats}


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT : Export my data (RGPD / portabilité)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/export/my-data")
async def export_my_data(_user: dict = Depends(get_current_user)):
    """
    Retourne toutes les données de l'utilisateur (produits + factures) en JSON
    téléchargeable. Filtrage par user_id pour isolation multi-tenant.
    """
    try:
        user_id = int(_user["sub"]) if _user.get("sub") else None
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID manquant")
        data = await DBManager.get_user_export_data(user_id)
        data["produits"] = [serialize_row(p) for p in data["produits"]]
        data["factures"] = [serialize_row(f) for f in data["factures"]]
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=docling-export-my-data.json",
            },
        )
    except HTTPException:
        raise
    except Exception as err:
        logger.error("Erreur export my-data", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de l'export") from err
# ─── Racine ───────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Docling Agent v3 API is running",
        "docs": "/docs",
        "version": "3.0.0"
    }


# ─── Web Vitals (Core Web Metrics) ──────────────────────────────────────────────
@app.post("/api/vitals")
async def receive_vitals(request: Request):
    """
    Reçoit les métriques Web Vitals (CLS, INP, LCP, FCP, TTFB) envoyées par sendBeacon.
    Optionnel : persister en BDD ou envoyer à un service analytics.
    """
    try:
        body = await request.json()
        logger.info(
            "Web Vitals: %s=%.2f (%s)",
            body.get("name"),
            body.get("value"),
            body.get("rating"),
        )
        return {"ok": True}
    except Exception as e:
        logger.warning("Vitals parse error: %s", e)
        return {"ok": False}


# ─── Web Vitals (optionnel, pour monitoring frontend) ──────────────────────────
@app.get("/api/vitals")
async def vitals():
    """Endpoint pour web-vitals / monitoring frontend."""
    return {"status": "ok"}


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    try:
        pool = await DBManager.get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ok", "db": "connected", "version": "3.0.0"}
    except Exception as err:
        raise HTTPException(status_code=503, detail="Database unreachable") from err


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
