"""Add idx_jobs_user_id and ck_factures_statut

Revision ID: a007
Revises: a006
Create Date: 2026-03-01

- idx_jobs_user_id: index for filtering jobs by user (multi-tenant)
- ck_factures_statut: CHECK constraint on factures.statut
"""
from collections.abc import Sequence

from alembic import op

revision: str = "a007"
down_revision: str | None = "a006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)")
    op.execute("""
        DO $$
        BEGIN
            ALTER TABLE factures
            ADD CONSTRAINT ck_factures_statut
            CHECK (statut IN ('traite', 'erreur', 'en_attente'));
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_jobs_user_id")
    op.execute("ALTER TABLE factures DROP CONSTRAINT IF EXISTS ck_factures_statut")
