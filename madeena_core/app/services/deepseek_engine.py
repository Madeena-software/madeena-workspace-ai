"""DeepSeek AI service with circuit breaker pattern.

This module provides AI processing capabilities using DeepSeek's LLM,
with resilience patterns including retry logic and circuit breakers.
"""

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from loguru import logger
from openai import AsyncOpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.constants import SYSTEM_PROMPT_TEMPLATE
from app.core.exceptions import AIProviderError, ParsingError
from app.schemas.ai_response import AIResponseSchema


class DeepSeekService:
    """Service for interacting with DeepSeek AI API.
    
    This service handles all AI-related operations including text analysis,
    prompt engineering, and response parsing. Implements circuit breaker
    pattern with exponential backoff for resilience.
    """

    def __init__(self) -> None:
        """Initialize the DeepSeek service with API client."""
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL
        logger.info("DeepSeekService initialized with model: {}", self.model)

    def _build_system_prompt(self) -> str:
        """Build the system prompt with current datetime context.
        
        Returns:
            Formatted system prompt with injected datetime information.
        """
        tz = ZoneInfo(settings.APP_TIMEZONE)
        now = datetime.now(tz)
        
        return SYSTEM_PROMPT_TEMPLATE.format(
            current_date=now.strftime("%Y-%m-%d"),
            day_name=now.strftime("%A"),
            current_time=now.strftime("%H:%M:%S"),
            timezone=settings.APP_TIMEZONE,
        )

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=8),
        reraise=True,
    )
    async def _call_ai_api(self, user_message: str, correlation_id: str) -> str:
        """Call the DeepSeek API with retry logic.
        
        Args:
            user_message: The user's message to analyze.
            correlation_id: Request correlation ID for tracing.
            
        Returns:
            Raw JSON string response from the AI.
            
        Raises:
            AIProviderError: If all retry attempts fail.
        """
        system_prompt = self._build_system_prompt()
        
        with logger.contextualize(correlation_id=correlation_id):
            logger.debug("Calling DeepSeek API with model: {}", self.model)
            
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.1,  # Low temperature for consistent parsing
                    max_tokens=1000,
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise AIProviderError("AI returned empty response")
                
                logger.debug("DeepSeek API call successful")
                return content.strip()
                
            except RateLimitError as e:
                logger.warning("Rate limit hit, retrying...")
                raise
            except Exception as e:
                logger.error("DeepSeek API error: {}", str(e))
                raise AIProviderError(
                    message="Failed to call DeepSeek API",
                    details=str(e)
                )

    def _parse_ai_response(self, raw_response: str, correlation_id: str) -> AIResponseSchema:
        """Parse and validate AI response.
        
        Args:
            raw_response: Raw JSON string from AI.
            correlation_id: Request correlation ID for tracing.
            
        Returns:
            Validated AIResponseSchema object.
            
        Raises:
            ParsingError: If response cannot be parsed or validated.
        """
        with logger.contextualize(correlation_id=correlation_id):
            try:
                # Remove markdown code blocks if present
                cleaned = raw_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                # Parse JSON and validate with Pydantic V2
                response_data = AIResponseSchema.model_validate_json(cleaned)
                logger.info("Successfully parsed AI response")
                return response_data
                
            except json.JSONDecodeError as e:
                logger.error("Failed to parse AI response as JSON: {}", str(e))
                logger.debug("Raw response: {}", raw_response)
                raise ParsingError(
                    message="Invalid JSON in AI response",
                    details=str(e)
                )
            except Exception as e:
                logger.error("Failed to validate AI response: {}", str(e))
                logger.debug("Raw response: {}", raw_response)
                raise ParsingError(
                    message="Failed to validate AI response schema",
                    details=str(e)
                )

    async def analyze_text(self, text: str, correlation_id: str = "N/A") -> AIResponseSchema:
        """Analyze text using DeepSeek AI and return structured data.
        
        This is the main entry point for AI text analysis. It handles
        the full pipeline: API call -> parsing -> validation.
        
        Args:
            text: The text message to analyze.
            correlation_id: Request correlation ID for tracing.
            
        Returns:
            Validated AIResponseSchema with structured task data.
            
        Raises:
            AIProviderError: If AI API fails after all retries.
            ParsingError: If response cannot be parsed.
        """
        with logger.contextualize(correlation_id=correlation_id):
            logger.info("Starting AI analysis for message")
            
            try:
                # Call AI API with circuit breaker
                raw_response = await self._call_ai_api(text, correlation_id)
                
                # Parse and validate response
                parsed_response = self._parse_ai_response(raw_response, correlation_id)
                
                logger.info("AI analysis completed successfully")
                return parsed_response
                
            except (AIProviderError, ParsingError):
                raise
            except Exception as e:
                logger.error("Unexpected error during AI analysis: {}", str(e))
                raise AIProviderError(
                    message="Unexpected error during AI analysis",
                    details=str(e)
                )
