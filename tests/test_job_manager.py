import os
import sys
import json
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.job_manager import JobManager, HISTORY_FILE

@pytest.fixture
def job_manager():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    manager = JobManager()
    yield manager
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def test_fail_pending(job_manager):
    """Test marking all pending jobs as failed."""
    job_manager.history = [
        {"id": "1", "status": "queue"},
        {"id": "2", "status": "downloading"},
        {"id": "3", "status": "completed"},
        {"id": "4", "status": "processing"}
    ]
    
    job_manager.fail_pending()
    
    assert job_manager.history[0]["status"] == "failed"
    assert job_manager.history[1]["status"] == "failed"
    assert job_manager.history[2]["status"] == "completed"
    assert job_manager.history[3]["status"] == "failed"
    
    # Check persistence
    with open(HISTORY_FILE, 'r') as f:
        data = json.load(f)
        assert data[0]["status"] == "failed"
