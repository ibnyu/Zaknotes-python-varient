#!/usr/bin/env python3
"""
Extract media links (Vimeo, YouTube, MediaDelivery) from a webpage using Playwright.
"""

import argparse
import sys
import os
import threading
import queue
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def parse_netscape_cookies(cookie_file_path, target_domain=None):
    """
    Parse Netscape-formatted cookie file and return cookies for Playwright.
    Returns all cookies in the file.
    """
    cookies = []
    
    try:
        with open(cookie_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or (line.startswith('#') and not line.startswith('#HttpOnly_')):
                    continue
                
                # Handle HttpOnly prefix
                if line.startswith('#HttpOnly_'):
                    line = line[len('#HttpOnly_'):]
                
                # Split by tab
                parts = line.split('\t')
                if len(parts) < 7:
                    continue
                
                domain = parts[0]
                domain_flag = parts[1].upper() == 'TRUE'
                path = parts[2]
                secure = parts[3].upper() == 'TRUE'
                expiration = parts[4]
                name = parts[5]
                value = ' '.join(parts[6:])
                
                expires = int(expiration) if expiration.isdigit() else -1
                if expires == 0:
                    expires = -1
                
                final_domain = domain
                if domain_flag:
                    if not final_domain.startswith('.'):
                        final_domain = '.' + final_domain
                else:
                    if final_domain.startswith('.'):
                        final_domain = final_domain.lstrip('.')

                if name.startswith('__Host-'):
                    secure = True
                    path = '/'
                    if final_domain.startswith('.'):
                        final_domain = final_domain.lstrip('.')
                    
                cookie = {
                    'name': name,
                    'value': value,
                    'domain': final_domain,
                    'path': path,
                    'secure': secure,
                    'expires': expires
                }
                cookies.append(cookie)
    
    except FileNotFoundError:
        print(f"ERROR: Cookie file not found: {cookie_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to parse cookie file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return cookies


def select_with_timeout(options, timeout=30):
    """
    Prompt user to select an option with a timeout.
    """
    print(f"\nMultiple links found. Please select one (1-{len(options)}) [Timeout {timeout}s]:", file=sys.stderr)
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}", file=sys.stderr)
    
    res_queue = queue.Queue()

    def get_input():
        try:
            choice = input(f"Select (1-{len(options)}, default 1): ")
            res_queue.put(choice)
        except EOFError:
            res_queue.put("")

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()

    try:
        choice = res_queue.get(timeout=timeout)
        if not choice or not choice.isdigit():
            return options[0]
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
        return options[0]
    except queue.Empty:
        print(f"\nTimeout reached. Defaulting to option 1.", file=sys.stderr)
        return options[0]


def extract_link(url, cookie_file, mode="vimeo"):
    """
    Extract media link based on mode.
    """
    try:
        cookies = parse_netscape_cookies(cookie_file)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            try:
                context.add_cookies(cookies)
            except Exception as e:
                print(f"ERROR: Failed to add cookies: {e}", file=sys.stderr)
                browser.close()
                sys.exit(1)
            
            page = context.new_page()
            print(f"INFO: Navigating to {url}...", file=sys.stderr)
            page.goto(url, wait_until="networkidle")
            
            try:
                page.wait_for_selector("iframe, embed, object", timeout=15000)
            except Exception:
                pass # Continue to scan even if specific selector wait fails
            
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            found_links = set()

            if mode == "vimeo":
                iframes = soup.find_all('iframe')
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if 'player.vimeo.com' in src or 'player.vidinfra.com' in src:
                        found_links.add(src.split('?')[0])
            
            elif mode == "yt":
                # 1. Scan iframes
                for iframe in soup.find_all('iframe'):
                    src = iframe.get('src', '') or iframe.get('data-src', '')
                    if any(domain in src for domain in ['youtube.com', 'youtube-nocookie.com', 'youtu.be']):
                        found_links.add(src.split('?')[0])
                
                # 2. Scan embed/object
                for tag in soup.find_all(['embed', 'object']):
                    src = tag.get('src', '') or tag.get('data', '')
                    if 'youtube' in src:
                        found_links.add(src.split('?')[0])
                
                # 3. Regex scan for IDs in raw content (similar to bookmarklet)
                import re
                id_regex = r'(?:v=|embed\/|vi\/|youtu\.be\/|videoId["\']?\s*[:=]\s*["\'])([a-zA-Z0-9_-]{11})'
                matches = re.findall(id_regex, content)
                for vid_id in matches:
                    found_links.add(f"https://www.youtube.com/watch?v={vid_id}")

            elif mode == "md":
                # Find BunnyCDN / mediadelivery links
                iframes = soup.find_all('iframe')
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if 'mediadelivery.net' in src:
                        found_links.add(src.split('?')[0])

            browser.close()

            if not found_links:
                print(f"ERROR: No links found in mode: {mode}", file=sys.stderr)
                return None

            sorted_links = sorted(list(found_links))
            if len(sorted_links) > 1:
                selected = select_with_timeout(sorted_links)
                return selected if selected else sorted_links[0]
            return sorted_links[0]
            
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description='Generalized Media Link Extractor')
    parser.add_argument('--url', required=True, help='Target webpage URL')
    parser.add_argument('--cookies', required=True, help='Path to Netscape cookie file')
    parser.add_argument('-yt', action='store_true', help='Search for YouTube links')
    parser.add_argument('-md', action='store_true', help='Search for MediaDelivery links')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.cookies):
        print(f"ERROR: Cookie file does not exist: {args.cookies}", file=sys.stderr)
        sys.exit(1)
    
    mode = "vimeo"
    if args.yt: mode = "yt"
    elif args.md: mode = "md"
    
    link = extract_link(args.url, args.cookies, mode=mode)
    
    if link:
        print(link)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()