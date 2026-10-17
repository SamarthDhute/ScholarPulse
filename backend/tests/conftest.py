"""Pytest configuration and shared fixtures for ScholarPulse."""

import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import Settings, get_settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide isolated test settings without external dependencies."""
    return Settings(
        APP_ENV="test",
        APP_NAME="ScholarPulse Test",
        API_V1_PREFIX="/api/v1",
        DATABASE_URL="sqlite:///./test.db",
        TEST_DATABASE_URL="sqlite:///./test.db",
        CORS_ORIGINS=["http://localhost:3000"],
        LOG_LEVEL="DEBUG",
        SECRET_KEY="test-secret-key-for-unit-testing-only",
        ACCESS_TOKEN_EXPIRE_MINUTES=60,
    )


@pytest.fixture(scope="function")
def client(test_settings: Settings) -> Generator[TestClient, None, None]:
    """Provide FastAPI TestClient with test settings override."""
    app.dependency_overrides[get_settings] = lambda: test_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
