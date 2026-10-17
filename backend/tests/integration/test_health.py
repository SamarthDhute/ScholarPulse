"""Integration tests for health endpoint, middleware, and error handling."""

from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    """Verify GET /api/v1/health returns 200 OK and expected schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "scholarpulse-api"
    assert data["version"] == "1.0.0"
    assert "X-Request-ID" in response.headers


def test_root_endpoint(client: TestClient):
    """Verify GET / returns basic service info and links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "docs" in data
    assert data["health"] == "/api/v1/health"


def test_not_found_error_envelope(client: TestClient):
    """Verify unknown route returns standardized error envelope."""
    response = client.get("/api/v1/non-existent-endpoint-xyz")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
