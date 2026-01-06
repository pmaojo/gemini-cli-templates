---
name: code-to-task
description: Convert code comments and TODOs into actionable task items or issue tickets.
allowed-tools: Read, Write, Bash
argument-hint: [path] | --format=json|markdown|issue
---

# Code to Task

Scan code for TODOs, FIXMEs, and custom tags to convert them into actionable tasks.

## Features

- **Tag Detection**: Finds `TODO:`, `FIXME:`, `HACK:`, `BUG:` and custom tags
- **Context Extraction**: Captures surrounding code and file location
- **Task Generation**: Formats items as tasks with priority and context
- **Export**: Supports export to Markdown, JSON, or direct issue creation (GitHub/GitLab)

## Usage

```bash
gemini code-to-task src/ --format=markdown > tasks.md
```
