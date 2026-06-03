import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Load .env from the backend root (two levels up from this file)
_env_file = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env_file)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models.job import Base  # noqa: E402

target_metadata = Base.metadata


def _get_sync_url() -> str:
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Make sure .env exists in the backend/ directory."
        )
    # Alembic uses sync psycopg2 — strip the asyncpg driver
    return db_url.replace("postgresql+asyncpg://", "postgresql://")


def run_migrations_offline() -> None:
    url = _get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = _get_sync_url()
    connectable = engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
