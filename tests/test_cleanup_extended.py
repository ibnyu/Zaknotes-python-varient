import os
import shutil
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleanup_service import FileCleanupService

@pytest.fixture
def temp_env(tmp_path):
    temp_dir = tmp_path / "temp"
    downloads_dir = tmp_path / "downloads"
    downloads_temp = downloads_dir / "temp"
    
    temp_dir.mkdir()
    downloads_dir.mkdir()
    downloads_temp.mkdir()
    
    # Create some files
    (temp_dir / "test.txt").write_text("test")
    (temp_dir / ".gitkeep").write_text("")
    
    (downloads_dir / "audio.mp3").write_text("audio")
    (downloads_dir / ".gitkeep").write_text("")
    
    (downloads_temp / "partial.part").write_text("partial")
    (downloads_temp / "nested_dir").mkdir()
    (downloads_temp / "nested_dir" / "junk.txt").write_text("junk")
    (downloads_temp / ".gitkeep").write_text("")
    
    return str(temp_dir), str(downloads_dir)

def test_cleanup_all_temp_files_extended(temp_env):
    temp_dir, downloads_dir = temp_env
    downloads_temp = os.path.join(downloads_dir, "temp")
    
    FileCleanupService.cleanup_all_temp_files(temp_dir, downloads_dir)
    
    # Verify root temp
    assert not os.path.exists(os.path.join(temp_dir, "test.txt"))
    assert os.path.exists(os.path.join(temp_dir, ".gitkeep"))
    
    # Verify downloads root (should delete mp3)
    assert not os.path.exists(os.path.join(downloads_dir, "audio.mp3"))
    assert os.path.exists(os.path.join(downloads_dir, ".gitkeep"))
    
    # Verify downloads/temp (NEW REQUIREMENT)
    assert os.path.exists(downloads_temp)
    assert not os.path.exists(os.path.join(downloads_temp, "partial.part"))
    assert not os.path.exists(os.path.join(downloads_temp, "nested_dir"))
    assert os.path.exists(os.path.join(downloads_temp, ".gitkeep"))
