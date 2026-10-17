"""Unit tests for objective IR Evaluation metrics (P@K, Recall@K, MAP, MRR, NDCG@K)."""

import math
import pytest

from backend.app.evaluation.retrieval_eval import (
    compute_precision_at_k,
    compute_recall_at_k,
    compute_average_precision,
    compute_reciprocal_rank,
    compute_dcg_at_k,
    compute_ndcg_at_k,
)


def test_precision_at_k():
    """Test Precision@K on hand-calculable ranking."""
    retrieved = ["d1", "d2", "d3", "d4", "d5"]
    relevant = {"d1", "d3"}

    assert compute_precision_at_k(retrieved, relevant, k=1) == 1.0
    assert compute_precision_at_k(retrieved, relevant, k=2) == 0.5
    assert math.isclose(compute_precision_at_k(retrieved, relevant, k=3), 2.0 / 3.0)
    assert compute_precision_at_k(retrieved, relevant, k=5) == 0.4
    assert compute_precision_at_k(retrieved, relevant, k=0) == 0.0


def test_recall_at_k():
    """Test Recall@K on hand-calculable ranking."""
    retrieved = ["d1", "d2", "d3", "d4", "d5"]
    relevant = {"d1", "d3"}

    assert compute_recall_at_k(retrieved, relevant, k=1) == 0.5
    assert compute_recall_at_k(retrieved, relevant, k=2) == 0.5
    assert compute_recall_at_k(retrieved, relevant, k=3) == 1.0
    assert compute_recall_at_k(retrieved, relevant, k=5) == 1.0
    assert compute_recall_at_k(retrieved, set(), k=5) == 0.0


def test_average_precision():
    """Test Average Precision (AP) calculation."""
    retrieved = ["d1", "d2", "d3"]
    relevant = {"d1", "d3"}
    # Rank 1: d1 -> P@1 = 1.0
    # Rank 2: d2 -> non-relevant
    # Rank 3: d3 -> P@3 = 2/3
    # AP = (1.0 + 2/3) / 2 = 5/6 approx 0.8333
    ap = compute_average_precision(retrieved, relevant)
    assert math.isclose(ap, 5.0 / 6.0, rel_tol=1e-3)

    # All non-relevant
    assert compute_average_precision(["d2", "d4"], relevant) == 0.0
    assert compute_average_precision([], relevant) == 0.0


def test_reciprocal_rank():
    """Test Reciprocal Rank (RR)."""
    assert compute_reciprocal_rank(["d1", "d2"], {"d1"}) == 1.0
    assert compute_reciprocal_rank(["d2", "d1"], {"d1"}) == 0.5
    assert compute_reciprocal_rank(["d2", "d3", "d1"], {"d1"}) == 1.0 / 3.0
    assert compute_reciprocal_rank(["d2", "d3"], {"d1"}) == 0.0


def test_ndcg_at_k():
    """Test DCG and NDCG calculation against ideal ranking."""
    judgments = {"d1": 2, "d3": 1}
    retrieved = ["d1", "d2", "d3"]

    # Hand-calculation:
    # Actual DCG@3 = (2^2 - 1)/log2(2) + 0 + (2^1 - 1)/log2(4) = 3/1 + 1/2 = 3.5
    dcg = compute_dcg_at_k(retrieved, judgments, k=3)
    assert math.isclose(dcg, 3.5, rel_tol=1e-3)

    # Ideal ranking is [d1 (grade 2), d3 (grade 1)]
    # IDCG@3 = 3/log2(2) + 1/log2(3) = 3 + 1/1.5849625 approx 3.6309
    ndcg = compute_ndcg_at_k(retrieved, judgments, k=3)
    assert 0.96 < ndcg < 0.97

    # Perfect ranking produces NDCG = 1.0
    perfect = ["d1", "d3"]
    assert math.isclose(compute_ndcg_at_k(perfect, judgments, k=2), 1.0, rel_tol=1e-4)

    # Zero relevant retrieved produces NDCG = 0.0
    assert compute_ndcg_at_k(["d99", "d98"], judgments, k=5) == 0.0
