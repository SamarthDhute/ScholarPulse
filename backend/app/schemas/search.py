"""Pydantic v2 schemas for Search requests and responses."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """Individual ranked paper search result."""
    doc_id: str = Field(..., description="Document identifier")
    score: float = Field(..., description="Relevance score assigned by ranker")
    rank: int = Field(..., description="1-indexed result position")
    method: str = Field(..., description="Algorithm used (bm25, tfidf, language_model, boolean)")
    term_scores: Dict[str, float] = Field(default_factory=dict, description="Explainable term breakdown")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Paper metadata (title, year, etc.)")
    snippet: Optional[str] = Field(None, description="Plain text snippet from abstract")
    highlighted_snippet: Optional[str] = Field(None, description="HTML marked passage snippet")


class SearchResponse(BaseModel):
    """Unified search response envelope."""
    query: str = Field(..., description="Original search query string")
    method: str = Field(..., description="Ranking algorithm applied")
    total_hits: int = Field(..., description="Total matching documents found")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Items per page")
    results: List[SearchResultItem] = Field(default_factory=list, description="Ranked list of results")
