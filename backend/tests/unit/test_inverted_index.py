"""Unit tests for custom Inverted Index implementation."""

import os
import tempfile
import pytest

from backend.app.retrieval.inverted_index import InvertedIndex
from backend.tests.fixtures.toy_corpus import TOY_DOCUMENTS


@pytest.fixture
def indexed_toy_corpus():
    """Build an inverted index using the 5-doc toy fixture corpus."""
    index = InvertedIndex()
    docs = [(doc["id"], doc["text"]) for doc in TOY_DOCUMENTS]
    index.build_from_documents(docs)
    return index


def test_inverted_index_basic_stats(indexed_toy_corpus):
    """Test document count, average document length, and vocabulary."""
    index = indexed_toy_corpus
    assert index.doc_count == 5
    assert len(index.doc_lengths) == 5
    assert index.avg_doc_length > 0.0

    vocab = index.get_vocabulary()
    assert "retriev" in vocab or "inform" in vocab
    assert "databas" in vocab


def test_inverted_index_postings(indexed_toy_corpus):
    """Test postings dictionary structure and term frequencies."""
    index = indexed_toy_corpus
    # 'search' stemmed is 'search'
    search_postings = index.get_postings("search")
    assert "doc1" in search_postings
    assert "doc2" in search_postings
    assert "doc4" in search_postings
    assert "doc3" not in search_postings
    assert "doc5" not in search_postings

    # doc2 text has "search search search" -> tf should be 3
    assert search_postings["doc2"] == 3
    assert search_postings["doc1"] == 1

    assert index.get_doc_frequency("search") == 3
    assert index.get_term_frequency("search", "doc2") == 3
    assert index.get_term_frequency("search", "doc5") == 0


def test_inverted_index_serialization(indexed_toy_corpus):
    """Test saving and loading the index artifact via JSON."""
    index = indexed_toy_corpus
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "test_index.json")
        index.save(save_path)

        assert os.path.exists(save_path)

        loaded = InvertedIndex.load(save_path)
        assert loaded.doc_count == index.doc_count
        assert loaded.avg_doc_length == index.avg_doc_length
        assert loaded.get_vocabulary() == index.get_vocabulary()
        assert loaded.get_postings("search") == index.get_postings("search")


def test_empty_index():
    """Test empty index edge cases."""
    index = InvertedIndex()
    assert index.doc_count == 0
    assert index.avg_doc_length == 0.0
    assert index.get_doc_frequency("anything") == 0
    assert index.get_term_frequency("anything", "doc1") == 0
    assert index.get_vocabulary() == set()
