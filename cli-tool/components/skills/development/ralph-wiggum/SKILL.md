---
name: "ralph-wiggum"
description: "Implements the 'Ralph Wiggum' Agentic Pattern: Iteration beats perfection. A robust loop that runs the agent repeatedly against verification steps (tests, linters) until the task is actually done. Supports HITL (Human-In-The-Loop) and AFK (Away-From-Keyboard) modes with automatic git state management."
author: "Gemini CLI Templates"
version: "1.0.0"
category: "development"
tags: ["agentic", "automation", "testing", "refactoring", "afk-mode"]
---

# Ralph Wiggum Pattern

> "I'm doing agentic engineering!" - Ralph

![Ralph Wiggum Agent Loop](../../../../../docs/images/ralph-agent-loop.jpg)

This skill implements the **Ralph Wiggum** pattern, which flips the standard "prompt-and-pray" dynamic. Instead of hoping for a perfect zero-shot solution, Ralph assumes the agent will make mistakes and wraps it in a feedback loop that iterates until success.

## Core Philosophy

1.  **Iteration > Perfection**: The agent doesn't need to be perfect; it needs to be persistent.
2.  **Deterministic Failure is Data**: Test failures and linter errors are fed back to the agent as precise instructions.
3.  **Green State Ratcheting**: Every time the verification passes, we commit. We never slide back.

## Capabilities

*   **AFK Mode**: Give Ralph a task and a verification command (e.g., `npm test`), and he will work while you sleep.
*   **Feedback Loops**: Automatically captures stderr/stdout from failed checks and constructs the next prompt.
*   **Git Checkpoints**: Commits on success, optionally reverts on catastrophic failure.
*   **VM/Sandbox Ready**: Includes a bootstrap script to spin up a disposable coding environment (Docker/VM).

## Usage

### Basic Loop

```bash
# Run until 'npm test' passes, max 10 iterations
./scripts/ralph.sh "Refactor the auth module to use JWT" --verify "npm test" --max-iter 10
```

### VM Launch

```bash
# Spin up a fresh environment and start working
./scripts/vm-launch.sh --repo "github.com/my/repo" --task "Fix all bugs"
```

## Structure

*   `scripts/ralph.sh`: The main engine. A bash script that orchestrates the agent-verify-commit loop.
*   `scripts/vm-launch.sh`: A bootstrapper for setting up a fresh cloud VM or container with Ralph pre-loaded.
*   `commands/ralph.md`: The Gemini Command definition for natural language invocation.
