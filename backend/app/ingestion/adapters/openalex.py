"""Optional OpenAlex metadata ingestion adapter.

Adheres to ScholarPulse AGENTS.md Section 3 & 4:
Gracefully unavailable when offline or credentials are missing.
"""

from typing import List, Dict, Any, Optional
import httpx
from backend.app.ingestion.adapters.base import BaseIngestionAdapter
from backend.app.core.logging import logger


class OpenAlexAdapter(BaseIngestionAdapter):
    """Adapter for querying and normalizing research metadata from OpenAlex API."""

    BASE_URL = "https://api.openalex.org/works"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 10.0):
        super().__init__(source_name="openalex", api_key=api_key)
        self.timeout = timeout

    def fetch_papers(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch papers from OpenAlex and map to ScholarPulse schema."""
        params = {
            "search": query,
            "per_page": min(limit, 50),
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(self.BASE_URL, params=params)
                if response.status_code != 200:
                    logger.warning("OpenAlex returned status %d", response.status_code)
                    return []
                data = response.json()
        except Exception as e:
            logger.warning("Failed to connect to OpenAlex API: %s", str(e))
            return []

        results: List[Dict[str, Any]] = []
        for item in data.get("results", []):
            # Parse authors
            authors = []
            for authorship in item.get("authorships", []):
                author_obj = authorship.get("author", {})
                if author_obj.get("display_name"):
                    authors.append(author_obj["display_name"])

            # Parse concepts / categories
            categories = [c.get("display_name") for c in item.get("concepts", []) if c.get("display_name")]

            # Parse keywords
            keywords = [k.get("keyword") for k in item.get("keywords", []) if k.get("keyword")]

            # Invert abstract index if present
            abstract = None
            abstract_inverted = item.get("abstract_inverted_index")
            if abstract_inverted and isinstance(abstract_inverted, dict):
                word_positions = []
                for word, positions in abstract_inverted.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join(w for _, w in word_positions)

            results.append({
                "title": item.get("title") or "Untitled",
                "abstract": abstract,
                "publication_year": item.get("publication_year"),
                "doi": item.get("doi"),
                "source_name": "openalex",
                "source_url": item.get("id"),
                "external_id": item.get("id"),
                "document_type": item.get("type", "paper"),
                "language": item.get("language", "en"),
                "authors": authors,
                "categories": categories[:3],
                "keywords": keywords[:10],
            })

        return results
