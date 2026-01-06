---
name: clean
description: Clean build artifacts, temporary files, and caches from the project.
allowed-tools: Bash
argument-hint: "--all | --build | --cache | --deps"
---

# Clean Project

Clean build artifacts, temporary files, and caches to ensure a fresh state.

## Targets

- **Build Artifacts**: `dist/`, `build/`, `out/` directories
- **Dependencies**: `node_modules/`, `venv/`, `target/` (optional)
- **Caches**: `npm` cache, `pip` cache, temporary files
- **Logs**: `*.log` files

## Usage

```bash
gemini clean          # Standard clean (artifacts and logs)
gemini clean --all    # Deep clean including dependencies and caches
```
