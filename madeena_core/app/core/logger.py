"""Logging configuration with Loguru and correlation ID support.

This module configures Loguru for structured logging with correlation IDs
for distributed tracing across services.
"""

import logging
import sys
from typing import Any

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to Loguru.
    
    This handler bridges Python's standard logging to Loguru,
    ensuring all logs go through a single pipeline.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record through Loguru.
        
        Args:
            record: The log record to emit.
        """
        # Get corresponding Loguru level if it exists
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame_or_none: logging._FrameType | None = logging.currentframe()  # type: ignore[name-defined]
        depth = 2
        while frame_or_none is not None and frame_or_none.f_code.co_filename == logging.__file__:
            frame_or_none = frame_or_none.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure logging for the application.
    
    Sets up Loguru with appropriate format, level, and handlers.
    Intercepts standard library logging to route through Loguru.
    """
    # Remove default handler
    logger.remove()

    # Configure format based on environment
    if settings.ENV == "production":
        # JSON format for production
        log_format = (
            "{{"
            '"time": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"correlation_id": "{extra[correlation_id]}", '
            '"message": "{message}", '
            '"module": "{module}", '
            '"function": "{function}", '
            '"line": {line}'
            "}}"
        )
    else:
        # Human-readable format for development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[correlation_id]}</cyan> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add handler with correlation_id default
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": log_format,
                "level": "DEBUG" if settings.DEBUG else "INFO",
            }
        ],
        extra={"correlation_id": "N/A"},  # Default value
    )

    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set specific loggers to WARNING to reduce noise
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]

    logger.info(f"Logging configured for {settings.ENV} environment")
