"""Related paper recommendation package."""

from backend.app.recommendations.content_based import (
    ContentBasedRecommender,
    RecommendedPaper,
)

__all__ = [
    "ContentBasedRecommender",
    "RecommendedPaper",
]
