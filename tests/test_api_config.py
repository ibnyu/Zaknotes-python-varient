import os
import sys
import json
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager

def test_default_config_includes_api_settings():
    """Verify that DEFAULT_CONFIG includes the new API reliability settings."""
    assert "api_timeout" in ConfigManager.DEFAULT_CONFIG
    assert ConfigManager.DEFAULT_CONFIG["api_timeout"] == 300
    assert "api_max_retries" in ConfigManager.DEFAULT_CONFIG
    assert ConfigManager.DEFAULT_CONFIG["api_max_retries"] == 3
    assert "api_retry_delay" in ConfigManager.DEFAULT_CONFIG
    assert ConfigManager.DEFAULT_CONFIG["api_retry_delay"] == 10

def test_config_manager_loads_defaults(tmp_path):
    """Verify that ConfigManager loads defaults if keys are missing from file."""
    config_file = tmp_path / "config.json"
    # Create a config file with only some keys
    with open(config_file, 'w') as f:
        json.dump({"transcription_model": "test-model"}, f)
    
    manager = ConfigManager(config_file=str(config_file))
    assert manager.get("api_timeout") == 300
    assert manager.get("api_max_retries") == 3
    assert manager.get("api_retry_delay") == 10
    assert manager.get("transcription_model") == "test-model"

def test_config_manager_saves_missing_defaults(tmp_path):
    """Verify that ConfigManager saves default values to file if they were missing."""
    config_file = tmp_path / "config.json"
    # Create empty config
    with open(config_file, 'w') as f:
        json.dump({}, f)
    
    manager = ConfigManager(config_file=str(config_file))
    # Forces a save by setting something or just check if it was auto-saved 
    # (The constructor saves if performance_profile is missing)
    
    with open(config_file, 'r') as f:
        saved_config = json.load(f)
    
    assert "api_timeout" in saved_config
    assert saved_config["api_timeout"] == 300

