"""Integration tests for DataScienceService against the 25-paper curated sample dataset.

Verifies end-to-end integration:
- Category classification training and inference on sample corpus
- K-Means and Hierarchical clustering on sample papers
- Apriori association rule mining from sample keyword transactions
- Content-based related-paper recommendations
- Bibliometric analytics on publication years and author networks
- Artifact serialization and reload
"""

import os
import json
import pytest
from backend.app.data_science.service import DataScienceService


@pytest.fixture
def sample_papers_dataset():
    """Load canonical 25-paper sample dataset."""
    dataset_path = os.path.join("datasets", "raw", "sample_papers.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_ds_service_classifier_lifecycle(sample_papers_dataset, tmp_path):
    """Test classifier training, evaluation, persistence, and inference via DataScienceService."""
    artifacts_dir = str(tmp_path / "ds_artifacts")
    service = DataScienceService(artifacts_dir=artifacts_dir)

    metrics = service.train_classifier(
        papers=sample_papers_dataset,
        model_type="logistic_regression",
        test_size=0.2,
        random_state=42,
    )

    assert service.classifier.is_trained is True
    assert "test_accuracy" in metrics
    assert "f1_macro" in metrics
    assert "confusion_matrix" in metrics
    assert os.path.exists(os.path.join(artifacts_dir, "classifier.joblib"))
    assert os.path.exists(os.path.join(artifacts_dir, "classifier_metadata.json"))

    # Test text classification
    pred = service.classify_text("Okapi BM25 term frequency saturation and document ranking", top_k=2)
    assert len(pred) > 0
    assert pred[0]["name"] == "Information Retrieval"

    # Test paper classification conforming to SRS 8.7 contract
    paper_res = service.classify_paper(
        paper_id="test-paper-uuid",
        title="Deep Residual Learning for Image Recognition",
        abstract="Deep convolutional neural network architecture with residual connections.",
    )
    assert paper_res["paper_id"] == "test-paper-uuid"
    assert len(paper_res["predicted_categories"]) > 0
    assert paper_res["predicted_categories"][0]["name"] == "Machine Learning"


def test_ds_service_clustering_pipeline(sample_papers_dataset, tmp_path):
    """Test K-Means and Hierarchical clustering on sample corpus via DataScienceService."""
    artifacts_dir = str(tmp_path / "ds_artifacts")
    service = DataScienceService(artifacts_dir=artifacts_dir)

    # K-Means clustering
    kmeans_result = service.cluster_corpus(
        papers=sample_papers_dataset,
        n_clusters=4,
        method="kmeans",
        random_state=42,
    )

    assert kmeans_result.n_clusters == 4
    assert kmeans_result.total_documents == 25
    assert kmeans_result.silhouette_score != 0.0
    assert len(kmeans_result.clusters) == 4
    assert os.path.exists(os.path.join(artifacts_dir, "clustering_results.json"))

    # Check top terms in cluster labels
    for cl in kmeans_result.clusters:
        assert len(cl.label) > 0
        assert len(cl.representative_papers) > 0

    # Hierarchical clustering comparison
    hier_result = service.cluster_corpus(
        papers=sample_papers_dataset,
        n_clusters=4,
        method="hierarchical",
        random_state=42,
    )
    assert hier_result.n_clusters == 4
    assert hier_result.method == "hierarchical"


def test_ds_service_association_rules(sample_papers_dataset, tmp_path):
    """Test Apriori association rule mining from paper keywords via DataScienceService."""
    artifacts_dir = str(tmp_path / "ds_artifacts")
    service = DataScienceService(artifacts_dir=artifacts_dir)

    result = service.mine_association_rules(
        papers=sample_papers_dataset,
        min_support=0.08,
        min_confidence=0.4,
        min_lift=1.0,
    )

    assert result.total_transactions == 25
    assert result.frequent_itemsets_count > 0
    assert result.rules_count > 0
    assert os.path.exists(os.path.join(artifacts_dir, "association_rules.json"))

    # Test pagination conforming to SRS 8.8
    paginated = service.association_miner.paginate_rules(page=1, page_size=5)
    assert paginated["page"] == 1
    assert len(paginated["rules"]) <= 5
    assert paginated["total_rules"] == result.rules_count


def test_ds_service_recommendations(sample_papers_dataset):
    """Test content-based related-paper recommendations on sample corpus."""
    service = DataScienceService()
    service.fit_recommender(sample_papers_dataset)

    # First paper is "The Probabilistic Relevance Framework: BM25 and Beyond" (external_id: ir-foundations-01)
    bm25_paper = sample_papers_dataset[0]
    bm25_id = bm25_paper.get("id") or bm25_paper.get("external_id")

    recs = service.get_related_papers(paper_id=bm25_id, top_n=5)
    assert len(recs) > 0
    # Seed paper MUST NOT be in recommendations
    rec_ids = [r.paper_id for r in recs]
    assert bm25_id not in rec_ids

    # Top recommendation should also be in Information Retrieval
    assert recs[0].category == "Information Retrieval"
    assert recs[0].similarity_score > 0.0


def test_ds_service_analytics(sample_papers_dataset):
    """Test comprehensive research analytics generation on sample corpus."""
    service = DataScienceService()
    analytics_data = service.get_analytics(sample_papers_dataset)

    assert "overview" in analytics_data
    assert "publication_trends" in analytics_data
    assert "category_distribution" in analytics_data
    assert "top_keywords" in analytics_data
    assert "top_authors" in analytics_data
    assert "coauthorship_network" in analytics_data

    # Overview assertions
    overview = analytics_data["overview"]
    assert overview["total_papers"] == 25
    assert overview["total_authors"] >= 50
    assert overview["total_categories"] == 5

    # Trends assertions
    trends = analytics_data["publication_trends"]
    assert len(trends) > 5

    # Network assertions
    network = analytics_data["coauthorship_network"]
    assert network["total_nodes"] >= 50
    assert network["total_edges"] > 0
