# Product Guidelines

## Visual & Interaction Style
-   **Phase 1 (Development):** Focus on clear, debug-oriented output.
-   **Phase 2 (Production):** Transition to a **Minimalist & Clean** style, focusing on clear text output with minimal distraction for CLI efficiency.

## Communication & Messaging
-   **Current Approach:** **Debug-Oriented**. Show technical details in the output (e.g., "Connected to Chromium on port 9222", "DOM injection successful").
-   **Goal:** Once complete, switch to a **Functional & Direct** approach, using clear, concise status updates without fluff.

## Error Handling
-   **Verbose Error Reporting:** Display full tracebacks and error details to the user to assist with debugging during the development and implementation of Phase 3 and 4.

## Content & Formatting
-   **Markdown Style:** The Markdown format is pre-defined by the system instructions and user-provided templates. The engine must preserve this formatting during extraction and conversion.

## Architectural Principles
-   **Modular Architecture:** The core logic should be encapsulated in separate, independent modules (e.g., for browser control, PDF conversion) to facilitate reuse and future expansion to a TUI or other interfaces.
