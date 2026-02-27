"""Update produits unique constraint to include user_id for multi-tenant

Revision ID: a006
Revises: a005
Create Date: 2026-02-26

- Drop old UNIQUE(designation_raw, fournisseur)
- Add UNIQUE NULLS NOT DISTINCT (designation_raw, fournisseur, user_id)
  (PostgreSQL 15+)
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a006"
down_revision: Union[str, None] = "a005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old unique constraint (designation_raw, fournisseur) - common PostgreSQL names
    op.execute("ALTER TABLE produits DROP CONSTRAINT IF EXISTS produits_designation_raw_fournisseur_key")
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_produits_unique_designation_fournisseur_user
        ON produits (designation_raw, fournisseur, user_id) NULLS NOT DISTINCT
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_produits_unique_designation_fournisseur_user")
    op.execute("""
        ALTER TABLE produits
        ADD CONSTRAINT produits_designation_raw_fournisseur_key
        UNIQUE (designation_raw, fournisseur)
    """)
