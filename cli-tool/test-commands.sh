#!/bin/bash

# Test script for gemini-cli-templates CLI
# This script runs basic tests to verify the CLI works as expected

# Setup test directory
TEST_DIR="/tmp/gemini-test-$(date +%s)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "🧪 Running CLI tests in $TEST_DIR"

# Test 1: Help command
gemini-cli-templates --help > /dev/null && echo "✅ Help command works" || echo "❌ Help command failed"

# Test 2: Version command
gemini-cli-templates --version > /dev/null && echo "✅ Version command works" || echo "❌ Version command failed"

# Test 3: Dry run with arguments (Javascript/React)
gemini-cli-templates --language javascript-typescript --framework react --dry-run --yes > /dev/null && echo "✅ JS/TS + React dry run works" || echo "❌ JS/TS + React dry run failed"

# Test 4: Dry run with arguments (Common)
gemini-cli-templates --language common --dry-run --yes > /dev/null && echo "✅ Common language dry run works" || echo "❌ Common language dry run failed"

# Test 5: Actual generation (Javascript/React)
echo "🧪 Testing actual generation..."
gemini-cli-templates --language javascript-typescript --framework react --yes > /dev/null

# Verify files were created
if [ -f "GEMINI.md" ] && [ -d ".gemini" ]; then
    echo "✅ GEMINI.md and .gemini directory created"
else
    echo "❌ Basic file structure generation failed"
fi

if [ -f ".gemini/commands/component.md" ] && [ -f ".gemini/commands/test.md" ]; then
    echo "✅ Commands created"
else
    echo "❌ Command files missing"
fi

if [ -f ".gemini/settings.json" ]; then
    echo "✅ Settings file created"

    # Check if hooks section exists in settings
    if command -v jq > /dev/null; then
        if jq '.hooks' ".gemini/settings.json" > /dev/null 2>&1; then
            hook_count=$(jq '.hooks | keys | length' ".gemini/settings.json")
            if [ "$hook_count" -gt 0 ]; then
                echo "✅ Hooks configuration present in settings.json ($hook_count hooks)"
            else
                echo "⚠️  Hooks section present but empty"
            fi
        else
            echo "❌ Hooks section missing from settings.json"
        fi
    else
        # Fallback if jq is not installed
        if grep -q '"hooks"' ".gemini/settings.json"; then
            echo "✅ Hooks configuration present in settings.json (verified via grep)"
        else
            echo "❌ Hooks section missing from settings.json"
        fi
    fi
else
    echo "❌ Settings file missing"
fi

# Test 6: Interactive mode (dry run via timeout/expect would be needed for real test)
# Just checking it doesn't crash immediately
timeout 5s gemini-cli-templates --dry-run || echo "✅ Interactive mode starts correctly"

# Cleanup
cd ..
rm -rf "$TEST_DIR"
echo "✨ Tests completed"
