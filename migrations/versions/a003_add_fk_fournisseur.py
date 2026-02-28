"""Add FK produits.fournisseur -> fournisseurs(nom)

Revision ID: a003
Revises: a002
Create Date: 2026-02-25

IMPORTANT — Run this verification query on staging BEFORE upgrade:

    SELECT DISTINCT p.fournisseur
    FROM produits p
    LEFT JOIN fournisseurs f ON p.fournisseur = f.nom
    WHERE f.nom IS NULL;

    -- If non-empty: the upgrade() auto-inserts missing fournisseurs.
    -- Review the list to confirm they are real suppliers, not data errors.

FK: produits.fournisseur -> fournisseurs(nom)
    ON UPDATE CASCADE  (name change propagates)
    ON DELETE RESTRICT (can't delete supplier with products)
"""
from collections.abc import Sequence

from alembic import op

revision: str = "a003"
down_revision: str | None = "a002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Auto-insert fournisseurs referenced by produits but missing from fournisseurs table
    op.execute("""
        INSERT INTO fournisseurs (nom)
        SELECT DISTINCT p.fournisseur
        FROM produits p
        LEFT JOIN fournisseurs f ON p.fournisseur = f.nom
        WHERE f.nom IS NULL
          AND p.fournisseur IS NOT NULL
          AND p.fournisseur <> ''
        ON CONFLICT (nom) DO NOTHING
    """)

    op.execute("""
        ALTER TABLE produits
        ADD CONSTRAINT fk_produits_fournisseur
        FOREIGN KEY (fournisseur) REFERENCES fournisseurs(nom)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE produits DROP CONSTRAINT IF EXISTS fk_produits_fournisseur")
