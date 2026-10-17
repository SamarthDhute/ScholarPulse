"""Pydantic v2 schemas for User Saved Library bookmarks."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SavePaperRequest(BaseModel):
    """Payload to save a paper to user library."""
    paper_id: uuid.UUID
    notes: Optional[str] = Field(None, max_length=1000)


class SavedPaperItem(BaseModel):
    """Saved paper representation."""
    id: uuid.UUID
    paper_id: uuid.UUID
    title: str
    notes: Optional[str] = None
    saved_at: datetime
    publication_year: Optional[int] = None
    doi: Optional[str] = None


class SavedLibraryResponse(BaseModel):
    """List of saved papers in library."""
    total: int
    items: List[SavedPaperItem] = Field(default_factory=list)
