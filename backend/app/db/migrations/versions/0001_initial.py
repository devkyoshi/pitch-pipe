"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-03 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.create_table(
        "pipeline_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("lead_name", sa.Text(), nullable=False),
        sa.Column("lead_company", sa.Text(), nullable=True),
        sa.Column("lead_industry", sa.Text(), nullable=True),
        sa.Column("pain_point", sa.Text(), nullable=True),
        sa.Column("funnel_stage", sa.Text(), nullable=True),
        sa.Column("target_channels", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(50), server_default=sa.text("'queued'"), nullable=False),
        sa.Column("script", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("clips", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("final_video_url", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipeline_jobs_status", "pipeline_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_jobs_status", table_name="pipeline_jobs")
    op.drop_table("pipeline_jobs")
