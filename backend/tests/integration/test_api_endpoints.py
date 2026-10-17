"""Integration tests for ScholarPulse Phase B6 Product API endpoints.

Tests all 21 endpoints mounted on /api/v1:
- Search endpoints (BM25, TF-IDF, Language Model, Boolean, filtering, pagination)
- Papers endpoints (listing, details, content-based related recommendations)
- Taxonomy endpoints (categories with paper counts, keywords prefix autocomplete)
- Analysis endpoints (text classification, clustering, member papers, association rules)
- Research Analytics endpoints (overview, trends, category/keyword share, collaboration network)
- Information Retrieval evaluation benchmarking endpoint
- Administration & Ingestion endpoints
- User Saved Library endpoints (save, list, delete, duplicate prevention)
"""

import os
import uuid
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.main import app
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.ingestion.service import IngestionService
from backend.app.models.paper import Paper


from sqlalchemy.pool import StaticPool

@pytest.fixture(scope="module")
def seeded_db_engine():
    """Provide a thread-safe in-memory SQLite database pre-populated with sample papers."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    sample_dataset = os.path.join("datasets", "raw", "sample_papers.json")
    if os.path.exists(sample_dataset):
        ingestion = IngestionService(db)
        ingestion.ingest_from_json_file(sample_dataset, source_name="test_fixture")
    db.close()

    yield engine, SessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="module")
def api_client(seeded_db_engine) -> Generator[TestClient, None, None]:
    """Provide TestClient with seeded database session override."""
    _, SessionLocal = seeded_db_engine

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seeded_db_session(seeded_db_engine) -> Generator[Session, None, None]:
    """Provide a per-test session from the seeded database."""
    _, SessionLocal = seeded_db_engine
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================================
# 1. Search Endpoints (/api/v1/search)
# =====================================================================

def test_search_bm25_default(api_client: TestClient):
    """Verify default BM25 search returns valid ranked papers with snippets."""
    response = api_client.get("/api/v1/search?query=transformer+attention")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "transformer attention"
    assert data["method"] == "bm25"
    assert data["total_hits"] > 0
    assert len(data["results"]) > 0

    first = data["results"][0]
    assert "doc_id" in first
    assert "score" in first
    assert "term_scores" in first
    assert "metadata" in first
    assert first["rank"] == 1


def test_search_all_algorithms(api_client: TestClient):
    """Verify all four supported IR algorithms execute through the API."""
    for method in ["bm25", "tfidf", "language_model", "boolean"]:
        response = api_client.get(f"/api/v1/search?query=retrieval&method={method}")
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == method
        assert data["page"] == 1


def test_search_metadata_filtering(api_client: TestClient):
    """Verify year and category filtering on search."""
    response = api_client.get("/api/v1/search?query=learning&year_min=2020&year_max=2024")
    assert response.status_code == 200
    data = response.json()
    for item in data["results"]:
        year = item["metadata"].get("publication_year")
        if year is not None:
            assert 2020 <= year <= 2024


def test_search_invalid_year_range(api_client: TestClient):
    """Verify year_min > year_max returns error response."""
    response = api_client.get("/api/v1/search?query=test&year_min=2025&year_max=2020")
    assert response.status_code in (400, 422)
    assert "error" in response.json()


# =====================================================================
# 2. Papers Endpoints (/api/v1/papers)
# =====================================================================

def test_list_papers_pagination(api_client: TestClient):
    """Verify paginated listing of papers."""
    response = api_client.get("/api/v1/papers?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) <= 5
    assert data["page"] == 1
    assert data["page_size"] == 5

    item = data["items"][0]
    assert "title" in item
    assert "authors" in item
    assert "categories" in item


def test_get_paper_details(api_client: TestClient, seeded_db_session: Session):
    """Verify full paper details retrieval by UUID."""
    paper = seeded_db_session.query(Paper).first()
    assert paper is not None

    response = api_client.get(f"/api/v1/papers/{paper.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(paper.id)
    assert data["title"] == paper.title
    assert len(data["authors"]) > 0


def test_get_paper_details_not_found(api_client: TestClient):
    """Verify non-existent paper UUID returns 404."""
    random_id = uuid.uuid4()
    response = api_client.get(f"/api/v1/papers/{random_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_related_papers(api_client: TestClient, seeded_db_session: Session):
    """Verify content-based recommendations exclude the query paper."""
    paper = seeded_db_session.query(Paper).first()
    assert paper is not None

    response = api_client.get(f"/api/v1/papers/{paper.id}/related?top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Target paper itself must not be in recommendations
    rec_ids = [r["paper_id"] for r in data]
    assert str(paper.id) not in rec_ids
    if paper.doi:
        assert paper.doi not in rec_ids


# =====================================================================
# 3. Taxonomy Endpoints (/api/v1/categories, /api/v1/keywords)
# =====================================================================

def test_list_categories(api_client: TestClient):
    """Verify category taxonomy list returns categories with paper counts."""
    response = api_client.get("/api/v1/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    assert "name" in categories[0]
    assert "paper_count" in categories[0]


def test_search_keywords_with_prefix(api_client: TestClient):
    """Verify keyword prefix search for auto-completion."""
    response = api_client.get("/api/v1/keywords?prefix=learn&limit=5")
    assert response.status_code == 200
    keywords = response.json()
    assert isinstance(keywords, list)
    for kw in keywords:
        assert "learn" in kw["normalized_term"]


# =====================================================================
# 4. Data Science Analysis Endpoints (/api/v1/analysis/*)
# =====================================================================

def test_classify_text(api_client: TestClient):
    """Verify text classification inference returns scored categories."""
    payload = {
        "text": "Deep residual neural networks with convolutional layers for image recognition.",
        "top_k": 3,
    }
    response = api_client.post("/api/v1/analysis/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["predicted_categories"]) > 0
    assert "model_version" in data
    top_pred = data["predicted_categories"][0]
    assert "name" in top_pred
    assert 0.0 <= top_pred["score"] <= 1.0


def test_classify_validation_error(api_client: TestClient):
    """Verify error when neither text nor paper_id is passed."""
    response = api_client.post("/api/v1/analysis/classify", json={})
    assert response.status_code in (400, 422)


def test_get_clusters_kmeans(api_client: TestClient):
    """Verify document clustering returns clusters with labels and silhouette score."""
    response = api_client.get("/api/v1/analysis/clusters?method=kmeans&n_clusters=3")
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "kmeans"
    assert data["n_clusters"] == 3
    assert len(data["clusters"]) == 3
    assert "silhouette_score" in data
    first_cluster = data["clusters"][0]
    assert "label" in first_cluster
    assert "top_terms" in first_cluster
    assert len(first_cluster["paper_ids"]) > 0


def test_get_cluster_papers(api_client: TestClient):
    """Verify retrieving member papers for a specific cluster."""
    clusters_res = api_client.get("/api/v1/analysis/clusters?method=kmeans&n_clusters=3")
    cluster_id = clusters_res.json()["clusters"][0]["cluster_id"]

    response = api_client.get(f"/api/v1/analysis/clusters/{cluster_id}/papers")
    assert response.status_code == 200
    data = response.json()
    assert data["cluster_id"] == cluster_id
    assert len(data["papers"]) > 0


def test_get_association_rules(api_client: TestClient):
    """Verify Apriori association rules endpoint."""
    response = api_client.get("/api/v1/analysis/association-rules?min_support=0.04&min_confidence=0.2")
    assert response.status_code == 200
    data = response.json()
    assert "total_rules" in data
    assert "rules" in data
    assert data["min_support"] == 0.04


# =====================================================================
# 5. Research Analytics Endpoints (/api/v1/analytics/*)
# =====================================================================

def test_analytics_overview(api_client: TestClient):
    """Verify collection overview analytics."""
    response = api_client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_papers"] > 0
    assert data["total_authors"] > 0
    assert data["total_categories"] > 0


def test_analytics_trends(api_client: TestClient):
    """Verify publication volume chronological trends."""
    response = api_client.get("/api/v1/analytics/trends")
    assert response.status_code == 200
    trends = response.json()
    assert isinstance(trends, list)
    assert len(trends) > 0
    assert "year" in trends[0]
    assert "count" in trends[0]


def test_analytics_categories(api_client: TestClient):
    """Verify category market share distribution."""
    response = api_client.get("/api/v1/analytics/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    assert "percentage_share" in categories[0]


def test_analytics_keywords(api_client: TestClient):
    """Verify keyword frequency distribution."""
    response = api_client.get("/api/v1/analytics/keywords?top_n=10")
    assert response.status_code == 200
    keywords = response.json()
    assert len(keywords) <= 10
    assert "count" in keywords[0]


def test_analytics_collaboration_network(api_client: TestClient):
    """Verify co-authorship collaboration network graph."""
    response = api_client.get("/api/v1/analytics/collaboration-network?min_collaborations=1")
    assert response.status_code == 200
    net = response.json()
    assert "total_nodes" in net
    assert "total_edges" in net
    assert "nodes" in net
    assert "edges" in net


# =====================================================================
# 6. Evaluation Endpoint (/api/v1/evaluation/retrieval)
# =====================================================================

def test_retrieval_evaluation_benchmark(api_client: TestClient):
    """Verify Information Retrieval multi-ranker benchmarking report."""
    response = api_client.get("/api/v1/evaluation/retrieval")
    assert response.status_code == 200
    data = response.json()
    assert data["query_count"] > 0
    assert len(data["reports"]) == 3  # bm25, tfidf, language_model

    rankers = [r["ranker_name"] for r in data["reports"]]
    assert "bm25" in rankers
    assert "tfidf" in rankers
    assert "language_model" in rankers

    bm25_report = next(r for r in data["reports"] if r["ranker_name"] == "bm25")
    assert "mean_average_precision" in bm25_report
    assert "mean_reciprocal_rank" in bm25_report
    assert "precision_at_k" in bm25_report


# =====================================================================
# 7. Administration Endpoints (/api/v1/admin/*)
# =====================================================================

def test_admin_ingest_and_status(api_client: TestClient):
    """Verify triggering ingestion and checking status history."""
    response = api_client.post("/api/v1/admin/ingest", json={"source_name": "test_batch"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("completed", "partial_success")
    assert data["total_processed"] > 0

    status_res = api_client.get("/api/v1/admin/ingest/status?limit=5")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["total_runs"] > 0


# =====================================================================
# 8. User Saved Library Endpoints (/api/v1/library/papers)
# =====================================================================

def test_saved_library_lifecycle(api_client: TestClient, seeded_db_session: Session):
    """Verify full CRUD cycle of saved papers with per-user isolation."""
    paper = seeded_db_session.query(Paper).first()
    assert paper is not None

    user_header = {"X-User-ID": str(uuid.uuid4())}

    # 1. Initial library is empty
    list_res = api_client.get("/api/v1/library/papers", headers=user_header)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 0

    # 2. Save paper
    save_res = api_client.post(
        "/api/v1/library/papers",
        json={"paper_id": str(paper.id), "notes": "Must read for literature review."},
        headers=user_header,
    )
    assert save_res.status_code == 201
    assert save_res.json()["paper_id"] == str(paper.id)

    # 3. Duplicate save returns 409 Conflict
    dup_res = api_client.post(
        "/api/v1/library/papers",
        json={"paper_id": str(paper.id)},
        headers=user_header,
    )
    assert dup_res.status_code == 409

    # 4. List now has 1 paper
    list_res2 = api_client.get("/api/v1/library/papers", headers=user_header)
    assert list_res2.status_code == 200
    assert list_res2.json()["total"] == 1
    assert list_res2.json()["items"][0]["title"] == paper.title

    # 5. Delete saved paper
    del_res = api_client.delete(f"/api/v1/library/papers/{paper.id}", headers=user_header)
    assert del_res.status_code == 200

    # 6. Delete again returns 404
    del_res2 = api_client.delete(f"/api/v1/library/papers/{paper.id}", headers=user_header)
    assert del_res2.status_code == 404
