"""Pydantic v2 schemas for Search Evaluation endpoints."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class EvaluationReportItem(BaseModel):
    """Ranker evaluation metrics summary."""
    ranker_name: str
    num_queries: int
    mean_average_precision: float
    mean_reciprocal_rank: float
    precision_at_k: Dict[str, float]
    recall_at_k: Dict[str, float]
    ndcg_at_k: Dict[str, float]


class EvaluationResponse(BaseModel):
    """Multi-ranker evaluation benchmarking response."""
    dataset_version: str
    query_count: int
    reports: List[EvaluationReportItem] = Field(default_factory=list)
