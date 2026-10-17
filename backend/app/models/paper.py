"""SQLAlchemy 2.0 models for Research Papers, Authors, Keywords, and Categories.

Adheres strictly to ScholarPulse SRS v1.0 Section 6.2 and 6.3:
- UUID primary keys
- Proper many-to-many relationship tables with order, origin, and label_source
- Normalized fields with unique constraints and indexing
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from sqlalchemy import (
    String,
    Text,
    SmallInteger,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    Uuid,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class Paper(Base):
    """Canonical research paper entity."""

    __tablename__ = "papers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publication_year: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, index=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="en")
    raw_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    normalized_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    authors: Mapped[List["PaperAuthor"]] = relationship(
        "PaperAuthor",
        back_populates="paper",
        cascade="all, delete-orphan",
        order_by="PaperAuthor.author_order",
    )
    keywords: Mapped[List["PaperKeyword"]] = relationship(
        "PaperKeyword",
        back_populates="paper",
        cascade="all, delete-orphan",
    )
    categories: Mapped[List["PaperCategory"]] = relationship(
        "PaperCategory",
        back_populates="paper",
        cascade="all, delete-orphan",
    )
    saved_by: Mapped[List["SavedPaper"]] = relationship(
        "SavedPaper",
        back_populates="paper",
        cascade="all, delete-orphan",
    )


class Author(Base):
    """Normalized author entity."""

    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    papers: Mapped[List["PaperAuthor"]] = relationship(
        "PaperAuthor",
        back_populates="author",
        cascade="all, delete-orphan",
    )


class PaperAuthor(Base):
    """Association table linking papers to authors with explicit order."""

    __tablename__ = "paper_authors"

    paper_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)
    author_order: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("paper_id", "author_order", name="uq_paper_author_order"),
    )

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="authors")
    author: Mapped["Author"] = relationship("Author", back_populates="papers")


class Keyword(Base):
    """Normalized keyword vocabulary."""

    __tablename__ = "keywords"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    display_term: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_term: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    papers: Mapped[List["PaperKeyword"]] = relationship(
        "PaperKeyword",
        back_populates="keyword",
        cascade="all, delete-orphan",
    )


class PaperKeyword(Base):
    """Association table linking papers to keywords with origin tracking."""

    __tablename__ = "paper_keywords"

    paper_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    keyword_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)
    origin: Mapped[str] = mapped_column(String(50), primary_key=True, default="source")  # source, manual, extracted

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="keywords")
    keyword: Mapped["Keyword"] = relationship("Keyword", back_populates="papers")


class Category(Base):
    """Research taxonomy category."""

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    papers: Mapped[List["PaperCategory"]] = relationship(
        "PaperCategory",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class PaperCategory(Base):
    """Association table connecting papers to categories with provenance."""

    __tablename__ = "paper_categories"

    paper_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    label_source: Mapped[str] = mapped_column(String(50), primary_key=True, default="verified")  # verified vs predicted
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="categories")
    category: Mapped["Category"] = relationship("Category", back_populates="papers")


# Forward reference import for type annotations
from backend.app.models.user import SavedPaper  # noqa: E402
