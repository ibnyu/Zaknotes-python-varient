# Implementation Plan: Generalized Media Link Extraction and Downloader Enhancement

## Phase 1: Link Extractor Generalization (TDD)
- [x] Task: Rename `src/find_vimeo_url.py` to `src/link_extractor.py` and update imports. e469cd1
- [x] Task: Write tests for `link_extractor.py` covering Vimeo/Vidinfra extraction. d3c32e9
- [x] Task: Implement interactive selection with timeout in `link_extractor.py`. d3c32e9
- [x] Task: Generalize cookie loading in `link_extractor.py` to load all cookies without domain filtering. d3c32e9
- [x] Task: Conductor - User Manual Verification 'Phase 1: Link Extractor Generalization' (Protocol in workflow.md) d3c32e9
- [x] Task: Remove -yt and -md logic and tests from Phase 1. 65114de

## Phase 2: Downloader Refactor and Enhancement (TDD)
- [x] Task: Update `JobManager` in `src/job_manager.py` to support `no_link_found` status and filter it out. b845503
- [x] Task: Write tests for `src/downloader.py` covering new `match/case` structure and specialized rules. d10a2c4
- [x] Task: Refactor `download_audio` in `src/downloader.py` to use `match/case`. d10a2c4
- [x] Task: Implement MediaDelivery rule (`mediadelivery.net`) with specialized headers. d10a2c4
- [x] Task: Implement fallback rule with direct download attempt and `no_link_found` handling. d10a2c4
- [x] Task: Ensure all `yt-dlp` calls use `cookies/bangi.txt` (or appropriate cookie path). d10a2c4
- [x] Task: Conductor - User Manual Verification 'Phase 2: Downloader Refactor and Enhancement' (Protocol in workflow.md) d10a2c4

## Phase 3: Cleanup and Finalization
- [~] Task: Delete `bookmarlet-apar.js` and `bookmarlet-youtube.js`.
- [ ] Task: Perform final verification of the entire pipeline.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Cleanup and Finalization' (Protocol in workflow.md)
