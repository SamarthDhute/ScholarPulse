"""SQLAlchemy 2.0 models for Relevance Judgments and Evaluation Runs & Metrics.

Adheres to ScholarPulse SRS v1.0 Section 6.3:
Supports repeatable, objective Information Retrieval and Data Science evaluation.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    String,
    SmallInteger,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Uuid,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class RelevanceJudgment(Base):
    """Ground-truth relevance label for a query-paper pair."""

    __tablename__ = "relevance_judgments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    query_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    paper_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    relevance_grade: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0: non-relevant, 1: relevant, etc.
    judge_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("query_id", "paper_id", "dataset_version", name="uq_query_paper_dataset"),
    )

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper")


class EvaluationRun(Base):
    """Metadata and execution record for a search or model evaluation run."""

    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evaluation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # search, classification, clustering
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    query_set_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_or_ranker: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")

    # Relationships
    metrics: Mapped[List["EvaluationMetric"]] = relationship(
        "EvaluationMetric",
        back_populates="evaluation_run",
        cascade="all, delete-orphan",
    )


class EvaluationMetric(Base):
    """Individual metric score associated with an evaluation run."""

    __tablename__ = "evaluation_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # MAP, NDCG, Precision, Recall, F1
    cutoff_k: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    evaluation_run: Mapped["EvaluationRun"] = relationship("EvaluationRun", back_populates="metrics")


# Import Paper for relationship
from backend.app.models.paper import Paper  # noqa: E402
