# Requirements: Gemini CLI Templates Transformation

## 1. Project Overview
The goal is to completely rebrand and transform the existing "Claude Code Templates" project into "Gemini CLI Templates". This tool will serve as the premier resource for users of the Google Gemini CLI (`@google/gemini-cli`), providing ready-to-use agents, commands, settings, and integrations, just as the original did for Claude Code.

## 2. Core Requirements

### 2.1 Rebranding & Identity
- **Name Change:** The project/package name must change from `claude-code-templates` to `gemini-cli-templates`.
- **Branding:** Update all visual assets, READMEs, and documentation to reflect "Gemini CLI" (Google branding colors, terminology) instead of "Claude Code" (Anthropic branding).
- **CLI Command:** The primary executable should be `gemini-templates` (or `npx gemini-cli-templates`).

### 2.2 Infrastructure Migration
- **Target CLI:** Fully support `@google/gemini-cli` as the runtime environment.
- **Configuration Files:**
  - Replace generation of `CLAUDE.md` with `GEMINI.md` (Project Context).
  - Manage `~/.gemini/settings.json` instead of `.claude/config.json`.
- **Directories:**
  - Rename local config directory from `.claude/` to `.gemini/` where applicable (e.g., for script downloads).
  - Update any git-ignore or file-watching rules to target `.gemini` paths.

### 2.3 Template Content Conversion
- **"Cool Solution" / Native Migration:** The repository's content (600+ agents, 200+ commands) must be permanently converted to be "Gemini-Native".
- **Agents:**
  - Content: Replace "You are Claude" with "You are Gemini".
  - Context: Ensure system prompts are compatible with Gemini's context window and formatting.
- **Commands:**
  - Convert Claude slash command definitions to Gemini Custom Commands / Extensions format.
- **MCPs:**
  - Verify and adapt MCP installation logic to write to Gemini's MCP configuration standard.

### 2.4 Analytics & Dashboard
- **Session Tracking:** Update the analytics engine to detect and track the `gemini` process (instead of `claude`).
- **State Detection:** Adapt "Conversation State" logic (Working, User Typing, etc.) to match Gemini CLI's terminal output patterns.
- **UI Refresh:** Rebrand the web dashboard (colors, logos) to match Gemini.

### 2.5 API & Telemetry
- **Backend:** Update the Vercel API endpoints to accept and track "Gemini" component downloads.
- **Database:** Ensure telemetry stores data correctly under the new product name/schema.

## 3. Compatibility Matrix

| Feature | Old (Claude Code) | New (Gemini CLI) |
| :--- | :--- | :--- |
| **Project Context** | `CLAUDE.md` | `GEMINI.md` |
| **Global Config** | `.claude/config.json` | `~/.gemini/settings.json` |
| **Ignore File** | `.claudeignore` | (Verify Gemini Equivalent) |
| **CLI Process** | `claude` | `gemini` |
| **Extensions** | Custom Commands / MCPs | Extensions / MCPs |
| **Terminlogy** | "Slash Command" | "Command" / "Extension" |

## 4. Success Criteria
1. User can run `npx gemini-cli-templates` and see a Gemini-branded interface.
2. Installing an "Agent" creates a valid entry in `GEMINI.md` or a context file that Gemini CLI respects.
3. Installing an "MCP" correctly updates `~/.gemini/settings.json` and the MCP works in Gemini.
4. The Analytics Dashboard correctly shows "Gemini Working..." status when the user is using the Gemini CLI.
5. All 800+ existing templates are textually converted to reference Gemini/Google instead of Claude/Anthropic.
