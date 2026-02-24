"""
Docling Agent REST API — Catalogue BTP.
FastAPI backend for mobile/web access to the invoice extraction pipeline.
"""
import os
import logging
from contextlib import asynccontextmanager
import numpy as np
import pandas as pd

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_config
from backend.core.db_manager import DBManager
from backend.core.orchestrator import ExtractionOrchestrator
from backend.core.monitoring import init_monitoring, Metrics

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
# ═══════════════════════════════════════
# LIFESPAN
# ═══════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialisation DB Pool AsyncPg et création des tables
    try:
        await DBManager.init_db()
    except Exception as e:
        logger.error(f"Failed to init DB on startup: {e}")

    # Injection dépendances globales (Orchestrateur n'a plus besoin d'instance DB)
    app.state.orchestrator = ExtractionOrchestrator(config=config)

    init_monitoring(sentry_dsn=os.getenv("SENTRY_DSN"))
    logger.info("Docling Agent API started with Neon DB")
    yield
    await DBManager.close()
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


# ═══════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════
@app.get("/health", tags=["System"])
async def healthcheck():
    """Healthcheck for uptime monitoring (Betterstack, Render)."""
    try:
        stats = await DBManager.get_stats()
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
async def process_invoice(file: UploadFile = File(...)):
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
        orch = app.state.orchestrator
        result = await orch.process_file(contents, file.filename)
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
):
    """
    Retrieve product catalogue with optional filters.

    - **famille**: Filter by product family (Ciment, Finition...)
    - **fournisseur**: Filter by supplier name
    - **search**: Full-text search on designations
    """
    df_list = await DBManager.get_catalogue()
    df = pd.DataFrame(df_list)
    if df.empty:
        return {"products": [], "total": 0}

    # Nettoyage anti-NaN/Inf robuste pour la sérialisation JSON
    df = df.replace([np.inf, -np.inf], 0).fillna(0)

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
async def get_stats():
    """Get database statistics."""
    return await DBManager.get_stats()


@app.get("/api/v1/invoices", tags=["Invoices"])
async def get_invoices():
    """List all processed invoices."""
    df_list = await DBManager.get_invoices()
    df = pd.DataFrame(df_list)
    if df.empty:
        return {"invoices": [], "total": 0}
    return {"invoices": df.to_dict("records"), "total": len(df)}


@app.get("/api/v1/watcher/activity", tags=["System"])
async def get_watcher_activity():
    """Get the latest activity from the folder watcher."""
    if hasattr(app.state, "watcher"):
        return {"activity": app.state.watcher.get_activity()}
    return {"activity": []}
