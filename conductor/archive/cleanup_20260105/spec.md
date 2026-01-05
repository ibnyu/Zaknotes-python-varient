# Specification: Project Unification and Cleanup (Zaknotes)

## Overview
This track aims to consolidate the Zaknotes codebase into a unified, professional structure. The current project has fragmented features and a cluttered root directory. We will reorganize the code into a `src/` directory, remove obsolete test files, and implement a single entry point (`zaknotes.py`) with an interactive menu.

## Functional Requirements

### 1. Directory Reorganization & Cleanup
- **Create `src/` Directory**: A new directory to house all application logic and resources.
- **Move Modules**: Move all core Python modules to `src/`:
  - `bot_engine.py`
  - `browser_driver.py`
  - `cookie_manager.py`
  - `downloader.py`
  - `find_vimeo_url.py`
  - `job_manager.py`
  - `pdf_converter_py.py`
- **Move Resources**: Move resource directories to `src/`:
  - `ui_elements/` -> `src/ui_elements/`
  - `pdf_converter/` -> `src/pdf_converter/`
- **Delete Test Files**: Remove all files matching `test_*.py` from the root directory.
- **Import Updates**: Update all internal imports across the codebase to ensure compatibility with the new `src/` structure.

### 2. Main Entry Point (`zaknotes.py`)
- Create a root-level script `zaknotes.py` that serves as the primary interface.
- Implement an interactive CLI menu with the following options:

#### Option 1: Start Note Generation (Process Videos)
- Leverages the existing logic in `job_manager.py`.
- Prompts the user for video names and URLs (as currently implemented in `job_manager`).
- Triggers the full processing pipeline (Download -> AI Studio Note Gen -> PDF Conversion).

#### Option 2: Refresh Browser Profile
- **Cleanup**: Delete the existing `browser_profile/` directory.
- **Initialization**: Launch a Chromium instance (using `browser_driver.py`) in non-headless mode to allow the user to manually log in to Google AI Studio and other necessary sites.
- **Persistence**: Ensure the new profile state is saved correctly for subsequent automated runs.

#### Option 3: Refresh Cookies
- Invoke the existing cookie refresh logic located in `cookie_manager.py`.

## Acceptance Criteria
- `python zaknotes.py` launches a menu with the 3 required options.
- The project root is clean, containing only `zaknotes.py`, configuration files (`requirements.txt`, `.gitignore`), and data/state directories (`downloads/`, `cookies/`, `browser_profile/`).
- All `test_*.py` files are removed.
- Choosing "Refresh Browser Profile" successfully clears the old profile and opens a browser for manual login.
- Note generation works end-to-end after the reorganization.

## Out of Scope
- Implementing new AI generation features.
- Modifying the core PDF conversion engine (only moving/updating paths).
