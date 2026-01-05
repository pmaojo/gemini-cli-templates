# Grafka: Neuro-Symbolic AI Engine

## Overview
Grafka gives your Gemini agents a **Long-term Memory** and a **Logical Left Brain**. It combines:
1.  **Knowledge Graph (Rust):** Stores facts as connected nodes, not just text.
2.  **OWL Reasoner:** Deducts new facts using logical rules (e.g., "If A is parent of B, and B is parent of C, then A is grandparent of C").
3.  **Vector Store (Qdrant):** Enables semantic search over the graph.

## Configuration
You can configure the underlying LLMs used for reasoning in `.mcp.json` or by setting environment variables:

-   `GEMINI_MODEL`: The default fast model (e.g., `gemini-2.5-flash`) used for extraction and routing.
-   `GEMINI_MODEL_REASONING`: The powerful model (e.g., `gemini-1.5-pro`) used for complex OWL deduction and synthesis.

## Quick Start

1.  **Setup:**
    ```bash
    gemini run setup
    ```
    (This compiles the Rust engine and installs Python deps)

2.  **Start Engine:**
    ```bash
    gemini run start-engine
    ```
    This launches the Rust backend and the MCP server.

3.  **Use with Gemini:**
    Once running, you can ask Gemini:
    > "Analyze 'The Lean Startup by Eric Ries' and extract the key principles into my knowledge graph."
    > "What are the dependencies between the concepts in my graph?"

## Architecture
-   **`crates/semantic-engine`**: High-performance graph database (Rust).
-   **`agents/`**: Python logic for RAG, Extraction, and Reasoning.
-   **`ontology/core.owl`**: The schema defining your domain logic.
