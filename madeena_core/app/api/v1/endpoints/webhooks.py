"""Webhook endpoint for processing messages.

This module handles incoming webhooks from messaging platforms,
processes them through AI, and creates Trello cards.
"""

import time
from typing import Any

from asgi_correlation_id import correlation_id
from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger

from app.core.constants import (
    AI_PROCESSING_ERROR,
    EMPTY_MESSAGE_ERROR,
    SUCCESS_MESSAGE,
    TRELLO_ERROR,
)
from app.core.exceptions import AIProviderError, ParsingError, TrelloAPIError
from app.core.security import verify_webhook_secret
from app.schemas.payload import WebhookPayload
from app.services.deepseek_engine import DeepSeekService
from app.services.trello_manager import TrelloService

router = APIRouter()

# Initialize services
deepseek_service = DeepSeekService()
trello_service = TrelloService()


@router.post("/webhook", tags=["Webhooks"])
async def process_webhook(
    request: Request,
    payload: WebhookPayload,
    secret: str = Depends(verify_webhook_secret),
) -> dict[str, Any]:
    """Process incoming webhook from messaging platforms.
    
    This endpoint receives messages from WhatsApp/WeChat, processes them
    through DeepSeek AI for parsing, and creates Trello cards.
    
    Security:
        - Requires X-Madeena-Secret header for authentication
    
    Args:
        request: The FastAPI request object.
        payload: The webhook payload containing message data.
        secret: Validated webhook secret from dependency.
        
    Returns:
        Success response with card URL and processing time.
        
    Raises:
        HTTPException: For various error conditions.
    """
    start_time = time.time()
    
    # Get correlation ID from request
    corr_id = correlation_id.get() or "N/A"
    
    with logger.contextualize(correlation_id=corr_id):
        logger.info("Received webhook from platform: {}", payload.platform)
        
        # Validate message is not empty
        if not payload.message_text or payload.message_text.strip() == "":
            logger.warning("Empty message received from {}", payload.sender_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EMPTY_MESSAGE_ERROR,
            )
        
        try:
            # Step 1: Analyze text with DeepSeek AI
            logger.info("Processing message with AI")
            ai_response = await deepseek_service.analyze_text(
                text=payload.message_text,
                correlation_id=corr_id,
            )
            
            logger.info("AI analysis completed: {}", ai_response.title)
            
            # Step 2: Create Trello card
            logger.info("Creating Trello card")
            trello_response = await trello_service.create_card(
                data=ai_response,
                original_message=payload.message_text,
                correlation_id=corr_id,
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            logger.info(
                "Webhook processed successfully in {:.2f}s - Card URL: {}",
                processing_time,
                trello_response.url,
            )
            
            return {
                "success": True,
                "message": SUCCESS_MESSAGE,
                "card_url": trello_response.url,
                "card_id": trello_response.id,
                "processing_time": f"{processing_time:.2f}s",
                "ai_data": {
                    "title": ai_response.title,
                    "priority": ai_response.priority,
                    "due_date": ai_response.due_date,
                    "requires_meeting": ai_response.requires_meeting,
                },
            }
            
        except AIProviderError as e:
            logger.error("AI processing failed: {}", e.message)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "error": AI_PROCESSING_ERROR,
                    "message": e.message,
                    "details": e.details,
                },
            )
        
        except ParsingError as e:
            logger.error("Failed to parse AI response: {}", e.message)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "AI response parsing failed",
                    "message": e.message,
                    "details": e.details,
                },
            )
        
        except TrelloAPIError as e:
            logger.error("Trello API error: {}", e.message)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "error": TRELLO_ERROR,
                    "message": e.message,
                    "details": e.details,
                },
            )
        
        except Exception as e:
            logger.exception("Unexpected error processing webhook")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "message": str(e),
                },
            )
