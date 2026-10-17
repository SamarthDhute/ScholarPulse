"""Unit tests for paper payload validation."""

import pytest
from backend.app.ingestion.validation import validate_paper_payload
from backend.app.core.errors import ValidationError


def test_validate_paper_payload_success():
    """Verify clean paper payload passes validation."""
    raw = {
        "title": "A Vector Space Model for Automatic Indexing",
        "abstract": "In a vector space model, textual documents and queries are represented as vectors.",
        "publication_year": 1975,
        "doi": "https://doi.org/10.1145/361219.361220",
        "source_name": "acm",
        "authors": ["Gerard Salton", "Anita Wong"],
        "keywords": ["information retrieval", "vector space model"],
        "categories": ["Information Retrieval"],
    }
    validated = validate_paper_payload(raw)
    assert validated["title"] == "A Vector Space Model for Automatic Indexing"
    assert validated["publication_year"] == 1975
    assert validated["doi"] == "10.1145/361219.361220"
    assert len(validated["authors"]) == 2
    assert validated["authors"][0]["display_name"] == "Gerard Salton"
    assert validated["authors"][0]["author_order"] == 1
    assert len(validated["keywords"]) == 2
    assert len(validated["categories"]) == 1


def test_validate_missing_title_raises_error():
    """Verify empty or whitespace title raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        validate_paper_payload({"title": "   ", "source_name": "arxiv"})
    assert "title" in exc_info.value.details


def test_validate_invalid_year_raises_error():
    """Verify out-of-range publication year raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        validate_paper_payload({"title": "Test Paper", "publication_year": 1750})
    assert "publication_year" in exc_info.value.details

    with pytest.raises(ValidationError) as exc_info:
        validate_paper_payload({"title": "Test Paper", "publication_year": "invalid_year"})
    assert "publication_year" in exc_info.value.details
