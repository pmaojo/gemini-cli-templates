---
description: Start the Apicentric Simulator
---

# Run the simulator

# This assumes apicentric is installed or we use cargo run

if command -v apicentric &> /dev/null; then
apicentric start --services ./services
else
echo "⚠️ 'apicentric' CLI not found."

if command -v cargo &> /dev/null; then
echo "📦 Cargo detected. Installing apicentric from GitHub..."
cargo install --git https://github.com/pmaojo/apicentric

    # Ensure cargo bin is in path for this session if needed, or call directly
    export PATH="$HOME/.cargo/bin:$PATH"

    if command -v apicentric &> /dev/null; then
      echo "✅ Installation complete. Starting simulator..."
      apicentric start --services ./services
    else
      echo "❌ Installation appeared to succeed but 'apicentric' is still not found in PATH."
      exit 1
    fi

else
echo "❌ Neither 'apicentric' nor 'cargo' found. Please install Rust/Cargo to authorize auto-installation."
exit 1
fi
fi
