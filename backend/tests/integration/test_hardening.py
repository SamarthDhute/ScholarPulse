"""Integration tests for Phase B7 Hardening.

Validates:
- Security: zero credential or secret leakage in responses, logs, or error payloads
- Strict input validation and boundary enforcement (caps on query lengths, page sizes, year bounds)
- Graceful handling of empty results, unknown queries, and no-match filters without 500 crashes
- Ingestion idempotency and duplicate record protection
- Resilient operation without optional external API credentials
"""

import os
import uuid
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.ingestion.service import IngestionService
from backend.app.core.config import get_settings


@pytest.fixture(scope="module")
def hardening_engine():
    """Create isolated in-memory database with sample papers."""
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
        ingestion.ingest_from_json_file(sample_dataset, source_name="hardening_fixture")
    db.close()

    yield engine, SessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="module")
def client(hardening_engine) -> Generator[TestClient, None, None]:
    """Provide TestClient with database session override."""
    _, SessionLocal = hardening_engine

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# =====================================================================
# 1. Security & Secret Leakage Audits
# =====================================================================

def test_health_check_leaks_no_secrets(client: TestClient):
    """Ensure health endpoint does not leak database credentials or secret keys."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body_text = response.text
    settings = get_settings()

    if settings.SECRET_KEY:
        assert settings.SECRET_KEY not in body_text
    if settings.DATABASE_URL:
        assert settings.DATABASE_URL not in body_text
    assert "password" not in body_text.lower()


def test_error_envelope_sanitizes_internal_details(client: TestClient):
    """Ensure 404, 400, and 422 error envelopes never expose tracebacks or secrets."""
    # 404 Not Found
    res_404 = client.get(f"/api/v1/papers/{uuid.uuid4()}")
    assert res_404.status_code == 404
    err_404 = res_404.json()
    assert "error" in err_404
    assert "traceback" not in err_404["error"]
    assert "stacktrace" not in err_404["error"]

    # 422 Validation Error
    res_422 = client.get("/api/v1/search?query=")
    assert res_422.status_code == 422
    err_422 = res_422.json()
    assert "error" in err_422
    assert "traceback" not in err_422["error"]


# =====================================================================
# 2. Strict Input Validation & Boundary Caps
# =====================================================================

def test_search_query_length_boundary(client: TestClient):
    """Ensure query strings exceeding maximum allowed length (500 chars) are rejected."""
    long_query = "a" * 501
    response = client.get(f"/api/v1/search?query={long_query}")
    assert response.status_code == 422
    assert "error" in response.json()


def test_search_invalid_page_bounds(client: TestClient):
    """Ensure page < 1 and page_size > 100 are rejected."""
    # page = 0
    res_zero = client.get("/api/v1/search?query=test&page=0")
    assert res_zero.status_code == 422

    # page_size > 100
    res_huge = client.get("/api/v1/search?query=test&page_size=101")
    assert res_huge.status_code == 422


def test_search_invalid_ranking_method(client: TestClient):
    """Ensure unsupported ranking algorithms return validation error."""
    response = client.get("/api/v1/search?query=test&method=quantum_super_rank")
    assert response.status_code == 422


def test_papers_invalid_year_boundaries(client: TestClient):
    """Ensure unreasonable years (< 1900 or > 2100) are rejected."""
    res_past = client.get("/api/v1/papers?year_from=1850")
    assert res_past.status_code == 422

    res_future = client.get("/api/v1/papers?year_to=2200")
    assert res_future.status_code == 422


def test_clustering_cluster_count_boundary(client: TestClient):
    """Ensure n_clusters parameter enforces min=2 and max=10 bounds."""
    res_too_small = client.get("/api/v1/analysis/clusters?n_clusters=1")
    assert res_too_small.status_code == 422

    res_too_large = client.get("/api/v1/analysis/clusters?n_clusters=15")
    assert res_too_large.status_code == 422


def test_association_rules_threshold_bounds(client: TestClient):
    """Ensure min_support and min_confidence validate boundary intervals (0.0 < x <= 1.0)."""
    res_support = client.get("/api/v1/analysis/association-rules?min_support=1.5")
    assert res_support.status_code == 422

    res_conf = client.get("/api/v1/analysis/association-rules?min_confidence=-0.1")
    assert res_conf.status_code == 422


# =====================================================================
# 3. Empty Results & Edge Cases
# =====================================================================

def test_search_zero_hits_returns_clean_envelope(client: TestClient):
    """Ensure queries matching no documents return clean 200 with empty results."""
    gibberish = "xyzzy9988qwerpoiuasdflkjh"
    response = client.get(f"/api/v1/search?query={gibberish}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_hits"] == 0
    assert data["results"] == []


def test_search_nonexistent_category_filter(client: TestClient):
    """Ensure filtering by an impossible category returns 0 results gracefully."""
    response = client.get("/api/v1/search?query=learning&category=NonExistentSubject99")
    assert response.status_code == 200
    data = response.json()
    assert data["total_hits"] == 0
    assert data["results"] == []


def test_classify_whitespace_text_error(client: TestClient):
    """Ensure classifying all-whitespace text triggers validation error."""
    response = client.post("/api/v1/analysis/classify", json={"text": "     \n\t  "})
    assert response.status_code in (400, 422)


def test_keywords_empty_prefix(client: TestClient):
    """Ensure searching keywords with empty or no prefix returns top vocabulary."""
    response = client.get("/api/v1/keywords?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


# =====================================================================
# 4. Ingestion Idempotency & Deduplication
# =====================================================================

def test_ingestion_idempotency(client: TestClient):
    """Ensure re-ingesting the exact same dataset causes no duplicate papers."""
    # First re-ingest run
    res1 = client.post("/api/v1/admin/ingest", json={"source_name": "idempotency_run_1"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] in ("completed", "partial_success")
    # All existing records should be updated or skipped, not newly created as duplicates
    assert data1["created_count"] == 0
    assert data1["skipped_count"] + data1["updated_count"] > 0
