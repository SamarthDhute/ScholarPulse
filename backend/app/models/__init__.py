"""SQLAlchemy models package exporting all database entities."""

from backend.app.models.paper import (
    Paper,
    Author,
    PaperAuthor,
    Keyword,
    PaperKeyword,
    Category,
    PaperCategory,
)
from backend.app.models.user import (
    User,
    SavedPaper,
)
from backend.app.models.ingestion import (
    IngestionRun,
)
from backend.app.models.evaluation import (
    RelevanceJudgment,
    EvaluationRun,
    EvaluationMetric,
)

__all__ = [
    "Paper",
    "Author",
    "PaperAuthor",
    "Keyword",
    "PaperKeyword",
    "Category",
    "PaperCategory",
    "User",
    "SavedPaper",
    "IngestionRun",
    "RelevanceJudgment",
    "EvaluationRun",
    "EvaluationMetric",
]
