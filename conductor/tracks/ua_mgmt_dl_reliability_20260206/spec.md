# Specification - User-Agent Management & Download Reliability Improvements

## Overview
This track aims to enhance the flexibility and reliability of the note generation pipeline by allowing users to configure a custom browser User-Agent, improving the cleanup process for temporary files, and resolving common download errors (403 Forbidden and HLS stream issues).

## Functional Requirements

### 1. User-Agent Configuration
- **Main Menu Integration:** Add a new option in the `zaknotes.py` main menu to "Configure Browser User-Agent".
- **Persistence:** Store the custom User-Agent string in `config.json` under the key `user_agent`.
- **System-Wide Application:** 
    - Use the configured User-Agent in `src/downloader.py` for all `yt-dlp` commands.
    - Pass and use the configured User-Agent in `src/link_extractor.py` for Playwright browser contexts.
- **Default Value:** If no User-Agent is configured, fall back to a sensible default (e.g., a modern Chrome/Linux UA).

### 2. Enhanced Cleanup Service
- **`downloads/temp` Cleanup:** Update `FileCleanupService.cleanup_all_temp_files` in `src/cleanup_service.py` to recursively clean the `downloads/temp` directory.
- **Preservation:** Ensure the `downloads/temp` directory itself and any `.gitkeep` files are preserved.

### 3. Download Reliability Fixes
- **YouTube 403 Forbidden:** 
    - Modify `src/downloader.py` to reduce or remove the concurrent fragments flag (`-N 16`) specifically for YouTube downloads to mitigate rate-limiting/forbidden errors.
- **HLS Stream Support (EdgeCourseBD/Vimeo):**
    - Update the `yt-dlp` command in `src/downloader.py` for EdgeCourseBD and Vimeo links to include `--downloader ffmpeg --hls-use-mpegts` when HLS streams are detected or as a preventative measure for these domains.

### 4. Documentation
- **Troubleshooting:** Update `README.md` with a "Troubleshooting" section covering:
    - HTTP 403 Forbidden errors (and how the new UA/concurrency changes help).
    - HLS stream issues.
    - General tips for YouTube download failures.

## Non-Functional Requirements
- **Maintainability:** Ensure the User-Agent is centrally managed via `ConfigManager`.
- **User Experience:** Provide clear feedback in the CLI when the User-Agent is updated or when cleanup is performed.

## Acceptance Criteria
- [ ] User can set and view a custom User-Agent from the main menu.
- [ ] `yt-dlp` commands and Playwright sessions use the custom User-Agent.
- [ ] `downloads/temp` is emptied during a manual cleanup.
- [ ] YouTube downloads no longer trigger 403 errors due to high concurrency.
- [ ] EdgeCourseBD/Vimeo HLS streams download successfully using the ffmpeg downloader.
- [ ] `README.md` contains the updated troubleshooting guide.

## Out of Scope
- Automated rotation of User-Agents.
- Support for browser-specific User-Agents (one for Chrome, one for Firefox, etc.).
