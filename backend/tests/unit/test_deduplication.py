"""Unit tests for Deduplicator logic."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.db.base import Base
from backend.app.models.paper import Paper, Author, PaperAuthor
from backend.app.ingestion.deduplication import Deduplicator


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


def test_deduplicate_exact_doi(session: Session):
    """Verify exact DOI match flags record as duplicate."""
    paper = Paper(
        title="Attention Is All You Need",
        doi="10.48550/arxiv.1706.03762",
        source_name="arxiv",
    )
    session.add(paper)
    session.commit()

    deduplicator = Deduplicator(session)
    result = deduplicator.check_duplicate({
        "title": "Attention Is All You Need (Reprint)",
        "doi": "10.48550/arxiv.1706.03762",
        "source_name": "neurips",
    })
    assert result.status == "duplicate"
    assert result.match_reason == "exact_doi"
    assert result.existing_paper.id == paper.id


def test_deduplicate_source_external_id(session: Session):
    """Verify source name and external identifier match flags duplicate."""
    paper = Paper(
        title="BERT Paper",
        source_name="arxiv",
        external_id="arxiv:1810.04805",
    )
    session.add(paper)
    session.commit()

    deduplicator = Deduplicator(session)
    result = deduplicator.check_duplicate({
        "title": "BERT: Pre-training",
        "source_name": "arxiv",
        "external_id": "arxiv:1810.04805",
    })
    assert result.status == "duplicate"
    assert result.match_reason == "source_external_id"


def test_deduplicate_title_and_author_overlap(session: Session):
    """Verify normalized title + overlapping author flags duplicate."""
    paper = Paper(title="Deep Residual Learning for Image Recognition", source_name="ieee")
    author = Author(display_name="Kaiming He", normalized_name="kaiming he")
    session.add_all([paper, author])
    session.flush()

    pa = PaperAuthor(paper_id=paper.id, author_id=author.id, author_order=1)
    session.add(pa)
    session.commit()

    deduplicator = Deduplicator(session)
    result = deduplicator.check_duplicate({
        "title": "Deep Residual Learning for Image Recognition",
        "source_name": "conference",
        "authors": [{"display_name": "Kaiming He", "normalized_name": "kaiming he"}],
    })
    assert result.status == "duplicate"
    assert result.match_reason == "title_and_author"


def test_deduplicate_ambiguous_title_different_authors(session: Session):
    """Verify identical title but completely different authors flags ambiguous without merging."""
    paper = Paper(title="Introduction to Machine Learning", source_name="publisher_a")
    author1 = Author(display_name="Alice Smith", normalized_name="alice smith")
    session.add_all([paper, author1])
    session.flush()
    session.add(PaperAuthor(paper_id=paper.id, author_id=author1.id, author_order=1))
    session.commit()

    deduplicator = Deduplicator(session)
    result = deduplicator.check_duplicate({
        "title": "Introduction to Machine Learning",
        "source_name": "publisher_b",
        "authors": [{"display_name": "Bob Jones", "normalized_name": "bob jones"}],
    })
    assert result.status == "ambiguous"
    assert result.match_reason == "title_match_author_mismatch"


def test_deduplicate_unique_record(session: Session):
    """Verify new unique paper is recognized as unique."""
    deduplicator = Deduplicator(session)
    result = deduplicator.check_duplicate({
        "title": "Completely Novel Research Paper",
        "doi": "10.1000/999999",
        "source_name": "arxiv",
    })
    assert result.status == "unique"
