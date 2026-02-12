import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.downloader import download_audio
from src.config_manager import ConfigManager

@pytest.fixture
def mock_config():
    with patch('src.downloader.ConfigManager') as mock:
        instance = mock.return_value
        instance.get.return_value = "TestUserAgent/1.0"
        yield instance

@pytest.fixture
def mock_run():
    with patch('subprocess.run') as mock:
        mock.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock

def test_download_audio_uses_configured_ua(mock_config, mock_run):
    """Test that download_audio uses the User-Agent from config."""
    job = {'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'name': 'test_job'}
    
    # We need to bypass the actual download
    # The current download_audio doesn't take config as input, it creates one
    # So we patched ConfigManager in src.downloader
    
    download_audio(job)
    
    # Check if any of the calls to subprocess.run contained the User-Agent
    found_ua = False
    for call in mock_run.call_args_list:
        args = call[0][0]
        cmd_str = " ".join(args) if isinstance(args, list) else args
        if "TestUserAgent/1.0" in cmd_str:
            found_ua = True
            break
    
    assert found_ua, "Configured User-Agent not found in any yt-dlp command"

def test_youtube_reduced_concurrency(mock_config, mock_run):
    """Test that YouTube downloads use reduced concurrency."""
    job = {'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'name': 'test_job'}
    download_audio(job)
    
    # Check if any call contained -N 16 (it should NOT for YouTube)
    found_high_concurrency = False
    for call in mock_run.call_args_list:
        args = call[0][0]
        cmd_str = " ".join(args) if isinstance(args, list) else args
        if "-N 16" in cmd_str:
            found_high_concurrency = True
            break
    
    assert not found_high_concurrency, "High concurrency (-N 16) found in YouTube command"

def test_hls_downloader_flags(mock_config, mock_run):
    """Test that EdgeCourseBD/Vimeo downloads use HLS-friendly flags."""
    # This URL should trigger EdgeCourseBD mode
    job = {'url': 'https://edgecoursebd.com/lesson/123', 'name': 'test_edge'}
    
    # We also need to mock link_extractor.py execution if it's called
    with patch('src.downloader.run_command', return_value="https://player.vimeo.com/video/456") as mock_run_cmd:
        # Mocking the first call (scraper) and second (download)
        mock_run_cmd.side_effect = ["https://player.vimeo.com/video/456", "done"]
        
        # We need to be careful because download_audio calls run_command
        # Let's just check if any of the commands had the flags
        try:
            download_audio(job)
        except:
            pass # We don't care about the return value here
            
        found_hls_flags = False
        for call in mock_run_cmd.call_args_list:
            cmd_args = call[0][0]
            if any("--downloader" == a for a in cmd_args) and any("ffmpeg" == a for a in cmd_args) and any("--hls-use-mpegts" == a for a in cmd_args):
                found_hls_flags = True
                break
        assert found_hls_flags, "HLS downloader flags not found in EdgeCourseBD/Vimeo command"
