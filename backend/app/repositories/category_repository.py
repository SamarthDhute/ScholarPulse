"""Category repository for research taxonomy categories."""

from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.paper import Category
from backend.app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Data access repository for Category entities."""

    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_by_name(self, name: str) -> Optional[Category]:
        """Find category by unique name."""
        stmt = select(Category).where(Category.name == name)
        return self.db.scalars(stmt).first()

    def get_or_create(self, name: str, description: Optional[str] = None) -> Category:
        """Find existing category or create a new category record."""
        existing = self.get_by_name(name)
        if existing:
            return existing
        category = Category(
            name=name,
            description=description,
        )
        return self.create(category)
