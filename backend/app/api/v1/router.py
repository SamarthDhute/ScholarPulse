"""API Version 1 main router.

Aggregates all version 1 endpoint controllers.
"""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
