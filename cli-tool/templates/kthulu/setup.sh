#!/bin/bash
set -e

echo "🐙 Setting up Kthulu Stack (Go + React)..."

# 1. Check Backend (Go)
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed. Please install Go: https://go.dev/doc/install"
    exit 1
fi
echo "✅ Go detected: $(go version)"

# 2. Check Frontend (Node/Npm)
if ! command -v npm &> /dev/null; then
    echo "❌ Node/npm is not installed. Please install Node.js."
    exit 1
fi
echo "✅ npm detected: $(npm --version)"

# 3. Install Dependencies
echo "📦 Installing Backend Dependencies..."
if [ -f "go.mod" ]; then
    go mod download
else
    echo "⚠️  No go.mod found. Run 'go mod init <module-name>' to initialize."
fi

echo "📦 Installing Frontend Dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    npm install
    cd ..
else
    echo "⚠️  'frontend' directory not found. Skipping frontend install."
fi

echo "✅ Kthulu initialization complete! Run 'gemini run dev' to start."
