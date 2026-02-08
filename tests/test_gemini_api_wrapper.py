import os
import sys
import pytest
import httpx
from unittest.mock import patch, MagicMock
from google.genai import errors

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_api_wrapper import GeminiAPIWrapper

@pytest.fixture
def mock_key_manager():
    manager = MagicMock()
    manager.get_available_key.side_effect = ["key-1", "key-2", None]
    return manager

@patch('google.genai.Client')
def test_generate_content_success(mock_client_class, mock_key_manager):
    """Test successful text generation with system instruction."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.models.generate_content.return_value = MagicMock(text="Generated text")
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager)
    response = wrapper.generate_content("prompt", model_type="note", system_instruction="system prompt")
    
    assert response == "Generated text"
    # Verify generate_content was called with system_instruction in config
    args, kwargs = mock_client.models.generate_content.call_args
    assert kwargs['contents'] == "prompt"
    assert kwargs['config'].system_instruction == "system prompt"
    mock_key_manager.record_usage.assert_called_with("key-1", "gemini-3-flash-preview")

@patch('google.genai.Client')
def test_generate_content_with_file_success(mock_client_class, mock_key_manager):
    """Test successful generation with a file and system instruction."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Mock file upload
    mock_file = MagicMock(name="files/test-file")
    mock_file.state = "ACTIVE"
    mock_client.files.upload.return_value = mock_file
    mock_client.files.get.return_value = mock_file
    
    mock_client.models.generate_content.return_value = MagicMock(text="Transcription text")
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager)
    response = wrapper.generate_content_with_file(
        "path/to/audio.mp3", 
        "user prompt", 
        model_type="transcription",
        system_instruction="system prompt"
    )
    
    assert response == "Transcription text"
    mock_client.files.upload.assert_called_with(file="path/to/audio.mp3")
    
    # Verify generate_content was called with system_instruction in config
    args, kwargs = mock_client.models.generate_content.call_args
    assert mock_file in kwargs['contents']
    assert "user prompt" in kwargs['contents']
    assert kwargs['config'].system_instruction == "system prompt"
    mock_key_manager.record_usage.assert_called_with("key-1", "gemini-2.5-flash")

@patch('google.genai.Client')
def test_key_rotation_on_429(mock_client_class, mock_key_manager):
    """Test that it rotates keys when hitting 429 (quota)."""
    # First client (key-1) fails with 429
    # Second client (key-2) succeeds
    mock_client_1 = MagicMock()
    
    # Simulate 429 error via httpx
    mock_response = MagicMock(status_code=429)
    error_429 = httpx.HTTPStatusError("Quota exceeded", request=MagicMock(), response=mock_response)
    
    mock_client_1.models.generate_content.side_effect = error_429
    
    mock_client_2 = MagicMock()
    mock_client_2.models.generate_content.return_value = MagicMock(text="Success after rotation")
    
    mock_client_class.side_effect = [mock_client_1, mock_client_2]
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager)
    response = wrapper.generate_content("prompt", system_instruction="system")
    
    assert response == "Success after rotation"
    assert mock_key_manager.get_available_key.call_count == 2
    mock_key_manager.mark_exhausted.assert_called_with("key-1", "gemini-3-flash-preview")
    mock_key_manager.record_usage.assert_called_with("key-2", "gemini-3-flash-preview")

@patch('google.genai.Client')
def test_key_rotation_on_client_error_429(mock_client_class, mock_key_manager):
    """Test rotation on google.genai.errors.ClientError 429."""
    mock_client_1 = MagicMock()
    
    # Mock ClientError with code 429
    error_429 = errors.ClientError(429, {"error": {"message": "Quota exhausted"}})
    mock_client_1.models.generate_content.side_effect = error_429
    
    mock_client_2 = MagicMock()
    mock_client_2.models.generate_content.return_value = MagicMock(text="Success after rotation")
    
    mock_client_class.side_effect = [mock_client_1, mock_client_2]
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager)
    response = wrapper.generate_content("prompt", system_instruction="system")
    
    assert response == "Success after rotation"
    mock_key_manager.mark_exhausted.assert_called_with("key-1", "gemini-3-flash-preview")
