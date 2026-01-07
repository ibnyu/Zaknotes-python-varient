# Specification: Enhanced Job Management and Browser Control

## Overview
This track refactors the CLI interaction in `zaknotes.py` to provide granular control over job processing and adds a utility to launch the automated browser manually for inspection or manual tasks. It also ensures the underlying `JobManager` logic supports these new workflows.

## Functional Requirements

### 1. Main Menu Refactoring (`zaknotes.py`)
- **Add Option 4: "Launch Browser"**:
  - Launches the Chromium instance using the existing `browser_profile`.
  - Runs in "headful" mode (visible UI).
  - The CLI should wait (e.g., "Press Enter to close browser...") so the session remains active until the user is done.
- **Shift "Exit" to Option 5**.

### 2. Job Sub-Menu (Refactored Option 1)
When the user selects "Start Note Generation", they should be presented with a sub-menu:
1. **Start New Jobs (Cancel Pending)**:
   - Cancels all currently "queue" status jobs in `history.json`.
   - Prompts for new "File Names" and "URLs".
   - Adds new jobs and starts the processing pipeline.
2. **Start New Jobs (Include Pending)**:
   - Prompts for new "File Names" and "URLs".
   - Adds new jobs.
   - Starts the processing pipeline for *all* pending jobs (new + old).
3. **Cancel Old Pending Jobs**:
   - Updates the status of all "queue" jobs to "cancelled" in `history.json`.
   - Returns to the main menu.
4. **Start Old Pending Jobs**:
   - Starts the processing pipeline for existing "queue" jobs without adding new ones.

### 3. `JobManager` Logic Enhancements (`src/job_manager.py`)
- Verify and implement `cancel_pending()`: Ensure it correctly marks all "queue" jobs as "cancelled".
- Ensure `get_pending_from_last_150()` (or a new method) accurately returns all jobs currently waiting to be processed.
- Ensure `history.json` is updated atomically to prevent state corruption.

## Acceptance Criteria
- Selecting "Launch Browser" opens Chromium and keeps it open until user interaction in the terminal.
- Sub-menu options correctly filter and process jobs as described.
- `history.json` accurately reflects status changes (queue -> cancelled or queue -> processing/completed).
- All local commits are pushed to the remote repository upon completion.

## Out of Scope
- Implementing a full TUI (Terminal User Interface).
- Changing the AI note generation prompt or logic.
