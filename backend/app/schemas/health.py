"""Pydantic schemas for health and readiness checks."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(default="ok", description="Service health status indicator")
    service: str = Field(default="scholarpulse-api", description="Service name")
    version: str = Field(default="1.0.0", description="API semantic version")
