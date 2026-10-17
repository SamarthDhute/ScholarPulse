"""Integration tests for IngestionService using datasets/raw/sample_papers.json."""

import os
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from backend.app.db.base import Base
from backend.app.models.paper import Paper, Author, Keyword, Category
from backend.app.models.ingestion import IngestionRun
from backend.app.ingestion.service import IngestionService


@pytest.fixture(scope="function")
def session() -> Session:
    """Create isolated SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sess = TestingSession()
    yield sess
    sess.close()
    Base.metadata.drop_all(bind=engine)


def test_ingest_sample_papers_dataset(session: Session):
    """Verify loading sample_papers.json creates papers, authors, categories, and keywords."""
    dataset_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "raw", "sample_papers.json")
    )
    assert os.path.exists(dataset_path), f"Sample dataset not found at {dataset_path}"

    service = IngestionService(session)
    run = service.ingest_from_file(dataset_path, source_name="local_sample")

    # Verify IngestionRun stats
    assert run.status == "completed"
    assert run.records_seen == 25
    assert run.records_created == 25
    assert run.records_skipped == 0
    assert run.error_count == 0

    # Verify entities in DB
    total_papers = session.scalar(select(Paper).with_only_columns(Paper.id).distinct().order_by(None))
    assert total_papers is not None

    papers = session.scalars(select(Paper)).all()
    assert len(papers) == 25

    # Check relationships on first paper (Robertson & Zaragoza)
    bm25_paper = session.scalars(select(Paper).where(Paper.title.contains("BM25"))).first()
    assert bm25_paper is not None
    assert bm25_paper.publication_year == 2009
    assert len(bm25_paper.authors) == 2
    assert len(bm25_paper.keywords) >= 4
    assert len(bm25_paper.categories) >= 1
    assert bm25_paper.categories[0].category.name == "Information Retrieval"
    assert bm25_paper.normalized_text is not None
    assert "bm25" in bm25_paper.normalized_text


def test_ingestion_idempotency(session: Session):
    """Verify that re-running ingestion does not create duplicate records."""
    dataset_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "raw", "sample_papers.json")
    )
    service = IngestionService(session)

    # First run
    run1 = service.ingest_from_file(dataset_path)
    assert run1.records_created == 25

    # Second run (exact same file)
    run2 = service.ingest_from_file(dataset_path)
    assert run2.records_seen == 25
    assert run2.records_created == 0
    assert run2.records_skipped == 25

    # Total papers in DB remains 25
    total_papers = len(session.scalars(select(Paper)).all())
    assert total_papers == 25


def test_ingest_record_enrichment(session: Session):
    """Verify that a duplicate record with new abstract enriches existing paper without duplicate."""
    service = IngestionService(session)

    # Initial paper with no abstract
    initial = {
        "title": "Novel Attention Architecture",
        "doi": "10.1000/enrich.01",
        "source_name": "arxiv",
        "authors": ["Test Researcher"],
    }
    paper1, action1, _ = service.ingest_record(initial)
    assert action1 == "created"
    assert paper1.abstract is None

    # Subsequent record with abstract
    enriched = {
        "title": "Novel Attention Architecture",
        "doi": "10.1000/enrich.01",
        "abstract": "This is the newly available abstract.",
        "source_name": "arxiv",
        "authors": ["Test Researcher"],
    }
    paper2, action2, _ = service.ingest_record(enriched)
    assert action2 == "updated"
    assert paper2.id == paper1.id
    assert paper2.abstract == "This is the newly available abstract."

    # Total count in DB is still 1
    total = len(session.scalars(select(Paper)).all())
    assert total == 1
