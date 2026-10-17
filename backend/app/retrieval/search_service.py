"""Search Service coordinating Inverted Index, Boolean, TF-IDF, BM25, and Language Model Rankers.

Adheres strictly to ScholarPulse SRS v1.0 and AGENTS.md:
- Transparent Python-native Information Retrieval algorithms
- BM25 as the default ranker
- TF-IDF with Vector Space Model cosine similarity
- Full Boolean Retrieval with Shunting-Yard parser
- Query-Likelihood Language Model with Dirichlet smoothing
- Passage retrieval with sentence-level snippet extraction and highlighting
- Metadata filtering (publication year range, category)
- Document ranking with explainable term breakdown
- Artifact serialization to and from JSON
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Sequence, Tuple

from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.retrieval.boolean import BooleanRetrievalEngine
from backend.app.retrieval.tfidf import TFIDFRetrievalEngine, ScoredDocument
from backend.app.retrieval.bm25 import BM25RetrievalEngine
from backend.app.retrieval.language_model import LanguageModelRetrievalEngine
from backend.app.retrieval.passage_retrieval import PassageRetrievalEngine


@dataclass
class SearchResult:
    """Represents a ranked search result item."""
    doc_id: str
    score: float
    rank: int
    method: str
    term_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    snippet: Optional[str] = None
    highlighted_snippet: Optional[str] = None


@dataclass
class SearchResponse:
    """Unified search response structure."""
    query: str
    method: str
    total_hits: int
    page: int
    page_size: int
    results: List[SearchResult]


class SearchService:
    """Orchestrator for indexing, filtering, snippet extraction, and multi-ranker retrieval."""

    def __init__(self, index: Optional[InvertedIndex] = None):
        self.index = index if index is not None else InvertedIndex()
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.document_texts: Dict[str, str] = {}
        self.passage_engine = PassageRetrievalEngine(max_snippet_length=250)

        self._boolean_engine: Optional[BooleanRetrievalEngine] = None
        self._tfidf_engine: Optional[TFIDFRetrievalEngine] = None
        self._bm25_engine: Optional[BM25RetrievalEngine] = None
        self._language_model_engine: Optional[LanguageModelRetrievalEngine] = None

    @property
    def boolean_engine(self) -> BooleanRetrievalEngine:
        if self._boolean_engine is None:
            self._boolean_engine = BooleanRetrievalEngine(self.index)
        return self._boolean_engine

    @property
    def tfidf_engine(self) -> TFIDFRetrievalEngine:
        if self._tfidf_engine is None:
            self._tfidf_engine = TFIDFRetrievalEngine(self.index)
        return self._tfidf_engine

    @property
    def bm25_engine(self) -> BM25RetrievalEngine:
        if self._bm25_engine is None:
            self._bm25_engine = BM25RetrievalEngine(self.index)
        return self._bm25_engine

    @property
    def language_model_engine(self) -> LanguageModelRetrievalEngine:
        if self._language_model_engine is None:
            self._language_model_engine = LanguageModelRetrievalEngine(self.index)
        return self._language_model_engine

    def _reset_engines(self) -> None:
        """Invalidate cached engines when index is modified."""
        self._boolean_engine = None
        self._tfidf_engine = None
        self._bm25_engine = None
        self._language_model_engine = None

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Index a single document with optional metadata."""
        self.index.add_document(doc_id, text)
        self.document_texts[doc_id] = text
        if metadata:
            self.metadata[doc_id] = metadata
        self._reset_engines()

    def build_from_documents(
        self,
        documents: Sequence[Tuple[str, str, Optional[Dict[str, Any]]]],
    ) -> None:
        """Batch index documents with metadata."""
        for doc_id, text, meta in documents:
            self.index.add_document(doc_id, text)
            self.document_texts[doc_id] = text
            if meta:
                self.metadata[doc_id] = meta
        self._reset_engines()

    def build_from_dataset(self, filepath: str) -> int:
        """Index papers directly from a local JSON dataset file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset not found at {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)

        docs = []
        for item in records:
            doc_id = item.get("doi") or item.get("external_id") or str(item.get("id"))
            title = item.get("title", "")
            abstract = item.get("abstract", "") or ""
            text = f"{title}. {abstract}".strip()
            meta = {
                "title": title,
                "abstract": abstract,
                "publication_year": item.get("publication_year"),
                "categories": item.get("categories", []),
                "keywords": item.get("keywords", []),
                "authors": item.get("authors", []),
                "doi": item.get("doi"),
                "source_name": item.get("source_name"),
            }
            docs.append((doc_id, text, meta))

        self.build_from_documents(docs)
        return len(docs)

    def _apply_metadata_filters(
        self,
        candidate_ids: Optional[Set[str]],
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        category: Optional[str] = None,
    ) -> Set[str]:
        """Filter candidate doc IDs by metadata criteria."""
        all_ids = candidate_ids if candidate_ids is not None else set(self.index.doc_ids)
        filtered = set()

        for doc_id in all_ids:
            meta = self.metadata.get(doc_id, {})
            pub_year = meta.get("publication_year")

            if year_min is not None and (pub_year is None or pub_year < year_min):
                continue
            if year_max is not None and (pub_year is None or pub_year > year_max):
                continue
            if category is not None:
                categories = [c.lower() for c in meta.get("categories", [])]
                if category.lower() not in categories:
                    continue

            filtered.add(doc_id)

        return filtered

    def search(
        self,
        query: str,
        method: str = "bm25",
        top_k: int = 10,
        page: int = 1,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        category: Optional[str] = None,
        candidate_ids: Optional[Set[str]] = None,
        include_snippets: bool = True,
    ) -> SearchResponse:
        """Execute search with specified ranker, metadata filters, and snippet extraction."""
        if not query or not query.strip():
            return SearchResponse(
                query=query,
                method=method,
                total_hits=0,
                page=page,
                page_size=top_k,
                results=[],
            )

        # Apply metadata filters first to narrow candidates if any filter is set
        has_filter = (year_min is not None) or (year_max is not None) or (category is not None)
        active_candidates = candidate_ids
        if has_filter:
            active_candidates = self._apply_metadata_filters(
                candidate_ids=candidate_ids,
                year_min=year_min,
                year_max=year_max,
                category=category,
            )
            if not active_candidates:
                return SearchResponse(
                    query=query,
                    method=method,
                    total_hits=0,
                    page=page,
                    page_size=top_k,
                    results=[],
                )

        scored_docs: List[ScoredDocument] = []
        method_norm = method.lower().strip()

        if method_norm == "boolean":
            # Boolean engine matches set of docs
            matched_ids = self.boolean_engine.search(query)
            if active_candidates is not None:
                matched_ids = matched_ids.intersection(active_candidates)

            # Sort matched IDs deterministically
            sorted_ids = sorted(list(matched_ids))
            for i, doc_id in enumerate(sorted_ids, start=1):
                scored_docs.append(
                    ScoredDocument(
                        doc_id=doc_id,
                        score=1.0,
                        rank=i,
                        method="boolean",
                        term_scores={},
                    )
                )
        elif method_norm == "tfidf":
            scored_docs = self.tfidf_engine.score(query=query, candidate_ids=active_candidates)
        elif method_norm == "bm25":
            scored_docs = self.bm25_engine.score(query=query, candidate_ids=active_candidates)
        elif method_norm in ("language_model", "lm", "query_likelihood", "ql"):
            scored_docs = self.language_model_engine.score(query=query, candidate_ids=active_candidates)
            method_norm = "language_model"
        else:
            raise ValueError(
                f"Unsupported ranking method: '{method}'. Choose from: 'bm25', 'tfidf', 'language_model', 'boolean'."
            )

        total_hits = len(scored_docs)

        # Pagination: 1-indexed page
        page = max(1, page)
        top_k = max(1, top_k)
        start_idx = (page - 1) * top_k
        end_idx = start_idx + top_k
        paged_docs = scored_docs[start_idx:end_idx]

        results: List[SearchResult] = []
        for doc in paged_docs:
            snippet_text: Optional[str] = None
            highlighted: Optional[str] = None

            if include_snippets:
                # Extract best passage from abstract or document text
                meta = self.metadata.get(doc.doc_id, {})
                text_to_search = meta.get("abstract") or self.document_texts.get(doc.doc_id, "")
                if text_to_search:
                    passage = self.passage_engine.extract_best_passage(text_to_search, query)
                    snippet_text = passage.text
                    highlighted = passage.highlighted_text

            results.append(
                SearchResult(
                    doc_id=doc.doc_id,
                    score=doc.score,
                    rank=doc.rank,
                    method=doc.method,
                    term_scores=doc.term_scores,
                    metadata=self.metadata.get(doc.doc_id, {}),
                    snippet=snippet_text,
                    highlighted_snippet=highlighted,
                )
            )

        return SearchResponse(
            query=query,
            method=method_norm,
            total_hits=total_hits,
            page=page,
            page_size=top_k,
            results=results,
        )

    def save(self, directory: str) -> None:
        """Persist inverted index and metadata artifacts."""
        os.makedirs(directory, exist_ok=True)
        index_path = os.path.join(directory, "inverted_index.json")
        metadata_path = os.path.join(directory, "index_metadata.json")
        texts_path = os.path.join(directory, "document_texts.json")

        self.index.save(index_path)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False)
        with open(texts_path, "w", encoding="utf-8") as f:
            json.dump(self.document_texts, f, ensure_ascii=False)

    @classmethod
    def load(cls, directory: str) -> "SearchService":
        """Load service from saved index and metadata artifacts."""
        index_path = os.path.join(directory, "inverted_index.json")
        metadata_path = os.path.join(directory, "index_metadata.json")
        texts_path = os.path.join(directory, "document_texts.json")

        index = InvertedIndex.load(index_path)
        service = cls(index=index)

        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                service.metadata = json.load(f)

        if os.path.exists(texts_path):
            with open(texts_path, "r", encoding="utf-8") as f:
                service.document_texts = json.load(f)

        return service
