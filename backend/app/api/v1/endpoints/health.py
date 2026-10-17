"""Health check endpoint.

Contract defined in ScholarPulse SRS v1.0 Section 8.1:
Method/Path: GET /api/v1/health
Public, minimal response without leaking internal configuration or credentials.
"""

from fastapi import APIRouter
from backend.app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns service health status without leaking internal secrets or environment details.",
)
def get_health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(
        status="ok",
        service="scholarpulse-api",
        version="1.0.0",
    )
