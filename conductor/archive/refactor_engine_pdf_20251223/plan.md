# Plan: Refactor Bot Engine & PDF Conversion

## Phase 1: Repository Cleanup & Setup [checkpoint: 7835346]
- [x] Task: Cleanup obsolete files and artifacts [199dfd5]
- [x] Task: Initialize testing environment (pytest) and update dependencies [e23c920]
- [x] Task: Conductor - User Manual Verification 'Cleanup & Setup' (Protocol in workflow.md) [7835346]

## Phase 2: Bot Engine - Foundation & Selection [checkpoint: 1bac4af]
- [x] Task: Write Tests: Browser connection and model/instruction selection [98b02ec]
- [x] Task: Refactor `browser_driver.py` and `bot_engine.py` for reliable connection and fresh chat navigation [98b02ec]
- [x] Task: Implement model and system instruction selection using `ui_elements/` selectors [98b02ec]
- [x] Task: Conductor - User Manual Verification 'Bot Engine Foundation' (Protocol in workflow.md) [1bac4af]

## Phase 3: Bot Engine - Upload & Extraction [checkpoint: a6c9900]
- [x] Task: Write Tests: File upload and clean Markdown extraction [2b41bd7]
- [x] Task: Implement robust file upload via direct DOM injection [2b41bd7]
- [x] Task: Implement completion verification and clean extraction using "Copy as Markdown" flow [2b41bd7]
- [x] Task: Conductor - User Manual Verification 'Bot Engine Upload & Extraction' (Protocol in workflow.md) [a6c9900]

## Phase 4: Python-Native PDF Conversion [checkpoint: 26cd4c4]
- [x] Task: Write Tests: MD to HTML and HTML to PDF conversion [2ff6947]
- [x] Task: Implement MD to HTML conversion using Pandoc [2ff6947]
- [x] Task: Implement HTML to PDF conversion using Playwright Python `page.pdf()` with CSS injection [2ff6947]
- [x] Task: Conductor - User Manual Verification 'PDF Conversion' (Protocol in workflow.md) [26cd4c4]

## Phase 5: Integration & Final Polish [checkpoint: 7f0e7a7]
- [x] Task: Write Tests: End-to-end integration of the pipeline [f4125b4]
- [x] Task: Integrate components into a unified execution flow in `bot_engine.py` [6be7789]
- [x] Task: Final verification and code style polish [a2c49a9]
- [x] Task: Conductor - User Manual Verification 'Integration & Final Polish' (Protocol in workflow.md) [7f0e7a7]
