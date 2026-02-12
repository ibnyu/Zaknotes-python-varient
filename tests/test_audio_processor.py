import os
import sys
import subprocess
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_processor import AudioProcessor

@pytest.fixture
def dummy_file(tmp_path):
    """Creates a 1KB dummy file."""
    p = tmp_path / "test.mp3"
    p.write_bytes(b"\0" * 1024)
    return str(p)

@pytest.fixture
def real_audio_file(tmp_path):
    """Creates a 100-second silent MP3 file."""
    p = tmp_path / "silent.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", 
        "-t", "100", "-b:a", "128k", str(p)
    ], check=True, capture_output=True)
    return str(p)

def test_get_file_size(dummy_file):
    """Test retrieving file size in bytes."""
    size = AudioProcessor.get_file_size(dummy_file)
    assert size == 1024

def test_get_bitrate(real_audio_file):
    """Test retrieving bitrate."""
    # real_audio_file was created with 128k
    bitrate = AudioProcessor.get_bitrate(real_audio_file)
    # ffmpeg might not match exactly 128000 due to encoding, but should be close
    assert 120000 < bitrate < 140000

def test_is_under_limit(dummy_file):
    """Test file size limit validation."""
    # 1KB is under 1MB limit
    assert AudioProcessor.is_under_limit(dummy_file, limit_mb=1) is True
    
    # Create a 2MB file
    large_file = os.path.join(os.path.dirname(dummy_file), "large.mp3")
    with open(large_file, "wb") as f:
        f.write(b"\0" * (2 * 1024 * 1024))
    
    # 2MB is NOT under 1MB limit
    assert AudioProcessor.is_under_limit(large_file, limit_mb=1) is False

def test_reencode_to_optimal(real_audio_file, tmp_path):
    """Test re-encoding audio to optimal bitrate."""
    output_file = str(tmp_path / "optimal.mp3")
    success = AudioProcessor.reencode_to_optimal(real_audio_file, output_file, bitrate="32k")
    assert success is True
    assert os.path.exists(output_file)

def test_remove_silence(real_audio_file, tmp_path):
    """Test removing silence from audio."""
    # Our real_audio_file is pure silence
    output_file = str(tmp_path / "nosilence.mp3")
    success = AudioProcessor.remove_silence(real_audio_file, output_file)
    assert success is True
    assert os.path.exists(output_file)
    # Since it's pure silence, it should be significantly smaller or empty-ish
    assert os.path.getsize(output_file) < os.path.getsize(real_audio_file)

def test_split_by_size(real_audio_file, tmp_path):
    """Test splitting audio by size."""
    output_pattern = str(tmp_path / "chunk_%03d.mp3")
    
    # 5s file at 128k is ~80KB. Let's force split by setting max_size to 0.05MB (~50KB)
    chunks = AudioProcessor.split_by_size(real_audio_file, output_pattern, max_size_mb=0.05)
    
    assert len(chunks) >= 2
    for chunk in chunks:
        assert os.path.exists(chunk)

def test_get_duration(real_audio_file):
    """Test retrieving duration of an audio file."""
    duration = AudioProcessor.get_duration(real_audio_file)
    # real_audio_file was created with -t 100
    assert 99.5 < duration < 100.5

def test_thread_support(real_audio_file, tmp_path):
    """Test that threads parameter is handled in ffmpeg commands."""
    output_file = str(tmp_path / "threaded.mp3")
    # Just verify it doesn't crash when threads=4 is passed
    success = AudioProcessor.reencode_to_optimal(real_audio_file, output_file, bitrate="32k", threads=4)
    assert success is True

def test_size_based_chunking(real_audio_file, tmp_path):
    """Test that chunking is decided based on size."""
    # 5s file @ 128k is ~80KB. 
    # max_size_mb=0.01 (10KB) -> Should definitely split even after re-encoding
    chunks = AudioProcessor.process_for_transcription(
        real_audio_file,
        max_size_mb=0.01,
        output_dir=str(tmp_path)
    )
    assert len(chunks) >= 2

    # max_size_mb=1 (1MB) -> Should NOT split
    chunks = AudioProcessor.process_for_transcription(
        real_audio_file,
        max_size_mb=1,
        output_dir=str(tmp_path)
    )
    assert len(chunks) == 1







def test_reencode_failure(tmp_path):



    """Test handling of re-encoding failure."""



    # Pass a non-existent file



    success = AudioProcessor.reencode_to_optimal("nonexistent.mp3", str(tmp_path / "failed.mp3"))



    assert success is False







def test_remove_silence_failure(tmp_path):



    """Test handling of silence removal failure."""



    # Pass a non-existent file



    success = AudioProcessor.remove_silence("nonexistent.mp3", str(tmp_path / "failed.mp3"))



    assert success is False








