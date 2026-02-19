"""API v1 router configuration.

This module configures the API v1 router with all endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, webhooks

router = APIRouter()

# Include endpoint routers
router.include_router(health.router)
router.include_router(webhooks.router)
