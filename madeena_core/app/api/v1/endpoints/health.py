"""Health check endpoint.

This module provides health check functionality for monitoring
and load balancer integration.
"""

from typing import Any

from fastapi import APIRouter
from loguru import logger

from app.core.config import settings
from app.core.constants import HEALTH_STATUS_OK

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint.
    
    Returns the current health status of the application.
    Used by load balancers and monitoring systems.
    
    Returns:
        Health status information.
    """
    logger.debug("Health check requested")
    
    return {
        "status": HEALTH_STATUS_OK,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@router.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint.
    
    Returns basic API information.
    
    Returns:
        API welcome message.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
    }
