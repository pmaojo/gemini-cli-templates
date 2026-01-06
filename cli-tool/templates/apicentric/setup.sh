#!/bin/bash
set -e

echo "📡 Setting up Apicentric Simulator..."

# 1. Check for Apicentric CLI
if ! command -v apicentric &> /dev/null; then
    echo "⚠️  'apicentric' CLI not found."
    echo "ℹ️  To install: cargo install --git https://github.com/pmaojo/apicentric"
else
    echo "✅ Apicentric CLI detected."
fi

echo "✅ Setup complete! Define services in 'services/*.yaml' and run 'gemini run start-simulator'."
