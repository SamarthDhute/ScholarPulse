"""Ingestion module exports."""

from backend.app.ingestion.validation import validate_paper_payload
from backend.app.ingestion.deduplication import Deduplicator, DeduplicationResult
from backend.app.ingestion.service import IngestionService

__all__ = [
    "validate_paper_payload",
    "Deduplicator",
    "DeduplicationResult",
    "IngestionService",
]
