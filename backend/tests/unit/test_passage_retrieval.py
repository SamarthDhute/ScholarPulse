"""Unit tests for Passage Retrieval and Snippet Extraction."""

import pytest
from backend.app.retrieval.passage_retrieval import PassageRetrievalEngine


@pytest.fixture
def passage_engine():
    return PassageRetrievalEngine(max_snippet_length=200)


def test_split_sentences(passage_engine):
    """Test sentence boundary splitting."""
    text = "First sentence about IR. Second sentence about deep learning! Third sentence about BM25?"
    sentences = passage_engine.split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "First sentence about IR."
    assert sentences[1] == "Second sentence about deep learning!"
    assert sentences[2] == "Third sentence about BM25?"


def test_extract_best_passage_with_term_overlap(passage_engine):
    """Test that the sentence containing the most query terms is chosen as the passage."""
    text = (
        "Inverted indexes are the core data structure for search engines. "
        "They map terms to postings containing document IDs and term frequencies. "
        "Query processing algorithms evaluate boolean and ranked queries using these lists."
    )
    query = "postings document term frequencies"
    passage = passage_engine.extract_best_passage(text, query)

    assert "postings containing document IDs" in passage.text
    assert passage.score > 0.0
    assert len(passage.matched_terms) > 0


def test_extract_best_passage_highlighting(passage_engine):
    """Test HTML mark tag highlighting around matched terms."""
    text = "Okapi BM25 scores documents based on term frequency saturation and document length normalization."
    query = "bm25 term frequency"
    passage = passage_engine.extract_best_passage(text, query)

    assert "<mark>" in passage.highlighted_text
    assert "</mark>" in passage.highlighted_text
    assert "<mark>bm25</mark>" in passage.highlighted_text.lower()


def test_extract_best_passage_empty_and_fallback(passage_engine):
    """Test empty text and stopword queries."""
    empty_passage = passage_engine.extract_best_passage("", "search")
    assert empty_passage.text == ""
    assert empty_passage.score == 0.0

    text = "A simple overview of search engines and their design."
    stopword_passage = passage_engine.extract_best_passage(text, "the and of in")
    assert stopword_passage.text == text
