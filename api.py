"""
Docling Agent REST API — Catalogue BTP.
FastAPI backend for mobile/web access to the invoice extraction pipeline.
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_config
from backend.core.db_manager import DBManager
from backend.core.orchestrator import ExtractionOrchestrator
from backend.core.monitoring import init_monitoring, Metrics
from backend.middleware.security import APIKeyMiddleware, RateLimitMiddleware

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("DoclingAPI")

config = get_config()
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ═══════════════════════════════════════
# LIFESPAN
# ═══════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_monitoring(sentry_dsn=os.getenv("SENTRY_DSN"))
    logger.info("Docling Agent API started")
    yield
    logger.info("Docling Agent API shutting down")


# ═══════════════════════════════════════
# APP
# ═══════════════════════════════════════
app = FastAPI(
    title="Docling Agent API",
    description=(
        "API REST pour l'extraction de factures BTP "
        "et la gestion du catalogue de prix."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Middleware (order matters: last added = first executed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)
app.add_middleware(RateLimitMiddleware, max_requests=30, window=60)
app.add_middleware(APIKeyMiddleware)


# ═══════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════
def get_db() -> DBManager:
    return DBManager(config.db_path)


def get_orchestrator(
    db: DBManager = Depends(get_db),
) -> ExtractionOrchestrator:
    return ExtractionOrchestrator(config=config, db_manager=db)


# ═══════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════
@app.get("/health", tags=["System"])
async def healthcheck():
    """Healthcheck for uptime monitoring (Betterstack, Render)."""
    try:
        db = get_db()
        stats = db.get_stats()
        return {
            "status": "healthy",
            "version": "2.0.0",
            "db": stats,
            "metrics": Metrics.get_all(),
        }
    except Exception as e:
        logger.error(f"Healthcheck failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/v1/invoices/process", tags=["Invoices"])
async def process_invoice(
    file: UploadFile = File(...),
    orch: ExtractionOrchestrator = Depends(get_orchestrator),
):
    """
    Upload and process an invoice (PDF or image).
    Extracts products, translates to French, stores in catalogue.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            400, detail=f"Unsupported file type: {file.content_type}"
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            413,
            detail=f"File too large (max {MAX_FILE_SIZE // 1024 // 1024} MB)",
        )

    try:
        result = orch.process_file(contents, file.filename)
        Metrics.increment("invoices_processed")
        Metrics.increment("products_added", result.products_added)
        Metrics.increment("products_updated", result.products_updated)

        return {
            "success": True,
            "invoice_number": result.invoice.numero_facture,
            "date": result.invoice.date_facture,
            "supplier": result.invoice.fournisseur,
            "products_added": result.products_added,
            "products_updated": result.products_updated,
            "was_cached": result.was_cached,
            "products": [
                p.model_dump() for p in result.invoice.products
            ],
        }
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        raise HTTPException(
            500, detail=f"Processing failed: {str(e)}"
        )


@app.get("/api/v1/catalogue", tags=["Catalogue"])
async def get_catalogue(
    famille: str | None = None,
    fournisseur: str | None = None,
    search: str | None = None,
    db: DBManager = Depends(get_db),
):
    """
    Retrieve product catalogue with optional filters.

    - **famille**: Filter by product family (Ciment, Finition...)
    - **fournisseur**: Filter by supplier name
    - **search**: Full-text search on designations
    """
    df = db.get_catalogue()
    if df.empty:
        return {"products": [], "total": 0}

    if famille:
        df = df[df["famille"] == famille]
    if fournisseur:
        df = df[df["fournisseur"] == fournisseur]
    if search:
        mask = (
            df["designation_fr"].str.contains(
                search, case=False, na=False
            )
            | df["designation_raw"].str.contains(
                search, case=False, na=False
            )
        )
        df = df[mask]

    return {"products": df.to_dict("records"), "total": len(df)}


@app.get("/api/v1/stats", tags=["System"])
async def get_stats(db: DBManager = Depends(get_db)):
    """Get database statistics."""
    return db.get_stats()


@app.get("/api/v1/invoices", tags=["Invoices"])
async def get_invoices(db: DBManager = Depends(get_db)):
    """List all processed invoices."""
    df = db.get_invoices()
    if df.empty:
        return {"invoices": [], "total": 0}
    return {"invoices": df.to_dict("records"), "total": len(df)}
