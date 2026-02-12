import os
import sys
import shutil
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_processor import AudioProcessor

TEST_TEMP_DIR = "test_temp_chunking"

@pytest.fixture
def setup_teardown():
    if not os.path.exists(TEST_TEMP_DIR):
        os.makedirs(TEST_TEMP_DIR)
    yield
    if os.path.exists(TEST_TEMP_DIR):
        shutil.rmtree(TEST_TEMP_DIR)

def create_dummy_file(path, size_mb):
    with open(path, "wb") as f:
        f.write(os.urandom(int(size_mb * 1024 * 1024)))

def test_is_under_limit(setup_teardown):
    small_file = os.path.join(TEST_TEMP_DIR, "small.bin")
    create_dummy_file(small_file, 5)
    assert AudioProcessor.is_under_limit(small_file, 10) is True
    assert AudioProcessor.is_under_limit(small_file, 2) is False

def test_encode_to_base64(setup_teardown):
    test_file = os.path.join(TEST_TEMP_DIR, "test.txt")
    with open(test_file, "w") as f:
        f.write("hello")
    
    encoded = AudioProcessor.encode_to_base64(test_file)
    assert encoded == "aGVsbG8=" # base64 for 'hello'
