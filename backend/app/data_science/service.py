"""Data Science Coordinator Service for ScholarPulse.

Unifies and coordinates:
- Text classification (predict_paper, train, compare_models)
- Unsupervised clustering (K-Means, Hierarchical, optimal k)
- Association rule mining (Apriori keyword rules, paginated queries)
- Bibliometric research analytics (trends, categories, keywords, co-authorship)
- Content-based related-paper recommendations
"""

import os
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from backend.app.data_science.classifier import PaperClassifier
from backend.app.data_science.clustering import PaperClustering, ClusteringResult
from backend.app.data_science.association_rules import (
    KeywordAssociationMiner,
    AssociationMiningResult,
)
from backend.app.data_science.analytics import ResearchAnalyticsService
from backend.app.recommendations.content_based import (
    ContentBasedRecommender,
    RecommendedPaper,
)
from backend.app.models.paper import Paper, Category, Keyword, Author


class DataScienceService:
    """High-level service coordinating all Data Science and Recommendation models."""

    def __init__(self, artifacts_dir: str = "artifacts/models"):
        self.artifacts_dir = artifacts_dir
        self.classifier = PaperClassifier()
        self.clustering = PaperClustering()
        self.association_miner = KeywordAssociationMiner()
        self.analytics = ResearchAnalyticsService()
        self.recommender = ContentBasedRecommender()

    def _extract_paper_dicts(self, papers: List[Paper]) -> List[Dict[str, Any]]:
        """Convert SQLAlchemy Paper models to flat dictionaries."""
        docs = []
        for p in papers:
            # Authors
            authors_list = [
                pa.author.display_name
                for pa in sorted(p.authors, key=lambda a: a.author_order)
                if pa.author
            ]
            # Categories
            categories_list = [pc.category.name for pc in p.categories if pc.category]
            # Keywords
            keywords_list = [pk.keyword.display_term for pk in p.keywords if pk.keyword]

            docs.append({
                "id": str(p.id),
                "paper_id": str(p.id),
                "title": p.title,
                "abstract": p.abstract or "",
                "publication_year": p.publication_year,
                "authors": authors_list,
                "categories": categories_list,
                "category": categories_list[0] if categories_list else None,
                "keywords": keywords_list,
                "doi": p.doi,
                "source_name": p.source_name,
            })
        return docs

    def train_classifier(
        self,
        papers: List[Dict[str, Any]],
        model_type: str = "multinomial_nb",
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train and evaluate the category classifier."""
        metrics = self.classifier.train(
            documents=papers,
            model_type=model_type,
            test_size=test_size,
            random_state=random_state,
        )
        # Serialize to artifacts
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.classifier.save(self.artifacts_dir)
        return metrics

    def classify_text(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Predict categories for arbitrary text."""
        return self.classifier.predict(text, top_k=top_k)

    def classify_paper(
        self, paper_id: str, title: str, abstract: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict categories for a paper matching SRS 8.7 contract."""
        return self.classifier.predict_paper(
            paper_id=paper_id, title=title, abstract=abstract
        )

    def cluster_corpus(
        self,
        papers: List[Dict[str, Any]],
        n_clusters: int = 4,
        method: str = "kmeans",
        random_state: int = 42,
    ) -> ClusteringResult:
        """Execute document clustering and save artifacts."""
        result = self.clustering.fit(
            documents=papers,
            n_clusters=n_clusters,
            method=method,
            random_state=random_state,
        )
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.clustering.save(os.path.join(self.artifacts_dir, "clustering_results.json"))
        return result

    def mine_association_rules(
        self,
        papers: List[Dict[str, Any]],
        min_support: float = 0.04,
        min_confidence: float = 0.3,
        min_lift: float = 1.0,
    ) -> AssociationMiningResult:
        """Mine keyword associations across papers and save artifacts."""
        transactions = [p.get("keywords", []) for p in papers if p.get("keywords")]
        result = self.association_miner.mine(
            transactions=transactions,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
        )
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.association_miner.save(
            os.path.join(self.artifacts_dir, "association_rules.json")
        )
        return result

    def fit_recommender(self, papers: List[Dict[str, Any]]) -> None:
        """Fit the content-based recommendation model."""
        self.recommender.fit(papers)

    def get_related_papers(
        self, paper_id: str, top_n: int = 5, min_similarity: float = 0.01
    ) -> List[RecommendedPaper]:
        """Retrieve related papers for a seed paper."""
        return self.recommender.recommend(
            paper_id=paper_id, top_n=top_n, min_similarity=min_similarity
        )

    def get_analytics(
        self,
        papers: List[Dict[str, Any]],
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate comprehensive bibliometric research analytics."""
        overview = self.analytics.get_overview_summary(papers, year_min, year_max)
        trends = self.analytics.get_publication_trends(papers, year_min, year_max)
        categories = self.analytics.get_category_distribution(papers, year_min, year_max)
        keywords = self.analytics.get_keyword_distribution(papers, top_n=20, year_min=year_min, year_max=year_max)
        authors = self.analytics.get_top_authors(papers, top_n=15, year_min=year_min, year_max=year_max)
        network = self.analytics.get_coauthorship_network(papers, min_collaborations=1, year_min=year_min, year_max=year_max)

        return {
            "overview": overview,
            "publication_trends": trends,
            "category_distribution": categories,
            "top_keywords": keywords,
            "top_authors": authors,
            "coauthorship_network": network,
        }
