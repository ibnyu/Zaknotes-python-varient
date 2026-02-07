# Implementation Plan: Enhanced Job Resilience, State Tracking, and Cleanup

## Phase 1: API Quota & Debug Logging Enhancements
Goal: Improve transparency and accuracy of API usage and responses.

- [x] Task: Update `APIKeyManager` to increment quota proactively before requests. fecca61
- [x] Task: Enhance `GeminiAPIWrapper` with extensive debug logging and truncated response output. fecca61
- [ ] Task: Conductor - User Manual Verification 'Phase 1: API Quota & Debug Logging' (Protocol in workflow.md)

## Phase 2: Granular State Tracking
Goal: Implement persistent intermediate states in the job management system.

- [ ] Task: Update `JobManager` state definitions to include intermediate processing steps (DOWNLOADED, CHUNKED, etc.).
- [ ] Task: Implement per-chunk transcription state tracking in `JobManager`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Granular State Tracking' (Protocol in workflow.md)

## Phase 3: Pipeline Resumption Logic
Goal: Modify the main pipeline to utilize new states for resuming interrupted jobs.

- [ ] Task: Refactor `Pipeline` to check for existing state/files and skip completed steps.
- [ ] Task: Implement transcription resumption logic (skip already transcribed chunks).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Pipeline Resumption Logic' (Protocol in workflow.md)

## Phase 4: Interactive Cleanup
Goal: Provide users with granular control over workspace cleanup.

- [ ] Task: Update `CleanupService` to support filtered purging (All vs. Completed/Cancelled Only).
- [ ] Task: Update CLI in `zaknotes.py` to present interactive cleanup options.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Interactive Cleanup' (Protocol in workflow.md)
