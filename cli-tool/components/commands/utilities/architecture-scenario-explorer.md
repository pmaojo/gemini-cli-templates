---
name: architecture-scenario-explorer
description: Explore architectural decisions through scenario simulation and trade-off analysis.
allowed-tools: Read, Write, Bash
argument-hint: "[scenario] | --simulation | --tradeoff | --report"
---

# Architecture Scenario Explorer

Analyze architectural decisions through scenario simulation and trade-off analysis.

## Core Capabilities

- **Scenario Simulation**: Model system behavior under various conditions (load, failure, scaling)
- **Trade-off Analysis**: Evaluate conflicting requirements (latency vs consistency, cost vs performance)
- **Decision Verification**: Validate architectural decisions against requirements and constraints
- **Risk Assessment**: Identify potential failure modes and architectural risks

## Usage

Provide a description of the architectural scenario or decision you want to explore. The tool will:
1. Model the scenario components and interactions
2. Simulate system behavior under specified conditions
3. Analyze trade-offs and potential issues
4. Provide recommendations and mitigation strategies

Example:
```bash
gemini architecture-scenario-explorer "Microservices vs Monolith for e-commerce platform with high peak loads"
```
