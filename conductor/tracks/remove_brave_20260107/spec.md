# Specification: Remove Brave Browser and Standardize on Chromium

## Overview
This track aims to remove all references to the Brave browser from the codebase and project documentation, standardizing the application to use Chromium exclusively for all browser-related tasks.

## Functional Requirements
- **Standardize Browser Automation:** Update the browser driver to search for and use Chromium instead of Brave.
- **Automated Detection:** Implement automatic detection of the Chromium executable using the system path (e.g., `shutil.which`).
- **Interactive Fallback:** If auto-detection fails, the application should prompt the user to manually enter the path to the Chromium executable via the CLI.
- **Error Handling:** If no valid Chromium path is provided or found, the application must exit with a clear error message.
- **Profile Persistence:** Continue using the existing `browser_profile/` directory for browser state, ensuring Chromium can access existing session data if possible.

## Documentation Updates
- Update `conductor/tech-stack.md` to reflect the move from Brave to Chromium.
- Update `conductor/product.md` and any `README.md` files to remove mentions of Brave and clarify the requirement for Chromium.

## Non-Functional Requirements
- **TDD Adherence:** Ensure all changes to browser detection and initialization logic are covered by unit tests.
- **Linux Compatibility:** Maintain focus on Linux environments for executable path detection.

## Acceptance Criteria
- [ ] No occurrences of the word "brave" (case-insensitive) remain in the codebase or documentation (except where absolutely unavoidable, e.g., in archival logs).
- [ ] The application successfully launches using the system's Chromium executable.
- [ ] The application correctly prompts for a path if Chromium is not in the system PATH.
- [ ] `tech-stack.md`, `product.md`, and `README.md` are updated.
- [ ] All tests pass.

## Out of Scope
- Migrating profile data to a different directory structure.
- Supporting browsers other than Chromium (e.g., Firefox).
