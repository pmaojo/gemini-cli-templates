# Tribal Marketing Stack

Welcome to the Tribal Marketing template. This environment is configured to help you build a Minimum Viable Audience (MVT) using Seth Godin's frameworks.

## 3-Layer Stack

### 1. The Research Layer (MCP)

This project is configured with **Brave Search** and **Puppeteer** to gather real-world data.

- **Brave Search**: Used to find customer conversations (forums, Reddit).
- **Puppeteer**: Used to analyze competitor websites.

**Recommended Extensions:**

- `exa-mcp-server`: For deeper search over high-quality data.
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

1. **Configure API Keys**: Open `.gemini/settings.json` and add your `BRAVE_API_KEY`.
2. **Run a Scout**: `gemini tribe:scout "your niche"`
3. **Draft Strategy**: Use `jules` to run deeper research in the background: `/jules tribe:scout "your niche" --deep`
