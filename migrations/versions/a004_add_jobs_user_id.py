"""Add user_id to jobs for multi-tenant isolation

Revision ID: a004
Revises: a003
Create Date: 2026-02-26

Jobs are now scoped by user. get_job_status filters WHERE job_id=$1 AND user_id=$2.
Existing jobs have user_id=NULL and return 404 for all users.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a004"
down_revision: Union[str, None] = "a003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE jobs
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE jobs DROP COLUMN IF EXISTS user_id")
