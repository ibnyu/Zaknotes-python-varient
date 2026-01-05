import sys
import os
from unittest.mock import patch, MagicMock

# Add root to sys.path
sys.path.append(os.getcwd())

def test_zaknotes_exists():
    assert os.path.exists("zaknotes.py")

def test_menu_structure():
    # This is a bit of a placeholder since we haven't written the code yet
    # but it will fail if zaknotes.py is missing or doesn't have the expected content
    with open("zaknotes.py", "r") as f:
        content = f.read()
    assert "input" in content
    assert "while" in content
    assert "1" in content
    assert "2" in content
    assert "3" in content
