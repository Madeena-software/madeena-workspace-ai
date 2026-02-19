"""Pydantic schemas for webhook payload data.

This module defines the data models for incoming webhook payloads
from messaging platforms.
"""

from pydantic import BaseModel, ConfigDict, Field


class WebhookPayload(BaseModel):
    """Schema for incoming webhook payload.
    
    This model represents the data structure expected from
    messaging platforms like WhatsApp or WeChat.
    """

    platform: str = Field(
        ...,
        description="Source platform (e.g., 'whatsapp', 'wechat')",
        min_length=1
    )
    
    message_text: str = Field(
        ...,
        description="The actual message content",
        min_length=1
    )
    
    sender_id: str = Field(
        ...,
        description="Unique identifier for the message sender",
        min_length=1
    )
    
    sender_name: str | None = Field(
        default=None,
        description="Display name of the sender"
    )
    
    timestamp: str | None = Field(
        default=None,
        description="Message timestamp in ISO format"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "platform": "whatsapp",
                "message_text": "Tolong buatkan task untuk meeting dengan client besok jam 2 siang",
                "sender_id": "6281234567890",
                "sender_name": "John Doe",
                "timestamp": "2026-02-19T10:30:00Z"
            }
        }
    )
