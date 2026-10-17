"""Unit tests for content-based related-paper recommendation engine.

Tests:
- Pairwise cosine similarity ranking over TF-IDF vectors
- Exclusion of seed paper itself from recommendations (FR-019)
- Explainable shared keywords extraction
- Top-N truncation and min_similarity cutoff
- KeyError handling for unknown paper IDs
"""

import pytest
from backend.app.recommendations.content_based import ContentBasedRecommender


@pytest.fixture
def recommender_corpus():
    """Curated corpus for recommendation testing."""
    return [
        {
            "id": "p1",
            "title": "The Okapi BM25 Retrieval Engine",
            "abstract": "Information retrieval probabilistic ranking model term frequency document length.",
            "category": "Information Retrieval",
            "keywords": ["bm25", "ranking", "retrieval", "probabilistic"],
        },
        {
            "id": "p2",
            "title": "Probabilistic Ranking Models in Modern Search Engines",
            "abstract": "Probabilistic retrieval framework term frequency normalization and BM25 ranking.",
            "category": "Information Retrieval",
            "keywords": ["bm25", "ranking", "probabilistic", "search"],
        },
        {
            "id": "p3",
            "title": "A Vector Space Model for Automatic Indexing",
            "abstract": "TF-IDF vector space model cosine similarity document ranking.",
            "category": "Information Retrieval",
            "keywords": ["vector space", "tf-idf", "ranking", "retrieval"],
        },
        {
            "id": "p4",
            "title": "Deep Neural Networks for Computer Vision",
            "abstract": "Convolutional neural network architectures for visual recognition and backpropagation.",
            "category": "Machine Learning",
            "keywords": ["deep learning", "neural networks", "computer vision"],
        },
        {
            "id": "p5",
            "title": "Generative Adversarial Nets",
            "abstract": "Machine learning generative models deep neural networks discriminator generator.",
            "category": "Machine Learning",
            "keywords": ["deep learning", "neural networks", "generative"],
        },
    ]


def test_content_based_recommendations_ranking(recommender_corpus):
    """Test related papers ranking orders most similar content first."""
    recommender = ContentBasedRecommender()
    recommender.fit(recommender_corpus)

    recs = recommender.recommend(paper_id="p1", top_n=3)
    assert len(recs) <= 3
    # p2 should be the most similar to p1 (both are BM25 probabilistic models)
    assert recs[0].paper_id == "p2"
    assert recs[0].similarity_score > 0.3
    # Assert sorted descending
    for i in range(len(recs) - 1):
        assert recs[i].similarity_score >= recs[i + 1].similarity_score


def test_exclude_query_paper_from_recommendations(recommender_corpus):
    """Test strict exclusion of seed paper itself per ScholarPulse FR-019."""
    recommender = ContentBasedRecommender()
    recommender.fit(recommender_corpus)

    for doc in recommender_corpus:
        doc_id = doc["id"]
        recs = recommender.recommend(paper_id=doc_id, top_n=5)
        # Ensure query paper ID is NEVER present in recommendations
        rec_ids = [r.paper_id for r in recs]
        assert doc_id not in rec_ids


def test_explainable_shared_keywords(recommender_corpus):
    """Test algorithmic transparency: extracting shared keywords between papers."""
    recommender = ContentBasedRecommender()
    recommender.fit(recommender_corpus)

    recs = recommender.recommend(paper_id="p1", top_n=2)
    top_rec = recs[0]
    assert top_rec.paper_id == "p2"
    assert len(top_rec.shared_keywords) > 0
    assert "bm25" in top_rec.shared_keywords
    assert "ranking" in top_rec.shared_keywords


def test_recommendation_top_n_and_threshold(recommender_corpus):
    """Test top_n limit and min_similarity cutoff."""
    recommender = ContentBasedRecommender()
    recommender.fit(recommender_corpus)

    recs_top1 = recommender.recommend(paper_id="p4", top_n=1)
    assert len(recs_top1) == 1
    assert recs_top1[0].paper_id == "p5"

    # High threshold filters out unrelated papers
    recs_high_thresh = recommender.recommend(paper_id="p1", top_n=5, min_similarity=0.99)
    assert len(recs_high_thresh) == 0


def test_unknown_paper_raises_error(recommender_corpus):
    """Test KeyError is raised for non-existent paper ID."""
    recommender = ContentBasedRecommender()
    recommender.fit(recommender_corpus)

    with pytest.raises(KeyError, match="not found"):
        recommender.recommend(paper_id="non_existent_uuid")
