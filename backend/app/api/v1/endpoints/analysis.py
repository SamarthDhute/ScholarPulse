"""Data Science Analysis API controller.

Adheres strictly to ScholarPulse SRS v1.0 Section 8.7 & 8.8:
- Category classification inference (/analysis/classify)
- Document clustering results and member papers (/analysis/clusters)
- Apriori association rules with threshold filtering (/analysis/association-rules)
"""

import uuid
from typing import Optional, Literal, List
from fastapi import APIRouter, Depends, Query, status

from backend.app.schemas.analysis import (
    ClassifyRequest,
    ClassifyResponse,
    PredictedCategory,
    ClustersResponse,
    ClusterSummarySchema,
    RepresentativePaperSchema,
    AssociationRulesResponse,
    AssociationRuleItem,
)
from backend.app.data_science.service import DataScienceService
from backend.app.repositories.paper_repository import PaperRepository
from backend.app.api.deps import get_ds_service, get_paper_repository
from backend.app.core.errors import ValidationError, NotFoundError

router = APIRouter()


@router.post(
    "/analysis/classify",
    response_model=ClassifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict research category for a text snippet or existing paper",
)
def classify_text_or_paper(
    payload: ClassifyRequest,
    ds_service: DataScienceService = Depends(get_ds_service),
    paper_repo: PaperRepository = Depends(get_paper_repository),
) -> ClassifyResponse:
    """Classify research paper content into subject categories."""
    if not payload.text and not payload.paper_id:
        raise ValidationError("Either 'text' or 'paper_id' must be provided.")

    if payload.text and payload.paper_id:
        raise ValidationError("Provide either 'text' or 'paper_id', not both.")

    if payload.paper_id:
        # Try parsing UUID
        try:
            p_uuid = uuid.UUID(payload.paper_id)
            paper = paper_repo.get(p_uuid)
        except ValueError:
            paper = None

        if paper:
            text_to_classify = f"{paper.title}. {paper.abstract or ''}".strip()
        elif payload.paper_id in ds_service.recommender.papers_data:
            meta = ds_service.recommender.papers_data[payload.paper_id]
            text_to_classify = f"{meta['title']}. {meta.get('abstract', '')}".strip()
        else:
            raise NotFoundError(f"Paper with ID '{payload.paper_id}' not found.")
    else:
        text_to_classify = payload.text.strip()
        if not text_to_classify:
            raise ValidationError("Provided 'text' cannot be empty or whitespace.")

    scored_categories = ds_service.classify_text(text_to_classify, top_k=payload.top_k)

    return ClassifyResponse(
        paper_id=payload.paper_id,
        predicted_categories=[
            PredictedCategory(name=c["name"], score=c["score"])
            for c in scored_categories
        ],
        model_version=ds_service.classifier.model_version,
    )


@router.get(
    "/analysis/clusters",
    response_model=ClustersResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document clustering groupings and topic labels",
)
def get_clusters(
    method: Literal["kmeans", "hierarchical"] = Query("kmeans", description="Clustering algorithm"),
    n_clusters: int = Query(4, ge=2, le=10, description="Target cluster count"),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> ClustersResponse:
    """Retrieve unsupervised document clusters and semantic topic labels."""
    # If last result matches requested parameters, return it; otherwise re-cluster
    last_res = ds_service.clustering.last_result
    if last_res and last_res.method == method and last_res.n_clusters == n_clusters:
        result = last_res
    else:
        sample_papers = list(ds_service.recommender.papers_data.values())
        if not sample_papers:
            raise NotFoundError("No paper collection available for clustering.")
        result = ds_service.cluster_corpus(sample_papers, n_clusters=n_clusters, method=method)

    cluster_schemas = [
        ClusterSummarySchema(
            cluster_id=c.cluster_id,
            label=c.label,
            size=c.size,
            top_terms=c.top_terms,
            representative_papers=[
                RepresentativePaperSchema(
                    paper_id=p.paper_id,
                    title=p.title,
                    similarity_to_centroid=p.similarity_to_centroid,
                    category=p.category,
                )
                for p in c.representative_papers
            ],
            paper_ids=c.paper_ids,
        )
        for c in result.clusters
    ]

    return ClustersResponse(
        model_version=result.model_version,
        method=result.method,
        n_clusters=result.n_clusters,
        total_documents=result.total_documents,
        silhouette_score=result.silhouette_score,
        inertia=result.inertia,
        clusters=cluster_schemas,
    )


@router.get(
    "/analysis/clusters/{cluster_id}/papers",
    status_code=status.HTTP_200_OK,
    summary="Get list of papers belonging to a specific cluster",
)
def get_cluster_papers(
    cluster_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ds_service: DataScienceService = Depends(get_ds_service),
):
    """Retrieve paginated member papers for a given cluster."""
    last_res = ds_service.clustering.last_result
    if not last_res:
        sample_papers = list(ds_service.recommender.papers_data.values())
        last_res = ds_service.cluster_corpus(sample_papers, n_clusters=4, method="kmeans")

    target_cluster = next((c for c in last_res.clusters if c.cluster_id == cluster_id), None)
    if not target_cluster:
        raise NotFoundError(f"Cluster with ID '{cluster_id}' not found.")

    paper_ids = target_cluster.paper_ids
    total = len(paper_ids)
    start_idx = (page - 1) * page_size
    paged_ids = paper_ids[start_idx : start_idx + page_size]

    papers = []
    for pid in paged_ids:
        meta = ds_service.recommender.papers_data.get(pid, {})
        papers.append({
            "paper_id": pid,
            "title": meta.get("title", f"Paper {pid}"),
            "category": meta.get("category"),
            "publication_year": meta.get("publication_year"),
        })

    return {
        "cluster_id": cluster_id,
        "label": target_cluster.label,
        "total": total,
        "page": page,
        "page_size": page_size,
        "papers": papers,
    }


@router.get(
    "/analysis/association-rules",
    response_model=AssociationRulesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get mined keyword association rules with thresholds and pagination",
)
def get_association_rules(
    min_support: float = Query(0.04, gt=0.0, le=1.0, description="Minimum itemset support"),
    min_confidence: float = Query(0.3, gt=0.0, le=1.0, description="Minimum rule confidence"),
    min_lift: float = Query(1.0, ge=0.0, description="Minimum rule lift"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> AssociationRulesResponse:
    """Retrieve frequent keyword itemsets and association rules."""
    # Check if existing mining results match parameters
    miner = ds_service.association_miner
    last_res = miner.last_result

    if (
        not last_res
        or last_res.min_support != min_support
        or last_res.min_confidence != min_confidence
        or last_res.min_lift != min_lift
    ):
        papers = list(ds_service.recommender.papers_data.values())
        last_res = ds_service.mine_association_rules(
            papers=papers,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
        )

    paginated = miner.paginate_rules(page=page, page_size=page_size)

    rule_items = [
        AssociationRuleItem(
            antecedents=r["antecedents"],
            consequents=r["consequents"],
            support=r["support"],
            confidence=r["confidence"],
            lift=r["lift"],
            leverage=r["leverage"],
            conviction=r["conviction"],
        )
        for r in paginated["rules"]
    ]

    return AssociationRulesResponse(
        page=paginated["page"],
        page_size=paginated["page_size"],
        total_rules=paginated["total_rules"],
        total_pages=paginated["total_pages"],
        min_support=paginated["min_support"],
        min_confidence=paginated["min_confidence"],
        min_lift=paginated["min_lift"],
        model_version=paginated["model_version"],
        rules=rule_items,
    )
