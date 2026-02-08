# Specification: System Instruction Integration & Transcription Refinement

## Overview
This track involves two main changes to how the Class-to-Notes Engine interacts with the Gemini API:
1.  **Refactoring Prompt Delivery:** Moving the `NOTE_GENERATION_PROMPT` and `TRANSCRIPTION_PROMPT` from the user message to the `system_instruction` parameter of the Gemini API.
2.  **Refining Transcription Logic:** Updating the transcription prompt to enforce "Clean Verbatim" and strictly preserve the language of the spoken content, specifically handling Bangla-English code-switching (e.g., English terms transcribed in English characters).

## Functional Requirements

### 1. API Interaction Refactor
-   Modify `src/gemini_api_wrapper.py` to use the `system_instruction` parameter in `models.generate_content`.
-   The user message should now only contain the content to be processed (the transcription for note generation, or the audio file for transcription).

### 2. Transcription Prompt Update
-   Update `TRANSCRIPTION_PROMPT` in `src/prompts.py` with the following rules:
    -   **Persona:** Act as a high-fidelity transcription agent.
    -   **Clean Verbatim:** Remove filler words (ums, ahs, you knows, etc.) but keep all academic content.
    -   **Language Preservation:** 
        -   Transcribe the audio in its original language.
        -   If multiple languages are spoken (e.g., Bangla and English), transcribe each part in its respective language (do not translate or transliterate English terms into Bangla script).
    -   **Strict Output:** Output ONLY the transcript text. No greetings, explanations, or meta-commentary.

### 3. Note Generation Prompt Integration
-   Ensure `NOTE_GENERATION_PROMPT` is also passed as a `system_instruction`.

## Non-Functional Requirements
-   **Reliability:** Ensure that moving to `system_instruction` does not negatively impact the quality or stability of the output.
-   **Maintainability:** The refactor should make the API interaction code cleaner and more aligned with official Gemini API best practices.

## Acceptance Criteria
-   Transcription jobs use the updated `TRANSCRIPTION_PROMPT` via `system_instruction`.
-   Transcription output is "Clean Verbatim" and preserves mixed-language content (Bangla/English).
-   Note generation jobs use `NOTE_GENERATION_PROMPT` via `system_instruction`.
-   All existing tests in `tests/test_gemini_api_wrapper.py` and other relevant test files are updated and passing.
-   The CLI continues to function as expected for the end user.

## Out of Scope
-   Changes to the actual content/logic of the `NOTE_GENERATION_PROMPT` (only its delivery method is changing).
-   Implementation of new TUI features.
