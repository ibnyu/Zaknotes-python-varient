import os
import sys
import pytest
from unittest.mock import patch, MagicMock, ANY

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import ProcessingPipeline
from src.prompts import TRANSCRIPTION_PROMPT

@pytest.fixture
def mock_config():
    config = MagicMock()
    # Default values for models
    def get_mock(key, default=None):
        if "transcription" in key: return "model-trans"
        if "note" in key: return "model-note"
        if "segment_time" in key: return 1800
        return default
    
    config.get.side_effect = get_mock
    return config

@pytest.fixture
def job():
    return {"id": "123", "name": "Test Job", "url": "http://example.com", "status": "queue"}

@patch('src.pipeline.download_audio')
@patch('src.pipeline.AudioProcessor')
@patch('src.pipeline.GeminiAPIWrapper')
@patch('src.pipeline.NoteGenerationService.generate')
@patch('src.pipeline.os')
@patch('src.pipeline.shutil')
@patch('src.pipeline.JobManager')
def test_execute_job_success(mock_job_manager_class, mock_shutil, mock_os, mock_notes, mock_api_class, mock_audio_class, mock_down, mock_config, job):
    """Test successful execution of the full pipeline."""
    # Setup mocks
    mock_down.return_value = "downloads/Test_Job.mp3"
    
    # Mock JobManager
    mock_manager = mock_job_manager_class.return_value
    
    # AudioProcessor mocks
    mock_audio_class.remove_silence.return_value = True
    mock_audio_class.reencode_to_optimal.return_value = True
    mock_audio_class.get_duration.return_value = 100 # Short duration, no splitting
    mock_audio_class.split_into_chunks.return_value = ["temp/job_123_chunk_001.mp3"]
    
    # OS mocks
    mock_os.path.exists.return_value = False # Default to false
    # But specific paths need to be true/false logic
    def exists_side_effect(path):
        if path == "downloads/Test_Job.mp3": return True # Downloaded file
        if "prepared" in path: return False # Not processed yet
        if "chunk" in path: return True # Chunks exist
        if "transcript.txt" in path: return False
        return False
    mock_os.path.exists.side_effect = exists_side_effect
    
    mock_os.listdir.return_value = [] # No existing chunks initially
    
    mock_os.path.join = os.path.join
    mock_os.path.basename = os.path.basename
    mock_os.path.dirname = os.path.dirname
    mock_os.path.splitext = os.path.splitext
    
    # API mocks
    mock_api = mock_api_class.return_value
    mock_api.generate_content_with_file.return_value = "Transcript text"
    
    mock_notes.return_value = True
    
    pipeline = ProcessingPipeline(mock_config, job_manager=mock_manager)
    
    # We need to handle the file opening in pipeline
    with patch('builtins.open', MagicMock()):
        success = pipeline.execute_job(job)
        
        assert success is True
        # Verify JobManager was updated to completed
        mock_manager.update_job_status.assert_called_with('123', 'completed')
        
        # Verify download skipped (since file exists)
        mock_down.assert_not_called()
        
        # Verify processing
        mock_audio_class.remove_silence.assert_called()
        mock_audio_class.reencode_to_optimal.assert_called()
        
        # Verify API call with system_instruction
        mock_api.generate_content_with_file.assert_called()
        args, kwargs = mock_api.generate_content_with_file.call_args
        assert kwargs['system_instruction'] == TRANSCRIPTION_PROMPT
        assert kwargs['prompt'] == "Please transcribe this audio chunk."
        
        # Verify notes generation
        mock_notes.assert_called_once()

@patch('src.pipeline.download_audio')
@patch('src.pipeline.AudioProcessor')
@patch('src.pipeline.GeminiAPIWrapper')
@patch('src.pipeline.os')
@patch('src.pipeline.JobManager')
def test_execute_job_download_failure(mock_job_manager_class, mock_os, mock_api, mock_audio, mock_down, mock_config, job):
    """Test pipeline failure when download fails."""
    mock_down.return_value = None
    mock_os.path.exists.return_value = False
    mock_manager = mock_job_manager_class.return_value
    
    pipeline = ProcessingPipeline(mock_config, job_manager=mock_manager)
    success = pipeline.execute_job(job)
    
    assert success is False
    mock_manager.update_job_status.assert_called_with('123', 'failed')