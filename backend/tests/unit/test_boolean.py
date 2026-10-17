"""Unit tests for Boolean Retrieval Engine with Shunting-Yard parser."""

import pytest
from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.retrieval.boolean import BooleanRetrievalEngine
from backend.tests.fixtures.toy_corpus import TOY_DOCUMENTS


@pytest.fixture
def boolean_engine():
    """Build a Boolean Retrieval Engine backed by toy corpus index."""
    index = InvertedIndex()
    docs = [(doc["id"], doc["text"]) for doc in TOY_DOCUMENTS]
    index.build_from_documents(docs)
    return BooleanRetrievalEngine(index)


def test_boolean_single_term(boolean_engine):
    """Test retrieving documents matching a single keyword."""
    docs = boolean_engine.search("sql")
    assert docs == {"doc5"}

    docs = boolean_engine.search("retrieval")
    assert docs == {"doc1", "doc2", "doc4"}


def test_boolean_and_operator(boolean_engine):
    """Test AND intersection between terms."""
    docs = boolean_engine.search("information AND search")
    assert docs == {"doc1", "doc2", "doc4"}

    docs = boolean_engine.search("neural AND search")
    assert docs == {"doc4"}

    docs = boolean_engine.search("sql AND retrieval")
    assert docs == set()


def test_boolean_or_operator(boolean_engine):
    """Test OR union between terms."""
    docs = boolean_engine.search("sql OR bm25")
    assert docs == {"doc2", "doc5"}


def test_boolean_not_operator(boolean_engine):
    """Test NOT set difference."""
    # Docs with retrieval but NOT neural
    docs = boolean_engine.search("retrieval NOT neural")
    assert docs == {"doc1", "doc2"}

    # Docs with learning but NOT search
    docs = boolean_engine.search("learning NOT search")
    assert docs == {"doc3"}


def test_boolean_parentheses_precedence(boolean_engine):
    """Test complex queries with parentheses and operator precedence."""
    # (neural OR deep) AND retrieval -> doc4
    docs = boolean_engine.search("(neural OR deep) AND retrieval")
    assert docs == {"doc4"}

    # (information AND retrieval) NOT (neural OR deep) -> doc1, doc2
    docs = boolean_engine.search("(information AND retrieval) NOT (neural OR deep)")
    assert docs == {"doc1", "doc2"}


def test_boolean_implicit_and(boolean_engine):
    """Test space-separated terms without explicit operator defaulting to AND."""
    docs = boolean_engine.search("information retrieval")
    assert docs == {"doc1", "doc2", "doc4"}

    docs = boolean_engine.search("neural learning search")
    assert docs == {"doc4"}


def test_boolean_empty_and_unknown(boolean_engine):
    """Test empty query and non-existent term handling."""
    assert boolean_engine.search("") == set()
    assert boolean_engine.search("nonexistentterm") == set()
    assert boolean_engine.search("nonexistentterm AND retrieval") == set()
