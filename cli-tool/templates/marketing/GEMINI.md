# Tribal Marketing Stack

Welcome to the Tribal Marketing template. This environment is configured to help you build a Minimum Viable Audience (MVT) using Seth Godin's frameworks.

## 3-Layer Stack

### 1. The Research Layer (Gemini 3)

This project is configured with **Gemini 3's Web Browse & Search Capabilities** to gather real-world data.

- **Google Search**: Used to find customer conversations (forums, Reddit) and validate assumptions.
- **Web Browse**: Used to visit and analyze competitor websites directly.

**Recommended Extensions:**

- `social-media-monitor`: To track real-time tribal conversations.

### 2. The Strategy Layer (Agents)

You have access to 3 specialized agents:

- **MVT Discovery** (`marketing:mvt`): Drills down to the psychographic persona.
- **XY Positioning** (`marketing:xy`): Finds the "Lonely Quadrant".
- **Culture Code** (`marketing:culture`): Drafts the manifesto.

**Recommended Extensions:**

- `conductor`: To manage the research and strategy workflow.
- `jules`: To automate background research tasks while you focus on strategy.

### 3. The Execution Layer (Commands)

Run these commands to execute the workflow:

- `gemini tribe:scout "topic"` - Find the enemy (status quo).
- `gemini tribe:map "url1 url2"` - Map the competitive landscape.
- `gemini tribe:launch` - Draft the first 10 application process.

## Getting Started

1. **Run a Scout**: `gemini tribe:scout "your niche"`
2. **Draft Strategy**: Use `jules` to run deeper research in the background: `/jules tribe:scout "your niche" --deep`

## Troubleshooting

- **Tool Not Found**: If you see "Tool not found" errors, ensure you are using Gemini 3 which has built-in search.
- **Unauthorized Tool Call**: This template uses a specialized `marketing-scout` agent that is restricted to web research. Avoid asking it to perform shell operations.
