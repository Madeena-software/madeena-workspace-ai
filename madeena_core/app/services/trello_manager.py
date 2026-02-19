"""Trello service for managing cards and boards.

This module provides Trello API integration for creating and managing
task cards with caching and error handling.
"""

from datetime import datetime
from typing import Any

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.exceptions import ConfigurationError, TrelloAPIError
from app.schemas.ai_response import AIResponseSchema
from app.schemas.trello_api import TrelloCardCreate, TrelloCardResponse


class TrelloService:
    """Service for interacting with Trello API.
    
    This service handles all Trello-related operations including
    card creation, description formatting, and error handling.
    """

    def __init__(self) -> None:
        """Initialize the Trello service with API credentials."""
        self.api_key = settings.TRELLO_API_KEY
        self.token = settings.TRELLO_TOKEN
        self.board_id = settings.TRELLO_BOARD_ID
        self.list_id = settings.TRELLO_LIST_ID_INBOX
        self.base_url = "https://api.trello.com/1"
        logger.info("TrelloService initialized for board: {}", self.board_id)

    def _build_card_description(
        self,
        data: AIResponseSchema,
        original_message: str,
    ) -> str:
        """Build a formatted Markdown description for the Trello card.
        
        Args:
            data: Parsed AI response data.
            original_message: The original user message.
            
        Returns:
            Formatted Markdown description.
        """
        parts = []
        
        # Add main description
        parts.append(data.description)
        parts.append("")  # Empty line
        
        # Add context section
        parts.append("## Context")
        parts.append(f"Original message: {original_message}")
        parts.append("")
        
        # Add links section if present
        if data.external_links:
            parts.append("## Links")
            for link in data.external_links:
                parts.append(f"- {link}")
            parts.append("")
        
        # Add metadata
        parts.append("## Metadata")
        parts.append(f"- **Priority**: {data.priority}")
        parts.append(f"- **Requires Meeting**: {'Yes' if data.requires_meeting else 'No'}")
        
        if data.tags:
            tags_str = ", ".join(data.tags)
            parts.append(f"- **Tags**: {tags_str}")
        
        return "\n".join(parts)

    def _format_due_date(self, due_date: str | None) -> str | None:
        """Format due date to Trello's expected format.
        
        Trello expects ISO 8601 format with timezone (e.g., 2026-02-20T23:59:59.000Z).
        
        Args:
            due_date: Due date in YYYY-MM-DD format or None.
            
        Returns:
            Formatted due date string or None.
        """
        if not due_date:
            return None
        
        try:
            # Parse the date and set time to end of day
            dt = datetime.strptime(due_date, "%Y-%m-%d")
            # Set to end of day in UTC
            dt = dt.replace(hour=23, minute=59, second=59, microsecond=0)
            # Format to ISO 8601 with milliseconds
            return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        except ValueError as e:
            logger.warning("Invalid due date format: {}. Error: {}", due_date, str(e))
            return None

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(2),
        wait=wait_fixed(2),
        reraise=True,
    )
    async def _make_api_call(
        self,
        card_data: TrelloCardCreate,
        correlation_id: str,
    ) -> dict[str, Any]:
        """Make the actual API call to Trello.
        
        Args:
            card_data: The card data to send.
            correlation_id: Request correlation ID for tracing.
            
        Returns:
            Response data from Trello API.
            
        Raises:
            ConfigurationError: If authentication fails (401).
            TrelloAPIError: For other API errors.
        """
        url = f"{self.base_url}/cards"
        params = {
            "key": self.api_key,
            "token": self.token,
        }
        
        with logger.contextualize(correlation_id=correlation_id):
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        url,
                        params=params,
                        json=card_data.model_dump(exclude_none=True),
                        timeout=30.0,
                    )
                    
                    # Check for authentication errors
                    if response.status_code == 401:
                        logger.error("Trello authentication failed")
                        raise ConfigurationError(
                            message="Trello API authentication failed",
                            details="Check TRELLO_API_KEY and TRELLO_TOKEN"
                        )
                    
                    # Check for rate limiting
                    if response.status_code == 429:
                        logger.warning("Trello rate limit hit, retrying...")
                        response.raise_for_status()
                    
                    # Raise for other HTTP errors
                    response.raise_for_status()
                    
                    logger.debug("Trello API call successful")
                    response_json: dict[str, Any] = response.json()
                    return response_json
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        raise  # Let retry handle this
                    logger.error("Trello API error: {} - {}", e.response.status_code, e.response.text)
                    raise TrelloAPIError(
                        message=f"Trello API returned status {e.response.status_code}",
                        details=e.response.text
                    )
                except httpx.RequestError as e:
                    logger.error("Trello request error: {}", str(e))
                    raise TrelloAPIError(
                        message="Failed to connect to Trello API",
                        details=str(e)
                    )

    async def create_card(
        self,
        data: AIResponseSchema,
        original_message: str,
        correlation_id: str = "N/A",
    ) -> TrelloCardResponse:
        """Create a Trello card from AI-parsed data.
        
        This is the main entry point for creating Trello cards.
        It handles description formatting, date conversion, and API calls.
        
        Args:
            data: Parsed AI response data.
            original_message: The original user message for context.
            correlation_id: Request correlation ID for tracing.
            
        Returns:
            Trello card response with URL and metadata.
            
        Raises:
            ConfigurationError: If Trello authentication fails.
            TrelloAPIError: If card creation fails.
        """
        with logger.contextualize(correlation_id=correlation_id):
            logger.info("Creating Trello card: {}", data.title)
            
            # Build card description
            description = self._build_card_description(data, original_message)
            
            # Format due date
            due_date = self._format_due_date(data.due_date)
            
            # Prepare card data
            card_data = TrelloCardCreate(
                name=data.title,
                desc=description,
                idList=self.list_id,
                due=due_date,
                pos="top",  # Add to top of list
            )
            
            try:
                # Make API call
                response_data = await self._make_api_call(card_data, correlation_id)
                
                # Parse response
                trello_response = TrelloCardResponse(**response_data)
                
                logger.info("Trello card created successfully: {}", trello_response.url)
                return trello_response
                
            except (ConfigurationError, TrelloAPIError):
                raise
            except Exception as e:
                logger.error("Unexpected error creating Trello card: {}", str(e))
                raise TrelloAPIError(
                    message="Unexpected error creating Trello card",
                    details=str(e)
                )
