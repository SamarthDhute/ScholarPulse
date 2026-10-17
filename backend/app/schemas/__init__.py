"""Pydantic schemas package for ScholarPulse API contracts."""

from backend.app.schemas.health import HealthResponse
from backend.app.schemas.search import SearchResultItem, SearchResponse
from backend.app.schemas.paper import (
    AuthorBrief,
    KeywordBrief,
    CategoryBrief,
    PaperBrief,
    PaperDetail,
    PaperListResponse,
    RelatedPaperItem,
)
from backend.app.schemas.taxonomy import CategoryItem, KeywordItem
from backend.app.schemas.analysis import (
    ClassifyRequest,
    PredictedCategory,
    ClassifyResponse,
    ClustersResponse,
    ClusterSummarySchema,
    RepresentativePaperSchema,
    AssociationRuleItem,
    AssociationRulesResponse,
)
from backend.app.schemas.analytics import (
    OverviewSummary,
    TrendItem,
    CategoryShare,
    KeywordShare,
    AuthorItem,
    CollaborationNode,
    CollaborationEdge,
    TopCollaboratorPair,
    CollaborationNetwork,
)
from backend.app.schemas.evaluation import EvaluationReportItem, EvaluationResponse
from backend.app.schemas.admin import IngestRequest, IngestResponse
from backend.app.schemas.library import SavePaperRequest, SavedPaperItem, SavedLibraryResponse

__all__ = [
    "HealthResponse",
    "SearchResultItem",
    "SearchResponse",
    "AuthorBrief",
    "KeywordBrief",
    "CategoryBrief",
    "PaperBrief",
    "PaperDetail",
    "PaperListResponse",
    "RelatedPaperItem",
    "CategoryItem",
    "KeywordItem",
    "ClassifyRequest",
    "PredictedCategory",
    "ClassifyResponse",
    "ClustersResponse",
    "ClusterSummarySchema",
    "RepresentativePaperSchema",
    "AssociationRuleItem",
    "AssociationRulesResponse",
    "OverviewSummary",
    "TrendItem",
    "CategoryShare",
    "KeywordShare",
    "AuthorItem",
    "CollaborationNode",
    "CollaborationEdge",
    "TopCollaboratorPair",
    "CollaborationNetwork",
    "EvaluationReportItem",
    "EvaluationResponse",
    "IngestRequest",
    "IngestResponse",
    "SavePaperRequest",
    "SavedPaperItem",
    "SavedLibraryResponse",
]
