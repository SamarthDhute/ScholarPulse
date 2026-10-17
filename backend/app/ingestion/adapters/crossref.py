"""Optional Crossref metadata ingestion adapter.

Adheres to ScholarPulse AGENTS.md Section 3 & 4:
Gracefully unavailable when offline; supports polite identification mailto.
"""

from typing import List, Dict, Any, Optional
import httpx
from backend.app.ingestion.adapters.base import BaseIngestionAdapter
from backend.app.core.logging import logger


class CrossrefAdapter(BaseIngestionAdapter):
    """Adapter for querying research metadata from Crossref API."""

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, mailto: Optional[str] = None, timeout: float = 10.0):
        super().__init__(source_name="crossref")
        self.mailto = mailto
        self.timeout = timeout

    def fetch_papers(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch papers from Crossref API and map to ScholarPulse schema."""
        headers = {}
        if self.mailto:
            headers["User-Agent"] = f"ScholarPulse/1.0 (mailto:{self.mailto})"

        params = {
            "query": query,
            "rows": min(limit, 50),
        }

        try:
            with httpx.Client(timeout=self.timeout, headers=headers) as client:
                response = client.get(self.BASE_URL, params=params)
                if response.status_code != 200:
                    logger.warning("Crossref returned status %d", response.status_code)
                    return []
                data = response.json()
        except Exception as e:
            logger.warning("Failed to connect to Crossref API: %s", str(e))
            return []

        items = data.get("message", {}).get("items", [])
        results: List[Dict[str, Any]] = []

        for item in items:
            title_list = item.get("title", [])
            title = title_list[0] if title_list else "Untitled"

            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip()
                if name:
                    authors.append(name)

            year = None
            published = item.get("published", {}).get("date-parts", [])
            if published and published[0]:
                year = published[0][0]

            results.append({
                "title": title,
                "abstract": item.get("abstract"),
                "publication_year": year,
                "doi": item.get("DOI"),
                "source_name": "crossref",
                "source_url": item.get("URL"),
                "external_id": item.get("DOI"),
                "document_type": item.get("type", "journal-article"),
                "language": item.get("language", "en"),
                "authors": authors,
                "categories": item.get("subject", [])[:3],
                "keywords": item.get("subject", [])[:10],
            })

        return results
