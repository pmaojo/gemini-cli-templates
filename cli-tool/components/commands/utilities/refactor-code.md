---
name: refactor-code
description: Apply refactoring patterns to improve code quality and maintainability.
allowed-tools: Read, Write, Bash
argument-hint: "[file-path] | --pattern=[pattern] | --dry-run"
---

# Refactor Code

Apply automated refactoring patterns to improve code quality, readability, and maintainability.

## Capabilities

- **Pattern Application**: Apply standard refactoring patterns (extract method, rename, etc.)
- **Code Cleanup**: Remove unused code, organize imports, fix formatting
- **Modernization**: Update legacy code to modern syntax/features
- **Complexity Reduction**: Simplify complex logic and control flow

## Usage

```bash
gemini refactor-code src/legacy-module.js --pattern="convert-to-es6-class"
```
