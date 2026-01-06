---
name: fix-issue
description: Analyze an issue description and apply a code fix.
allowed-tools: Read, Write, Bash
argument-hint: "[issue-description] | --file=[path] | --apply"
---

# Fix Issue

Analyze an issue description, locate the relevant code, and apply a fix.

## Process

1. **Issue Analysis**: Understand the reported problem and expected behavior
2. **Code Location**: Find the files and lines responsible for the issue
3. **Reproduction**: Create a reproduction case (optional)
4. **Fix Implementation**: Generate and apply the code fix
5. **Verification**: Verify the fix resolves the issue

## Usage

```bash
gemini fix-issue "Navigation bar crashes on mobile resize" --file=src/components/NavBar.tsx
```
