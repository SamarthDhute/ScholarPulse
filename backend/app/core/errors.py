"""Application error classes and standardized error response handlers.

Adheres to ScholarPulse SRS v1.0 Section 7 & 9:
Error envelope format:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable description",
        "details": {},
        "request_id": "UUID/string"
    }
}
"""

import uuid
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.app.core.logging import logger


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(self, message: str = "Requested resource was not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND, details=details)


class ValidationError(AppException):
    """Business validation error (422)."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, details=details)


class ConflictError(AppException):
    """Resource conflict (409)."""

    def __init__(self, message: str = "Resource conflict occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="CONFLICT", status_code=status.HTTP_409_CONFLICT, details=details)


class UnauthorizedError(AppException):
    """Authentication required or invalid (401)."""

    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="UNAUTHENTICATED", status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class ForbiddenError(AppException):
    """Permission denied (403)."""

    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="FORBIDDEN", status_code=status.HTTP_403_FORBIDDEN, details=details)


class ServiceUnavailableError(AppException):
    """Dependency or model artifact unavailable (503)."""

    def __init__(self, message: str = "Required service or model artifact is unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="SERVICE_UNAVAILABLE", status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=details)


def format_error_payload(code: str, message: str, details: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Produce standard error envelope."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": request_id or str(uuid.uuid4()),
        }
    }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.warning("AppException [%s] on %s: %s", exc.code, request.url.path, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_payload(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request_id,
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI / Pydantic request validation errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    errors = exc.errors()
    details = {"errors": errors}
    logger.info("Validation error on %s: %d errors", request.url.path, len(errors))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=format_error_payload(
            code="VALIDATION_ERROR",
            message="Request input validation failed.",
            details=details,
            request_id=request_id,
        ),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette / FastAPI HTTPExceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHENTICATED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_payload(
            code=code,
            message=str(exc.detail),
            details={},
            request_id=request_id,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected internal server errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error("Unhandled exception on %s [%s]: %s", request.url.path, request_id, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_payload(
            code="INTERNAL_ERROR",
            message="An unexpected internal server error occurred. Please contact support with the request ID.",
            details={},
            request_id=request_id,
        ),
    )
