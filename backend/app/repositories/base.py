"""Generic BaseRepository offering standard CRUD operations for SQLAlchemy models."""

from typing import Generic, TypeVar, Type, Optional, List, Any, Sequence
import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from backend.app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository for CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        """Retrieve entity by primary key."""
        return self.db.get(self.model, id)

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """List entities with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def count(self) -> int:
        """Count total entities in table."""
        stmt = select(func.count()).select_from(self.model)
        return self.db.scalar(stmt) or 0

    def create(self, entity: ModelType) -> ModelType:
        """Add and commit new entity."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        """Commit modified entity."""
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        """Delete entity and commit."""
        self.db.delete(entity)
        self.db.commit()
