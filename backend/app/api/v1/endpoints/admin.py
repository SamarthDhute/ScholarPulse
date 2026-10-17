"""Administration and Ingestion API controller.

Adheres to ScholarPulse SRS v1.0 Section 8.10:
- Trigger batch paper ingestion
- Track batch status, deduplication, and record counts
"""

import os
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from backend.app.schemas.admin import IngestRequest, IngestResponse
from backend.app.ingestion.service import IngestionService
from backend.app.repositories.ingestion_repository import IngestionRepository
from backend.app.api.deps import get_ingestion_service, get_db
from backend.app.core.errors import NotFoundError, ValidationError
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/admin/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger paper dataset ingestion run",
)
def trigger_ingestion(
    payload: IngestRequest = IngestRequest(),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    """Ingest papers from local dataset file into database."""
    target_path = payload.filepath or os.path.join("datasets", "raw", "sample_papers.json")
    if not os.path.exists(target_path):
        raise NotFoundError(f"Dataset file '{target_path}' not found.")

    run = ingestion_service.ingest_from_json_file(
        filepath=target_path,
        source_name=payload.source_name or "local_sample",
    )

    return IngestResponse(
        run_id=str(run.id),
        status=run.status,
        total_processed=run.records_seen,
        created_count=run.records_created,
        updated_count=run.records_updated,
        skipped_count=run.records_skipped,
        error_count=run.error_count,
    )


@router.get(
    "/admin/ingest/status",
    status_code=status.HTTP_200_OK,
    summary="Get recent ingestion runs history and status",
)
def get_ingestion_status(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Retrieve history of ingestion batches."""
    repo = IngestionRepository(db)
    runs = repo.list(limit=limit)

    return {
        "total_runs": len(runs),
        "runs": [
            {
                "run_id": str(r.id),
                "source_name": r.source_name,
                "status": r.status,
                "total_records": r.records_seen,
                "created_count": r.records_created,
                "updated_count": r.records_updated,
                "skipped_count": r.records_skipped,
                "error_count": r.error_count,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
            }
            for r in runs
        ],
    }
