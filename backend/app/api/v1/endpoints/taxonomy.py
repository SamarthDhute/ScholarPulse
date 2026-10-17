"""Categories and Keywords taxonomy API controller.

Adheres to ScholarPulse SRS v1.0 Section 8.5:
- Category taxonomy retrieval
- Keyword auto-completion / prefix search
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from backend.app.schemas.taxonomy import CategoryItem, KeywordItem
from backend.app.repositories.category_repository import CategoryRepository
from backend.app.repositories.keyword_repository import KeywordRepository
from backend.app.api.deps import get_category_repository, get_keyword_repository

router = APIRouter()


@router.get(
    "/categories",
    response_model=List[CategoryItem],
    status_code=status.HTTP_200_OK,
    summary="List research taxonomy categories",
)
def list_categories(
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> List[CategoryItem]:
    """Retrieve all academic subject categories with paper counts."""
    categories = category_repo.list_all()
    results = []
    for c in categories:
        count = len(c.papers) if hasattr(c, "papers") and c.papers else 0
        results.append(
            CategoryItem(
                id=c.id,
                name=c.name,
                description=c.description,
                paper_count=count,
            )
        )
    return sorted(results, key=lambda x: x.name)


@router.get(
    "/keywords",
    response_model=List[KeywordItem],
    status_code=status.HTTP_200_OK,
    summary="Search keyword vocabulary with prefix matching",
)
def search_keywords(
    prefix: Optional[str] = Query(None, description="Prefix search query string"),
    limit: int = Query(20, ge=1, le=100, description="Max keywords to return"),
    keyword_repo: KeywordRepository = Depends(get_keyword_repository),
) -> List[KeywordItem]:
    """Retrieve keywords for autocomplete and filtering."""
    if prefix:
        keywords = keyword_repo.find_by_prefix(prefix, limit=limit)
    else:
        keywords = keyword_repo.list(limit=limit)

    results = []
    for k in keywords:
        count = len(k.papers) if hasattr(k, "papers") and k.papers else 0
        results.append(
            KeywordItem(
                id=k.id,
                display_term=k.display_term,
                normalized_term=k.normalized_term,
                paper_count=count,
            )
        )
    return results
