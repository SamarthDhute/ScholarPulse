"""Unit tests for bibliometric and research analytics service.

Tests:
- Publication trends by year and growth calculations
- Category distributions and percentage share
- Keyword frequency distributions
- Top productive authors ranking
- Co-authorship collaboration network graph
- Year range boundary filtering
"""

import pytest
from backend.app.data_science.analytics import ResearchAnalyticsService


@pytest.fixture
def sample_papers_for_analytics():
    """Curated paper collection for analytics testing."""
    return [
        {
            "id": "p1",
            "title": "BM25 Ranking",
            "publication_year": 2018,
            "authors": ["Stephen Robertson", "Hugo Zaragoza"],
            "categories": ["Information Retrieval"],
            "keywords": ["bm25", "ranking", "retrieval"],
        },
        {
            "id": "p2",
            "title": "Vector Space Retrieval",
            "publication_year": 2018,
            "authors": ["Gerard Salton", "Anita Wong"],
            "categories": ["Information Retrieval"],
            "keywords": ["vector space", "tf-idf", "retrieval"],
        },
        {
            "id": "p3",
            "title": "Attention Is All You Need",
            "publication_year": 2019,
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            "categories": ["Machine Learning", "NLP"],
            "keywords": ["transformers", "attention", "deep learning"],
        },
        {
            "id": "p4",
            "title": "BERT Pretraining",
            "publication_year": 2020,
            "authors": ["Jacob Devlin", "Ming-Wei Chang"],
            "categories": ["NLP"],
            "keywords": ["bert", "transformers", "language models"],
        },
        {
            "id": "p5",
            "title": "Spanner Globally-Distributed Database",
            "publication_year": 2020,
            "authors": ["James Corbett", "Jeffrey Dean"],
            "categories": ["Databases"],
            "keywords": ["spanner", "transactions", "distributed systems"],
        },
    ]


def test_overview_summary(sample_papers_for_analytics):
    """Test high-level collection overview counts and metrics."""
    analytics = ResearchAnalyticsService()
    summary = analytics.get_overview_summary(sample_papers_for_analytics)

    assert summary["total_papers"] == 5
    assert summary["total_authors"] == 11
    assert summary["total_categories"] >= 3
    assert summary["year_min"] == 2018
    assert summary["year_max"] == 2020
    assert summary["avg_authors_per_paper"] > 1.0


def test_publication_trends(sample_papers_for_analytics):
    """Test chronological publication volume and year-over-year growth."""
    analytics = ResearchAnalyticsService()
    trends = analytics.get_publication_trends(sample_papers_for_analytics)

    assert len(trends) == 3
    assert trends[0]["year"] == 2018
    assert trends[0]["count"] == 2
    assert trends[1]["year"] == 2019
    assert trends[1]["count"] == 1
    assert trends[1]["growth_percentage"] == -50.0
    assert trends[2]["year"] == 2020
    assert trends[2]["count"] == 2
    assert trends[2]["cumulative_count"] == 5


def test_category_distribution(sample_papers_for_analytics):
    """Test category counts and percentage shares summing to 100%."""
    analytics = ResearchAnalyticsService()
    dist = analytics.get_category_distribution(sample_papers_for_analytics)

    assert len(dist) > 0
    total_pct = sum(c["percentage_share"] for c in dist)
    assert 99.0 <= total_pct <= 101.0  # Floating point rounding allowance


def test_keyword_distribution(sample_papers_for_analytics):
    """Test keyword ranking and frequency extraction."""
    analytics = ResearchAnalyticsService()
    kws = analytics.get_keyword_distribution(sample_papers_for_analytics, top_n=5)

    assert len(kws) <= 5
    assert kws[0]["count"] >= kws[-1]["count"]
    # Check that "retrieval" and "transformers" are detected
    terms = [k["keyword"] for k in kws]
    assert any("retrieval" in t or "transformers" in t for t in terms)


def test_top_authors(sample_papers_for_analytics):
    """Test author productivity ranking."""
    analytics = ResearchAnalyticsService()
    authors = analytics.get_top_authors(sample_papers_for_analytics, top_n=5)

    assert len(authors) <= 5
    for a in authors:
        assert a["paper_count"] >= 1


def test_coauthorship_network(sample_papers_for_analytics):
    """Test co-authorship collaboration network graph construction."""
    analytics = ResearchAnalyticsService()
    network = analytics.get_coauthorship_network(sample_papers_for_analytics)

    assert "nodes" in network
    assert "edges" in network
    assert "top_collaborators" in network
    assert network["total_nodes"] == 11
    assert network["total_edges"] > 0

    # Vaswani, Shazeer, and Parmar co-authored paper p3
    vaswani_edges = [
        e for e in network["edges"]
        if e["source"] == "Ashish Vaswani" or e["target"] == "Ashish Vaswani"
    ]
    assert len(vaswani_edges) == 2


def test_analytics_year_filtering(sample_papers_for_analytics):
    """Test year_min and year_max filtering on trends and overview."""
    analytics = ResearchAnalyticsService()
    filtered_trends = analytics.get_publication_trends(
        sample_papers_for_analytics, year_min=2019, year_max=2020
    )

    years = [t["year"] for t in filtered_trends]
    assert 2018 not in years
    assert 2019 in years
    assert 2020 in years
