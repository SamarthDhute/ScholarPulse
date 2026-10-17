"""Keyword repository for vocabulary management and term suggestions."""

from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.paper import Keyword
from backend.app.repositories.base import BaseRepository


class KeywordRepository(BaseRepository[Keyword]):
    """Data access repository for Keyword entities."""

    def __init__(self, db: Session):
        super().__init__(Keyword, db)

    def get_by_normalized_term(self, normalized_term: str) -> Optional[Keyword]:
        """Find keyword by normalized lowercase term."""
        stmt = select(Keyword).where(Keyword.normalized_term == normalized_term)
        return self.db.scalars(stmt).first()

    def get_or_create(self, display_term: str, normalized_term: str) -> Keyword:
        """Find existing keyword or create new one."""
        existing = self.get_by_normalized_term(normalized_term)
        if existing:
            return existing
        keyword = Keyword(
            display_term=display_term,
            normalized_term=normalized_term,
        )
        return self.create(keyword)

    def search_prefix(self, prefix: str, limit: int = 20) -> Sequence[Keyword]:
        """Prefix search for keywords (supports autocomplete / filters)."""
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Keyword)
            .options(selectinload(Keyword.papers))
            .where(Keyword.normalized_term.startswith(prefix.lower()))
            .order_by(Keyword.normalized_term)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def find_by_prefix(self, prefix: str, limit: int = 20) -> Sequence[Keyword]:
        """Prefix search alias for find_by_prefix."""
        return self.search_prefix(prefix=prefix, limit=limit)

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Keyword]:
        """List keywords with papers association eagerly loaded."""
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Keyword)
            .options(selectinload(Keyword.papers))
            .offset(skip)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()
