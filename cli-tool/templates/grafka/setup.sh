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

echo "✅ Setup complete! run 'gemini run start-engine' to launch."
