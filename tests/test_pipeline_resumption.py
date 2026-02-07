import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import ProcessingPipeline
from src.config_manager import ConfigManager

@pytest.fixture
def pipeline_setup():
    config = MagicMock(spec=ConfigManager)
    config.get.side_effect = lambda k, default=None: default
    mock_api = MagicMock()
    pipeline = ProcessingPipeline(config, api_wrapper=mock_api)
    return pipeline

def test_resume_from_downloaded(pipeline_setup):
    """Test that if status is DOWNLOADED and file exists, download is skipped."""
    pipeline = pipeline_setup
    job = {
        "id": "job1",
        "name": "Test Job",
        "url": "http://example.com",
        "status": "DOWNLOADED"
    }
    
    with patch("src.downloader.get_expected_audio_path") as mock_path, \
         patch("src.pipeline.os.path.exists") as mock_exists, \
         patch("src.downloader.download_audio") as mock_download, \
         patch("src.audio_processor.AudioProcessor.process_for_transcription") as mock_process, \
         patch("src.pipeline.JobManager") as mock_jm_class:
        
        mock_path.return_value = "downloads/Test_Job.mp3"
        # mock_exists must cover all modules
        mock_exists.side_effect = lambda p: True if "Test_Job" in p or p == "temp" or "downloads" in p else False
        
        mock_process.return_value = ["temp/job1_chunk_001.mp3"]
        pipeline.api.generate_content_with_file.side_effect = Exception("Stop here")
        
        try:
            pipeline.execute_job(job)
        except Exception as e:
            if str(e) != "Stop here": raise
        
        mock_download.assert_not_called()
        mock_process.assert_called_once()

def test_resume_from_chunked(pipeline_setup):
    """Test that if status is CHUNKED, download and processing are skipped."""
    pipeline = pipeline_setup
    job = {
        "id": "job1",
        "name": "Test Job",
        "url": "http://example.com",
        "status": "CHUNKED"
    }
    
    with patch("src.downloader.get_expected_audio_path") as mock_path, \
         patch("src.pipeline.os.path.exists") as mock_exists, \
         patch("src.pipeline.os.listdir") as mock_listdir, \
         patch("src.downloader.download_audio") as mock_download, \
         patch("src.audio_processor.AudioProcessor.process_for_transcription") as mock_process, \
         patch("src.pipeline.JobManager") as mock_jm_class, \
         patch("src.pipeline.open", create=True) as mock_open:
        
        mock_path.return_value = "downloads/Test_Job.mp3"
        mock_exists.side_effect = lambda p: True if "job1" in p or p == "temp" or "downloads" in p or "Test_Job" in p else False
        mock_listdir.return_value = ["job_job1_chunk_001.mp3", "job_job1_chunk_002.mp3"]
        
        pipeline.api.generate_content_with_file.side_effect = Exception("Stop here")
        
        try:
            pipeline.execute_job(job)
        except Exception as e:
            if str(e) != "Stop here": raise
        
        mock_download.assert_not_called()
        mock_process.assert_not_called()
        assert pipeline.api.generate_content_with_file.called

def test_resume_transcription_from_chunk_2(pipeline_setup):
    """Test that if some chunks are already transcribed, they are skipped."""
    pipeline = pipeline_setup
    job = {
        "id": "job1",
        "name": "Test Job",
        "url": "http://example.com",
        "status": "TRANSCRIBING_CHUNK_1",
        "transcriptions": {"1": "Already done"}
    }
    
    with patch("src.downloader.get_expected_audio_path") as mock_path, \
         patch("src.pipeline.os.path.exists") as mock_exists, \
         patch("src.pipeline.os.listdir") as mock_listdir, \
         patch("src.downloader.download_audio") as mock_download, \
         patch("src.audio_processor.AudioProcessor.process_for_transcription") as mock_process, \
         patch("src.pipeline.JobManager") as mock_jm_class, \
         patch("src.pipeline.open", create=True) as mock_open:
        
        mock_path.return_value = "downloads/Test_Job.mp3"
        mock_exists.side_effect = lambda p: True if "job1" in p or p == "temp" or "downloads" in p or "Test_Job" in p else False
        mock_listdir.return_value = ["job_job1_chunk_001.mp3", "job_job1_chunk_002.mp3"]
        
        pipeline.api.generate_content_with_file.return_value = "Chunk 2 result"
        
        with patch("src.note_generation_service.NoteGenerationService.generate") as mock_gen:
            mock_gen.return_value = False
            pipeline.execute_job(job)
        
        # Verify only chunk 2 was called
        assert pipeline.api.generate_content_with_file.call_count == 1
        args, kwargs = pipeline.api.generate_content_with_file.call_args
        assert "chunk_002" in kwargs["file_path"]
