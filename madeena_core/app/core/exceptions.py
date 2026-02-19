"""Custom exception classes for the Madeena Core application.

This module defines all custom exceptions used throughout the application
for better error handling and debugging.
"""


class MadeenaBaseException(Exception):
    """Base exception for all Madeena Core exceptions."""

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the base exception.
        
        Args:
            message: Main error message.
            details: Additional error details.
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class ConfigurationError(MadeenaBaseException):
    """Raised when there's a configuration error."""

    pass


class AIProviderError(MadeenaBaseException):
    """Raised when DeepSeek API fails after all retries."""

    pass


class ParsingError(MadeenaBaseException):
    """Raised when AI response cannot be parsed."""

    pass


class TrelloAPIError(MadeenaBaseException):
    """Raised when Trello API encounters an error."""

    pass


class AuthenticationError(MadeenaBaseException):
    """Raised when authentication fails."""

    pass


class RateLimitExceededError(MadeenaBaseException):
    """Raised when rate limit is exceeded."""

    pass
