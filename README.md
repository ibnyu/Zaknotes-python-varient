# Zaknotes (Python Variant)

Automated class-to-notes engine using Gemini API.

## Prerequisites

Before running Zaknotes, ensure you have the following system-level tools installed:

1.  **Python 3.13+**
2.  **uv** (recommended for dependency management): `curl -LsSf https://astral.sh/uv/install.sh | sh`
3.  **ffmpeg**: Required for audio processing and extraction.
    -   Linux: `sudo apt install ffmpeg` (or your distro's equivalent)
4.  **Node.js**: Required by `yt-dlp-ejs` to solve YouTube's "n challenge".
    -   Ensure `node` is available in your PATH.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ShoyebOP/Zaknotes-python-varient.git
    cd Zaknotes-python-varient
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Configure API Keys:**
    -   Run the application: `uv run python zaknotes.py`
    -   Select **Option 2: Manage API Keys**
    -   Add one or more Google Gemini API keys.

## Usage

1.  **Start Note Generation:**
    -   Run `uv run python zaknotes.py`
    -   Select **Option 1: Start Note Generation**
    -   Follow the prompts to provide video names and URLs.

2.  **Configure Audio Chunking:**
    -   If you have very long videos or want to adjust processing chunks, use **Option 3: Configure Audio Chunking**. The default is 1800s (30 minutes).

## Output

Generated notes are saved as Markdown files in the `notes/` directory.

## Testing

Run the test suite using pytest:
```bash
uv run pytest
```
