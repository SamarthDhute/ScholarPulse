"""Unit tests for Apriori association rule mining engine.

Tests:
- Frequent itemsets generation with support thresholds
- Association rules generation with support, confidence, lift, leverage, conviction
- Parameter validation per ScholarPulse SRS 8.8
- Query filtering by keyword in antecedents/consequents
- Bounded pagination
- JSON serialization and deserialization
- Empty transaction resilience
"""

import os
import json
import pytest
from backend.app.data_science.association_rules import KeywordAssociationMiner


@pytest.fixture
def keyword_transactions():
    """Curated transactions representing paper keywords for association mining."""
    return [
        ["information retrieval", "bm25", "ranking", "indexing"],
        ["information retrieval", "vector space model", "tf-idf", "cosine similarity", "ranking"],
        ["information retrieval", "bm25", "ranking", "probabilistic models"],
        ["information retrieval", "language models", "ranking", "smoothing"],
        ["machine learning", "deep learning", "neural networks", "classification"],
        ["machine learning", "deep learning", "neural networks", "transformers"],
        ["machine learning", "classification", "support vector machines"],
        ["relational databases", "sql", "transactions", "indexing"],
        ["relational databases", "sql", "query optimization", "indexing"],
        ["relational databases", "sql", "transactions", "acid"],
    ]


def test_apriori_frequent_itemsets(keyword_transactions):
    """Test frequent itemsets extraction and support threshold enforcement."""
    miner = KeywordAssociationMiner(model_version="test-assoc-v1")
    result = miner.mine(
        transactions=keyword_transactions,
        min_support=0.2,
        min_confidence=0.5,
        min_lift=1.0,
    )

    assert result.total_transactions == 10
    assert result.frequent_itemsets_count > 0
    for itemset in result.frequent_itemsets:
        assert itemset.support >= 0.2
        assert len(itemset.items) >= 1


def test_association_rules_generation(keyword_transactions):
    """Test rule generation and metrics calculation."""
    miner = KeywordAssociationMiner()
    result = miner.mine(
        transactions=keyword_transactions,
        min_support=0.2,
        min_confidence=0.5,
        min_lift=1.0,
    )

    assert result.rules_count > 0
    for rule in result.rules:
        assert len(rule.antecedents) >= 1
        assert len(rule.consequents) >= 1
        assert rule.support >= 0.2
        assert rule.confidence >= 0.5
        assert rule.lift >= 1.0
        assert rule.leverage is not None
        assert rule.conviction >= 0.0


def test_association_rules_parameter_validation():
    """Test validation of min_support, min_confidence, and min_lift thresholds."""
    miner = KeywordAssociationMiner()

    with pytest.raises(ValueError, match="min_support must be in range"):
        miner.validate_parameters(min_support=0.0, min_confidence=0.5, min_lift=1.0)

    with pytest.raises(ValueError, match="min_support must be in range"):
        miner.validate_parameters(min_support=1.5, min_confidence=0.5, min_lift=1.0)

    with pytest.raises(ValueError, match="min_confidence must be in range"):
        miner.validate_parameters(min_support=0.1, min_confidence=0.0, min_lift=1.0)

    with pytest.raises(ValueError, match="min_lift must be >= 0.0"):
        miner.validate_parameters(min_support=0.1, min_confidence=0.5, min_lift=-0.5)


def test_find_rules_for_term(keyword_transactions):
    """Test finding rules matching a target keyword."""
    miner = KeywordAssociationMiner()
    miner.mine(
        transactions=keyword_transactions,
        min_support=0.2,
        min_confidence=0.5,
        min_lift=1.0,
    )

    matched = miner.find_rules_for_term("bm25", position="antecedent")
    assert len(matched) > 0
    for rule in matched:
        assert any("bm25" in a.lower() for a in rule.antecedents)


def test_paginate_rules(keyword_transactions):
    """Test bounded pagination conforming to SRS 8.8."""
    miner = KeywordAssociationMiner()
    miner.mine(
        transactions=keyword_transactions,
        min_support=0.2,
        min_confidence=0.4,
        min_lift=1.0,
    )

    page1 = miner.paginate_rules(page=1, page_size=2)
    assert page1["page"] == 1
    assert page1["page_size"] == 2
    assert len(page1["rules"]) <= 2
    assert page1["total_rules"] == len(miner.last_result.rules)


def test_association_rules_save_and_load(keyword_transactions, tmp_path):
    """Test saving association mining output to JSON and loading back."""
    miner = KeywordAssociationMiner(model_version="persist-assoc-v1")
    miner.mine(
        transactions=keyword_transactions,
        min_support=0.2,
        min_confidence=0.5,
        min_lift=1.0,
    )

    out_file = str(tmp_path / "association_rules.json")
    miner.save(out_file)
    assert os.path.exists(out_file)

    loaded_miner = KeywordAssociationMiner()
    loaded_res = loaded_miner.load(out_file)
    assert loaded_res.total_transactions == 10
    assert loaded_res.model_version == "persist-assoc-v1"
    assert loaded_res.rules_count == len(miner.last_result.rules)


def test_empty_transactions():
    """Test graceful handling when transactions are empty."""
    miner = KeywordAssociationMiner()
    res = miner.mine(transactions=[], min_support=0.1, min_confidence=0.5)
    assert res.total_transactions == 0
    assert res.frequent_itemsets_count == 0
    assert res.rules_count == 0
