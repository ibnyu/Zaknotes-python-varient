# Track Specification: Duration-Based Audio Chunking, Vidinfra Support & Dynamic Scaling

## Overview
This track refactors the `AudioProcessor` to prioritize duration-based chunking, adds support for `player.vidinfra.com` in the URL finder, and introduces dynamic resource scaling to optimize `ffmpeg` performance based on system capabilities.

## Functional Requirements

### 1. Duration-Based Audio Chunking
- **Refactor `AudioProcessor`**:
    - Remove size-based chunking logic (`size_mb < limit_mb`).
    - **New Logic**: Always prepare audio (silence removal + re-encoding), then chunk ONLY if `duration > segment_time`.
- **Duration Retrieval**: Implement `AudioProcessor.get_duration(file_path)` using `ffprobe`.

### 2. Vidinfra URL Support
- **Update `src/find_vimeo_url.py`**:
    - Add support for detecting and extracting URLs from `player.vidinfra.com` iframes.
    - Maintain existing support for `player.vimeo.com`.

### 3. Dynamic Resource Scaling
- **System Profiling**:
    - On the first run (or if not configured), detect CPU core count and available RAM.
    - Save a `performance_mode` or `thread_limit` to `config.json` (options: `low`, `balanced`, `high`).
- **FFmpeg Optimization**:
    - Use the `-threads` flag in `ffmpeg` commands.
    - `high`: Use all available cores.
    - `low`: Limit to 1-2 cores to prevent system lag.
- **Hybrid Approach**: Default to auto-detected settings but allow manual override in `config.json`.

## Non-Functional Requirements
- **Performance**: Optimize processing speed on high-end systems without compromising stability on low-end hardware.
- **Persistence**: System profiling results must be saved to avoid redundant checks.

## Acceptance Criteria
- Audio chunking triggers correctly based on `segment_time`.
- `vidinfra.com` URLs are successfully extracted.
- `ffmpeg` commands use a variable number of threads based on detected/configured system power.
- `config.json` is updated with a performance setting if it doesn't exist.

## Out of Scope
- Parallel processing of multiple chunks (sticking to single-file threading for now).
