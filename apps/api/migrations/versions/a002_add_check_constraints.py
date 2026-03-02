"""Add CHECK constraints on status/role/confidence/source columns

Revision ID: a002
Revises: a001
Create Date: 2026-02-25

Constraints added:
  - jobs.status       IN ('processing', 'completed', 'error')
  - users.role        IN ('user', 'admin')
  - produits.confidence IN ('high', 'low')
  - produits.source   IN ('pc', 'mobile', 'watchdog')
"""
from collections.abc import Sequence

from alembic import op

revision: str = "a002"
down_revision: str | None = "a001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Idempotent: skip if constraint already exists
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_jobs_status') THEN
                ALTER TABLE jobs ADD CONSTRAINT ck_jobs_status
                CHECK (status IN ('processing', 'completed', 'error'));
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_users_role') THEN
                ALTER TABLE users ADD CONSTRAINT ck_users_role
                CHECK (role IN ('user', 'admin'));
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_produits_confidence') THEN
                ALTER TABLE produits ADD CONSTRAINT ck_produits_confidence
                CHECK (confidence IN ('high', 'low'));
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_produits_source') THEN
                ALTER TABLE produits ADD CONSTRAINT ck_produits_source
                CHECK (source IN ('pc', 'mobile', 'watchdog'));
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE produits DROP CONSTRAINT IF EXISTS ck_produits_source")
    op.execute("ALTER TABLE produits DROP CONSTRAINT IF EXISTS ck_produits_confidence")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_role")
    op.execute("ALTER TABLE jobs DROP CONSTRAINT IF EXISTS ck_jobs_status")
