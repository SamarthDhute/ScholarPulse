"""SQLAlchemy 2.0 models for Users and Saved Papers Library.

Adheres to ScholarPulse SRS v1.0 Section 6.3:
- User identity with role-based authorization support (user / admin)
- Isolated user library (SavedPaper) with composite primary key
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    """User account entity for authentication and saved research library."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=True)  # user, admin
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    saved_papers: Mapped[List["SavedPaper"]] = relationship(
        "SavedPaper",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class SavedPaper(Base):
    """Association table representing a user's saved research library."""

    __tablename__ = "saved_papers"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    paper_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_papers")
    paper: Mapped["Paper"] = relationship("Paper", back_populates="saved_by")


# Import Paper for type hinting and relationship resolution
from backend.app.models.paper import Paper  # noqa: E402
