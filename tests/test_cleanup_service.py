import os
import sys
import pytest
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleanup_service import FileCleanupService

def test_cleanup_job_files(tmp_path):
    """Test deletion of specific files."""
    f1 = tmp_path / "test1.txt"
    f1.write_text("content")
    f2 = tmp_path / "test2.txt"
    f2.write_text("content")
    
    FileCleanupService.cleanup_job_files([str(f1), str(f2)])
    
    assert not os.path.exists(f1)
    assert not os.path.exists(f2)

def test_cleanup_all_temp_files(tmp_path):
    """Test manual cleanup of directories."""
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "junk.mp3").write_text("junk")
    (temp_dir / ".gitkeep").write_text("")
    
    down_dir = tmp_path / "downloads"
    down_dir.mkdir()
    (down_dir / "movie.mp3").write_text("movie")
    (down_dir / "doc.pdf").write_text("doc") # Should NOT be deleted by downloads logic if we only target audio
    (down_dir / ".gitkeep").write_text("")
    
    FileCleanupService.cleanup_all_temp_files(temp_dir=str(temp_dir), downloads_dir=str(down_dir))
    
    assert not os.path.exists(temp_dir / "junk.mp3")
    assert os.path.exists(temp_dir / ".gitkeep")
    
    assert not os.path.exists(down_dir / "movie.mp3")
    assert os.path.exists(down_dir / "doc.pdf") # Because it's not .mp3/.part etc
    assert os.path.exists(down_dir / ".gitkeep")
