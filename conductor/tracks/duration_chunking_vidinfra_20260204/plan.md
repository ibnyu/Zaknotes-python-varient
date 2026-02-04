# Implementation Plan: Duration-Based Chunking, Vidinfra Support & Dynamic Scaling

This plan outlines the refactoring of the `AudioProcessor` for duration-based chunking, updating the URL finder for Vidinfra support, and implementing dynamic resource scaling for FFmpeg.

## Phase 1: System Profiling and Configuration Update [checkpoint: f608379]
Implement the logic to detect system resources and update `config.json` with a performance profile.

- [x] Task: Implement system resource detection logic in `ConfigManager`. b7f2b94
    - [x] Sub-task: Create a method to detect CPU core count and available RAM.
    - [x] Sub-task: Map detected resources to a performance profile (`low`, `balanced`, `high`).
- [x] Task: Update `ConfigManager` to save the performance profile to `config.json` if it's missing. b7f2b94
    - [x] Sub-task: Ensure it only runs once (on first run or if key is missing).
- [x] Task: Write tests for resource detection and configuration persistence. b7f2b94
- [x] Task: Conductor - User Manual Verification 'Phase 1: System Profiling' (Protocol in workflow.md)

## Phase 2: Refactor AudioProcessor for Duration and Scaling [checkpoint: 738039c]
Update `AudioProcessor` to use `ffprobe` for duration and apply scaling to `ffmpeg` commands.

- [x] Task: Implement `AudioProcessor.get_duration(file_path)` using `ffprobe`. 59eed0c
    - [x] Sub-task: Add a robust wrapper to extract total duration in seconds.
- [x] Task: Modify `AudioProcessor` to accept a `thread_count` or `performance_profile`. 59eed0c
    - [x] Sub-task: Update `reencode_to_optimal`, `remove_silence`, and `split_into_chunks` to use the `-threads` flag.
- [x] Task: Refactor `process_for_transcription` to use duration-based chunking. 59eed0c
    - [x] Sub-task: Remove size-based checks.
    - [x] Sub-task: Implement logic: `Always Prepare -> Check Duration -> Chunk if needed`.
- [x] Task: Write tests for duration retrieval and duration-based chunking logic. 59eed0c
- [x] Task: Conductor - User Manual Verification 'Phase 2: Audio Processor Refactor' (Protocol in workflow.md)

## Phase 3: Update URL Finder for Vidinfra [checkpoint: 840531e]
Update the `find_vimeo_url.py` script to support the new iframe source.

- [x] Task: Update `extract_vimeo_url` in `src/find_vimeo_url.py`. 230cf8f
    - [x] Sub-task: Update the BeautifulSoup search to include `player.vidinfra.com`.
    - [x] Sub-task: Ensure it still supports `player.vimeo.com`.
- [x] Task: Write tests for the updated URL extraction logic using mock HTML content. 230cf8f
- [x] Task: Conductor - User Manual Verification 'Phase 3: Vidinfra Support' (Protocol in workflow.md)

## Phase 4: Integration and Final Verification
Ensure all components work together within the pipeline.

- [ ] Task: Update `Pipeline` (if necessary) to pass configuration settings to `AudioProcessor`.
- [ ] Task: Run end-to-end tests with sample audio and mock URLs.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration' (Protocol in workflow.md)
