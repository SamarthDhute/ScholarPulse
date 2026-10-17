"""Integration tests for SearchService against the curated 25-paper dataset."""

import os
import tempfile
import pytest

from backend.app.retrieval.search_service import SearchService
from backend.app.core.config import get_settings

SETTINGS = get_settings()


@pytest.fixture(scope="module")
def search_service():
    """Build and return SearchService indexed on sample_papers.json."""
    service = SearchService()
    count = service.build_from_dataset(SETTINGS.DATASET_PATH)
    assert count == 25
    return service


def test_bm25_search_known_paper(search_service):
    """Test BM25 query correctly surfaces relevant paper at rank 1."""
    response = search_service.search("bm25 probabilistic ranking", method="bm25", top_k=5)
    assert response.method == "bm25"
    assert response.total_hits > 0
    assert len(response.results) <= 5

    top_paper = response.results[0]
    assert "BM25" in top_paper.metadata.get("title", "")
    assert top_paper.rank == 1
    assert top_paper.score > 0.0
    assert len(top_paper.term_scores) > 0


def test_tfidf_search(search_service):
    """Test TF-IDF retrieval ranks Vector Space Model paper high."""
    response = search_service.search("vector space model cosine similarity", method="tfidf", top_k=5)
    assert response.method == "tfidf"
    assert response.total_hits > 0

    top_paper = response.results[0]
    assert "Vector Space" in top_paper.metadata.get("title", "")
    assert 0.0 < top_paper.score <= 1.0


def test_boolean_search(search_service):
    """Test Boolean search returning unranked matches with score 1.0."""
    response = search_service.search("retrieval AND probabilistic", method="boolean")
    assert response.method == "boolean"
    assert response.total_hits > 0

    for result in response.results:
        assert result.score == 1.0


def test_search_metadata_filtering(search_service):
    """Test year range and category filters."""
    # Filter papers from 2015 onwards
    response = search_service.search(
        "neural network",
        method="bm25",
        year_min=2015,
        top_k=10,
    )
    for result in response.results:
        year = result.metadata.get("publication_year")
        assert year is not None and year >= 2015

    # Filter by category
    response_ir = search_service.search(
        "search",
        method="bm25",
        category="Information Retrieval",
        top_k=10,
    )
    for result in response_ir.results:
        categories = [c.lower() for c in result.metadata.get("categories", [])]
        assert "information retrieval" in categories


def test_search_pagination(search_service):
    """Test pagination across search results."""
    page_1 = search_service.search("model", method="bm25", top_k=3, page=1)
    page_2 = search_service.search("model", method="bm25", top_k=3, page=2)

    assert page_1.page == 1
    assert page_2.page == 2
    assert page_1.total_hits == page_2.total_hits

    ids_page_1 = [r.doc_id for r in page_1.results]
    ids_page_2 = [r.doc_id for r in page_2.results]

    # No overlap between page 1 and page 2
    assert set(ids_page_1).isdisjoint(set(ids_page_2))


def test_search_service_save_load_roundtrip(search_service):
    """Test saving and loading the SearchService artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        search_service.save(tmpdir)

        loaded_service = SearchService.load(tmpdir)
        assert loaded_service.index.doc_count == search_service.index.doc_count
        assert len(loaded_service.metadata) == len(search_service.metadata)

        # Query both services and verify identical results
        query = "probabilistic retrieval language"
        resp_orig = search_service.search(query, method="bm25", top_k=5)
        resp_loaded = loaded_service.search(query, method="bm25", top_k=5)

        assert resp_orig.total_hits == resp_loaded.total_hits
        assert [r.doc_id for r in resp_orig.results] == [r.doc_id for r in resp_loaded.results]
        assert [r.score for r in resp_orig.results] == [r.score for r in resp_loaded.results]
