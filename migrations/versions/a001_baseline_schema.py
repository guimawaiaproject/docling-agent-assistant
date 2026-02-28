"""Baseline schema from schema_neon.sql

Revision ID: a001
Revises:
Create Date: 2026-02-25

For an EXISTING database (staging/prod):
    alembic stamp a001        # marks baseline as applied without executing
For a NEW database:
    alembic upgrade head      # creates all tables from scratch
"""
from collections.abc import Sequence

from alembic import op

revision: str = "a001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ── Fournisseurs ──────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS fournisseurs (
            id         SERIAL PRIMARY KEY,
            nom        VARCHAR(200) UNIQUE NOT NULL,
            pays       VARCHAR(10)  DEFAULT 'ES',
            langue     VARCHAR(10)  DEFAULT 'ca',
            created_at TIMESTAMPTZ  DEFAULT NOW()
        )
    """)

    # ── Produits ──────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS produits (
            id               SERIAL PRIMARY KEY,
            fournisseur      VARCHAR(200) NOT NULL,
            designation_raw  TEXT         NOT NULL,
            designation_fr   TEXT         NOT NULL,
            famille          VARCHAR(100),
            unite            VARCHAR(50),
            prix_brut_ht     NUMERIC(10,4) DEFAULT 0,
            remise_pct       NUMERIC(5,2)  DEFAULT 0,
            prix_remise_ht   NUMERIC(10,4) DEFAULT 0,
            prix_ttc_iva21   NUMERIC(10,4) DEFAULT 0,
            numero_facture   VARCHAR(100),
            date_facture     DATE,
            confidence       VARCHAR(10)   DEFAULT 'high',
            source           VARCHAR(20)   DEFAULT 'pc',
            created_at       TIMESTAMPTZ   DEFAULT NOW(),
            updated_at       TIMESTAMPTZ   DEFAULT NOW(),
            UNIQUE(designation_raw, fournisseur)
        )
    """)

    # ── Jobs ──────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id     UUID PRIMARY KEY,
            status     VARCHAR(20) DEFAULT 'processing',
            result     JSONB,
            error      TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC)")

    # ── Factures ──────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id                   SERIAL PRIMARY KEY,
            filename             VARCHAR(500),
            statut               VARCHAR(20)  DEFAULT 'traite',
            nb_produits_extraits INTEGER      DEFAULT 0,
            cout_api_usd         NUMERIC(8,6) DEFAULT 0,
            modele_ia            VARCHAR(50)  DEFAULT 'gemini-3-flash',
            source               VARCHAR(20)  DEFAULT 'pc',
            pdf_url              TEXT,
            created_at           TIMESTAMPTZ  DEFAULT NOW()
        )
    """)

    # ── Indexes produits ──────────────────────────────────────────
    op.execute("CREATE INDEX IF NOT EXISTS idx_produits_famille ON produits(famille)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_produits_fournisseur ON produits(fournisseur)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_produits_updated ON produits(updated_at DESC)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_trgm_raw "
        "ON produits USING GIN (designation_raw gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_trgm_fr "
        "ON produits USING GIN (designation_fr gin_trgm_ops)"
    )
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_produits_search_combined
        ON produits USING GIN (
            (designation_raw || ' ' || designation_fr || ' ' || fournisseur) gin_trgm_ops
        )
    """)

    # ── Trigger updated_at ────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION trigger_set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("DROP TRIGGER IF EXISTS set_updated_at ON produits")
    op.execute("""
        CREATE TRIGGER set_updated_at
        BEFORE UPDATE ON produits
        FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at()
    """)

    # ── Prix historique ───────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS prix_historique (
            id          SERIAL PRIMARY KEY,
            produit_id  INTEGER REFERENCES produits(id) ON DELETE CASCADE,
            fournisseur VARCHAR(200) NOT NULL,
            designation_fr TEXT NOT NULL,
            prix_ht     NUMERIC(10,4) NOT NULL,
            prix_brut   NUMERIC(10,4),
            remise_pct  NUMERIC(5,2) DEFAULT 0,
            facture_id  INTEGER REFERENCES factures(id) ON DELETE SET NULL,
            recorded_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_prixhist_produit "
        "ON prix_historique(produit_id, recorded_at DESC)"
    )

    # ── Users ─────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            SERIAL PRIMARY KEY,
            email         VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name  VARCHAR(200),
            role          VARCHAR(20) DEFAULT 'user',
            created_at    TIMESTAMPTZ DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS set_updated_at ON produits")
    op.execute("DROP FUNCTION IF EXISTS trigger_set_updated_at()")
    op.execute("DROP TABLE IF EXISTS prix_historique CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS jobs CASCADE")
    op.execute("DROP TABLE IF EXISTS factures CASCADE")
    op.execute("DROP TABLE IF EXISTS produits CASCADE")
    op.execute("DROP TABLE IF EXISTS fournisseurs CASCADE")
