#!/bin/bash
set -e

echo "🔷 Setting up Hexanorm Stack..."

# 1. Check for Node.js (assuming JS/TS based adapter generation)
if ! command -v npm &> /dev/null; then
    echo "❌ Node/npm is not installed."
    exit 1
fi

# 2. Install dependencies
echo "📦 Installing dependencies..."
if [ -f "package.json" ]; then
    npm install
else
    echo "⚠️  package.json not found. Run 'npm init' to start."
fi

echo "✅ Hexanorm setup complete."
