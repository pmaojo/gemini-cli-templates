# Apicentric: API Simulator & Service Registry

## Overview

**Apicentric** is a powerful API simulator and registry designed for developers who love the terminal. It allows you to define mock services in YAML, run them locally, and manage them via CLI or MCP.

## Features

- **YAML-based Definitions:** Define services, endpoints, and responses in simple YAML files.
- **Hot Reloading:** Changes to YAML files are applied instantly.
- **MCP Integration:** Control your mock services directly through Gemini agents.

## Quick Start

1. **Define a Service**: Edit `services/example.yaml`.
2. **Start the Simulator**:
   ```bash
   gemini run start-simulator
   ```
3. **Interact**: Use Gemini to manage services:
   > "Create a new mock service for a user API with 3 endpoints."
   > "Simulate a 500 error on the /checkout endpoint."

## Configuration

Review `.mcp.json` to see how the `apicentric` MCP server is connected.
