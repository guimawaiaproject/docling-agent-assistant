"""
Alembic environment — Docling Agent v3
Uses asyncpg via SQLAlchemy async engine (no extra sync driver needed).
"""

import asyncio
import os
import re
import ssl as ssl_module
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def _get_url_and_ssl() -> tuple[str, dict]:
    """Read DATABASE_URL from env, return (asyncpg_url, connect_args)."""
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL non définie — impossible de lancer les migrations.")

    needs_ssl = "sslmode=require" in url or "sslmode=verify" in url

    # Strip sslmode from URL — asyncpg doesn't accept it as a query param;
    # we pass ssl via connect_args instead.
    url = re.sub(r"[?&]sslmode=[^&]*", "", url)
    url = url.replace("?&", "?").rstrip("?")

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    connect_args: dict = {}
    if needs_ssl:
        ctx = ssl_module.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl_module.CERT_NONE
        connect_args["ssl"] = ctx

    return url, connect_args


def run_migrations_offline() -> None:
    """Generate SQL script without connecting to the database."""
    url, _ = _get_url_and_ssl()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    url, connect_args = _get_url_and_ssl()

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations against a live database (async)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
