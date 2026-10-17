"""Pydantic v2 schemas for Data Science analysis endpoints (classification, clustering, association rules)."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    """Request payload for text or paper category prediction."""
    text: Optional[str] = Field(None, max_length=10000, description="Raw text snippet to categorize")
    paper_id: Optional[str] = Field(None, description="Database paper UUID or identifier")
    top_k: int = Field(3, ge=1, le=10, description="Number of category predictions to return")


class PredictedCategory(BaseModel):
    """Predicted category and confidence score."""
    name: str = Field(..., description="Predicted category name")
    score: float = Field(..., description="Prediction confidence score")


class ClassifyResponse(BaseModel):
    """Category classification response matching SRS 8.7 contract."""
    paper_id: Optional[str] = Field(None, description="Paper identifier if provided")
    predicted_categories: List[PredictedCategory] = Field(default_factory=list)
    model_version: str = Field(..., description="Classifier artifact version identifier")


class RepresentativePaperSchema(BaseModel):
    """Representative paper for a cluster."""
    paper_id: str
    title: str
    similarity_to_centroid: float
    category: Optional[str] = None


class ClusterSummarySchema(BaseModel):
    """Explainable topic cluster summary."""
    cluster_id: int
    label: str
    size: int
    top_terms: List[Dict[str, Any]] = Field(default_factory=list)
    representative_papers: List[RepresentativePaperSchema] = Field(default_factory=list)
    paper_ids: List[str] = Field(default_factory=list)


class ClustersResponse(BaseModel):
    """Document clustering response matching SRS 8.7."""
    model_version: str
    method: str
    n_clusters: int
    total_documents: int
    silhouette_score: float
    inertia: Optional[float] = None
    clusters: List[ClusterSummarySchema] = Field(default_factory=list)


class AssociationRuleItem(BaseModel):
    """Mined association rule."""
    antecedents: List[str]
    consequents: List[str]
    support: float
    confidence: float
    lift: float
    leverage: float
    conviction: float


class AssociationRulesResponse(BaseModel):
    """Paginated association rules response matching SRS 8.8."""
    page: int
    page_size: int
    total_rules: int
    total_pages: int
    min_support: float
    min_confidence: float
    min_lift: float
    model_version: str
    rules: List[AssociationRuleItem] = Field(default_factory=list)
