#!/bin/bash
set -e

echo "🚀 Setting up Grafka Neuro-Symbolic Engine..."

# 1. Check for Rust
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust/Cargo not found. Please install Rust: https://rustup.rs/"
    exit 1
fi

# 2. Build Rust Backend
echo "📦 Building Rust Semantic Engine (Release mode)..."
cd crates/semantic-engine
cargo build --release
cd ../..

# 3. Setup Python Environment
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "📥 Installing Python dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

echo "🛠️ Generating gRPC stubs..."
mkdir -p agents/infrastructure/persistence/proto
python3 -m grpc_tools.protoc -I./crates/semantic-engine/proto --python_out=./agents/infrastructure/persistence/ --grpc_python_out=./agents/infrastructure/persistence/ ./crates/semantic-engine/proto/semantic_engine.proto

echo "✅ Setup complete! run 'gemini run start-engine' to launch."
