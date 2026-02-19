"""Timing middleware for request processing time logging.

This middleware tracks and logs the processing time for each request.
"""

import time
from typing import Any, Awaitable, Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request processing time.
    
    This middleware captures the time taken to process each request
    and logs it with the correlation ID for observability.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Process the request and log timing information.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            The response from the route handler.
        """
        start_time = time.time()
        
        # Get correlation_id from request state if available
        correlation_id = getattr(request.state, "correlation_id", "N/A")
        
        with logger.contextualize(correlation_id=correlation_id):
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom header
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # Log timing
            logger.info(
                "Request processed: {} {} - Status: {} - Time: {:.4f}s",
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )
            
            return response
