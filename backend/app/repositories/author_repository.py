"""Author repository for querying and deduplicating authors."""

from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.paper import Author
from backend.app.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[Author]):
    """Data access repository for Author entities."""

    def __init__(self, db: Session):
        super().__init__(Author, db)

    def get_by_normalized_name(self, normalized_name: str) -> Optional[Author]:
        """Find author by normalized name."""
        stmt = select(Author).where(Author.normalized_name == normalized_name)
        return self.db.scalars(stmt).first()

    def get_or_create(self, display_name: str, normalized_name: str, external_id: Optional[str] = None) -> Author:
        """Find existing author or create new author record."""
        existing = self.get_by_normalized_name(normalized_name)
        if existing:
            return existing
        author = Author(
            display_name=display_name,
            normalized_name=normalized_name,
            external_id=external_id,
        )
        return self.create(author)
