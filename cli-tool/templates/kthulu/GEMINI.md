# Kthulu: Go + Frontend Stack

## Overview

**Kthulu** is a modern full-stack template featuring a **Go (Golang)** backend and a rich **Frontend**. It is designed for high-performance applications with type safety and concurrency.

## Stack

- **Backend**: Go (Chi/Echo/Fiber - configurable)
- **Frontend**: React/Vite (or similar modern framework)
- **Dependency Injection**: [Uber Fx](https://github.com/uber-go/fx) for modular application composition.
- **MCP Integration**: Includes `kthulu-go` MCP for stack management.

## Project Structure

The project follows a modular architecture:

```
internal/modules/{name}/
├── core/   # Core logic, domain models, and interfaces
├── store/  # Data access layer (repositories)
└── api/    # HTTP handlers and transport layer
```

## Quick Start

1. **Setup**:
   ```bash
   gemini run setup
   ```
2. **Run**:
   ```bash
   gemini run dev
   ```

## Architecture

The project is structured to support scalability and maintainability, with a clear separation between the Go API and the frontend client. It leverages **Uber Fx** to wire components together, ensuring loose coupling and easy testing.

## Resources

- Repository: [https://github.com/pmaojo/kthulu-go](https://github.com/pmaojo/kthulu-go)
