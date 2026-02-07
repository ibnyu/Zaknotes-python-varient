# Specification: Enhanced Job Resilience, State Tracking, and Cleanup

## Overview
This track aims to improve the reliability and granularity of the job processing pipeline. By introducing intermediate job states and persistent progress tracking, the system will be able to resume interrupted jobs from the exact point of failure. Additionally, it improves API quota management accuracy and provides more control over workspace cleanup.

## Functional Requirements

### 1. Granular State Tracking & Resumption
- **Persistent States:** Track and save the following states in the job history:
    - `DOWNLOADED`: Media successfully fetched.
    - `SILENCE_REMOVED`: Audio processing (silence removal) complete.
    - `BITRATE_MODIFIED`: Audio conversion/normalization complete.
    - `CHUNKED`: Audio split into segments.
    - `TRANSCRIBING_CHUNK_N`: Progress tracking for individual audio chunks.
- **Resumption Logic:** 
    - On startup, the system must detect partially completed jobs.
    - If a job is resumed, it must skip already completed steps (e.g., if `CHUNKED`, go straight to transcription).
    - If interrupted during transcription, it must resume from the first non-transcribed chunk while keeping existing transcripts intact.

### 2. Universal Gemini API Debug Logging
- Add extensive `DEBUG` level logs for **all** Gemini API interactions (Transcription and Note Generation).
- Logs must include:
    - Request parameters (excluding API keys).
    - Request type (Transcription vs. Note Gen).
    - **Truncated Responses:** The `text` content of transcriptions and notes in the logs must be truncated (e.g., first 100 characters) to keep logs readable while confirming data receipt.
    - Timing data and raw API response status.

### 3. API Quota Management
- **Proactive Counting:** Increment the API request counter *before* making the network request.
- **Fail-Safe:** Failed requests remain counted (aligning with Google API billing/quota behavior).

### 4. Interactive Cleanup Sub-options
When the cleanup/purge process is triggered, present the user with two choices:
1. **Purge Everything:** Remove all temporary files and downloads for all jobs (current behavior).
2. **Purge Completed/Cancelled Only:** Remove files only for jobs that are no longer active (Done/Cancelled), preserving files for "Pending" or "In Progress" jobs.

## Non-Functional Requirements
- **Data Integrity:** Ensure the `job_manager` safely writes state updates to disk to prevent corruption during unexpected shutdowns.
- **Minimal Redundancy:** Resumption logic must strictly avoid re-downloading or re-processing files that are already present and valid.

## Acceptance Criteria
- [ ] A job interrupted after downloading does not re-download on the next run.
- [ ] A job interrupted during chunk 3 of transcription resumes at chunk 3 on the next run.
- [ ] The API counter increments immediately before any `genai` call.
- [ ] Cleanup menu correctly purges either "All" or "Completed/Cancelled Only".
- [ ] Debug logs show truncated responses for both transcriptions and final notes.

## Out of Scope
- Implementing a full TUI for job management.
