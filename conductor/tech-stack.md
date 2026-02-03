# Tech Stack

## Programming Language
- **Python 3.x:** Primary language for orchestration, browser automation, and pipeline management.

## Browser Automation
- **Playwright (Python):** Used for connecting to an existing Chromium instance (port 9222), automating Google AI Studio, and generating PDF files from HTML.

## AI Platform
- **Gemini API:** Utilizing official Google Generative AI API for transcription and note generation.
- **google-genai:** Official Python SDK for the Gemini API (successor to `google-generativeai`).

## Formatting & Conversion
- **Markdown:** Final output format for generated notes.
- **Pandoc:** (Deprecated) Previously used for converting Markdown to HTML.
- **HTML/CSS:** (Deprecated) Previously used for PDF generation.

## Environment
- **Linux:** Target operating system for the CLI tool.

## Key Dependencies
- `google-genai`: Python library for Gemini API interaction.
- `yt-dlp`: For video metadata and audio extraction.
- `pytest`: For automated testing.
