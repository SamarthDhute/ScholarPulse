"""Repositories package exporting database access layers."""

from backend.app.repositories.base import BaseRepository
from backend.app.repositories.paper_repository import PaperRepository
from backend.app.repositories.author_repository import AuthorRepository
from backend.app.repositories.keyword_repository import KeywordRepository
from backend.app.repositories.category_repository import CategoryRepository
from backend.app.repositories.ingestion_repository import IngestionRepository

__all__ = [
    "BaseRepository",
    "PaperRepository",
    "AuthorRepository",
    "KeywordRepository",
    "CategoryRepository",
    "IngestionRepository",
]
