"""SQLAlchemy database engine and session factory.

Configured with pool pre-ping to detect stale connections and dependency injection support.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import get_settings
from backend.app.core.logging import logger

settings = get_settings()

# Configure engine arguments
engine_kwargs = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

try:
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.warning("Failed to initialize database engine for %s: %s", settings.DATABASE_URL.split("@")[-1], str(e))
    # Fallback placeholder engine for testing/local setups where DB is initialized later
    engine = None
    SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and safely closes it."""
    if SessionLocal is None:
        raise RuntimeError("Database engine is not configured or reachable.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
