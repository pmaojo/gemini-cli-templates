#!/bin/bash
set -e

echo "🚀 Setting up Grafka Neuro-Symbolic Engine..."

# 1. Check for Rust (Only if crates exist)
if [ -d "crates" ]; then
    if ! command -v cargo &> /dev/null; then
        echo "❌ Rust/Cargo not found. Please install Rust: https://rustup.rs/"
        exit 1
    fi
    
    # 2. Build Rust Backend
    if [ -d "crates/semantic-engine" ]; then
        echo "📦 Building Rust Semantic Engine (Release mode)..."
        cd crates/semantic-engine
        cargo build --release
        cd ../..
    fi
else
    echo "⚠️  No 'crates' directory found. Skipping Rust build."
fi

# 3. Setup Python Environment
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "📥 Installing Python dependencies..."
source .venv/bin/activate
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
     echo "⚠️  requirements.txt not found."
fi

# 4. Generate Stubs (Only if proto exists)
if [ -d "crates/semantic-engine/proto" ]; then
    echo "🛠️ Generating gRPC stubs..."
    mkdir -p agents/infrastructure/persistence/proto
    python3 -m grpc_tools.protoc -I./crates/semantic-engine/proto --python_out=./agents/infrastructure/persistence/ --grpc_python_out=./agents/infrastructure/persistence/ ./crates/semantic-engine/proto/semantic_engine.proto
else
    echo "⚠️  Proto definitions not found. Skipping gRPC stub generation."
fi

echo "✅ Setup complete! run 'gemini run start-engine' to launch."
