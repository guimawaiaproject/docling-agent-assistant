"""Add prix_anonymes table and user community consent columns

Revision ID: a008
Revises: a007
Create Date: 2026-03-01

- Table prix_anonymes for anonymous price sharing
- users.community_consent, users.zone_geo
"""
from collections.abc import Sequence

from alembic import op

revision: str = "a008"
down_revision: str | None = "a007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS community_consent BOOLEAN DEFAULT FALSE")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS zone_geo VARCHAR(10)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS prix_anonymes (
            id           SERIAL PRIMARY KEY,
            produit_hash TEXT NOT NULL,
            fournisseur  VARCHAR(200) NOT NULL,
            zone_geo     VARCHAR(10) NOT NULL,
            pays         CHAR(2) NOT NULL,
            prix_ht      NUMERIC(10,4) NOT NULL,
            date_facture DATE,
            created_at   TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_prix_anonymes_hash_zone ON prix_anonymes(produit_hash, zone_geo)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_prix_anonymes_fournisseur ON prix_anonymes(fournisseur)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS prix_anonymes")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS community_consent")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS zone_geo")
