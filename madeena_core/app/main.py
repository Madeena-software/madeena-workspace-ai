"""Main FastAPI application entrypoint.

This module configures and initializes the FastAPI application with
all middleware, routers, and settings.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.logger import setup_logging
from app.middlewares.timing import TimingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.
    
    Handles startup and shutdown events.
    
    Args:
        app: The FastAPI application instance.
        
    Yields:
        None during application runtime.
    """
    # Startup
    setup_logging()
    logger.info("Starting {} v{}", settings.PROJECT_NAME, settings.VERSION)
    logger.info("Environment: {}", settings.ENV)
    logger.info("Debug mode: {}", settings.DEBUG)
    
    yield
    
    # Shutdown
    logger.info("Shutting down {} v{}", settings.PROJECT_NAME, settings.VERSION)


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Middleware for orchestrating messaging channels and task management",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add middlewares (order matters!)
# 1. Correlation ID middleware (first, so it's available for all other middleware)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Correlation-ID",
    generator=lambda: None,  # Will auto-generate if not provided
    validator=None,
    transformer=lambda x: x,
)

# 2. SlowAPI middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)

# 3. Timing middleware
app.add_middleware(TimingMiddleware)

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API routers
app.include_router(v1_router.router, prefix="/api/v1")

# Root level health check (without /api/v1 prefix)
app.include_router(v1_router.router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
