"""Pytest configuration and fixtures.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app.
    
    Returns:
        TestClient instance for making test requests.
    """
    return TestClient(app)


@pytest.fixture
def valid_webhook_secret() -> str:
    """Get the valid webhook secret for testing.
    
    Returns:
        Valid webhook secret string.
    """
    from app.core.config import settings
    return settings.MADEENA_WEBHOOK_SECRET


@pytest.fixture
def sample_webhook_payload() -> dict:
    """Create a sample webhook payload for testing.
    
    Returns:
        Dictionary with sample webhook data.
    """
    return {
        "platform": "whatsapp",
        "message_text": "TOLONG CEPAT! Perbaiki bug di production besok pagi",
        "sender_id": "6281234567890",
        "sender_name": "Test User",
        "timestamp": "2026-02-19T10:30:00Z"
    }


@pytest.fixture
def sample_ai_response() -> dict:
    """Create a sample AI response for testing.
    
    Returns:
        Dictionary with sample AI response data.
    """
    return {
        "title": "Perbaiki Bug Production",
        "description": "Bug kritis di production perlu diperbaiki segera",
        "due_date": "2026-02-20",
        "priority": "High",
        "external_links": [],
        "requires_meeting": False,
        "tags": ["bug", "production", "urgent"]
    }
