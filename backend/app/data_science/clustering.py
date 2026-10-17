"""Document Clustering Engine for Academic Topic Exploration.

Adheres strictly to ScholarPulse SRS v1.0 Section 4 (FR-014, FR-018) & Section 8.7:
- Unsupervised K-Means and Hierarchical (Agglomerative) clustering
- TF-IDF feature space representation with cosine metrics
- Explainable cluster topic labeling using top centroid feature weights
- Quality indicators: Silhouette Score and Inertia
- Optimal cluster count ($k$) search across candidate values
- Representative paper identification based on cosine proximity to cluster centers
- JSON serialization for API and artifact persistence
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Sequence
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RepresentativePaper:
    """A paper that best exemplifies a cluster centroid."""
    paper_id: str
    title: str
    similarity_to_centroid: float
    category: Optional[str] = None


@dataclass
class ClusterSummary:
    """Explainable topic cluster metadata and member details."""
    cluster_id: int
    label: str
    size: int
    top_terms: List[Dict[str, float]]
    representative_papers: List[RepresentativePaper] = field(default_factory=list)
    paper_ids: List[str] = field(default_factory=list)


@dataclass
class ClusteringResult:
    """Comprehensive clustering execution output."""
    method: str
    n_clusters: int
    silhouette_score: float
    inertia: Optional[float]
    clusters: List[ClusterSummary]
    total_documents: int
    model_version: str = "clustering-v1"


class PaperClustering:
    """Unsupervised clustering engine for paper corpus topic discovery."""

    SUPPORTED_METHODS = {"kmeans", "hierarchical"}

    def __init__(self, model_version: str = "clustering-v1"):
        self.model_version = model_version
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.last_result: Optional[ClusteringResult] = None
        self.paper_metadata: List[Dict[str, Any]] = []

    def fit(
        self,
        documents: List[Dict[str, Any]],
        n_clusters: int = 4,
        method: str = "kmeans",
        random_state: int = 42,
        top_terms_count: int = 5,
        max_representatives: int = 3,
    ) -> ClusteringResult:
        """Fit clustering model on document corpus and produce explainable topic groups.

        Args:
            documents: List of dicts with 'id' or 'paper_id', 'title', and optional 'abstract', 'category'.
            n_clusters: Number of target clusters $k$.
            method: 'kmeans' or 'hierarchical'.
            random_state: Random seed for deterministic reproducibility.
            top_terms_count: Number of salient terms to extract for cluster labels.
            max_representatives: Maximum representative papers per cluster.

        Returns:
            ClusteringResult containing metrics, clusters, labels, and representative papers.
        """
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(
                f"Unsupported clustering method: '{method}'. Choose from {self.SUPPORTED_METHODS}"
            )

        if len(documents) < 2:
            raise ValueError("Clustering requires at least 2 documents.")

        if n_clusters < 2:
            raise ValueError("n_clusters must be >= 2.")

        if n_clusters >= len(documents):
            # Cap n_clusters to len(documents) - 1
            n_clusters = max(2, len(documents) - 1)

        # Prepare corpus texts and retain metadata
        self.paper_metadata = []
        texts: List[str] = []

        for i, doc in enumerate(documents):
            doc_id = str(doc.get("id") or doc.get("paper_id") or f"doc_{i}")
            title = doc.get("title", "")
            abstract = doc.get("abstract", "") or ""
            category = doc.get("category")
            if not category and doc.get("categories"):
                cats = doc.get("categories")
                category = cats[0] if isinstance(cats, list) and cats else None

            combined = f"{title} {abstract}".strip()
            if not combined:
                combined = title or f"Document {doc_id}"

            texts.append(combined)
            self.paper_metadata.append({
                "id": doc_id,
                "title": title,
                "category": category,
            })

        # Build TF-IDF representation
        self.vectorizer = TfidfVectorizer(
            max_features=2500,
            sublinear_tf=True,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(texts).toarray()
        feature_names = np.array(self.vectorizer.get_feature_names_out())

        # Fit selected model
        inertia_val: Optional[float] = None

        if method == "kmeans":
            model = KMeans(
                n_clusters=n_clusters,
                random_state=random_state,
                n_init=10,
                max_iter=300,
            )
            labels = model.fit_predict(self.tfidf_matrix)
            centroids = model.cluster_centers_
            inertia_val = round(float(model.inertia_), 4)
        else:
            # Hierarchical / Agglomerative clustering with cosine metric
            model = AgglomerativeClustering(
                n_clusters=n_clusters,
                metric="cosine",
                linkage="average",
            )
            labels = model.fit_predict(self.tfidf_matrix)
            # Compute mean centroid for each cluster
            centroids = np.zeros((n_clusters, self.tfidf_matrix.shape[1]))
            for c_id in range(n_clusters):
                cluster_points = self.tfidf_matrix[labels == c_id]
                if len(cluster_points) > 0:
                    centroids[c_id] = cluster_points.mean(axis=0)

        # Compute silhouette score if possible
        num_unique_labels = len(set(labels))
        if 1 < num_unique_labels < len(documents):
            score = float(silhouette_score(self.tfidf_matrix, labels, metric="cosine"))
            silhouette_val = round(score, 4)
        else:
            silhouette_val = 0.0

        # Build explainable cluster summaries
        clusters_summary: List[ClusterSummary] = []

        for c_id in range(n_clusters):
            member_indices = np.where(labels == c_id)[0]
            cluster_size = len(member_indices)

            if cluster_size == 0:
                continue

            centroid = centroids[c_id]

            # Top terms extraction from centroid weights
            if len(feature_names) > 0:
                top_term_indices = centroid.argsort()[::-1][:top_terms_count]
                top_terms = [
                    {
                        "term": str(feature_names[idx]),
                        "weight": round(float(centroid[idx]), 4),
                    }
                    for idx in top_term_indices
                    if centroid[idx] > 0
                ]
            else:
                top_terms = []

            # Generate semantic label from top 3 terms
            label_terms = [t["term"] for t in top_terms[:3]]
            label_str = " / ".join(label_terms) if label_terms else f"Cluster {c_id}"

            # Identify representative papers based on cosine similarity to centroid
            member_vectors = self.tfidf_matrix[member_indices]
            sims = cosine_similarity(member_vectors, centroid.reshape(1, -1)).flatten()

            sorted_member_order = np.argsort(sims)[::-1]
            representatives: List[RepresentativePaper] = []

            for rank_idx in sorted_member_order[:max_representatives]:
                orig_doc_idx = member_indices[rank_idx]
                meta = self.paper_metadata[orig_doc_idx]
                sim_score = float(sims[rank_idx])
                representatives.append(
                    RepresentativePaper(
                        paper_id=meta["id"],
                        title=meta["title"],
                        similarity_to_centroid=round(sim_score, 4),
                        category=meta.get("category"),
                    )
                )

            cluster_paper_ids = [self.paper_metadata[idx]["id"] for idx in member_indices]

            clusters_summary.append(
                ClusterSummary(
                    cluster_id=int(c_id),
                    label=label_str,
                    size=cluster_size,
                    top_terms=top_terms,
                    representative_papers=representatives,
                    paper_ids=cluster_paper_ids,
                )
            )

        # Sort clusters descending by size
        clusters_summary.sort(key=lambda c: c.size, reverse=True)

        self.last_result = ClusteringResult(
            method=method,
            n_clusters=len(clusters_summary),
            silhouette_score=silhouette_val,
            inertia=inertia_val,
            clusters=clusters_summary,
            total_documents=len(documents),
            model_version=self.model_version,
        )

        return self.last_result

    def find_optimal_k(
        self,
        documents: List[Dict[str, Any]],
        k_range: Sequence[int] = (2, 3, 4, 5, 6),
        method: str = "kmeans",
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Evaluate clustering quality across candidate k values to determine the optimal cluster count."""
        max_k_possible = max(2, len(documents) - 1)
        valid_k_values = [k for k in k_range if 2 <= k <= max_k_possible]

        if not valid_k_values:
            valid_k_values = [2]

        evaluations: Dict[int, Dict[str, Any]] = {}
        best_k = valid_k_values[0]
        best_silhouette = -1.0

        for k in valid_k_values:
            result = self.fit(
                documents=documents,
                n_clusters=k,
                method=method,
                random_state=random_state,
            )
            evaluations[k] = {
                "silhouette_score": result.silhouette_score,
                "inertia": result.inertia,
            }
            if result.silhouette_score > best_silhouette:
                best_silhouette = result.silhouette_score
                best_k = k

        # Re-fit at optimal k
        optimal_result = self.fit(
            documents=documents,
            n_clusters=best_k,
            method=method,
            random_state=random_state,
        )

        return {
            "method": method,
            "optimal_k": best_k,
            "best_silhouette_score": best_silhouette,
            "evaluations": evaluations,
            "optimal_result": self.to_dict(optimal_result),
        }

    def to_dict(self, result: Optional[ClusteringResult] = None) -> Dict[str, Any]:
        """Convert ClusteringResult to a JSON-serializable dictionary."""
        res = result or self.last_result
        if res is None:
            return {}

        return {
            "model_version": res.model_version,
            "method": res.method,
            "n_clusters": res.n_clusters,
            "total_documents": res.total_documents,
            "silhouette_score": res.silhouette_score,
            "inertia": res.inertia,
            "clusters": [
                {
                    "cluster_id": c.cluster_id,
                    "label": c.label,
                    "size": c.size,
                    "top_terms": c.top_terms,
                    "representative_papers": [
                        {
                            "paper_id": p.paper_id,
                            "title": p.title,
                            "similarity_to_centroid": p.similarity_to_centroid,
                            "category": p.category,
                        }
                        for p in c.representative_papers
                    ],
                    "paper_ids": c.paper_ids,
                }
                for c in res.clusters
            ],
        }

    def save(self, filepath: str) -> None:
        """Save clustering results to JSON file."""
        if self.last_result is None:
            raise RuntimeError("No clustering results to save. Call fit() first.")

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(self.last_result), f, indent=2)

    def load(self, filepath: str) -> ClusteringResult:
        """Load clustering results from JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Clustering file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        clusters = [
            ClusterSummary(
                cluster_id=c["cluster_id"],
                label=c["label"],
                size=c["size"],
                top_terms=c["top_terms"],
                representative_papers=[
                    RepresentativePaper(
                        paper_id=p["paper_id"],
                        title=p["title"],
                        similarity_to_centroid=p["similarity_to_centroid"],
                        category=p.get("category"),
                    )
                    for p in c.get("representative_papers", [])
                ],
                paper_ids=c.get("paper_ids", []),
            )
            for c in data.get("clusters", [])
        ]

        self.last_result = ClusteringResult(
            method=data["method"],
            n_clusters=data["n_clusters"],
            silhouette_score=data["silhouette_score"],
            inertia=data.get("inertia"),
            clusters=clusters,
            total_documents=data["total_documents"],
            model_version=data.get("model_version", self.model_version),
        )
        return self.last_result
