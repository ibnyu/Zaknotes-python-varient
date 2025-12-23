import pytest
from unittest.mock import MagicMock, patch, ANY
import os
from bot_engine import AIStudioBot
from pdf_converter_py import PdfConverter

@pytest.fixture
def mock_bot_deps():
    with patch('bot_engine.BrowserDriver') as MockDriver:
        driver_instance = MockDriver.return_value
        mock_page = MagicMock()
        driver_instance.page = mock_page
        yield driver_instance, mock_page

@pytest.fixture
def mock_pdf_deps():
    with patch('pdf_converter_py.sync_playwright') as mock_sync_playwright, \
         patch('subprocess.run') as mock_run:
        
        mock_sync_playwright_cm = MagicMock()
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value = mock_sync_playwright_cm
        mock_sync_playwright_cm.__enter__.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        yield mock_run, mock_page

def test_full_pipeline_integration(mock_bot_deps, mock_pdf_deps, tmp_path):
    driver_instance, bot_page = mock_bot_deps
    mock_run, pdf_page = mock_pdf_deps
    
    # 1. Bot Engine Mocking
    bot = AIStudioBot()
    bot.page = bot_page
    
    m = MagicMock()
    m.is_enabled.return_value = True
    m.count.side_effect = [1, 0, 0, 0, 0, 0]
    m.locator.return_value = m
    m.filter.return_value = m
    m.first = m
    m.last = m
    
    bot_page.locator.return_value = m
    bot_page.get_by_label.return_value = m
    bot_page.get_by_text.return_value = m
    bot_page.evaluate.return_value = "# Integrated Test Content"
    
    audio_path = tmp_path / "test.mp3"
    audio_path.write_text("dummy audio")
    
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()):
        md_text, md_path = bot.generate_notes(str(audio_path))
    
    assert md_text == "# Integrated Test Content"
    
    # 2. PDF Conversion Mocking
    converter = PdfConverter()
    html_path = md_path.replace(".md", ".html")
    pdf_path = md_path.replace(".md", ".pdf")
    
    with patch('os.path.exists', return_value=True):
        converter.convert_md_to_html(md_path, html_path)
        converter.convert_html_to_pdf(html_path, pdf_path)
    
    # Verifications
    mock_run.assert_called_once() # Pandoc called
    pdf_page.goto.assert_called_once() # Playwright called
    pdf_page.pdf.assert_called_once() # PDF generated
