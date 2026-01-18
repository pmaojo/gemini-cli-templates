---
name: "ralph-manager"
description: "A Meta-Manager CLI that orchestrates AI coding agents using the Ralph Wiggum pattern. Turns ideas into specs and executes them via autonomous loops."
author: "Antigravity & User"
version: "1.0.0"
category: "agents"
tags: ["manager", "cli", "agentic", "orchestration"]
---

# Ralph Manager

This component installs the `ralph-manager` CLI into your project.

## Installation

The files will be installed into `manager/`. It includes:

- `cli.ts`: The entry point
- `adapters/`: Pluggable agent adapters
- `core/`: Architect logic

## Usage

```bash
cd manager
npm install
npm run new   # Draft a new idea
npm run loop  # Start the execution loop
```
