"""Unit tests for text preprocessing, tokenization, stemming, and DOI cleaning."""

import pytest
from backend.app.preprocessing import (
    normalize_text,
    clean_doi,
    tokenize,
    stem,
    preprocess_text,
    build_searchable_text,
)


def test_normalize_text():
    """Verify lowercasing, whitespace stripping, and accent removal."""
    raw = "  Deep  Learning \n & Natural—Language Processing! naïve café  "
    normalized = normalize_text(raw)
    assert normalized == "deep learning natural language processing naive cafe"


def test_clean_doi():
    """Verify standard DOI URL prefixes are cleaned properly."""
    assert clean_doi("https://doi.org/10.1145/361219.361220") == "10.1145/361219.361220"
    assert clean_doi("http://dx.doi.org/10.1000/182") == "10.1000/182"
    assert clean_doi("doi:10.48550/arXiv.1706.03762") == "10.48550/arxiv.1706.03762"
    assert clean_doi("  10.1561/1500000019  ") == "10.1561/1500000019"
    assert clean_doi(None) is None
    assert clean_doi("") is None


def test_tokenize():
    """Verify tokenization splits words and strips punctuation."""
    text = "BM25 is a probabilistic ranking function for text retrieval."
    tokens = tokenize(text)
    assert "bm25" in tokens
    assert "probabilistic" in tokens
    assert "retrieval" in tokens
    assert "." not in tokens


def test_stem():
    """Verify Porter stemming rules."""
    assert stem("retrieval") == "retriev"
    assert stem("retrieving") == "retriev"
    assert stem("connected") == "connect"
    assert stem("connections") == "connect"


def test_preprocess_text():
    """Verify stopwords removal and stemming pipeline."""
    text = "The quick brown fox is jumping over the lazy dog"
    processed = preprocess_text(text, remove_stopwords=True, apply_stemming=True)
    # 'the', 'is', 'over' are stopwords
    assert "the" not in processed
    assert "is" not in processed
    assert "over" not in processed
    assert "quick" in processed
    assert "brown" in processed
    assert "fox" in processed
    assert "jump" in processed  # jumping stemmed to jump


def test_build_searchable_text():
    """Verify combination of title, abstract, and keywords into normalized stemmed text."""
    title = "Attention Is All You Need"
    abstract = "We propose the Transformer model based on self-attention."
    keywords = ["Transformers", "Attention", "Deep Learning"]

    searchable = build_searchable_text(title=title, abstract=abstract, keywords=keywords)
    assert "attent" in searchable
    assert "transform" in searchable
    assert "deep" in searchable
    assert "is" not in searchable.split()  # stopword excluded
