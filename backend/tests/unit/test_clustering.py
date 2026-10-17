"""Unit tests for document clustering engine.

Tests:
- K-Means and Hierarchical/Agglomerative clustering
- Silhouette score and inertia calculations
- Topic label generation via top centroid features
- Representative paper ranking based on cosine proximity
- Finding optimal cluster count k
- JSON serialization and deserialization
- Edge case handling
"""

import os
import json
import pytest
from backend.app.data_science.clustering import PaperClustering


@pytest.fixture
def sample_papers_corpus():
    """Curated academic paper corpus for clustering evaluation."""
    return [
        {
            "id": "c1",
            "title": "BM25 Probabilistic Ranking and Inverted Indexes",
            "abstract": "Information retrieval search ranking term frequency saturation document length.",
            "category": "Information Retrieval",
        },
        {
            "id": "c2",
            "title": "Vector Space Model and Cosine Similarity Indexing",
            "abstract": "Information retrieval TF-IDF cosine similarity term weighting search query processing.",
            "category": "Information Retrieval",
        },
        {
            "id": "c3",
            "title": "Statistical Language Models for Text Search",
            "abstract": "Information retrieval unigram language models query likelihood smoothing Dirichlet.",
            "category": "Information Retrieval",
        },
        {
            "id": "c4",
            "title": "Deep Convolutional Neural Networks for Image Recognition",
            "abstract": "Machine learning neural networks deep learning backpropagation gradient descent.",
            "category": "Machine Learning",
        },
        {
            "id": "c5",
            "title": "Generative Adversarial Networks and Deep Generative Models",
            "abstract": "Machine learning neural networks generator discriminator loss optimization.",
            "category": "Machine Learning",
        },
        {
            "id": "c6",
            "title": "Transformers and Self-Attention Deep Learning",
            "abstract": "Machine learning neural networks attention mechanism language representation models.",
            "category": "Machine Learning",
        },
        {
            "id": "c7",
            "title": "Relational Database Transactions Concurrency and ACID",
            "abstract": "Databases relational transactions locks two-phase commit write-ahead logging.",
            "category": "Databases",
        },
        {
            "id": "c8",
            "title": "B-Tree Indexing and SQL Query Optimization",
            "abstract": "Databases relational SQL query execution cost-based optimization indexing.",
            "category": "Databases",
        },
    ]


def test_kmeans_clustering_basic(sample_papers_corpus):
    """Test K-Means clustering execution and metrics."""
    clustering = PaperClustering()
    result = clustering.fit(
        documents=sample_papers_corpus,
        n_clusters=3,
        method="kmeans",
        random_state=42,
    )

    assert result.method == "kmeans"
    assert result.n_clusters == 3
    assert result.total_documents == 8
    assert result.inertia is not None
    assert result.inertia >= 0.0
    assert -1.0 <= result.silhouette_score <= 1.0
    assert len(result.clusters) == 3


def test_hierarchical_clustering(sample_papers_corpus):
    """Test Hierarchical (Agglomerative) clustering with cosine linkage."""
    clustering = PaperClustering()
    result = clustering.fit(
        documents=sample_papers_corpus,
        n_clusters=3,
        method="hierarchical",
        random_state=42,
    )

    assert result.method == "hierarchical"
    assert result.n_clusters == 3
    assert result.inertia is None  # Inertia is specific to K-Means
    assert -1.0 <= result.silhouette_score <= 1.0


def test_cluster_topic_labels(sample_papers_corpus):
    """Test explainable cluster topic labels and top centroid features."""
    clustering = PaperClustering()
    result = clustering.fit(
        documents=sample_papers_corpus,
        n_clusters=3,
        method="kmeans",
        random_state=42,
        top_terms_count=4,
    )

    for cluster in result.clusters:
        assert cluster.size > 0
        assert len(cluster.label) > 0
        assert len(cluster.top_terms) > 0
        for t in cluster.top_terms:
            assert "term" in t
            assert "weight" in t
            assert t["weight"] >= 0.0


def test_representative_papers(sample_papers_corpus):
    """Test representative papers are identified and ranked by cosine similarity."""
    clustering = PaperClustering()
    result = clustering.fit(
        documents=sample_papers_corpus,
        n_clusters=3,
        method="kmeans",
        random_state=42,
        max_representatives=2,
    )

    for cluster in result.clusters:
        assert len(cluster.representative_papers) <= 2
        for rep in cluster.representative_papers:
            assert rep.paper_id in cluster.paper_ids
            assert len(rep.title) > 0
            assert -1.0 <= rep.similarity_to_centroid <= 1.0


def test_find_optimal_k(sample_papers_corpus):
    """Test evaluating optimal cluster count over candidate k values."""
    clustering = PaperClustering()
    opt_res = clustering.find_optimal_k(
        documents=sample_papers_corpus,
        k_range=(2, 3, 4),
        method="kmeans",
        random_state=42,
    )

    assert "optimal_k" in opt_res
    assert opt_res["optimal_k"] in (2, 3, 4)
    assert "evaluations" in opt_res
    assert 2 in opt_res["evaluations"]
    assert 3 in opt_res["evaluations"]


def test_clustering_save_and_load(sample_papers_corpus, tmp_path):
    """Test saving clustering results to JSON and reloading."""
    clustering = PaperClustering(model_version="cluster-test-v1")
    clustering.fit(
        documents=sample_papers_corpus,
        n_clusters=3,
        method="kmeans",
        random_state=42,
    )

    out_file = str(tmp_path / "clusters.json")
    clustering.save(out_file)
    assert os.path.exists(out_file)

    loaded_clustering = PaperClustering()
    loaded_result = loaded_clustering.load(out_file)

    assert loaded_result.n_clusters == 3
    assert loaded_result.total_documents == 8
    assert len(loaded_result.clusters) == 3
    assert loaded_result.model_version == "cluster-test-v1"


def test_clustering_edge_cases():
    """Test error handling on invalid cluster configurations."""
    clustering = PaperClustering()

    with pytest.raises(ValueError, match="at least 2 documents"):
        clustering.fit(documents=[{"title": "Single doc"}], n_clusters=2)

    with pytest.raises(ValueError, match="n_clusters must be >= 2"):
        clustering.fit(documents=[{"title": "D1"}, {"title": "D2"}], n_clusters=1)
