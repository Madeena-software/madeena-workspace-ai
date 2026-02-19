"""Pydantic schemas for Trello API data.

This module defines the data models for Trello API requests and responses.
"""

from typing import Any

from pydantic import BaseModel, Field


class TrelloCardCreate(BaseModel):
    """Schema for creating a Trello card.
    
    This model represents the data structure for Trello's
    card creation API endpoint.
    """

    name: str = Field(
        ...,
        description="Card title",
        min_length=1,
        max_length=16384
    )
    
    desc: str | None = Field(
        default=None,
        description="Card description in Markdown format"
    )
    
    idList: str = Field(
        ...,
        description="ID of the list where the card should be created"
    )
    
    due: str | None = Field(
        default=None,
        description="Due date in ISO 8601 format"
    )
    
    pos: str = Field(
        default="top",
        description="Position of the card in the list"
    )

    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "name": "Fix Production Bug",
                "desc": "## Context\nCritical bug in payment gateway\n\n## Links\n- https://github.com/org/repo/issues/123",
                "idList": "5abbe4b7ddc1b351ef961414",
                "due": "2026-02-20T23:59:59.000Z",
                "pos": "top"
            }
        }


class TrelloCardResponse(BaseModel):
    """Schema for Trello card creation response.
    
    This model represents the response from Trello after
    successfully creating a card.
    """

    id: str = Field(..., description="Card ID")
    name: str = Field(..., description="Card title")
    url: str = Field(..., description="Card URL")
    shortUrl: str = Field(..., description="Short card URL")
    idBoard: str = Field(..., description="Board ID")
    idList: str = Field(..., description="List ID")

    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "5abbe4b7ddc1b351ef961414",
                "name": "Fix Production Bug",
                "url": "https://trello.com/c/abc123/1-fix-production-bug",
                "shortUrl": "https://trello.com/c/abc123",
                "idBoard": "5abbe4b7ddc1b351ef961413",
                "idList": "5abbe4b7ddc1b351ef961414"
            }
        }
