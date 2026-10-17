"""Paper retrieval and recommendation API controller.

Adheres to ScholarPulse SRS v1.0 Section 8.3 & 8.4:
- Paper details with authors, keywords, and categories
- Metadata filtering and bounded pagination
- Content-based related paper recommendations (FR-019)
"""

import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.schemas.paper import (
    PaperDetail,
    PaperBrief,
    PaperListResponse,
    RelatedPaperItem,
    AuthorBrief,
    KeywordBrief,
    CategoryBrief,
)
from backend.app.repositories.paper_repository import PaperRepository
from backend.app.data_science.service import DataScienceService
from backend.app.api.deps import get_paper_repository, get_ds_service
from backend.app.core.errors import NotFoundError, ValidationError

router = APIRouter()


@router.get(
    "/papers",
    response_model=PaperListResponse,
    status_code=status.HTTP_200_OK,
    summary="List research papers with metadata filters and pagination",
)
def list_papers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    year_from: Optional[int] = Query(None, ge=1900, le=2100),
    year_to: Optional[int] = Query(None, ge=1900, le=2100),
    author: Optional[str] = Query(None, description="Author name filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    keyword: Optional[str] = Query(None, description="Keyword filter"),
    paper_repo: PaperRepository = Depends(get_paper_repository),
) -> PaperListResponse:
    """Retrieve paginated list of research papers matching filter criteria."""
    if year_from is not None and year_to is not None and year_from > year_to:
        raise ValidationError(f"year_from ({year_from}) cannot exceed year_to ({year_to})")

    skip = (page - 1) * page_size
    papers, total = paper_repo.list_with_filters(
        year_from=year_from,
        year_to=year_to,
        author_name=author,
        category_name=category,
        keyword_term=keyword,
        skip=skip,
        limit=page_size,
    )

    items = []
    for p in papers:
        author_names = [pa.author.display_name for pa in p.authors if pa.author]
        cat_names = [pc.category.name for pc in p.categories if pc.category]
        kw_terms = [pk.keyword.display_term for pk in p.keywords if pk.keyword]

        items.append(
            PaperBrief(
                id=p.id,
                title=p.title,
                abstract=p.abstract,
                publication_year=p.publication_year,
                doi=p.doi,
                source_name=p.source_name,
                source_url=p.source_url,
                authors=author_names,
                categories=cat_names,
                keywords=kw_terms,
            )
        )

    return PaperListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get(
    "/papers/{id}",
    response_model=PaperDetail,
    status_code=status.HTTP_200_OK,
    summary="Get full metadata for a specific paper",
)
def get_paper_details(
    id: uuid.UUID,
    paper_repo: PaperRepository = Depends(get_paper_repository),
) -> PaperDetail:
    """Retrieve full canonical paper details by UUID."""
    paper = paper_repo.get_with_details(id)
    if not paper:
        raise NotFoundError(f"Paper with ID '{id}' was not found.")

    authors = [
        AuthorBrief(
            id=pa.author.id,
            display_name=pa.author.display_name,
            author_order=pa.author_order,
        )
        for pa in paper.authors
        if pa.author
    ]
    keywords = [
        KeywordBrief(
            id=pk.keyword.id,
            display_term=pk.keyword.display_term,
        )
        for pk in paper.keywords
        if pk.keyword
    ]
    categories = [
        CategoryBrief(
            id=pc.category.id,
            name=pc.category.name,
            label_source=pc.label_source,
            confidence=pc.confidence,
        )
        for pc in paper.categories
        if pc.category
    ]

    return PaperDetail(
        id=paper.id,
        title=paper.title,
        abstract=paper.abstract,
        publication_year=paper.publication_year,
        doi=paper.doi,
        source_name=paper.source_name,
        source_url=paper.source_url,
        external_id=paper.external_id,
        document_type=paper.document_type,
        language=paper.language,
        raw_metadata=paper.raw_metadata,
        authors=authors,
        keywords=keywords,
        categories=categories,
        created_at=paper.created_at,
        updated_at=paper.updated_at,
    )


@router.get(
    "/papers/{id}/related",
    response_model=List[RelatedPaperItem],
    status_code=status.HTTP_200_OK,
    summary="Get content-based related paper recommendations",
)
def get_related_papers(
    id: uuid.UUID,
    top_n: int = Query(5, ge=1, le=50, description="Maximum recommendations to return"),
    paper_repo: PaperRepository = Depends(get_paper_repository),
    ds_service: DataScienceService = Depends(get_ds_service),
) -> List[RelatedPaperItem]:
    """Retrieve content-similar papers based on TF-IDF cosine similarity excluding self."""
    paper = paper_repo.get(id)
    if not paper:
        # Check if paper exists in recommender index
        str_id = str(id)
        if str_id not in ds_service.recommender.id_to_idx:
            raise NotFoundError(f"Paper with ID '{id}' was not found.")

    target_id = str(paper.id) if paper else str(id)
    try:
        recommendations = ds_service.get_related_papers(paper_id=target_id, top_n=top_n)
    except KeyError:
        # Fallback by title / DOI if UUID not yet in recommender
        if paper and paper.doi and str(paper.doi) in ds_service.recommender.id_to_idx:
            recommendations = ds_service.get_related_papers(paper_id=str(paper.doi), top_n=top_n)
        elif paper and paper.external_id and str(paper.external_id) in ds_service.recommender.id_to_idx:
            recommendations = ds_service.get_related_papers(paper_id=str(paper.external_id), top_n=top_n)
        else:
            return []

    return [
        RelatedPaperItem(
            paper_id=r.paper_id,
            title=r.title,
            similarity_score=r.similarity_score,
            shared_keywords=r.shared_keywords,
            category=r.category,
            publication_year=r.publication_year,
        )
        for r in recommendations
    ]
