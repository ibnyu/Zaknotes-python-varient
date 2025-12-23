# Specification: Refactor Bot Engine & PDF Conversion

## 1. Introduction
This track focuses on migrating the "Class-to-Notes" project to a cleaner, more robust architecture. The primary goals are repository cleanup, fixing critical stability issues in the Google AI Studio automation (`bot_engine.py`), and replacing the legacy Node.js/Puppeteer PDF conversion with a native Python implementation using Playwright.

## 2. Technical Goals
- **Repository Cleanup:** Remove all prototype and legacy files that are no longer needed.
- **Robust Selectors:** Transition all browser interactions in `bot_engine.py` to use selectors derived from the provided `ui_elements/` HTML snapshots.
- **Stable File Upload:** Resolve hangs during file upload by using direct DOM injection into the hidden `<input type="file">`.
- **Clean Content Extraction:** Ensure only the final model response is extracted (excluding reasoning blocks) by utilizing the "Copy as Markdown" feature in the AI Studio UI.
- **Python-Native PDF Conversion:** Implement a Python-based pipeline (Pandoc + Playwright Python) to convert Markdown to PDF, deprecating the Node.js dependency.

## 3. Detailed Requirements

### 3.1 Cleanup
- **Delete Files:** `find_input.py`, `manual_test.py`, `macro_rec.py`, `ui_inspector.py`, `browser_launcher.py`, `test_*.py`, `pdf_converter/pdf.js`.
- **Preserve/Refactor:** `bot_engine.py`, `browser_driver.py`, `downloader.py`, `find_vimeo_url.py`, `job_manager.py`, `cookie_manager.py`, `ui_elements/`, `pdf_converter/style.css`.

### 3.2 Bot Engine Refactoring (`bot_engine.py`)
- **Connection:** Reliably connect to Chromium on port 9222 with the existing profile.
- **Navigation:** Fresh session via `https://aistudio.google.com/prompts/new_chat`.
- **Model Selection:** Use `ui_elements/` to select "Gemini 3 Pro Preview".
- **System Instructions:** Use `ui_elements/` to select "note generator".
- **File Upload:** 
    - Click "+" button to render menu.
    - Target hidden input (via selector from `ui_elements/`).
    - Inject file path directly using Playwright's `set_input_files`.
- **Generation & Extraction:**
    - Wait for "Run" button to finish (or stop button to vanish).
    - Locate the final response container.
    - Open "More options" menu and click "Copy as Markdown".
    - Save extracted Markdown to `temp/[filename].md`.

### 3.3 PDF Conversion Pipeline
- **Markdown to HTML:** Use `pandoc` (via Python `subprocess`) to convert `.md` to `.html`.
- **HTML to PDF:** 
    - Load the `.html` file into a headless Playwright browser.
    - Inject `pdf_converter/style.css`.
    - Generate PDF using `page.pdf()`.

## 4. Success Criteria
- Clean repository with only active files.
- `bot_engine.py` successfully uploads and extracts content without timing out or capturing "thinking" blocks.
- PDF conversion works end-to-end in Python, producing correctly styled documents with Bangla font support.
- All new/refactored logic is covered by unit tests (>80% coverage).
