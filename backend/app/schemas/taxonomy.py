"""Pydantic v2 schemas for Category and Keyword endpoints."""

import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class CategoryItem(BaseModel):
    """Category taxonomy item."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    paper_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class KeywordItem(BaseModel):
    """Keyword vocabulary item."""
    id: uuid.UUID
    display_term: str
    normalized_term: str
    paper_count: Optional[int] = 0

    model_config = {"from_attributes": True}
