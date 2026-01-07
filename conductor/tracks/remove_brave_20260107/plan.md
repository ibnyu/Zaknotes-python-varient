# Plan: Remove Brave Browser and Standardize on Chromium

## Phase 1: Documentation Cleanup
- [x] Task: Remove Brave references from `conductor/tech-stack.md`
- [x] Task: Remove Brave references from `conductor/product.md`
- [x] Task: Search for and remove Brave references in `README.md` and other root documentation
- [x] Task: Conductor - User Manual Verification 'Documentation Cleanup' (Protocol in workflow.md)

## Phase 2: Browser Driver Refactor
- [x] Task: Create `tests/test_browser_driver.py` with tests for Chromium auto-detection and user prompt fallback (Red Phase)
- [x] Task: Implement `shutil.which` detection logic for 'chromium' and 'chromium-browser' in `src/browser_driver.py`
- [x] Task: Implement interactive CLI prompt fallback in `src/browser_driver.py` when detection fails
- [x] Task: Remove hardcoded Brave paths and specific Brave logic from `src/browser_driver.py`
- [x] Task: Verify that `src/browser_driver.py` correctly uses the existing `browser_profile/` directory
- [ ] Task: Conductor - User Manual Verification 'Browser Driver Refactor' (Protocol in workflow.md)

## Phase 3: Deployment
- [ ] Task: Push all committed changes to the remote repository
- [ ] Task: Conductor - User Manual Verification 'Deployment' (Protocol in workflow.md)
