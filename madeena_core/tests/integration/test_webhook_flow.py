"""Integration tests for webhook flow.

This module tests the complete webhook processing flow including
AI analysis and Trello card creation.
"""

import json

import httpx
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_full_flow_success(
    client: TestClient,
    valid_webhook_secret: str,
    sample_webhook_payload: dict,
    sample_ai_response: dict,
    mocker: MockerFixture,
) -> None:
    """Test successful end-to-end webhook processing.
    
    Verifies that a webhook is successfully processed through:
    1. Authentication
    2. AI analysis
    3. Trello card creation
    4. Response returned with 200 OK
    """
    # Mock DeepSeek AI response
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content=json.dumps(sample_ai_response))
        )
    ]
    
    mock_ai_client = mocker.MagicMock()
    mock_ai_client.chat.completions.create = mocker.AsyncMock(return_value=mock_completion)
    
    # Mock Trello API response
    mock_trello_response = {
        "id": "test-card-id-123",
        "name": sample_ai_response["title"],
        "url": "https://trello.com/c/test123/1-test-card",
        "shortUrl": "https://trello.com/c/test123",
        "idBoard": "test-board-id",
        "idList": "test-list-id",
    }
    
    mock_http_response = mocker.MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_trello_response
    mock_http_response.raise_for_status = mocker.MagicMock()
    
    # Mock httpx.AsyncClient
    mock_async_client = mocker.MagicMock()
    mock_async_client.post = mocker.AsyncMock(return_value=mock_http_response)
    mock_async_client.__aenter__ = mocker.AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = mocker.AsyncMock()
    
    mocker.patch("httpx.AsyncClient", return_value=mock_async_client)
    
    # Inject mocks into services
    from app.api.v1.endpoints import webhooks
    webhooks.deepseek_service.client = mock_ai_client
    
    # Make request
    response = client.post(
        "/api/v1/webhook",
        json=sample_webhook_payload,
        headers={"X-Madeena-Secret": valid_webhook_secret},
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "card_url" in data
    assert data["card_url"] == mock_trello_response["url"]
    assert "processing_time" in data
    assert "ai_data" in data


def test_invalid_secret(
    client: TestClient,
    sample_webhook_payload: dict,
) -> None:
    """Test webhook with invalid secret.
    
    Verifies that requests without proper authentication
    are rejected with 403 Forbidden.
    """
    # Make request with invalid secret
    response = client.post(
        "/api/v1/webhook",
        json=sample_webhook_payload,
        headers={"X-Madeena-Secret": "invalid-secret"},
    )
    
    # Verify forbidden response
    assert response.status_code == 403
    assert "Invalid or missing webhook secret" in response.text


def test_missing_secret(
    client: TestClient,
    sample_webhook_payload: dict,
) -> None:
    """Test webhook without secret header.
    
    Verifies that requests without the secret header
    are rejected.
    """
    # Make request without secret header
    response = client.post(
        "/api/v1/webhook",
        json=sample_webhook_payload,
    )
    
    # Verify error response (422 for missing required header)
    assert response.status_code == 422


def test_empty_message(
    client: TestClient,
    valid_webhook_secret: str,
) -> None:
    """Test webhook with empty message.
    
    Verifies that empty messages are rejected with 400 Bad Request.
    """
    payload = {
        "platform": "whatsapp",
        "message_text": "",
        "sender_id": "6281234567890",
    }
    
    # Make request
    response = client.post(
        "/api/v1/webhook",
        json=payload,
        headers={"X-Madeena-Secret": valid_webhook_secret},
    )
    
    # Verify bad request response
    assert response.status_code == 400
    assert "empty" in response.text.lower()


@pytest.mark.asyncio
async def test_trello_down(
    client: TestClient,
    valid_webhook_secret: str,
    sample_webhook_payload: dict,
    sample_ai_response: dict,
    mocker: MockerFixture,
) -> None:
    """Test handling of Trello API failure.
    
    Verifies that when Trello API returns 500, the webhook
    endpoint returns 502 Bad Gateway.
    """
    # Mock DeepSeek AI response (success)
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content=json.dumps(sample_ai_response))
        )
    ]
    
    mock_ai_client = mocker.MagicMock()
    mock_ai_client.chat.completions.create = mocker.AsyncMock(return_value=mock_completion)
    
    # Mock Trello API failure (500)
    mock_http_response = mocker.MagicMock()
    mock_http_response.status_code = 500
    mock_http_response.text = "Internal Server Error"
    mock_http_response.raise_for_status = mocker.MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Server error",
            request=mocker.MagicMock(),
            response=mock_http_response,
        )
    )
    
    # Mock httpx.AsyncClient
    mock_async_client = mocker.MagicMock()
    mock_async_client.post = mocker.AsyncMock(return_value=mock_http_response)
    mock_async_client.__aenter__ = mocker.AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = mocker.AsyncMock()
    
    mocker.patch("httpx.AsyncClient", return_value=mock_async_client)
    
    # Inject mocks into services
    from app.api.v1.endpoints import webhooks
    webhooks.deepseek_service.client = mock_ai_client
    
    # Make request
    response = client.post(
        "/api/v1/webhook",
        json=sample_webhook_payload,
        headers={"X-Madeena-Secret": valid_webhook_secret},
    )
    
    # Verify bad gateway response
    assert response.status_code == 502
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]


def test_health_endpoint(client: TestClient) -> None:
    """Test health check endpoint.
    
    Verifies that the health endpoint returns 200 OK
    with proper status information.
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint.
    
    Verifies that the root endpoint returns welcome message.
    """
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
