"""Unit tests for custom exception classes and error formatting."""

from backend.app.core.errors import (
    AppException,
    NotFoundError,
    ValidationError,
    ConflictError,
    format_error_payload,
)


def test_custom_exceptions():
    """Verify AppException subclasses have appropriate status codes and error codes."""
    exc_not_found = NotFoundError("Paper not found")
    assert exc_not_found.status_code == 404
    assert exc_not_found.code == "NOT_FOUND"
    assert exc_not_found.message == "Paper not found"

    exc_val = ValidationError("Invalid year range", details={"field": "year_from"})
    assert exc_val.status_code == 422
    assert exc_val.code == "VALIDATION_ERROR"
    assert exc_val.details["field"] == "year_from"

    exc_conflict = ConflictError("Paper with DOI already exists")
    assert exc_conflict.status_code == 409
    assert exc_conflict.code == "CONFLICT"


def test_format_error_payload():
    """Verify error envelope conforms to ScholarPulse SRS Section 7."""
    payload = format_error_payload(
        code="NOT_FOUND",
        message="Item not found",
        details={"id": "123"},
        request_id="req-test-999",
    )
    assert "error" in payload
    assert payload["error"]["code"] == "NOT_FOUND"
    assert payload["error"]["message"] == "Item not found"
    assert payload["error"]["details"] == {"id": "123"}
    assert payload["error"]["request_id"] == "req-test-999"
