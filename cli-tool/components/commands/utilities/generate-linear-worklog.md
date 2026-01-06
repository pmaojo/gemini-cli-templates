---
name: generate-linear-worklog
description: Generate a structured worklog or changelog from git history.
allowed-tools: Read, Git, Bash
argument-hint: --since=[date] | --format=markdown|text
---

# Generate Linear Worklog

Generate a structured worklog, changelog, or status report from git commit history.

## Features

- **Commit Parsing**: Parse conventional commits for types (feat, fix, etc.)
- **Grouping**: Group changes by type, scope, or component
- **Formatting**: Output as Markdown, plain text, or JSON
- **Filtering**: Filter by author, date range, or path

## Usage

```bash
gemini generate-linear-worklog --since="last week" --format=markdown
```
