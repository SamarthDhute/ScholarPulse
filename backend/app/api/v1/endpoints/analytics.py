"""Research Analytics API controller.

Adheres strictly to ScholarPulse SRS v1.0 Section 8.6:
- Overview collection metrics
- Chronological publication volume trends
- Category market share breakdown
- Top keyword frequency distribution
- Co-authorship collaboration network graph
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status

from backend.app.schemas.analytics import (
    OverviewSummary,
    TrendItem,
    CategoryShare,
    KeywordShare,
    CollaborationNetwork,
    CollaborationNode,
    CollaborationEdge,
    TopCollaboratorPair,
)
from backend.app.data_science.service import DataScienceService
from backend.app.api.deps import get_ds_service
from backend.app.core.errors import ValidationError

router = APIRouter()


import os
import json

def _get_corpus_papers(ds_service: DataScienceService) -> List[dict]:
    """Extract unique corpus papers from recommender data store, with dataset fallback."""
    papers = list(ds_service.recommender.papers_data.values())
    if not papers:
        sample_dataset = os.path.join("datasets", "raw", "sample_papers.json")
        if os.path.exists(sample_dataset):
            try:
                with open(sample_dataset, "r", encoding="utf-8") as f:
                    raw_papers = json.load(f)
                    ds_service.fit_recommender(raw_papers)
                    papers = list(ds_service.recommender.papers_data.values())
            except Exception:
                pass

    seen_ids = set()
    unique_papers = []
    for p in papers:
        pid = p.get("id") or p.get("doi") or p.get("title")
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            unique_papers.append(p)
    return unique_papers


@router.get(
    "/analytics/overview",
    response_model=OverviewSummary,
    status_code=status.HTTP_200_OK,
    summary="Get collection overview statistics",
)
def get_overview(
    year_min: Optional[int] = Query(None, ge=1900, le=2100),
    year_max: Optional[int] = Query(None, ge=1900, le=2100),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> OverviewSummary:
    """Retrieve high-level statistics for research paper collection."""
    if year_min is not None and year_max is not None and year_min > year_max:
        raise ValidationError(f"year_min ({year_min}) cannot exceed year_max ({year_max})")

    papers = _get_corpus_papers(ds_service)
    summary = ds_service.analytics.get_overview_summary(papers, year_min=year_min, year_max=year_max)
    return OverviewSummary(**summary)


@router.get(
    "/analytics/trends",
    response_model=List[TrendItem],
    status_code=status.HTTP_200_OK,
    summary="Get chronological publication trends and growth",
)
def get_publication_trends(
    year_min: Optional[int] = Query(None, ge=1900, le=2100),
    year_max: Optional[int] = Query(None, ge=1900, le=2100),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> List[TrendItem]:
    """Retrieve yearly publication counts and percentage growth."""
    if year_min is not None and year_max is not None and year_min > year_max:
        raise ValidationError(f"year_min ({year_min}) cannot exceed year_max ({year_max})")

    papers = _get_corpus_papers(ds_service)
    trends = ds_service.analytics.get_publication_trends(papers, year_min=year_min, year_max=year_max)
    return [TrendItem(**t) for t in trends]


@router.get(
    "/analytics/categories",
    response_model=List[CategoryShare],
    status_code=status.HTTP_200_OK,
    summary="Get category distribution and percentage share",
)
def get_category_distribution(
    year_min: Optional[int] = Query(None, ge=1900, le=2100),
    year_max: Optional[int] = Query(None, ge=1900, le=2100),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> List[CategoryShare]:
    """Retrieve category counts and market share."""
    papers = _get_corpus_papers(ds_service)
    categories = ds_service.analytics.get_category_distribution(papers, year_min=year_min, year_max=year_max)
    return [CategoryShare(**c) for c in categories]


@router.get(
    "/analytics/keywords",
    response_model=List[KeywordShare],
    status_code=status.HTTP_200_OK,
    summary="Get top recurring keywords with frequency and share",
)
def get_keyword_distribution(
    top_n: int = Query(20, ge=1, le=100),
    year_min: Optional[int] = Query(None, ge=1900, le=2100),
    year_max: Optional[int] = Query(None, ge=1900, le=2100),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> List[KeywordShare]:
    """Retrieve top recurring keywords across collection."""
    papers = _get_corpus_papers(ds_service)
    keywords = ds_service.analytics.get_keyword_distribution(papers, top_n=top_n, year_min=year_min, year_max=year_max)
    return [KeywordShare(**k) for k in keywords]


@router.get(
    "/analytics/collaboration-network",
    response_model=CollaborationNetwork,
    status_code=status.HTTP_200_OK,
    summary="Get co-authorship collaboration network graph",
)
def get_collaboration_network(
    min_collaborations: int = Query(1, ge=1),
    year_min: Optional[int] = Query(None, ge=1900, le=2100),
    year_max: Optional[int] = Query(None, ge=1900, le=2100),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> CollaborationNetwork:
    """Construct and return author collaboration graph nodes and links."""
    papers = _get_corpus_papers(ds_service)
    net = ds_service.analytics.get_coauthorship_network(
        papers, min_collaborations=min_collaborations, year_min=year_min, year_max=year_max
    )
    return CollaborationNetwork(
        total_nodes=net["total_nodes"],
        total_edges=net["total_edges"],
        nodes=[CollaborationNode(**n) for n in net["nodes"]],
        edges=[CollaborationEdge(**e) for e in net["edges"]],
        top_collaborators=[TopCollaboratorPair(**p) for p in net["top_collaborators"]],
    )
