---
description: Start the Grafka Neuro-Symbolic Engine (Rust + MCP)
---

# Start Rust backend (if available)

if [ -f "./crates/semantic-engine/target/release/semantic-engine" ]; then
./crates/semantic-engine/target/release/semantic-engine &
PID=$!
else
echo "⚠️ Rust engine binary not found. Running Python only."
fi

# Start MCP Server

source .venv/bin/activate

# Check if the module exists before running

if python -c "import agents.infrastructure.web.mcp_server" &> /dev/null; then
python -m agents.infrastructure.web.mcp_server
else
echo "⚠️ MCP Server module not found. Please check agents/infrastructure/web/mcp_server.py"
fi

# Cleanup

if [ -n "$PID" ]; then
kill $PID
fi
