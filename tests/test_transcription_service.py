import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.transcription_service import TranscriptionService

@pytest.fixture
def output_file(tmp_path):
    return str(tmp_path / "transcript.txt")

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_transcribe_chunks_success(mock_run, output_file):
    """Test successful transcription of multiple chunks."""
    mock_run.side_effect = [
        {"success": True, "stdout": json.dumps({"response": "Part 1"})},
        {"success": True, "stdout": json.dumps({"response": "Part 2"})}
    ]
    
    chunks = ["chunk1.mp3", "chunk2.mp3"]
    success = TranscriptionService.transcribe_chunks(chunks, "model-x", output_file)
    
    assert success is True
    assert mock_run.call_count == 2
    
    # Verify arguments
    args1 = mock_run.call_args_list[0][0][0]
    assert "-m" in args1
    assert "model-x" in args1
    assert "@chunk1.mp3" in args1[-1]
    
    with open(output_file, 'r') as f:
        content = f.read()
    # Now includes newlines between chunks
    assert "Part 1\nPart 2\n" == content

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_transcribe_chunks_failure(mock_run, output_file):
    """Test failure in one chunk stops process."""
    mock_run.return_value = {"success": False, "stderr": "error"}
    
    chunks = ["chunk1.mp3", "chunk2.mp3"]
    success = TranscriptionService.transcribe_chunks(chunks, "model-x", output_file)
    
    assert success is False