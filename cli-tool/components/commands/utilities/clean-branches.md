---
name: clean-branches
description: Clean up merged, stale, or deleted local git branches interactively.
allowed-tools: Bash, Git
argument-hint: --merged | --stale | --force | --dry-run
---

# Clean Branches

Clean up local git branches that are no longer needed.

## Features

- **Merged Branches**: Identify and delete branches that have been merged into the main branch
- **Stale Branches**: Find branches that haven't been touched in a long time
- **Gone Branches**: Remove local references to remote branches that have been deleted
- **Interactive Mode**: Select which branches to delete safely

## Usage

```bash
gemini clean-branches            # Interactive cleanup
gemini clean-branches --merged   # Clean merged branches
gemini clean-branches --dry-run  # Show what would be deleted without taking action
```
