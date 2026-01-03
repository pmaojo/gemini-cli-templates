# Tasks: Gemini CLI Templates Transformation

## Phase 1: Preparation & "The Great Rename"

- [x] **Repo Cleanup:** Remove Gemini-specific legacy files (`.gemini/`, `CLAUDE.md` in root) to clear confusion.
- [x] **Infrastructure Rename:**
  - Rename `cli-tool/package.json` name to `gemini-cli-templates`.
  - Update `README.md` title, badges, and descriptions.
  - Rename `CLAUDE.md` to `GEMINI.md` in the root.
- [/] **Mass Text Replacement (Repo-wide):**
  - Run a script to replace "Gemini Code" with "Gemini CLI" in all documentation and comments.
  - Replace "Google" with "Google" where appropriate in docs.

## Phase 2: Content Migration (The "Cool Solution")

- [ ] **Create Migration Script (`scripts/convert_templates_to_gemini.py`):**
  - Script to iterate through `cli-tool/components/`.
  - **Agents:** Read markdown, regex replace "You are Gemini" -> "You are Gemini", "Google" -> "Google". Save in place.
  - **Commands:** Rename any headers "Slash Command" to "Gemini Command".
- [ ] **Execute Migration:** Run the script to permanently transform the 800+ template files.
- [ ] **Manual Review:** Spot check high-value templates (Development, Security) for grammar after auto-replacement.

## Phase 3: CLI Tool Logic Updates

- [ ] **Config Logic (`src/managers/ConfigManager.js`):**
  - Change target config path to `~/.gemini/settings.json`.
  - Implement `readGeminiConfig()` and `writeGeminiConfig()`.
- [ ] **Context Logic (`src/managers/ContextManager.js`):**
  - Change target context file from `CLAUDE.md` to `GEMINI.md`.
  - Update the injection logic to append/replace content in `GEMINI.md`.
- [ ] **Install Logic (`src/index.js`):**
  - Update `installComponent` to use the new Config and Context managers.
  - Ensure MCP installation formats the JSON correctly for Gemini.

## Phase 4: Analytics & Dashboard Adaptation

- [ ] **Process Detection (`src/analytics/core/ProcessDetector.js`):**
  - Update process name filter to `gemini`.
- [ ] **Frontend Rebranding (`cli-tool/src/analytics-web/`):**
  - Update `index.html` title and meta tags.
  - Update CSS variables (primary colors) to match Gemini Blue.
  - Update "Gemini State" components to say "Gemini State".

## Phase 5: Verification & Release

- [ ] **Integration Test:**
  - Install the CLI locally.
  - Run `npx gemini-cli-templates --agent development-team/frontend-developer`.
  - Verify `GEMINI.md` is created/updated.
  - Verify content refers to Gemini.
- [ ] **API Check:** Ensure telemetry sends correct data.
- [ ] **Final Polish:** Check `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for stray "Gemini" references.
