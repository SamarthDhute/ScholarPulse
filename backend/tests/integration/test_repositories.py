"""Integration tests for Repository abstractions."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.db.base import Base
from backend.app.models.paper import (
    Paper,
    PaperAuthor,
    PaperKeyword,
    PaperCategory,
)
from backend.app.repositories import (
    PaperRepository,
    AuthorRepository,
    KeywordRepository,
    CategoryRepository,
    IngestionRepository,
)


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


def test_author_repository_deduplication(session: Session):
    """Verify AuthorRepository deduplicates authors by normalized name."""
    repo = AuthorRepository(session)
    a1 = repo.get_or_create(display_name="Andrew Ng", normalized_name="andrew ng")
    a2 = repo.get_or_create(display_name="Andrew Y. Ng", normalized_name="andrew ng")

    assert a1.id == a2.id
    assert repo.count() == 1


def test_keyword_repository_prefix_search(session: Session):
    """Verify KeywordRepository creation and prefix search."""
    repo = KeywordRepository(session)
    repo.get_or_create("Information Retrieval", "information retrieval")
    repo.get_or_create("Information Extraction", "information extraction")
    repo.get_or_create("Machine Learning", "machine learning")

    results = repo.search_prefix("info")
    assert len(results) == 2
    terms = [k.normalized_term for k in results]
    assert "information retrieval" in terms
    assert "information extraction" in terms


def test_category_repository(session: Session):
    """Verify CategoryRepository creation and retrieval."""
    repo = CategoryRepository(session)
    c1 = repo.get_or_create("Artificial Intelligence", "AI research")
    c2 = repo.get_or_create("Artificial Intelligence")

    assert c1.id == c2.id
    assert c1.name == "Artificial Intelligence"
    assert repo.count() == 1


def test_paper_repository_filtering_and_retrieval(session: Session):
    """Verify PaperRepository lookup by DOI, external_id, and filter combinations."""
    paper_repo = PaperRepository(session)
    author_repo = AuthorRepository(session)
    cat_repo = CategoryRepository(session)
    kw_repo = KeywordRepository(session)

    # Create author, category, keywords
    author = author_repo.get_or_create("Geoffrey Hinton", "geoffrey hinton")
    category = cat_repo.get_or_create("Neural Networks")
    kw1 = kw_repo.get_or_create("Deep Learning", "deep learning")
    kw2 = kw_repo.get_or_create("Backpropagation", "backpropagation")

    # Create papers
    p1 = Paper(
        title="Deep Learning Breakthroughs",
        publication_year=2015,
        doi="10.1000/182",
        source_name="arxiv",
        external_id="arxiv:1501.0001",
    )
    p2 = Paper(
        title="Modern Information Retrieval",
        publication_year=2020,
        doi="10.1000/183",
        source_name="crossref",
        external_id="crossref:2020.1",
    )
    session.add_all([p1, p2])
    session.flush()

    # Link p1 to author, category, keywords
    pa = PaperAuthor(paper_id=p1.id, author_id=author.id, author_order=1)
    pc = PaperCategory(paper_id=p1.id, category_id=category.id, label_source="verified")
    pk1 = PaperKeyword(paper_id=p1.id, keyword_id=kw1.id, origin="source")
    pk2 = PaperKeyword(paper_id=p1.id, keyword_id=kw2.id, origin="source")
    session.add_all([pa, pc, pk1, pk2])
    session.commit()

    # 1. Lookup by DOI
    by_doi = paper_repo.get_by_doi("10.1000/182")
    assert by_doi is not None
    assert by_doi.title == "Deep Learning Breakthroughs"

    # 2. Lookup by external ID
    by_ext = paper_repo.get_by_external_id("crossref", "crossref:2020.1")
    assert by_ext is not None
    assert by_ext.title == "Modern Information Retrieval"

    # 3. Lookup with details
    detailed = paper_repo.get_with_details(p1.id)
    assert detailed is not None
    assert len(detailed.authors) == 1
    assert detailed.authors[0].author.display_name == "Geoffrey Hinton"
    assert len(detailed.categories) == 1
    assert len(detailed.keywords) == 2

    # 4. Filter by year range
    items, total = paper_repo.list_with_filters(year_from=2018, year_to=2022)
    assert total == 1
    assert items[0].title == "Modern Information Retrieval"

    # 5. Filter by author
    items, total = paper_repo.list_with_filters(author_name="Hinton")
    assert total == 1
    assert items[0].title == "Deep Learning Breakthroughs"

    # 6. Filter by category
    items, total = paper_repo.list_with_filters(category_name="Neural Networks")
    assert total == 1
    assert items[0].title == "Deep Learning Breakthroughs"

    # 7. Filter by keyword
    items, total = paper_repo.list_with_filters(keyword_term="deep learning")
    assert total == 1
    assert items[0].title == "Deep Learning Breakthroughs"


def test_ingestion_repository_lifecycle(session: Session):
    """Verify IngestionRepository records run lifecycle and outcome statistics."""
    repo = IngestionRepository(session)
    run = repo.start_run("openalex")
    assert run.status == "started"
    assert run.started_at is not None

    finished = repo.finish_run(
        run_id=run.id,
        status="completed",
        records_seen=100,
        records_created=85,
        records_updated=10,
        records_skipped=5,
        error_count=0,
        summary={"duration_seconds": 3.4},
    )
    assert finished is not None
    assert finished.status == "completed"
    assert finished.records_created == 85
    assert finished.summary["duration_seconds"] == 3.4

    recent = repo.list_recent(limit=5)
    assert len(recent) == 1
    assert recent[0].source_name == "openalex"
