"""Integration tests for objective Information Retrieval Evaluation Harness and Benchmarking."""

import os
import pytest

from backend.app.retrieval.search_service import SearchService
from backend.app.evaluation.retrieval_eval import RetrievalEvaluator
from backend.app.core.config import get_settings

SETTINGS = get_settings()
JUDGMENTS_FILE = os.path.join("datasets", "eval", "relevance_judgments.json")


@pytest.fixture(scope="module")
def search_service():
    """Index sample dataset papers in SearchService."""
    service = SearchService()
    service.build_from_dataset(SETTINGS.DATASET_PATH)
    return service


@pytest.fixture(scope="module")
def benchmark_queries():
    """Load ground-truth benchmark judgments."""
    evaluator = RetrievalEvaluator()
    return evaluator.load_judgments(JUDGMENTS_FILE)


def test_bm25_evaluation(search_service, benchmark_queries):
    """Test BM25 evaluation returns non-zero MAP and NDCG scores."""
    evaluator = RetrievalEvaluator(cutoffs=[5, 10])
    summary = evaluator.evaluate_ranker(search_service, method="bm25", benchmark_queries=benchmark_queries)

    assert summary.method == "bm25"
    assert summary.num_queries == len(benchmark_queries)
    assert 0.0 < summary.map_score <= 1.0
    assert 0.0 < summary.mrr_score <= 1.0
    assert 0.0 < summary.mean_ndcg_at_k[5] <= 1.0
    assert 0.0 < summary.mean_precision_at_k[5] <= 1.0


def test_tfidf_evaluation(search_service, benchmark_queries):
    """Test TF-IDF evaluation against benchmark judgments."""
    evaluator = RetrievalEvaluator(cutoffs=[5, 10])
    summary = evaluator.evaluate_ranker(search_service, method="tfidf", benchmark_queries=benchmark_queries)

    assert summary.method == "tfidf"
    assert 0.0 < summary.map_score <= 1.0
    assert 0.0 < summary.mrr_score <= 1.0


def test_language_model_evaluation(search_service, benchmark_queries):
    """Test Query-Likelihood Language Model evaluation against benchmark judgments."""
    evaluator = RetrievalEvaluator(cutoffs=[5, 10])
    summary = evaluator.evaluate_ranker(
        search_service,
        method="language_model",
        benchmark_queries=benchmark_queries,
    )

    assert summary.method == "language_model"
    assert 0.0 < summary.map_score <= 1.0
    assert 0.0 < summary.mrr_score <= 1.0


def test_multi_ranker_comparison_report(search_service, benchmark_queries):
    """Test comparative benchmark report generation across BM25, TF-IDF, and Language Model."""
    evaluator = RetrievalEvaluator(cutoffs=[5, 10])
    report = evaluator.compare_rankers(
        search_service=search_service,
        methods=["bm25", "tfidf", "language_model"],
        benchmark_queries=benchmark_queries,
    )

    assert report["num_evaluated_queries"] == 5
    comparison = report["ranker_comparison"]

    assert "bm25" in comparison
    assert "tfidf" in comparison
    assert "language_model" in comparison

    for method in ["bm25", "tfidf", "language_model"]:
        m_stats = comparison[method]
        assert "map" in m_stats
        assert "mrr" in m_stats
        assert "ndcg@5" in m_stats
        assert 0.0 < m_stats["map"] <= 1.0


def test_search_service_passage_snippets(search_service):
    """Test that SearchService populates snippets and highlight tags in results."""
    response = search_service.search("probabilistic relevance bm25", method="bm25", top_k=3)
    assert len(response.results) > 0

    top_result = response.results[0]
    assert top_result.snippet is not None
    assert len(top_result.snippet) > 0
    assert top_result.highlighted_snippet is not None
    assert "<mark>" in top_result.highlighted_snippet
