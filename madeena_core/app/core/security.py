"""Security utilities for API authentication and validation.

This module provides security-related functions including
webhook secret validation and API key verification.
"""

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.core.constants import INVALID_SECRET_MESSAGE
from app.core.exceptions import AuthenticationError


async def verify_webhook_secret(
    x_madeena_secret: str = Header(..., description="Webhook authentication secret")
) -> str:
    """Verify the webhook secret from request headers.
    
    This dependency function validates the X-Madeena-Secret header
    against the configured webhook secret.
    
    Args:
        x_madeena_secret: The secret provided in the request header.
        
    Returns:
        The validated secret.
        
    Raises:
        HTTPException: If the secret is invalid or missing.
    """
    if x_madeena_secret != settings.MADEENA_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=INVALID_SECRET_MESSAGE,
        )
    return x_madeena_secret


def validate_api_key(api_key: str) -> bool:
    """Validate an API key format.
    
    Args:
        api_key: The API key to validate.
        
    Returns:
        True if the key is valid, False otherwise.
    """
    if not api_key:
        return False
    if not api_key.startswith("sk-"):
        return False
    if len(api_key) < 10:
        return False
    return True
