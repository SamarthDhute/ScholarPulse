"""ScholarPulse Information Retrieval Module."""

from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.retrieval.boolean import BooleanRetrievalEngine
from backend.app.retrieval.tfidf import TFIDFRetrievalEngine, ScoredDocument
from backend.app.retrieval.bm25 import BM25RetrievalEngine
from backend.app.retrieval.language_model import LanguageModelRetrievalEngine
from backend.app.retrieval.passage_retrieval import PassageRetrievalEngine, ExtractedPassage
from backend.app.retrieval.search_service import SearchService, SearchResult, SearchResponse

__all__ = [
    "InvertedIndex",
    "BooleanRetrievalEngine",
    "TFIDFRetrievalEngine",
    "BM25RetrievalEngine",
    "LanguageModelRetrievalEngine",
    "PassageRetrievalEngine",
    "ExtractedPassage",
    "SearchService",
    "SearchResult",
    "SearchResponse",
    "ScoredDocument",
]
