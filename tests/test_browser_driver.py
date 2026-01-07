import pytest
from unittest.mock import MagicMock, patch
import os
from src.browser_driver import BrowserDriver

@pytest.fixture
def driver():
    return BrowserDriver()

def test_chromium_detection_success(driver):
    """Test that it finds Chromium when it exists in the path."""
    with patch('shutil.which', side_effect=lambda x: f"/usr/bin/{x}" if x == "chromium" else None), \
         patch('os.path.exists', return_value=True):
        
        # We need to mock Popen to avoid actually launching a browser
        with patch('subprocess.Popen') as mock_popen, \
             patch.object(BrowserDriver, 'verify_correct_profile', return_value=None), \
             patch.object(BrowserDriver, 'is_port_open', side_effect=[False, True]), \
             patch.object(BrowserDriver, 'verify_correct_profile', side_effect=[None, True]), \
             patch('time.sleep'):
            
            driver.launch_browser()
            
            # Verify it used the chromium path
            args, _ = mock_popen.call_args
            assert "/usr/bin/chromium" in args[0]

def test_chromium_detection_fallback_to_manual_input(driver):
    """Test that it prompts for input when auto-detection fails."""
    with patch('shutil.which', return_value=None), \
         patch('builtins.input', return_value="/custom/path/chromium"), \
         patch('os.path.exists', return_value=True), \
         patch('subprocess.Popen') as mock_popen, \
         patch.object(BrowserDriver, 'verify_correct_profile', return_value=None), \
         patch.object(BrowserDriver, 'is_port_open', side_effect=[False, True]), \
         patch.object(BrowserDriver, 'verify_correct_profile', side_effect=[None, True]), \
         patch('time.sleep'):
        
        driver.launch_browser()
        
        # Verify it used the manually entered path
        args, _ = mock_popen.call_args
        assert "/custom/path/chromium" in args[0]

def test_no_chromium_found_raises_exception(driver):
    """Test that it raises an exception if no Chromium is found and user provides invalid path."""
    with patch('shutil.which', return_value=None), \
         patch('builtins.input', return_value="/invalid/path"), \
         patch('os.path.exists', return_value=False), \
         patch.object(BrowserDriver, 'verify_correct_profile', return_value=None):
        
        with pytest.raises(Exception, match="❌ Could not find Chromium executable"):
            driver.launch_browser()

