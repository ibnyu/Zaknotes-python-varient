import os
import json
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager

TEST_CONFIG_FILE = "test_config.json"

@pytest.fixture
def config_manager():
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)
    manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    yield manager
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)

def test_load_defaults(config_manager):
    """Test that defaults are loaded when config file does not exist."""
    assert config_manager.get("transcription_model") == "gemini-2.5-flash"
    assert config_manager.get("note_generation_model") == "gemini-3-pro-preview"

def test_save_and_load(config_manager):
    """Test saving and reloading configuration."""
    config_manager.set("transcription_model", "test-model")
    config_manager.save()
    
    # Reload with a new instance
    new_manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    assert new_manager.get("transcription_model") == "test-model"

def test_get_nonexistent_key(config_manager):
    """Test retrieving nonexistent keys with and without defaults."""
    assert config_manager.get("nonexistent") is None
    assert config_manager.get("nonexistent", "default") == "default"

def test_detect_system_resources(config_manager):
    """Test detection of CPU and RAM."""
    # This might vary by environment, but should return positive numbers on linux
    cores, ram_gb = config_manager.detect_system_resources()
    assert cores > 0
    assert ram_gb > 0

def test_map_resources_to_profile(config_manager):
    """Test mapping resources to performance profiles."""
    # Low end
    assert config_manager.map_resources_to_profile(1, 1) == "low"
    assert config_manager.map_resources_to_profile(2, 3) == "low"
    
    # Balanced
    assert config_manager.map_resources_to_profile(4, 8) == "balanced"
    assert config_manager.map_resources_to_profile(2, 8) == "balanced"
    
    # High end
    assert config_manager.map_resources_to_profile(8, 16) == "high"
    assert config_manager.map_resources_to_profile(16, 8) == "high"

def test_auto_profile_assignment(config_manager):
    """Test that performance_profile is automatically assigned if missing."""
    # performance_profile should be set during init if not in file
    profile = config_manager.get("performance_profile")
    assert profile in ["low", "balanced", "high"]
    
    # Verify it persists
    config_manager.save()
    with open(TEST_CONFIG_FILE, 'r') as f:
        data = json.load(f)
        assert "performance_profile" in data
