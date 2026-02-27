"""Add user_id to produits/factures, CHECK constraints, and performance indexes

Revision ID: a005
Revises: a004
Create Date: 2026-02-26

- user_id on produits, factures (nullable, REFERENCES users(id))
- CHECK prix_brut_ht>=0, prix_remise_ht>=0, remise_pct BETWEEN 0 AND 100
- idx_produits_user_id, idx_produits_user_famille, idx_produits_user_fournisseur
- idx_factures_user_id, idx_factures_user_date
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a005"
down_revision: Union[str, None] = "a004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_id sur produits/factures si absent (compatibilité schémas anciens)
    op.execute("""
        ALTER TABLE produits
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
    """)
    op.execute("""
        ALTER TABLE factures
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_factures_user_id ON factures(user_id)")

    # Fix invalid data before adding CHECK constraints
    op.execute("UPDATE produits SET prix_brut_ht = 0 WHERE prix_brut_ht < 0")
    op.execute("UPDATE produits SET prix_remise_ht = 0 WHERE prix_remise_ht < 0")
    op.execute("""
        UPDATE produits SET remise_pct = GREATEST(0, LEAST(100, COALESCE(remise_pct, 0)))
        WHERE remise_pct < 0 OR remise_pct > 100
    """)
    op.execute("""
        ALTER TABLE produits ADD CONSTRAINT ck_produits_prix_brut_ht CHECK (prix_brut_ht >= 0)
    """)
    op.execute("""
        ALTER TABLE produits ADD CONSTRAINT ck_produits_prix_remise_ht CHECK (prix_remise_ht >= 0)
    """)
    op.execute("""
        ALTER TABLE produits ADD CONSTRAINT ck_produits_remise_pct CHECK (remise_pct BETWEEN 0 AND 100)
    """)

    # Indexes performance
    op.execute("CREATE INDEX IF NOT EXISTS idx_produits_user_id ON produits(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_produits_user_famille ON produits(user_id, famille)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_produits_user_fournisseur ON produits(user_id, fournisseur)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_factures_user_date ON factures(user_id, created_at DESC)")


def downgrade() -> None:
    op.execute("ALTER TABLE produits DROP CONSTRAINT IF EXISTS ck_produits_remise_pct")
    op.execute("ALTER TABLE produits DROP CONSTRAINT IF EXISTS ck_produits_prix_remise_ht")
    op.execute("ALTER TABLE produits DROP CONSTRAINT IF EXISTS ck_produits_prix_brut_ht")
    op.execute("DROP INDEX IF EXISTS idx_factures_user_date")
    op.execute("DROP INDEX IF EXISTS idx_factures_user_id")
    op.execute("DROP INDEX IF EXISTS idx_produits_user_fournisseur")
    op.execute("DROP INDEX IF EXISTS idx_produits_user_famille")
    op.execute("DROP INDEX IF EXISTS idx_produits_user_id")
