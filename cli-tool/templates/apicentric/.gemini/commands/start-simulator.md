---
description: Start the Apicentric Simulator
---

# Run the simulator

# This assumes apicentric is installed or we use cargo run

if command -v apicentric &> /dev/null; then
apicentric start --services ./services
else
echo "⚠️ 'apicentric' CLI not found. Trying cargo..."
cargo run -- start --services ./services
fi
