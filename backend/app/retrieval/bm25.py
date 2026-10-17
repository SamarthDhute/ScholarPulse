"""Okapi BM25 Probabilistic Retrieval Engine.

Implements the Robertson-Spärck Jones Okapi BM25 ranking algorithm:
- RSJ-IDF: ln((N - df + 0.5) / (df + 0.5) + 1.0)
- Term frequency saturation governed by k1 (default 1.5)
- Document length normalization governed by b (default 0.75)
- Explainable scoring breakdown per query term
"""

import math
from collections import defaultdict
from typing import Dict, List, Optional, Set

from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.retrieval.tfidf import ScoredDocument
from backend.app.preprocessing.tokenizer import preprocess_text


class BM25RetrievalEngine:
    """Okapi BM25 probabilistic retrieval engine."""

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1
        self.b = b
        self._rsj_idf_cache: Dict[str, float] = {}

    def compute_rsj_idf(self, term: str) -> float:
        """Compute Robertson-Spärck Jones IDF with smoothing: ln((N - df + 0.5)/(df + 0.5) + 1)."""
        if term in self._rsj_idf_cache:
            return self._rsj_idf_cache[term]

        n = self.index.doc_count
        df = self.index.get_doc_frequency(term)
        if n == 0:
            return 0.0

        # +1.0 ensures non-negative RSJ-IDF for very common terms
        idf = math.log(((n - df + 0.5) / (df + 0.5)) + 1.0)
        self._rsj_idf_cache[term] = idf
        return idf

    def score_term(self, term: str, doc_id: str) -> float:
        """Compute BM25 contribution for a single term in a document."""
        tf = self.index.get_term_frequency(term, doc_id)
        if tf <= 0:
            return 0.0

        idf = self.compute_rsj_idf(term)
        doc_len = self.index.doc_lengths.get(doc_id, 0)
        avgdl = self.index.avg_doc_length

        len_norm = 1.0 - self.b + (self.b * (doc_len / avgdl)) if avgdl > 0 else 1.0
        numerator = tf * (self.k1 + 1.0)
        denominator = tf + (self.k1 * len_norm)

        return idf * (numerator / denominator)

    def score(
        self,
        query: str,
        top_k: Optional[int] = None,
        candidate_ids: Optional[Set[str]] = None,
    ) -> List[ScoredDocument]:
        """Rank documents for a query using Okapi BM25."""
        query_tokens = preprocess_text(query, remove_stopwords=True, apply_stemming=True)
        if not query_tokens or self.index.doc_count == 0:
            return []

        # Find all documents containing at least one query term
        unique_terms = set(query_tokens)
        candidate_docs: Set[str] = set()

        for term in unique_terms:
            postings = self.index.get_postings(term)
            candidate_docs.update(postings.keys())

        if candidate_ids is not None:
            candidate_docs = candidate_docs.intersection(candidate_ids)

        if not candidate_docs:
            return []

        avgdl = self.index.avg_doc_length
        scored_docs: List[ScoredDocument] = []

        for doc_id in candidate_docs:
            doc_len = self.index.doc_lengths.get(doc_id, 0)
            len_norm = 1.0 - self.b + (self.b * (doc_len / avgdl)) if avgdl > 0 else 1.0

            total_score = 0.0
            term_breakdown: Dict[str, float] = {}

            for term in unique_terms:
                tf = self.index.get_term_frequency(term, doc_id)
                if tf > 0:
                    idf = self.compute_rsj_idf(term)
                    numerator = tf * (self.k1 + 1.0)
                    denominator = tf + (self.k1 * len_norm)
                    term_score = idf * (numerator / denominator)
                    total_score += term_score
                    term_breakdown[term] = round(term_score, 4)

            scored_docs.append(
                ScoredDocument(
                    doc_id=doc_id,
                    score=round(total_score, 6),
                    method="bm25",
                    term_scores=term_breakdown,
                )
            )

        # Sort descending by score, tie-break by doc_id
        scored_docs.sort(key=lambda d: (-d.score, d.doc_id))

        # Assign ranks
        for i, doc in enumerate(scored_docs, start=1):
            doc.rank = i

        if top_k is not None and top_k > 0:
            return scored_docs[:top_k]
        return scored_docs
