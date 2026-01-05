import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

class TestCLIMenu(unittest.TestCase):
    @patch('zaknotes.BrowserDriver')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_launch_browser_option(self, mock_print, mock_input, mock_driver_class):
        # We need to import zaknotes here so the patches apply
        import zaknotes
        
        # Mock inputs: '4' to launch browser, then 'Enter' to return, then '5' to exit
        mock_input.side_effect = ['4', '', '5']
        
        # Mock driver instance
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver
        
        # Run main_menu
        try:
            zaknotes.main_menu()
        except SystemExit:
            pass
        
        # Verify launch_browser was called
        mock_driver.launch_browser.assert_called_once()
        
        # Verify it printed something about launching
        # (We can check if any print call contains "Launching Browser" or similar)
        # But assert_called_once is already good proof of routing.

if __name__ == '__main__':
    unittest.main()
