---
name: directory-deep-dive
description: Recursively analyze directory structure and content summaries.
allowed-tools: Read, Bash
argument-hint: "[path] | --depth=[n] | --ignore=[patterns]"
---

# Directory Deep Dive

Recursively analyze directory structures to provide content summaries and structural insights.

## Features

- **Recursive Listing**: List files and directories up to a specified depth
- **Content Summary**: Generate brief summaries of file contents
- **Structure Visualization**: Tree-like visualization of the directory
- **Pattern Matching**: Filter by file type or ignore patterns

## Usage

```bash
gemini directory-deep-dive src/ --depth=2
```
