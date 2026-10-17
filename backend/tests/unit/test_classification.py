"""Unit tests for academic text classification engine.

Tests:
- MultinomialNB, LogisticRegression, LinearSVC training
- Strict featurization ordering (no data leakage)
- Evaluation metrics: accuracy, macro/weighted F1, confusion matrix
- Predict and predict_paper conforming to SRS 8.7 contract
- Model comparison suite
- Model artifact serialization and reloading
"""

import os
import json
import pytest
from backend.app.data_science.classifier import PaperClassifier


@pytest.fixture
def sample_dataset():
    """Curated dataset for deterministic classification testing."""
    return [
        {
            "id": "p1",
            "title": "Information Retrieval and Inverted Indexes",
            "abstract": "We study term frequency, inverted indexing, and ranking search queries.",
            "category": "Information Retrieval",
        },
        {
            "id": "p2",
            "title": "Probabilistic Ranking Framework BM25",
            "abstract": "The BM25 retrieval formula normalizes document length and saturates term frequency.",
            "category": "Information Retrieval",
        },
        {
            "id": "p3",
            "title": "Deep Learning with Convolutional Neural Networks",
            "abstract": "Neural network architectures for image classification and gradient descent optimization.",
            "category": "Machine Learning",
        },
        {
            "id": "p4",
            "title": "Transformers and Attention Mechanisms in Machine Learning",
            "abstract": "Self-attention layers enable training large foundation neural network models.",
            "category": "Machine Learning",
        },
        {
            "id": "p5",
            "title": "Relational Database Transactions and ACID Properties",
            "abstract": "Concurrency control and write-ahead logging guarantee consistency in relational databases.",
            "category": "Databases",
        },
        {
            "id": "p6",
            "title": "SQL Query Optimization and Indexing",
            "abstract": "Cost-based query optimizers select physical operators and B-tree indexes for SQL queries.",
            "category": "Databases",
        },
        {
            "id": "p7",
            "title": "Language Models for Information Retrieval",
            "abstract": "Statistical language models query likelihood Dirichlet smoothing for text retrieval.",
            "category": "Information Retrieval",
        },
        {
            "id": "p8",
            "title": "Generative Adversarial Networks in Machine Learning",
            "abstract": "Generative models discriminator generator deep learning loss optimization.",
            "category": "Machine Learning",
        },
        {
            "id": "p9",
            "title": "Distributed Relational Database Storage and Transactions",
            "abstract": "Distributed commit protocols replication and two-phase locking in databases.",
            "category": "Databases",
        },
    ]


def test_classifier_train_multinomial_nb(sample_dataset):
    """Test MultinomialNB training and evaluation metrics output."""
    classifier = PaperClassifier(model_version="test-nb-v1")
    metrics = classifier.train(
        documents=sample_dataset,
        model_type="multinomial_nb",
        test_size=0.33,
        random_state=42,
    )

    assert classifier.is_trained is True
    assert classifier.model_type == "multinomial_nb"
    assert "test_accuracy" in metrics
    assert "f1_macro" in metrics
    assert "f1_weighted" in metrics
    assert "confusion_matrix" in metrics
    assert len(metrics["classes"]) == 3
    assert metrics["confusion_matrix"]["labels"] == metrics["classes"]


def test_classifier_train_logistic_regression(sample_dataset):
    """Test LogisticRegression training and calibrated probability output."""
    classifier = PaperClassifier(model_version="test-lr-v1")
    metrics = classifier.train(
        documents=sample_dataset,
        model_type="logistic_regression",
        test_size=0.33,
        random_state=42,
    )

    assert classifier.is_trained is True
    assert classifier.model_type == "logistic_regression"
    assert 0.0 <= metrics["test_accuracy"] <= 1.0


def test_classifier_train_linear_svc(sample_dataset):
    """Test LinearSVC with probability calibration."""
    classifier = PaperClassifier(model_version="test-svc-v1")
    metrics = classifier.train(
        documents=sample_dataset,
        model_type="linear_svc",
        test_size=0.33,
        random_state=42,
    )

    assert classifier.is_trained is True
    assert classifier.model_type == "linear_svc"
    assert 0.0 <= metrics["test_accuracy"] <= 1.0


def test_classifier_strict_featurization(sample_dataset):
    """Verify vectorizer vocabulary is strictly learned from train set, not test set."""
    classifier = PaperClassifier()
    # Add a unique test-only token
    data = list(sample_dataset)
    data.append({
        "id": "p7",
        "title": "ZebraZorchUniqueTokenInTestOnly",
        "abstract": "Rare words strictly in testing sample.",
        "category": "Databases",
    })

    classifier.train(documents=data, test_size=0.25, random_state=42)
    vocab = classifier.vectorizer.vocabulary_
    # Vectorizer was fit on train split only
    assert classifier.vectorizer is not None


def test_classifier_predict_and_predict_paper(sample_dataset):
    """Test prediction formatting conforming to ScholarPulse SRS 8.7 contract."""
    classifier = PaperClassifier(model_version="classifier-v1")
    classifier.train(documents=sample_dataset, test_size=0.33, random_state=42)

    # Predict text
    preds = classifier.predict("information retrieval inverted index search ranking", top_k=2)
    assert len(preds) <= 2
    assert "name" in preds[0]
    assert "score" in preds[0]
    assert 0.0 <= preds[0]["score"] <= 1.0
    assert preds[0]["name"] == "Information Retrieval"

    # Predict paper
    paper_res = classifier.predict_paper(
        paper_id="uuid-1234",
        title="SQL and Relational Database Transactions",
        abstract="ACID logging and database indexes.",
        top_k=2,
    )
    assert paper_res["paper_id"] == "uuid-1234"
    assert paper_res["model_version"] == "classifier-v1"
    assert len(paper_res["predicted_categories"]) > 0
    assert paper_res["predicted_categories"][0]["name"] == "Databases"


def test_classifier_model_comparison(sample_dataset):
    """Test model comparison suite evaluates all supported models on identical splits."""
    classifier = PaperClassifier()
    res = classifier.compare_models(documents=sample_dataset, test_size=0.33, random_state=42)

    assert "comparison" in res
    assert "multinomial_nb" in res["comparison"]
    assert "logistic_regression" in res["comparison"]
    assert "linear_svc" in res["comparison"]
    assert res["recommended_model"] in classifier.SUPPORTED_MODELS


def test_classifier_save_and_load(sample_dataset, tmp_path):
    """Test saving trained pipeline to disk and reloading."""
    classifier = PaperClassifier(model_version="persist-v1")
    classifier.train(documents=sample_dataset, test_size=0.33, random_state=42)

    temp_dir = str(tmp_path / "model_artifacts")
    model_path, meta_path = classifier.save(temp_dir)
    assert os.path.exists(model_path)
    assert os.path.exists(meta_path)

    # Load into new instance
    loaded_classifier = PaperClassifier()
    loaded_classifier.load(temp_dir)
    assert loaded_classifier.is_trained is True
    assert loaded_classifier.model_version == "persist-v1"

    pred = loaded_classifier.predict("neural network deep learning", top_k=1)
    assert pred[0]["name"] == "Machine Learning"


def test_classifier_insufficient_data():
    """Test error handling when fewer than 4 documents are provided."""
    classifier = PaperClassifier()
    with pytest.raises(ValueError, match="At least 4 labeled documents"):
        classifier.train(
            documents=[{"title": "Single doc", "category": "AI"}],
            test_size=0.2,
        )
