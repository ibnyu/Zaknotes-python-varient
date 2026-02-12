import os
import json
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.usage_tracker import UsageTracker

TEST_USAGE_FILE = "test_usage_stats.json"

@pytest.fixture
def usage_tracker():
    if os.path.exists(TEST_USAGE_FILE):
        os.remove(TEST_USAGE_FILE)
    tracker = UsageTracker(usage_file=TEST_USAGE_FILE)
    yield tracker
    if os.path.exists(TEST_USAGE_FILE):
        os.remove(TEST_USAGE_FILE)

def test_record_usage(usage_tracker):
    usage_tracker.record_usage("user@example.com", "gemini-2.0-flash")
    usage_tracker.record_usage("user@example.com", "gemini-2.0-flash")
    usage_tracker.record_usage("user@example.com", "gemini-3-flash-preview")
    usage_tracker.record_usage("other@example.com", "gemini-2.0-flash")

    stats = usage_tracker.get_usage_report()
    
    assert stats["user@example.com"]["gemini-2.0-flash"] == 2
    assert stats["user@example.com"]["gemini-3-flash-preview"] == 1
    assert stats["other@example.com"]["gemini-2.0-flash"] == 1

def test_persistence(usage_tracker):
    usage_tracker.record_usage("user@example.com", "gemini-2.0-flash")
    
    # New instance loading from same file
    new_tracker = UsageTracker(usage_file=TEST_USAGE_FILE)
    assert new_tracker.get_usage_report()["user@example.com"]["gemini-2.0-flash"] == 1
