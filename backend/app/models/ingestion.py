"""SQLAlchemy 2.0 model for tracking data ingestion runs.

Adheres to ScholarPulse SRS v1.0 Section 6.3:
Tracks source imports, runtime status, record counts, and failure summaries.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Uuid,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class IngestionRun(Base):
    """Execution log and metrics for research metadata import runs."""

    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="started", index=True)  # started, completed, failed
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    records_seen: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
