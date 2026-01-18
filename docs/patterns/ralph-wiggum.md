---
title: Ralph Wiggum Pattern
description: "Agentic Engineering: Iteration beats perfection. Fix code autonomously until tests pass."
---

# Ralph Wiggum Pattern

> "I'm doing agentic engineering!" - Ralph

![Ralph Wiggum](https://i.imgur.com/example-ralph.png)

The **Ralph Wiggum** pattern flips the standard "prompt-and-pray" dynamic of AI coding. Instead of hoping for a perfect zero-shot solution, Ralph assumes the agent will make mistakes and wraps it in a feedback loop that iterates until success.

## Core Philosophy

1.  **Iteration > Perfection**: The agent doesn't need to be perfect; it needs to be persistent.
2.  **Deterministic Failure is Data**: Test failures and linter errors are fed back to the agent as precise instructions.
3.  **Green State Ratcheting**: Every time the verification passes, we commit. We never slide back.

## How to Use

### 1. The Spec Interview (Architect)

Don't write a long prompt. Let the AI interview you.

```bash
./cli-tool/components/skills/development/ralph-wiggum/scripts/architect.sh
```

This starts an interactive session where the **Spec Architect** asks you about your goals, tech stack, and constraints. It outputs a `SPECS.md` file.

### 2. The Ralph Loop (AFK Mode)

Once you have a spec and a verification command (like `npm test`), launch Ralph.

```bash
./cli-tool/components/skills/development/ralph-wiggum/scripts/ralph.sh \
  --spec SPECS.md \
  --verify "npm test" \
  --max-iter 20 \
  --afk
```

**What Ralph does:**
1.  Reads your `SPECS.md`.
2.  Writes code.
3.  Runs `npm test`.
4.  **If fail**: Reads the error log, fixes the code, and retries.
5.  **If pass**: Commits the code (`git commit`) and stops.

### 3. Notion Integration (Optional)

Collaborate on specs with your team in Notion.

```bash
# Push local spec to Notion
./cli-tool/components/skills/development/ralph-wiggum/scripts/notion-sync.sh push

# Pull updated spec from Notion
./cli-tool/components/skills/development/ralph-wiggum/scripts/notion-sync.sh pull
```

*(Requires `NOTION_TOKEN` and `NOTION_PAGE_ID` in `.gemini/notion-config.json`)*

## Components

This pattern is implemented via the `ralph-wiggum` skill in the Gemini CLI Templates.

*   **`architect.sh`**: Requirements gathering agent.
*   **`ralph.sh`**: The autonomous loop engine.
*   **`notion-sync.sh`**: Bridge for docs-as-code.
*   **`commands/ralph.md`**: Specialized persona for the runner.
*   **`commands/spec-architect.md`**: Specialized persona for the interviewer.
