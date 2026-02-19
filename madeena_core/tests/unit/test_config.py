"""Unit tests for configuration module.

This module tests the configuration loading and validation.
"""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_validation_valid() -> None:
    """Test that valid settings are loaded correctly."""
    # This test assumes environment variables are set
    settings = Settings()
    
    assert settings.PROJECT_NAME is not None
    assert settings.VERSION is not None
    assert settings.APP_TIMEZONE == "Asia/Jakarta"


def test_deepseek_key_validation_invalid_prefix() -> None:
    """Test that DeepSeek key must start with 'sk-'."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DEEPSEEK_API_KEY="invalid-key",
            MADEENA_WEBHOOK_SECRET="test-secret-12345",
            TRELLO_API_KEY="test",
            TRELLO_TOKEN="test",
            TRELLO_BOARD_ID="test",
            TRELLO_LIST_ID_INBOX="test",
        )
    
    assert "DEEPSEEK_API_KEY must start with 'sk-'" in str(exc_info.value)


def test_deepseek_key_validation_too_short() -> None:
    """Test that DeepSeek key must be long enough."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DEEPSEEK_API_KEY="sk-123",
            MADEENA_WEBHOOK_SECRET="test-secret-12345",
            TRELLO_API_KEY="test",
            TRELLO_TOKEN="test",
            TRELLO_BOARD_ID="test",
            TRELLO_LIST_ID_INBOX="test",
        )
    
    assert "too short" in str(exc_info.value)


def test_webhook_secret_validation_too_short() -> None:
    """Test that webhook secret must be at least 8 characters."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DEEPSEEK_API_KEY="sk-1234567890",
            MADEENA_WEBHOOK_SECRET="short",
            TRELLO_API_KEY="test",
            TRELLO_TOKEN="test",
            TRELLO_BOARD_ID="test",
            TRELLO_LIST_ID_INBOX="test",
        )
    
    assert "at least 8 characters" in str(exc_info.value)


def test_default_values() -> None:
    """Test that default values are set correctly."""
    settings = Settings(
        DEEPSEEK_API_KEY="sk-1234567890",
        MADEENA_WEBHOOK_SECRET="test-secret-12345",
        TRELLO_API_KEY="test",
        TRELLO_TOKEN="test",
        TRELLO_BOARD_ID="test",
        TRELLO_LIST_ID_INBOX="test",
    )
    
    assert settings.ENV == "development"
    assert settings.DEBUG is True
    assert settings.DEEPSEEK_BASE_URL == "https://api.deepseek.com"
    assert settings.DEEPSEEK_MODEL == "deepseek-chat"
    assert settings.APP_TIMEZONE == "Asia/Jakarta"
