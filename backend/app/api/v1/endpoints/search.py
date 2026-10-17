"""Search API controller.

Adheres to ScholarPulse SRS v1.0 Section 8.2:
- Supports BM25 (default), TF-IDF, Language Model, and Boolean retrieval
- Explainable term scoring breakdowns
- Passage snippets with HTML mark tags
- Metadata filters (year_min, year_max, category)
- 1-indexed pagination
"""

from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, status
from backend.app.schemas.search import SearchResponse, SearchResultItem
from backend.app.retrieval.search_service import SearchService
from backend.app.api.deps import get_search_service
from backend.app.core.errors import ValidationError

router = APIRouter()


@router.get(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search papers using Information Retrieval algorithms",
)
def search_papers(
    query: str = Query(..., min_length=1, max_length=500, description="Search query string"),
    method: Literal["bm25", "tfidf", "language_model", "boolean"] = Query(
        "bm25", description="IR Ranking algorithm (default: bm25)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page"),
    year_min: Optional[int] = Query(None, ge=1900, le=2100, description="Minimum publication year"),
    year_max: Optional[int] = Query(None, ge=1900, le=2100, description="Maximum publication year"),
    category: Optional[str] = Query(None, description="Category filter (case-insensitive)"),
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Execute information retrieval search over academic papers."""
    if year_min is not None and year_max is not None and year_min > year_max:
        raise ValidationError(
            f"year_min ({year_min}) cannot be greater than year_max ({year_max})"
        )

    response = search_service.search(
        query=query,
        method=method,
        top_k=page_size,
        page=page,
        year_min=year_min,
        year_max=year_max,
        category=category,
    )

    items = [
        SearchResultItem(
            doc_id=r.doc_id,
            score=round(r.score, 4),
            rank=r.rank,
            method=r.method,
            term_scores=r.term_scores,
            metadata=r.metadata,
            snippet=r.snippet,
            highlighted_snippet=r.highlighted_snippet,
        )
        for r in response.results
    ]

    return SearchResponse(
        query=response.query,
        method=response.method,
        total_hits=response.total_hits,
        page=response.page,
        page_size=response.page_size,
        results=items,
    )
