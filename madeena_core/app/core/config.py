"""Application configuration using Pydantic Settings.

This module defines all configuration settings for the Madeena Core application,
loaded from environment variables with validation.
"""

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings are loaded from environment variables and validated
    using Pydantic V2's settings management.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Settings
    ENV: str = Field(default="development", description="Environment (development/production)")
    DEBUG: bool = Field(default=True, description="Debug mode")
    PROJECT_NAME: str = Field(default="Madeena Core", description="Project name")
    VERSION: str = Field(default="1.0.0", description="Application version")
    APP_TIMEZONE: str = Field(default="Asia/Jakarta", description="Application timezone")

    # Security
    MADEENA_WEBHOOK_SECRET: str = Field(..., description="Webhook secret for authentication")

    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str = Field(..., description="DeepSeek API key")
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API base URL"
    )
    DEEPSEEK_MODEL: str = Field(
        default="deepseek-chat",
        description="DeepSeek model name"
    )

    # Trello Configuration
    TRELLO_API_KEY: str = Field(..., description="Trello API key")
    TRELLO_TOKEN: str = Field(..., description="Trello authentication token")
    TRELLO_BOARD_ID: str = Field(..., description="Trello board ID")
    TRELLO_LIST_ID_INBOX: str = Field(..., description="Trello inbox list ID")

    @field_validator("DEEPSEEK_API_KEY")
    @classmethod
    def validate_deepseek_key(cls, v: str) -> str:
        """Validate DeepSeek API key format.
        
        Args:
            v: The API key to validate.
            
        Returns:
            The validated API key.
            
        Raises:
            ValueError: If the key format is invalid.
        """
        if not v.startswith("sk-"):
            raise ValueError("DEEPSEEK_API_KEY must start with 'sk-'")
        if len(v) < 10:
            raise ValueError("DEEPSEEK_API_KEY appears to be too short")
        return v

    @field_validator("MADEENA_WEBHOOK_SECRET")
    @classmethod
    def validate_webhook_secret(cls, v: str) -> str:
        """Validate webhook secret is not empty.
        
        Args:
            v: The webhook secret to validate.
            
        Returns:
            The validated webhook secret.
            
        Raises:
            ValueError: If the secret is empty or too short.
        """
        if len(v) < 8:
            raise ValueError("MADEENA_WEBHOOK_SECRET must be at least 8 characters")
        return v


# Global settings instance
settings = Settings()
