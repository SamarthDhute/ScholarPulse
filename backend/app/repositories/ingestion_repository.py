"""Ingestion repository for recording data import runs and statistics."""

from typing import Optional, Sequence, Dict, Any
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from backend.app.models.ingestion import IngestionRun
from backend.app.repositories.base import BaseRepository


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class IngestionRepository(BaseRepository[IngestionRun]):
    """Data access repository for IngestionRun records."""

    def __init__(self, db: Session):
        super().__init__(IngestionRun, db)

    def start_run(self, source_name: str) -> IngestionRun:
        """Create and persist a new running ingestion log."""
        run = IngestionRun(
            source_name=source_name,
            status="started",
            started_at=utc_now(),
        )
        return self.create(run)

    def finish_run(
        self,
        run_id: uuid.UUID,
        status: str,
        records_seen: int,
        records_created: int,
        records_updated: int,
        records_skipped: int,
        error_count: int,
        summary: Optional[Dict[str, Any]] = None,
    ) -> Optional[IngestionRun]:
        """Update and finalize an ingestion run with counts and summary."""
        run = self.get_by_id(run_id)
        if not run:
            return None
        run.status = status
        run.finished_at = utc_now()
        run.records_seen = records_seen
        run.records_created = records_created
        run.records_updated = records_updated
        run.records_skipped = records_skipped
        run.error_count = error_count
        run.summary = summary
        return self.update(run)

    def list_recent(self, limit: int = 20) -> Sequence[IngestionRun]:
        """List most recent ingestion runs."""
        stmt = select(IngestionRun).order_by(desc(IngestionRun.started_at)).limit(limit)
        return self.db.scalars(stmt).all()

    def list(self, limit: int = 20) -> Sequence[IngestionRun]:
        """List recent ingestion runs (alias for list_recent)."""
        return self.list_recent(limit=limit)
