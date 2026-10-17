"""Unit tests for centralized configuration and secret handling."""

import os
from backend.app.core.config import Settings, get_settings


def test_settings_default_values():
    """Verify that settings provide safe defaults without requiring external keys."""
    settings = Settings()
    assert settings.APP_NAME == "ScholarPulse"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.OPENALEX_API_KEY is None
    assert settings.CROSSREF_MAILTO is None
    assert isinstance(settings.CORS_ORIGINS, list)


def test_cors_origins_parsing():
    """Verify CORS_ORIGINS validator correctly parses JSON array and comma-separated string."""
    # JSON string
    settings_json = Settings(CORS_ORIGINS='["http://example.com", "http://test.local"]')
    assert settings_json.CORS_ORIGINS == ["http://example.com", "http://test.local"]

    # Comma-separated string
    settings_csv = Settings(CORS_ORIGINS="http://localhost:3000, https://scholarpulse.org")
    assert "http://localhost:3000" in settings_csv.CORS_ORIGINS
    assert "https://scholarpulse.org" in settings_csv.CORS_ORIGINS


def test_get_settings_singleton():
    """Verify get_settings returns consistent cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
