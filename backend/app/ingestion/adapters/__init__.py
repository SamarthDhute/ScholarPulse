"""External ingestion adapters package."""

from backend.app.ingestion.adapters.base import BaseIngestionAdapter
from backend.app.ingestion.adapters.openalex import OpenAlexAdapter
from backend.app.ingestion.adapters.crossref import CrossrefAdapter

__all__ = [
    "BaseIngestionAdapter",
    "OpenAlexAdapter",
    "CrossrefAdapter",
]
