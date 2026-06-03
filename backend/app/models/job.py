import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PipelineJob(Base):
    __tablename__ = "pipeline_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    lead_name: Mapped[str] = mapped_column(Text, nullable=False)
    lead_company: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead_industry: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pain_point: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    funnel_stage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_channels: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), server_default=text("'queued'"), nullable=False)
    script: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    clips: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    final_video_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
