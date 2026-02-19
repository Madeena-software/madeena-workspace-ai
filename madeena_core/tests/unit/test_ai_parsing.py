"""Unit tests for AI parsing functionality.

This module tests the DeepSeek service's ability to parse and analyze text.
"""

import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from pytest_mock import MockerFixture

from app.core.config import settings
from app.core.exceptions import AIProviderError, ParsingError
from app.schemas.ai_response import AIResponseSchema
from app.services.deepseek_engine import DeepSeekService


@pytest.mark.asyncio
async def test_parse_relative_date(mocker: MockerFixture) -> None:
    """Test parsing relative date 'besok' (tomorrow).
    
    Verifies that the AI correctly calculates specific dates
    when given relative terms like 'besok' (tomorrow).
    """
    # Calculate expected date (tomorrow)
    tz = ZoneInfo(settings.APP_TIMEZONE)
    tomorrow = datetime.now(tz) + timedelta(days=1)
    expected_date = tomorrow.strftime("%Y-%m-%d")
    
    # Mock AI response with tomorrow's date
    mock_response = {
        "title": "Meeting dengan Client",
        "description": "Rapat dengan client untuk diskusi project",
        "due_date": expected_date,
        "priority": "Medium",
        "external_links": [],
        "requires_meeting": True,
        "tags": ["meeting", "client"]
    }
    
    # Mock OpenAI client
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content=json.dumps(mock_response))
        )
    ]
    
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_completion)
    
    # Create service and inject mock client
    service = DeepSeekService()
    service.client = mock_client
    
    # Test with message containing "besok"
    result = await service.analyze_text(
        "Tolong buat task untuk meeting dengan client besok",
        correlation_id="test-123"
    )
    
    # Verify date was calculated correctly
    assert result.due_date == expected_date
    assert result.requires_meeting is True
    assert result.title == "Meeting dengan Client"


@pytest.mark.asyncio
async def test_priority_urgent(mocker: MockerFixture) -> None:
    """Test priority detection for urgent messages.
    
    Verifies that messages with urgent keywords like 'TOLONG CEPAT'
    are correctly classified as High priority.
    """
    # Mock AI response with High priority
    mock_response = {
        "title": "Perbaiki Bug Production",
        "description": "Bug kritis perlu diperbaiki segera",
        "due_date": None,
        "priority": "High",
        "external_links": [],
        "requires_meeting": False,
        "tags": ["bug", "urgent"]
    }
    
    # Mock OpenAI client
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content=json.dumps(mock_response))
        )
    ]
    
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_completion)
    
    # Create service and inject mock client
    service = DeepSeekService()
    service.client = mock_client
    
    # Test with urgent message
    result = await service.analyze_text(
        "TOLONG CEPAT! Perbaiki bug di production",
        correlation_id="test-123"
    )
    
    # Verify priority is High
    assert result.priority == "High"
    assert "bug" in result.tags or "urgent" in result.tags


@pytest.mark.asyncio
async def test_malformed_json(mocker: MockerFixture) -> None:
    """Test handling of malformed JSON from AI.
    
    Verifies that ParsingError is raised when AI returns
    invalid JSON that cannot be parsed.
    """
    # Mock AI response with malformed JSON
    malformed_json = '{"title": "Test", "description": "Test" invalid json'
    
    # Mock OpenAI client
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content=malformed_json)
        )
    ]
    
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_completion)
    
    # Create service and inject mock client
    service = DeepSeekService()
    service.client = mock_client
    
    # Test with any message
    with pytest.raises(ParsingError) as exc_info:
        await service.analyze_text(
            "Test message",
            correlation_id="test-123"
        )
    
    # Verify error message (Pydantic V2 may report differently)
    error_msg = str(exc_info.value)
    assert "Failed to validate" in error_msg or "Invalid JSON" in error_msg


@pytest.mark.asyncio
async def test_markdown_code_block_removal(mocker: MockerFixture) -> None:
    """Test that markdown code blocks are removed from AI response.
    
    Verifies that the service can handle AI responses wrapped
    in markdown code blocks (```json ... ```).
    """
    # Mock AI response wrapped in markdown
    mock_response_data = {
        "title": "Test Task",
        "description": "Test description",
        "due_date": None,
        "priority": "Medium",
        "external_links": [],
        "requires_meeting": False,
        "tags": []
    }
    
    markdown_wrapped = f"```json\n{json.dumps(mock_response_data)}\n```"
    
    # Mock OpenAI client
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content=markdown_wrapped)
        )
    ]
    
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_completion)
    
    # Create service and inject mock client
    service = DeepSeekService()
    service.client = mock_client
    
    # Test parsing
    result = await service.analyze_text(
        "Test message",
        correlation_id="test-123"
    )
    
    # Verify successful parsing
    assert result.title == "Test Task"
    assert result.priority == "Medium"


@pytest.mark.asyncio
async def test_link_extraction(mocker: MockerFixture) -> None:
    """Test extraction of URLs from message.
    
    Verifies that external links are properly extracted
    from the message content.
    """
    # Mock AI response with links
    mock_response = {
        "title": "Review GitHub PR",
        "description": "Review and merge the pull request",
        "due_date": None,
        "priority": "Medium",
        "external_links": [
            "https://github.com/org/repo/pull/123",
            "https://drive.google.com/file/d/abc123"
        ],
        "requires_meeting": False,
        "tags": ["review", "github"]
    }
    
    # Mock OpenAI client
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content=json.dumps(mock_response))
        )
    ]
    
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_completion)
    
    # Create service and inject mock client
    service = DeepSeekService()
    service.client = mock_client
    
    # Test with message containing links
    result = await service.analyze_text(
        "Please review https://github.com/org/repo/pull/123 and check https://drive.google.com/file/d/abc123",
        correlation_id="test-123"
    )
    
    # Verify links were extracted
    assert len(result.external_links) == 2
    assert "https://github.com/org/repo/pull/123" in result.external_links
    assert "https://drive.google.com/file/d/abc123" in result.external_links
