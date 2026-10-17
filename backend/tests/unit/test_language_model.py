"""Unit tests for Query-Likelihood Language Model retrieval engine."""

import math
import pytest
from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.retrieval.language_model import LanguageModelRetrievalEngine
from backend.tests.fixtures.toy_corpus import TOY_DOCUMENTS


@pytest.fixture
def lm_engine():
    """Build a LanguageModelRetrievalEngine on toy corpus."""
    index = InvertedIndex()
    docs = [(doc["id"], doc["text"]) for doc in TOY_DOCUMENTS]
    index.build_from_documents(docs)
    return LanguageModelRetrievalEngine(index, smoothing="dirichlet", mu=500.0)


def test_language_model_collection_prob(lm_engine):
    """Test background collection probability calculation."""
    # Total collection tokens > 0
    assert lm_engine.total_collection_tokens > 0

    p_c_search = lm_engine.get_collection_prob("search")
    assert p_c_search > 0.0

    # Non-existent term gets fallback epsilon, never 0
    p_c_unknown = lm_engine.get_collection_prob("nonexistenttoken123")
    assert p_c_unknown > 0.0


def test_language_model_dirichlet_smoothing(lm_engine):
    """Test Dirichlet smoothing assigns non-zero probabilities to unseen words in a document."""
    # doc1 has 'retriev', does not have 'neural'
    p_retriev = lm_engine.score_term_dirichlet("retriev", "doc1")
    p_neural = lm_engine.score_term_dirichlet("neural", "doc1")

    assert p_retriev > p_neural
    assert p_neural > 0.0  # Smooths to background collection model


def test_language_model_jelinek_mercer_smoothing():
    """Test Jelinek-Mercer linear interpolation smoothing."""
    index = InvertedIndex()
    docs = [(doc["id"], doc["text"]) for doc in TOY_DOCUMENTS]
    index.build_from_documents(docs)
    engine = LanguageModelRetrievalEngine(index, smoothing="jm", lam=0.2)

    p_search = engine.score_term_jm("search", "doc2")
    assert p_search > 0.0

    p_unseen = engine.score_term_jm("databas", "doc2")
    assert p_unseen > 0.0
    assert p_search > p_unseen


def test_language_model_ranking(lm_engine):
    """Test Query Likelihood log-likelihood ranking."""
    results = lm_engine.score("database sql transactions")
    assert len(results) > 0
    top = results[0]
    assert top.doc_id == "doc5"
    assert top.method == "language_model"
    assert top.rank == 1
    # Log likelihood is negative
    assert top.score < 0.0
    assert "sql" in top.term_scores or "databas" in top.term_scores


def test_language_model_empty_and_unknown(lm_engine):
    """Test empty query and unknown query handling."""
    assert lm_engine.score("") == []
    assert lm_engine.score("   ") == []
    assert lm_engine.score("xyzfoobar12345") == []
