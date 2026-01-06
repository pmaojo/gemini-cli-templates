# Hexanorm: Hexagonal Architecture Stack

## Overview

**Hexanorm** is a robust stack implementing **Hexagonal Architecture (Ports and Adapters)**. It enforces a strict separation between:

1.  **Domain**: Core business logic (pure, no dependencies).
2.  **Application**: Use cases and orchestration.
3.  **Infrastructure**: Adapters for databases, APIs, and UIs.

## Features

- **Strict Layering**: Dependencies only point inwards.
- **Domain-Driven Design (DDD)**: First-class support for Entities, Value Objects, and Aggregates.
- **MCP-Native**: Controlled via the `hexanorm-mcp` server.

## Quick Start

1. **Initialize**:
   ```bash
   gemini run setup
   ```
2. **Develop**:
   Use Gemini to generate domain models or adapters:
   > "Create a new Domain Entity 'Order' with lines and total amount."
   > "Generate a Postgres adapter for the OrderRepository port."

## Resources

- Repository: [https://github.com/pmaojo/hexanorm-mcp](https://github.com/pmaojo/hexanorm-mcp)
