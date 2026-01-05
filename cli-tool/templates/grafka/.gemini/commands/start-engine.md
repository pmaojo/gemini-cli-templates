---
description: Start the Grafka Neuro-Symbolic Engine (Rust + MCP)
---

# Start Rust backend in background
./crates/semantic-engine/target/release/semantic-engine &
PID=$!

# Start MCP Server using the virtual environment
source .venv/bin/activate
python -m agents.infrastructure.web.mcp_server

# Cleanup on exit
kill $PID
