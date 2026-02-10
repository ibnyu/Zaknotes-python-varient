import os
import json
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager

TEST_CONFIG_FILE = "test_config_notion.json"

@pytest.fixture
def config_manager():
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)
    manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    yield manager
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)

def test_notion_integration_default_false(config_manager):
    """Test that notion_integration_enabled defaults to False."""
    assert config_manager.get("notion_integration_enabled") is False

def test_notion_keys_structure():
    """Test that notion_keys.json exists and has the correct keys."""
    notion_keys_path = os.path.join("keys", "notion_keys.json")
    assert os.path.exists(notion_keys_path)
    with open(notion_keys_path, 'r') as f:
        data = json.load(f)
        assert "NOTION_SECRET" in data
        assert "DATABASE_ID" in data
