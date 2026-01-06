---
name: debug-error
description: Analyze and debug error messages or stack traces.
allowed-tools: Read, Bash
argument-hint: "[error-message]" | --log-file=[path]
---

# Debug Error

Analyze error messages, stack traces, and logs to identify root causes and suggest fixes.

## Capabilities

- **Stack Trace Analysis**: Parse and explain stack traces
- **Log Correlation**: Correlate error logs with code locations
- **Root Cause Identification**: Suggest potential causes for the error
- **Fix Suggestions**: Provide actionable steps or code patches to resolve the issue

## Usage

```bash
gemini debug-error "TypeError: Cannot read property 'map' of undefined"
gemini debug-error --log-file=server.log
```
