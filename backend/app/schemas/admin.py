"""Pydantic v2 schemas for Administration and Ingestion endpoints."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Trigger ingestion batch run."""
    source_name: Optional[str] = Field("local_sample", description="Data source name")
    filepath: Optional[str] = Field(None, description="Optional path to local dataset file")


class IngestResponse(BaseModel):
    """Batch ingestion outcome."""
    run_id: str
    status: str
    total_processed: int
    created_count: int
    updated_count: int
    skipped_count: int
    error_count: int
