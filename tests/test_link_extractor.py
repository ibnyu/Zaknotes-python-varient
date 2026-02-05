import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.link_extractor import extract_link, parse_netscape_cookies

@pytest.fixture
def mock_cookie_file(tmp_path):
    cookie_content = (
        "example.com\tTRUE\t/\tFALSE\t2147483647\ttest_name\ttest_value\n"
        "example.com\tFALSE\t/\tTRUE\t2147483647\t__Host-test\thost_val\n"
        "another.com\tTRUE\t/\tFALSE\t2147483647\tanother_name\tanother_value\n"
    )
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text(cookie_content)
    return str(cookie_file)

def test_parse_netscape_cookies(mock_cookie_file):
    # Should now return ALL cookies regardless of domain argument (which might be removed or ignored)
    cookies = parse_netscape_cookies(mock_cookie_file, "example.com")
    assert len(cookies) == 3
    
    # Check standard cookie
    c1 = next(c for c in cookies if c['name'] == 'test_name')
    assert c1['domain'] == '.example.com'
    
    # Check __Host- cookie
    c2 = next(c for c in cookies if c['name'] == '__Host-test')
    assert c2['domain'] == 'example.com'
    assert c2['secure'] is True
    
    # Check another domain cookie
    c3 = next(c for c in cookies if c['name'] == 'another_name')
    assert c3['domain'] == '.another.com'

@patch('src.link_extractor.sync_playwright')
def test_extract_vimeo_url_success(mock_playwright, mock_cookie_file):
    # Setup mock playwright
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    mock_page.content.return_value = '<html><body><iframe src="https://player.vimeo.com/video/12345"></iframe></body></html>'
    
    url = "https://example.com/video"
    result = extract_link(url, mock_cookie_file)
    
    assert result == "https://player.vimeo.com/video/12345"
    mock_browser.close.assert_called_once()

@patch('src.link_extractor.sync_playwright')
def test_extract_youtube_url_success(mock_playwright, mock_cookie_file):
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    yt_url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
    mock_page.content.return_value = f'<html><body><iframe src="{yt_url}"></iframe></body></html>'
    
    url = "https://example.com/video"
    # Testing -yt flag behavior
    result = extract_link(url, mock_cookie_file, mode="yt")
    
    assert result == yt_url

@patch('src.link_extractor.sync_playwright')
def test_extract_mediadelivery_url_success(mock_playwright, mock_cookie_file):
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    md_url = "https://iframe.mediadelivery.net/embed/123/456?autoplay=true"
    mock_page.content.return_value = f'<html><body><iframe src="{md_url}"></iframe></body></html>'
    
    url = "https://example.com/video"
    # Testing -md flag behavior
    result = extract_link(url, mock_cookie_file, mode="md")
    
    assert result == "https://iframe.mediadelivery.net/embed/123/456" # Cleaned URL

@patch('src.link_extractor.sync_playwright')
@patch('builtins.input', return_value='2')
def test_extract_multiple_links_selection(mock_input, mock_playwright, mock_cookie_file):
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    yt_url1 = "https://www.youtube.com/embed/ID1"
    yt_url2 = "https://www.youtube.com/embed/ID2"
    mock_page.content.return_value = f'<html><body><iframe src="{yt_url1}"></iframe><iframe src="{yt_url2}"></iframe></body></html>'
    
    url = "https://example.com/video"
    result = extract_link(url, mock_cookie_file, mode="yt")
    
    assert result == yt_url2
    mock_input.assert_called()

@patch('src.link_extractor.sync_playwright')
@patch('src.link_extractor.select_with_timeout', return_value=None)
def test_extract_multiple_links_timeout(mock_timeout, mock_playwright, mock_cookie_file):
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    yt_url1 = "https://www.youtube.com/embed/ID1"
    yt_url2 = "https://www.youtube.com/embed/ID2"
    mock_page.content.return_value = f'<html><body><iframe src="{yt_url1}"></iframe><iframe src="{yt_url2}"></iframe></body></html>'
    
    url = "https://example.com/video"
    result = extract_link(url, mock_cookie_file, mode="yt")
    
    assert result == yt_url1 # Defaults to first