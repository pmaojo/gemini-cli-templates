# GEMINI.md

This file provides guidance to Gemini Code (gemini.ai/code) when working with code in this repository.

## Project Overview

This is a Rust project optimized for modern systems programming. The project uses standard tools and follows best practices for performance and safety.

## Development Commands

### Package Management

- `cargo build` - Build the project
- `cargo run` - Run the project
- `cargo update` - Update dependencies in Cargo.lock
- `cargo add <crate>` - Add a dependency (requires cargo-edit)
- `cargo remove <crate>` - Remove a dependency

### Testing Commands

- `cargo test` - Run all tests
- `cargo test -- --nocapture` - Run tests with stdout enabled
- `cargo test <test_name>` - Run a specific test

### Code Quality Commands

- `cargo fmt` - Format code with rustfmt
- `cargo clippy` - Run clippy linter for common mistakes
- `cargo check` - Check if the project compiles without building
- `cargo doc` - Generate documentation

## Technology Stack

### Core Technologies

- **Rust** - Primary programming language
- **Cargo** - Build system and package manager

### Common Crates

- **Serde** - Serialization/Deserialization
- **Tokio** - Asynchronous runtime
- **Anyhow** - Flexible error handling
- **Tracing** - Instrumentation and logging
- **Clap** - Command-line argument parsing

## Project Structure Guidelines

### File Organization

```
src/
├── main.rs          # Binary entry point (if applicable)
├── lib.rs           # Library entry point (if applicable)
├── models/          # Data structures and domain models
├── services/        # Business logic
├── utils/           # Utility functions
└── tests/           # Integration tests
```

### Naming Conventions

- **Files/Modules**: Use snake_case (`user_profile.rs`)
- **Structs/Enums**: Use PascalCase (`UserProfile`)
- **Functions/Variables**: Use snake_case (`get_user_data`)
- **Constants**: Use SCREAMING_SNAKE_CASE (`API_BASE_URL`)

## Rust Guidelines

### Safety and Best Practices

- Use `match` or `if let` for robust error handling
- Avoid `unwrap()` and `expect()` in production code
- Leverage the type system for safety (Newtype pattern, Enums)
- Follow standard Rust ownership and borrowing patterns
- Use `Result` and `Option` types appropriately

### Code Style

- Follow standard Rust formatting (rustfmt)
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Document public APIs with doc comments (`///`)
- Use Clippy to maintain high code quality

## Agentic Workflow with Conductor

For tasks complex than simple code edits, use **Conductor** for context-driven development.

### 1. Establish Context

Run `/conductor:setup` to define your project's core components:

- **Product**: Users, goals, and high-level features.
- **Tech Stack**: Language, database, and frameworks.
- **Workflow**: Testing strategies, coding standards.

### 2. Specify and Plan

Initialize a new unit of work (Track) with `/conductor:newTrack`. This generates:

- **Specs**: Detailed requirements.
- **Plan**: Actionable to-do list (`plan.md`).

### 3. Implement

Execute the approved plan with `/conductor:implement`. The agent will work through `plan.md`, persisting state so you can pause and resume as needed.

> [!TIP]
> Install Conductor with: `gemini extensions install https://github.com/gemini-cli-extensions/conductor`

## Development Workflow

### Before Starting

1. Ensure Rust and Cargo are installed
2. Run `cargo check` to verify setup
3. Review existing code architecture

### During Development

1. Write tests for new functionality
2. Run `cargo clippy` frequently
3. Use meaningful commit messages
4. Format code with `cargo fmt`

### Before Committing

1. Run full test suite: `cargo test`
2. Run linting: `cargo clippy`
3. Verify formatting: `cargo fmt --check`
4. Run `cargo build` to ensure project compiles
