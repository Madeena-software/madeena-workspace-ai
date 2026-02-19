"""Pydantic schemas for AI response data.

This module defines the data models for DeepSeek AI responses,
ensuring type safety and validation.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AIResponseSchema(BaseModel):
    """Schema for DeepSeek AI response.
    
    This model represents the parsed JSON response from the AI,
    containing structured task information.
    """

    title: str = Field(
        ...,
        description="Concise task title (max 5-7 words)",
        min_length=1,
        max_length=100
    )
    
    description: str = Field(
        ...,
        description="Detailed task description",
        min_length=1
    )
    
    due_date: str | None = Field(
        default=None,
        description="Due date in ISO format (YYYY-MM-DD) or null"
    )
    
    priority: str = Field(
        default="Medium",
        description="Task priority: Low, Medium, or High"
    )
    
    external_links: list[str] = Field(
        default_factory=list,
        description="List of extracted URLs"
    )
    
    requires_meeting: bool = Field(
        default=False,
        description="Whether the task requires a meeting"
    )
    
    tags: list[str] = Field(
        default_factory=list,
        description="Extracted tags or categories"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Fix Production Bug",
                "description": "Critical bug in payment gateway needs immediate attention",
                "due_date": "2026-02-20",
                "priority": "High",
                "external_links": ["https://github.com/org/repo/issues/123"],
                "requires_meeting": False,
                "tags": ["bug", "production", "payment"]
            }
        }
    )
