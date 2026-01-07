# Initial Concept
Class-to-Notes Engine

# Product Guide

## Project Overview
The "Class-to-Notes Engine" is a Linux CLI tool designed to automate the conversion of online class URLs into formatted PDF notes. It leverages a local Chromium instance and Google AI Studio to transcribe audio and generate high-quality notes, which are then converted to PDF.

## Core Goals
-   **Automate Note Taking:** Streamline the process of turning video/audio content into study notes.
-   **Robust Browser Automation:** Use Playwright with a specific user profile to interact with Google AI Studio reliably.
-   **High-Quality Output:** Generate well-formatted PDF notes using Pandoc and Puppeteer.
-   **User-Friendly Interface:** Provide a CLI (and eventually a TUI) for easy operation on Linux.

## Key Features
-   **Enhanced Queue Management:** Provides granular control over job processing, allowing users to start new jobs (with optional clearing of pending tasks), cancel old jobs, or resume existing queued tasks.
-   **Automated Retry Logic:** Automatically retries failed or interrupted jobs (e.g., from network issues or browser crashes).
-   **Media Download:** Downloads audio/video content for processing.
-   **AI-Powered Generation:** Automates Google AI Studio (Gemini 3 Pro Preview) to generate notes from uploaded audio.
-   **Smart Extraction:** Distinguishes final responses from reasoning blocks (ignoring 'Thinking' phase) and copies content as Markdown only after stability verification.
-   **Robust Recovery:** Implements hard browser resets upon interaction timeouts to maintain long-running automation stability.
-   **PDF Conversion:** Converts Markdown to PDF with custom styling via Pandoc and Playwright (Python).
-   **Manual Browser Control:** Utility to launch the automated browser instance manually for inspection or manual authentication tasks.
-   **TUI (Planned):** A terminal user interface for seamless interaction.

## Target Audience
-   Students and learners who want to digitize and summarize their class material.
-   Linux users who prefer CLI tools and automation.
