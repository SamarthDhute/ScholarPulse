"""Paper repository for querying and managing research papers."""

from typing import Optional, Sequence, List, Tuple
import uuid
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session, selectinload
from backend.app.models.paper import (
    Paper,
    PaperAuthor,
    Author,
    PaperKeyword,
    Keyword,
    PaperCategory,
    Category,
)
from backend.app.repositories.base import BaseRepository


class PaperRepository(BaseRepository[Paper]):
    """Data access repository for Paper entities."""

    def __init__(self, db: Session):
        super().__init__(Paper, db)

    def get_by_doi(self, doi: str) -> Optional[Paper]:
        """Find paper by normalized DOI."""
        stmt = select(Paper).where(Paper.doi == doi.lower().strip())
        return self.db.scalars(stmt).first()

    def get_by_external_id(self, source_name: str, external_id: str) -> Optional[Paper]:
        """Find paper by source name and external identifier."""
        stmt = select(Paper).where(
            and_(Paper.source_name == source_name, Paper.external_id == external_id)
        )
        return self.db.scalars(stmt).first()

    def get_with_details(self, paper_id: uuid.UUID) -> Optional[Paper]:
        """Retrieve paper with authors, keywords, and categories eagerly loaded."""
        stmt = (
            select(Paper)
            .where(Paper.id == paper_id)
            .options(
                selectinload(Paper.authors).selectinload(PaperAuthor.author),
                selectinload(Paper.keywords).selectinload(PaperKeyword.keyword),
                selectinload(Paper.categories).selectinload(PaperCategory.category),
            )
        )
        return self.db.scalars(stmt).first()

    def list_with_filters(
        self,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        author_name: Optional[str] = None,
        category_name: Optional[str] = None,
        keyword_term: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Paper], int]:
        """List papers with metadata filtering and return total count."""
        stmt = select(Paper).distinct()

        # Build filter criteria
        conditions = []
        if year_from is not None:
            conditions.append(Paper.publication_year >= year_from)
        if year_to is not None:
            conditions.append(Paper.publication_year <= year_to)
        if author_name:
            stmt = stmt.join(Paper.authors).join(PaperAuthor.author)
            conditions.append(Author.normalized_name.contains(author_name.lower().strip()))
        if category_name:
            stmt = stmt.join(Paper.categories).join(PaperCategory.category)
            conditions.append(Category.name.ilike(category_name.strip()))
        if keyword_term:
            stmt = stmt.join(Paper.keywords).join(PaperKeyword.keyword)
            conditions.append(Keyword.normalized_term == keyword_term.lower().strip())

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Count total matching records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        # Fetch page items
        paged_stmt = (
            stmt.options(
                selectinload(Paper.authors).selectinload(PaperAuthor.author),
                selectinload(Paper.keywords).selectinload(PaperKeyword.keyword),
                selectinload(Paper.categories).selectinload(PaperCategory.category),
            )
            .order_by(Paper.publication_year.desc().nullslast(), Paper.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(self.db.scalars(paged_stmt).all())
        return items, total
