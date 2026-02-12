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

def test_granular_states_retrieval(job_manager):
    """Test that jobs in granular states are correctly retrieved as pending."""
    job_manager.history = [
        {"id": "1", "status": "DOWNLOADED"},
        {"id": "2", "status": "SILENCE_REMOVED"},
        {"id": "3", "status": "BITRATE_MODIFIED"},
        {"id": "4", "status": "CHUNKED"},
        {"id": "5", "status": "TRANSCRIBING_CHUNK_1"},
        {"id": "6", "status": "done"}
    ]
    
    pending = job_manager.get_pending_from_last_150()
    assert len(pending) == 5
    assert all(j["status"] != "done" for j in pending)

def test_failure_state_preservation(job_manager):
    """Test that granular state is preserved when a job fails."""
    job_id = "test_fail"
    job_manager.history = [{"id": job_id, "status": "CHUNKED"}]
    
    # Mark as failed
    job_manager.update_job_status(job_id, "failed")
    
    job = job_manager.get_job(job_id)
    assert job["status"] == "failed"
    assert job["last_granular_state"] == "CHUNKED"

    # Test fail_pending preservation
    job_id_2 = "test_fail_2"
    job_manager.history.append({"id": job_id_2, "status": "TRANSCRIBING_CHUNK_2"})
    job_manager.fail_pending()
    
    job2 = job_manager.get_job(job_id_2)
    assert job2["status"] == "failed"
    assert job2["last_granular_state"] == "TRANSCRIBING_CHUNK_2"
