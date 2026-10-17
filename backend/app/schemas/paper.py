"""Pydantic v2 schemas for Paper entities, details, and listing responses."""

import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class AuthorBrief(BaseModel):
    """Author summary."""
    id: uuid.UUID
    display_name: str
    author_order: Optional[int] = 0

    model_config = {"from_attributes": True}


class KeywordBrief(BaseModel):
    """Keyword summary."""
    id: uuid.UUID
    display_term: str

    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    """Category summary."""
    id: uuid.UUID
    name: str
    label_source: Optional[str] = "verified"
    confidence: Optional[float] = None

    model_config = {"from_attributes": True}


class PaperBrief(BaseModel):
    """Summary of a paper for list views and cards."""
    id: uuid.UUID
    title: str
    abstract: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    source_name: str
    source_url: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PaperDetail(BaseModel):
    """Complete canonical paper metadata."""
    id: uuid.UUID
    title: str
    abstract: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    source_name: str
    source_url: Optional[str] = None
    external_id: Optional[str] = None
    document_type: Optional[str] = None
    language: Optional[str] = "en"
    raw_metadata: Optional[Dict[str, Any]] = None
    authors: List[AuthorBrief] = Field(default_factory=list)
    keywords: List[KeywordBrief] = Field(default_factory=list)
    categories: List[CategoryBrief] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PaperListResponse(BaseModel):
    """Paginated paper list response."""
    total: int = Field(..., description="Total records matching filters")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    items: List[PaperBrief] = Field(default_factory=list)


class RelatedPaperItem(BaseModel):
    """Content-based recommended paper item."""
    paper_id: str
    title: str
    similarity_score: float
    shared_keywords: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    publication_year: Optional[int] = None
