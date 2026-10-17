"""Pydantic v2 schemas for Research Analytics endpoints."""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class OverviewSummary(BaseModel):
    """Collection overview counts."""
    total_papers: int
    total_authors: int
    total_categories: int
    total_keywords: int
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    avg_authors_per_paper: float


class TrendItem(BaseModel):
    """Publication volume by year."""
    year: int
    count: int
    cumulative_count: int
    growth_percentage: Optional[float] = None


class CategoryShare(BaseModel):
    """Category share percentage."""
    category: str
    count: int
    percentage_share: float


class KeywordShare(BaseModel):
    """Keyword frequency item."""
    keyword: str
    count: int
    percentage_share: float


class AuthorItem(BaseModel):
    """Productive author item."""
    author: str
    paper_count: int


class CollaborationNode(BaseModel):
    """Network graph author node."""
    id: str
    name: str
    paper_count: int


class CollaborationEdge(BaseModel):
    """Network graph co-authorship edge."""
    source: str
    target: str
    weight: int
    paper_titles: List[str] = Field(default_factory=list)


class TopCollaboratorPair(BaseModel):
    """Top collaborating author pair."""
    author_1: str
    author_2: str
    joint_papers: int


class CollaborationNetwork(BaseModel):
    """Co-authorship collaboration network graph."""
    total_nodes: int
    total_edges: int
    nodes: List[CollaborationNode] = Field(default_factory=list)
    edges: List[CollaborationEdge] = Field(default_factory=list)
    top_collaborators: List[TopCollaboratorPair] = Field(default_factory=list)
