"""Integration test verifying Alembic migration upgrades and downgrades from scratch."""

import os
import tempfile
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_and_downgrade():
    """Verify that Alembic migrations run cleanly up to head and down to base."""
    # Use temporary SQLite file database to test full file-based migration cycle
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = None
    try:
        db_url = f"sqlite:///{db_path}"
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        ini_path = os.path.join(backend_dir, "alembic.ini")

        alembic_cfg = Config(ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "migrations"))
        alembic_cfg.set_main_option("version_locations", os.path.join(backend_dir, "migrations", "versions"))

        # Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        # Inspect tables in migrated database
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())

        expected_tables = {
            "users",
            "papers",
            "authors",
            "paper_authors",
            "keywords",
            "paper_keywords",
            "categories",
            "paper_categories",
            "saved_papers",
            "ingestion_runs",
            "relevance_judgments",
            "evaluation_runs",
            "evaluation_metrics",
            "alembic_version",
        }
        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

        # Run downgrade to base
        command.downgrade(alembic_cfg, "base")
        inspector_post_downgrade = inspect(engine)
        remaining_tables = set(inspector_post_downgrade.get_table_names())
        assert "papers" not in remaining_tables
        assert "users" not in remaining_tables
        assert "authors" not in remaining_tables

    finally:
        if engine is not None:
            engine.dispose()
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass
