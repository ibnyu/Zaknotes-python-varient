# Tech Stack

## Programming Language
- **Python 3.x:** Primary language for orchestration, browser automation, and pipeline management.

## Browser Automation
- **Playwright (Python):** Used for connecting to an existing Chromium instance (port 9222), automating Google AI Studio, and generating PDF files from HTML.

## AI Platform
- **Google AI Studio:** Specifically utilizing the **Gemini 3 Pro Preview** model for note generation.

## Formatting & Conversion
- **Markdown:** Intermediate format for generated notes.
- **Pandoc:** Used for converting Markdown to HTML.
- **HTML/CSS:** Used as the source for PDF generation, with custom styling from `style.css`.

## Environment
- **Linux:** Target operating system for the CLI tool.

## Key Dependencies (to be managed)
- `playwright`: Python library for browser automation and PDF rendering.
- `pandoc`: System-level tool for document conversion.
