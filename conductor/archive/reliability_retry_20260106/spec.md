# Specification: Enhanced Reliability and Job Retry Logic

## Overview
This track aims to resolve several reliability issues in the `zaknotes` automation engine. Key focus areas include validating AI response completion to prevent empty PDFs, fixing the root cause of UI selection stalls (with a backup retry mechanism), and updating job management to automatically retry failed tasks.

## Functional Requirements

### 1. AI Response Validation (Anti-Empty PDF)
- **Upload Delay:** Introduce a mandatory 2-second sleep after file upload completion before clicking the "Run" button.
- **Response Block Detection:** The script must verify the existence of the AI response block even if the "Run" button is visible.
- **Growth Monitoring Loop:** 
    - After the response block appears, enter a loop that waits 1 second and checks the content length.
    - The loop continues as long as the content length is increasing.
    - **Inactivity Timeout:** If the content length does not change for 15 seconds, the response is considered complete (or stalled) and the script proceeds to copy.

### 2. UI Interaction Stability
- **Root Cause Analysis & Fix:** 
    - Investigate the `src/ui_elements/` definitions and `bot_engine.py` logic to determine why Model/System Instruction selection hangs.
    - Implement a direct fix for the interaction (e.g., improved selectors, explicit wait conditions, handling dynamic UI states).
- **Fallback Retry Logic:** 
    - If the interaction still fails after the fix (timeout reached), implement a catch-all recovery:
    - Close the current browser instance.
    - Restart a fresh browser session for that specific job attempt.

### 3. Job Management Updates
- **Retry Logic:** Update the `JobManager` to include jobs with a `failed` status in the processing queue.
- **Pending Definition:** Redefine "pending" in the context of the Job Menu to include both `pending` and `failed` jobs.
- **Exclusion:** Jobs with a `cancelled` status must remain excluded from automated processing.

## Acceptance Criteria
- [ ] No empty PDFs are generated for successfully processed files.
- [ ] The script waits for the AI response to stabilize before copying content.
- [ ] The root cause of the Model/System selection hang is identified and fixed.
- [ ] A backup retry (browser restart) occurs if the selection still fails.
- [ ] Running "Start Processing" on old jobs correctly picks up both `pending` and `failed` tasks.
- [ ] `cancelled` jobs are correctly ignored by the processing logic.

## Out of Scope
- Modifications to the PDF styling or Pandoc conversion logic.
- Changes to the Gemini model prompts or system instructions themselves.
