import os
import sys
import subprocess
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_wrapper import GeminiCLIWrapper

@patch('subprocess.run')
def test_run_command_success(mock_run):
    """Test successful command execution."""
    mock_run.return_value = MagicMock(
        stdout='{"response": "test"}', 
        stderr='', 
        returncode=0
    )
    
    result = GeminiCLIWrapper.run_command(["arg1", "arg2"])
    
    mock_run.assert_called_once()
    # Check that 'gemini' is prepended if not in args, or just check the list passed
    args, kwargs = mock_run.call_args
    assert args[0][0] == "gemini"
    assert "arg1" in args[0]
    
    assert result['success'] is True
    assert result['stdout'] == '{"response": "test"}'

@patch('subprocess.run')
def test_run_command_failure(mock_run):
    """Test command failure."""
    mock_run.side_effect = subprocess.CalledProcessError(1, ['gemini'], stderr="error")
    
    result = GeminiCLIWrapper.run_command(["arg1"])
    
    assert result['success'] is False
    assert result['stderr'] == "error"
