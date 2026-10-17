"""Abstract base adapter for external research metadata sources.

Adheres to ScholarPulse AGENTS.md Section 3:
External data providers are optional ingestion adapters, not hard dependencies for startup.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseIngestionAdapter(ABC):
    """Abstract interface for metadata providers (OpenAlex, Crossref, etc.)."""

    def __init__(self, source_name: str, api_key: Optional[str] = None):
        self.source_name = source_name
        self.api_key = api_key

    @abstractmethod
    def fetch_papers(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch papers matching query from the source provider."""
        pass
