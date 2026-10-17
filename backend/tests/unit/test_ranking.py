"""Unit tests for TF-IDF Cosine Similarity and Okapi BM25 Ranking Engines."""

import pytest
import math
from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.retrieval.tfidf import TFIDFRetrievalEngine
from backend.app.retrieval.bm25 import BM25RetrievalEngine
from backend.tests.fixtures.toy_corpus import TOY_DOCUMENTS


@pytest.fixture
def ranked_toy_corpus():
    """Build index from toy corpus for ranking verification."""
    index = InvertedIndex()
    docs = [(doc["id"], doc["text"]) for doc in TOY_DOCUMENTS]
    index.build_from_documents(docs)
    return index


def test_tfidf_scores_and_bounds(ranked_toy_corpus):
    """Test TF-IDF cosine similarity scores are bounded in [0, 1]."""
    engine = TFIDFRetrievalEngine(ranked_toy_corpus)
    results = engine.score("database sql transactions")

    assert len(results) > 0
    top_result = results[0]
    assert top_result.doc_id == "doc5"
    assert 0.0 < top_result.score <= 1.0
    assert top_result.rank == 1

    # Term scores should explain the total
    assert "sql" in top_result.term_scores or "transact" in top_result.term_scores


def test_tfidf_empty_and_unknown(ranked_toy_corpus):
    """Test TF-IDF with empty queries or terms not in vocabulary."""
    engine = TFIDFRetrievalEngine(ranked_toy_corpus)
    assert engine.score("") == []
    assert engine.score("xyzfoobar123") == []


def test_bm25_term_frequency_saturation(ranked_toy_corpus):
    """Test that BM25 exhibits sublinear term frequency saturation."""
    engine = BM25RetrievalEngine(ranked_toy_corpus, k1=1.5, b=0.75)
    results = engine.score("search")

    # In toy corpus, doc2 has tf=3 for 'search', doc1 has tf=1
    scores_by_id = {r.doc_id: r.score for r in results}
    assert "doc2" in scores_by_id
    assert "doc1" in scores_by_id

    score_doc2 = scores_by_id["doc2"]
    score_doc1 = scores_by_id["doc1"]

    # doc2 has 3x term frequency, but BM25 score must be strictly less than 3x doc1 score
    assert score_doc2 > score_doc1
    assert score_doc2 < (3.0 * score_doc1), "BM25 must saturate and not scale linearly with tf"


def test_bm25_explainable_breakdown(ranked_toy_corpus):
    """Test that BM25 returns explainable term scores summing to total score."""
    engine = BM25RetrievalEngine(ranked_toy_corpus)
    results = engine.score("deep neural retrieval")

    for result in results:
        # Sum of individual term contributions should approximate the total score
        term_sum = sum(result.term_scores.values())
        assert math.isclose(term_sum, result.score, abs_tol=1e-3)


def test_bm25_empty_query(ranked_toy_corpus):
    """Test BM25 empty query handling."""
    engine = BM25RetrievalEngine(ranked_toy_corpus)
    assert engine.score("") == []
    assert engine.score("     ") == []
    assert engine.score("completelyunknowntokendetected") == []
