"""Integration tests for SQLAlchemy 2.0 models, relationships, and constraints."""

import uuid
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from backend.app.db.base import Base
from backend.app.models.paper import (
    Paper,
    Author,
    PaperAuthor,
    Keyword,
    PaperKeyword,
    Category,
    PaperCategory,
)
from backend.app.models.user import User, SavedPaper
from backend.app.models.ingestion import IngestionRun
from backend.app.models.evaluation import RelevanceJudgment, EvaluationRun, EvaluationMetric


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Create a fresh in-memory SQLite database session for model verification."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_paper_author_relationship(db_session: Session):
    """Verify paper and author relationship preserves ordering and cascades."""
    paper = Paper(
        title="Attention Is All You Need",
        abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
        publication_year=2017,
        doi="10.48550/arxiv.1706.03762",
        source_name="arxiv",
    )
    author1 = Author(display_name="Ashish Vaswani", normalized_name="ashish vaswani")
    author2 = Author(display_name="Noam Shazeer", normalized_name="noam shazeer")

    db_session.add_all([paper, author1, author2])
    db_session.flush()

    pa1 = PaperAuthor(paper_id=paper.id, author_id=author1.id, author_order=1)
    pa2 = PaperAuthor(paper_id=paper.id, author_id=author2.id, author_order=2)
    db_session.add_all([pa1, pa2])
    db_session.commit()

    # Re-fetch paper and verify authors ordered
    fetched_paper = db_session.get(Paper, paper.id)
    assert fetched_paper is not None
    assert len(fetched_paper.authors) == 2
    assert fetched_paper.authors[0].author.display_name == "Ashish Vaswani"
    assert fetched_paper.authors[0].author_order == 1
    assert fetched_paper.authors[1].author.display_name == "Noam Shazeer"
    assert fetched_paper.authors[1].author_order == 2


def test_paper_keyword_relationship(db_session: Session):
    """Verify paper and keywords relationship with origin tracking."""
    paper = Paper(title="BERT: Pre-training of Deep Bidirectional Transformers", source_name="arxiv")
    kw1 = Keyword(display_term="Transformers", normalized_term="transformers")
    kw2 = Keyword(display_term="NLP", normalized_term="nlp")

    db_session.add_all([paper, kw1, kw2])
    db_session.flush()

    pk1 = PaperKeyword(paper_id=paper.id, keyword_id=kw1.id, origin="source")
    pk2 = PaperKeyword(paper_id=paper.id, keyword_id=kw2.id, origin="extracted")
    db_session.add_all([pk1, pk2])
    db_session.commit()

    fetched = db_session.get(Paper, paper.id)
    assert fetched is not None
    assert len(fetched.keywords) == 2
    origins = {pk.origin for pk in fetched.keywords}
    assert origins == {"source", "extracted"}


def test_paper_category_relationship(db_session: Session):
    """Verify paper categories with label_source and confidence score."""
    paper = Paper(title="Deep Residual Learning for Image Recognition", source_name="arxiv")
    cat = Category(name="Computer Vision", description="Visual perception and image understanding")

    db_session.add_all([paper, cat])
    db_session.flush()

    pc = PaperCategory(
        paper_id=paper.id,
        category_id=cat.id,
        label_source="predicted",
        confidence=0.94,
        model_version="classifier-v1",
    )
    db_session.add(pc)
    db_session.commit()

    fetched = db_session.get(Paper, paper.id)
    assert fetched is not None
    assert len(fetched.categories) == 1
    assert fetched.categories[0].label_source == "predicted"
    assert fetched.categories[0].confidence == pytest.approx(0.94)
    assert fetched.categories[0].category.name == "Computer Vision"


def test_user_saved_paper(db_session: Session):
    """Verify user can save papers and access them via relationship."""
    user = User(email="researcher@example.com", password_hash="dummy_hash", role="user")
    paper = Paper(title="A Survey of Information Retrieval", source_name="crossref")
    db_session.add_all([user, paper])
    db_session.flush()

    saved = SavedPaper(user_id=user.id, paper_id=paper.id)
    db_session.add(saved)
    db_session.commit()

    fetched_user = db_session.get(User, user.id)
    assert fetched_user is not None
    assert len(fetched_user.saved_papers) == 1
    assert fetched_user.saved_papers[0].paper.title == "A Survey of Information Retrieval"


def test_ingestion_and_evaluation_entities(db_session: Session):
    """Verify IngestionRun, EvaluationRun, and EvaluationMetric entities."""
    # Ingestion run
    run = IngestionRun(source_name="arxiv", status="completed", records_created=42)
    db_session.add(run)

    # Evaluation run with metrics
    eval_run = EvaluationRun(
        evaluation_type="search",
        dataset_version="v1",
        model_or_ranker="bm25",
        status="completed",
    )
    db_session.add(eval_run)
    db_session.flush()

    m1 = EvaluationMetric(evaluation_run_id=eval_run.id, metric_name="MAP", metric_value=0.785)
    m2 = EvaluationMetric(evaluation_run_id=eval_run.id, metric_name="NDCG@10", cutoff_k=10, metric_value=0.812)
    db_session.add_all([m1, m2])
    db_session.commit()

    fetched_eval = db_session.get(EvaluationRun, eval_run.id)
    assert fetched_eval is not None
    assert len(fetched_eval.metrics) == 2
    metrics_map = {m.metric_name: m.metric_value for m in fetched_eval.metrics}
    assert metrics_map["MAP"] == pytest.approx(0.785)
    assert metrics_map["NDCG@10"] == pytest.approx(0.812)
