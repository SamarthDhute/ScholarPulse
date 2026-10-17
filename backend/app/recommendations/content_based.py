"""Content-Based Related-Paper Recommendation Engine.

Adheres strictly to ScholarPulse SRS v1.0 Section 4 (FR-019) & Section 8.4:
- Pairwise cosine similarity ranking over TF-IDF document vectors
- Paper representations combining title, abstract, and keywords
- Strict exclusion of the query paper from recommendation results
- Explainable shared keywords between seed paper and candidates
- Fast top-N candidate retrieval with metadata enrichment
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RecommendedPaper:
    """Represents a related paper recommendation item."""
    paper_id: str
    title: str
    similarity_score: float
    shared_keywords: List[str] = field(default_factory=list)
    category: Optional[str] = None
    publication_year: Optional[int] = None


class ContentBasedRecommender:
    """Calculates related paper recommendations based on textual and topical content similarity."""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.paper_ids: List[str] = []
        self.id_to_idx: Dict[str, int] = {}
        self.papers_data: Dict[str, Dict[str, Any]] = {}
        self.is_fitted: bool = False

    def fit(self, papers: List[Dict[str, Any]]) -> "ContentBasedRecommender":
        """Fit TF-IDF representations and precompute pairwise cosine similarity matrix.

        Args:
            papers: List of paper dicts with 'id' or 'paper_id', 'title', optional 'abstract',
                    'keywords', 'category', 'publication_year'.

        Returns:
            self
        """
        if not papers:
            self.paper_ids = []
            self.id_to_idx = {}
            self.papers_data = {}
            self.is_fitted = False
            return self

        self.paper_ids = []
        self.id_to_idx = {}
        self.papers_data = {}
        corpus_texts: List[str] = []

        for idx, p in enumerate(papers):
            pid = str(p.get("id") or p.get("paper_id") or p.get("external_id") or f"paper_{idx}")
            ext_id = str(p.get("external_id")) if p.get("external_id") else None
            doi = str(p.get("doi")) if p.get("doi") else None
            title = p.get("title", "")
            abstract = p.get("abstract", "") or ""
            year = p.get("publication_year")

            # Extract category
            cat = p.get("category")
            if not cat and p.get("categories"):
                cats = p.get("categories")
                cat = cats[0] if isinstance(cats, list) and cats else None

            # Extract keywords
            kws = p.get("keywords", [])
            kw_terms = []
            for k in kws:
                term = k if isinstance(k, str) else k.get("display_term", "")
                if term and term.strip():
                    kw_terms.append(term.strip().lower())

            # Combined representation
            kw_string = " ".join(kw_terms)
            combined_text = f"{title} {abstract} {kw_string}".strip()
            if not combined_text:
                combined_text = title or f"Document {pid}"

            corpus_texts.append(combined_text)
            self.paper_ids.append(pid)
            self.id_to_idx[pid] = idx
            if ext_id:
                self.id_to_idx[ext_id] = idx
            if doi:
                self.id_to_idx[doi] = idx
            self.papers_data[pid] = {
                "id": pid,
                "title": title,
                "abstract": abstract,
                "category": cat,
                "publication_year": year,
                "keywords": kw_terms,
            }

        # Vectorize corpus
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=3000,
            sublinear_tf=True,
            stop_words="english",
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_texts)
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        self.is_fitted = True
        return self

    def recommend(
        self,
        paper_id: str,
        top_n: int = 5,
        min_similarity: float = 0.01,
    ) -> List[RecommendedPaper]:
        """Retrieve top-N content-similar papers excluding the queried paper itself.

        Args:
            paper_id: Target seed paper ID.
            top_n: Maximum number of recommendations to return.
            min_similarity: Minimum cosine similarity threshold.

        Returns:
            List of RecommendedPaper items sorted descending by similarity.
        """
        if not self.is_fitted or self.similarity_matrix is None:
            raise RuntimeError("Recommender has not been fitted. Call fit() first.")

        pid_str = str(paper_id)
        if pid_str not in self.id_to_idx:
            raise KeyError(f"Paper ID '{paper_id}' not found in recommendation corpus.")

        target_idx = self.id_to_idx[pid_str]
        target_meta = self.papers_data[pid_str]
        target_kws: Set[str] = set(target_meta.get("keywords", []))

        # Row of pairwise cosine similarities
        sim_scores = self.similarity_matrix[target_idx]

        # Rank all papers descending by similarity
        ranked_indices = np.argsort(sim_scores)[::-1]

        recommendations: List[RecommendedPaper] = []

        for candidate_idx in ranked_indices:
            # Exclude the seed paper itself per FR-019
            if candidate_idx == target_idx:
                continue

            score = float(sim_scores[candidate_idx])
            if score < min_similarity:
                continue

            cand_id = self.paper_ids[candidate_idx]
            cand_meta = self.papers_data[cand_id]
            cand_kws: Set[str] = set(cand_meta.get("keywords", []))

            # Shared keywords for algorithmic transparency
            shared = sorted(list(target_kws.intersection(cand_kws)))

            recommendations.append(
                RecommendedPaper(
                    paper_id=cand_id,
                    title=cand_meta["title"],
                    similarity_score=round(score, 4),
                    shared_keywords=shared,
                    category=cand_meta.get("category"),
                    publication_year=cand_meta.get("publication_year"),
                )
            )

            if len(recommendations) >= top_n:
                break

        return recommendations
