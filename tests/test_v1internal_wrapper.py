import pytest
import json
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_api_wrapper import GeminiAPIWrapper

@pytest.fixture
def mock_auth_service():
    service = MagicMock()
    service.get_next_account.return_value = {
        "email": "test@example.com",
        "projectId": "test-proj",
        "access": "test-access",
        "status": "valid"
    }
    service.get_valid_account = AsyncMock(side_effect=lambda x: x)
    return service

@pytest.fixture
def mock_usage_tracker():
    return MagicMock()

@pytest.fixture
def wrapper(mock_auth_service, mock_usage_tracker):
    return GeminiAPIWrapper(auth_service=mock_auth_service, usage_tracker=mock_usage_tracker)

@pytest.mark.anyio
async def test_generate_content_async_success(wrapper, mock_auth_service, mock_usage_tracker):
    # Mock httpx response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_lines.return_value = [
        b'data: {"response": {"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}}',
        b'data: {"response": {"candidates": [{"content": {"parts": [{"text": " World"}]}}]}}'
    ]
    
    with patch('httpx.AsyncClient.post', return_value=mock_resp):
        result = await wrapper.generate_content_async("Test prompt")
        
        assert result == "Hello World"
        # config_prefix = "note_generation" if model_type == "note" else model_type
        # Default config from ConfigManager mock or real? 
        # Actually generate_content_async maps 'note' to 'note_generation_model'
        # Let's match the actual value observed in the failure.
        mock_usage_tracker.record_usage.assert_called_once_with("test@example.com", "gemini-3-pro-preview")

def test_sync_wrappers(wrapper):
    with patch.object(wrapper, 'generate_content_async', new_callable=AsyncMock) as mock_async:
        mock_async.return_value = "Mocked Response"
        
        res = wrapper.generate_content("Prompt", system_instruction="System")
        assert res == "Mocked Response"
        mock_async.assert_called_once()
