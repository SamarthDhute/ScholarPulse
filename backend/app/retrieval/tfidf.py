"""TF-IDF Vector Space Retrieval Engine.

Implements Vector Space Model with Cosine Similarity:
- Sublinear TF scaling: tf(t, d) = 1 + ln(count) if count > 0 else 0
- Smoothed IDF: idf(t) = ln((N + 1) / (df(t) + 1)) + 1.0
- Precomputed Euclidean document norms ||d||
- Cosine similarity: dot(q, d) / (||q|| * ||d||)
- Explainable term-level score breakdowns
"""

import math
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.preprocessing.tokenizer import preprocess_text


@dataclass
class ScoredDocument:
    """Represents a scored document from retrieval."""
    doc_id: str
    score: float
    rank: int = 0
    method: str = "tfidf"
    term_scores: Dict[str, float] = field(default_factory=dict)


class TFIDFRetrievalEngine:
    """Vector Space Model retrieval engine using TF-IDF and Cosine Similarity."""

    def __init__(self, index: InvertedIndex):
        self.index = index
        self._doc_norms: Dict[str, float] = {}
        self._idf_cache: Dict[str, float] = {}
        self._compute_document_norms()

    def compute_idf(self, term: str) -> float:
        """Compute smoothed IDF: ln((N + 1) / (df + 1)) + 1."""
        if term in self._idf_cache:
            return self._idf_cache[term]

        n = self.index.doc_count
        df = self.index.get_doc_frequency(term)
        if n == 0:
            return 1.0

        idf = math.log((n + 1.0) / (df + 1.0)) + 1.0
        self._idf_cache[term] = idf
        return idf

    def _compute_document_norms(self) -> None:
        """Precompute Euclidean L2 norm ||d|| for all documents in index."""
        doc_sq_sums: Dict[str, float] = defaultdict(float)

        for term, postings in self.index.postings.items():
            idf = self.compute_idf(term)
            for doc_id, count in postings.items():
                if count > 0:
                    tf = 1.0 + math.log(count)
                    w = tf * idf
                    doc_sq_sums[doc_id] += w * w

        self._doc_norms = {
            doc_id: math.sqrt(sq_sum) if sq_sum > 0 else 0.0
            for doc_id, sq_sum in doc_sq_sums.items()
        }

    def score(
        self,
        query: str,
        top_k: Optional[int] = None,
        candidate_ids: Optional[set] = None,
    ) -> List[ScoredDocument]:
        """Rank documents for a query using TF-IDF Cosine Similarity."""
        query_tokens = preprocess_text(query, remove_stopwords=True, apply_stemming=True)
        if not query_tokens or self.index.doc_count == 0:
            return []

        # Count query term frequencies
        qtf_counts: Dict[str, int] = defaultdict(int)
        for token in query_tokens:
            qtf_counts[token] += 1

        # Calculate query vector weights and query norm
        query_weights: Dict[str, float] = {}
        query_sq_sum = 0.0
        for term, qtf in qtf_counts.items():
            idf = self.compute_idf(term)
            w_q = (1.0 + math.log(qtf)) * idf
            query_weights[term] = w_q
            query_sq_sum += w_q * w_q

        query_norm = math.sqrt(query_sq_sum)
        if query_norm == 0.0:
            return []

        # Find candidate documents and accumulate dot products & term contributions
        doc_dots: Dict[str, float] = defaultdict(float)
        doc_term_contributions: Dict[str, Dict[str, float]] = defaultdict(dict)

        for term, w_q in query_weights.items():
            postings = self.index.get_postings(term)
            idf = self.compute_idf(term)
            for doc_id, count in postings.items():
                if candidate_ids is not None and doc_id not in candidate_ids:
                    continue
                if count > 0:
                    w_d = (1.0 + math.log(count)) * idf
                    term_dot = w_q * w_d
                    doc_dots[doc_id] += term_dot
                    doc_term_contributions[doc_id][term] = term_dot

        # Normalize by (||q|| * ||d||)
        scored_docs: List[ScoredDocument] = []
        for doc_id, dot in doc_dots.items():
            doc_norm = self._doc_norms.get(doc_id, 0.0)
            if doc_norm > 0:
                cosine_sim = dot / (query_norm * doc_norm)
                # Normalize term scores
                term_scores = {
                    t: round(contrib / (query_norm * doc_norm), 4)
                    for t, contrib in doc_term_contributions[doc_id].items()
                }
                scored_docs.append(
                    ScoredDocument(
                        doc_id=doc_id,
                        score=round(cosine_sim, 6),
                        method="tfidf",
                        term_scores=term_scores,
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
