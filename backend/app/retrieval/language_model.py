"""Query-Likelihood Language Model Retrieval Engine.

Implements statistical unigram language modeling for Information Retrieval
(Ponte & Croft 1998, Zhai & Lafferty 2004):
- Generative query likelihood ranking: P(q | M_d) = prod P(q_i | M_d)
- Log-space computation: ln P(q | M_d) = sum ln P(q_i | M_d)
- Bayesian Dirichlet prior smoothing: P(t | M_d) = (c(t, d) + mu * P(t | C)) / (|d| + mu)
- Jelinek-Mercer linear interpolation smoothing: P(t | M_d) = (1 - lambda) * P_ml(t | d) + lambda * P(t | C)
- Background collection language model P(t | C) = cf(t) / |C|
- Explainable term log-probabilities
"""

import math
from collections import defaultdict
from typing import Dict, List, Optional, Set

from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.retrieval.tfidf import ScoredDocument
from backend.app.preprocessing.tokenizer import preprocess_text


class LanguageModelRetrievalEngine:
    """Probabilistic query-likelihood retrieval engine with smoothing."""

    def __init__(
        self,
        index: InvertedIndex,
        smoothing: str = "dirichlet",
        mu: float = 1000.0,
        lam: float = 0.1,
    ):
        self.index = index
        self.smoothing = smoothing.lower().strip()
        self.mu = mu
        self.lam = lam

        # Precompute collection size |C| and collection frequencies cf(t)
        self.total_collection_tokens: int = sum(index.doc_lengths.values())
        self._cf_cache: Dict[str, int] = {}
        self._collection_prob_cache: Dict[str, float] = {}

    def get_collection_frequency(self, term: str) -> int:
        """Return total count of term across all documents in the collection (cf)."""
        if term in self._cf_cache:
            return self._cf_cache[term]
        postings = self.index.get_postings(term)
        cf = sum(postings.values())
        self._cf_cache[term] = cf
        return cf

    def get_collection_prob(self, term: str) -> float:
        """Return collection background probability P(t | C) = cf(t) / |C|."""
        if term in self._collection_prob_cache:
            return self._collection_prob_cache[term]

        if self.total_collection_tokens == 0:
            return 1e-9

        cf = self.get_collection_frequency(term)
        if cf == 0:
            prob = 1e-9
        else:
            prob = cf / float(self.total_collection_tokens)

        self._collection_prob_cache[term] = prob
        return prob

    def score_term_dirichlet(self, term: str, doc_id: str) -> float:
        """Compute Dirichlet smoothed term probability P(t | M_d)."""
        count = self.index.get_term_frequency(term, doc_id)
        doc_len = self.index.doc_lengths.get(doc_id, 0)
        p_c = self.get_collection_prob(term)

        # Dirichlet formula: (count + mu * P(t|C)) / (|d| + mu)
        prob = (count + (self.mu * p_c)) / (doc_len + self.mu)
        return prob

    def score_term_jm(self, term: str, doc_id: str) -> float:
        """Compute Jelinek-Mercer smoothed term probability P(t | M_d)."""
        count = self.index.get_term_frequency(term, doc_id)
        doc_len = self.index.doc_lengths.get(doc_id, 0)
        p_c = self.get_collection_prob(term)

        p_ml = (count / float(doc_len)) if doc_len > 0 else 0.0
        # Jelinek-Mercer formula: (1 - lam) * P_ml + lam * P(t|C)
        prob = ((1.0 - self.lam) * p_ml) + (self.lam * p_c)
        return max(prob, 1e-12)

    def score(
        self,
        query: str,
        top_k: Optional[int] = None,
        candidate_ids: Optional[Set[str]] = None,
    ) -> List[ScoredDocument]:
        """Rank documents by query log-likelihood ln P(q | M_d)."""
        query_tokens = preprocess_text(query, remove_stopwords=True, apply_stemming=True)
        if not query_tokens or self.index.doc_count == 0 or self.total_collection_tokens == 0:
            return []

        # Find candidates matching at least one query term
        unique_terms = set(query_tokens)
        candidate_docs: Set[str] = set()

        for term in unique_terms:
            postings = self.index.get_postings(term)
            candidate_docs.update(postings.keys())

        if candidate_ids is not None:
            candidate_docs = candidate_docs.intersection(candidate_ids)

        if not candidate_docs:
            return []

        scored_docs: List[ScoredDocument] = []
        is_jm = self.smoothing in ("jm", "jelinek_mercer")

        for doc_id in candidate_docs:
            total_log_likelihood = 0.0
            term_breakdown: Dict[str, float] = {}

            for term in query_tokens:
                if is_jm:
                    prob = self.score_term_jm(term, doc_id)
                else:
                    prob = self.score_term_dirichlet(term, doc_id)

                term_ll = math.log(max(prob, 1e-15))
                total_log_likelihood += term_ll
                term_breakdown[term] = round(term_ll, 4)

            scored_docs.append(
                ScoredDocument(
                    doc_id=doc_id,
                    score=round(total_log_likelihood, 6),
                    method="language_model",
                    term_scores=term_breakdown,
                )
            )

        # Sort descending by log likelihood (highest probability first)
        scored_docs.sort(key=lambda d: (-d.score, d.doc_id))

        # Assign ranks
        for i, doc in enumerate(scored_docs, start=1):
            doc.rank = i

        if top_k is not None and top_k > 0:
            return scored_docs[:top_k]
        return scored_docs
