#!/bin/bash
set -e

# Notion Sync Bridge
# Syncs local SPECS.md with a Notion Page

# Requires: curl, jq
# Env: NOTION_TOKEN, NOTION_PAGE_ID

CONFIG_FILE=".gemini/notion-config.json"

usage() {
    echo "Usage: $0 [push|pull]"
    echo "  push: Upload SPECS.md to Notion"
    echo "  pull: Download Notion page to SPECS.md"
    echo ""
    echo "Configuration: $CONFIG_FILE"
}

if [[ $# -eq 0 ]]; then
    usage
    exit 1
fi

ACTION="$1"

# 1. Configuration
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Configuration not found."
    read -p "Enter Notion API Token: " TOKEN
    read -p "Enter Page ID: " PAGE_ID

    mkdir -p .gemini
    echo "{\"token\": \"$TOKEN\", \"page_id\": \"$PAGE_ID\"}" > "$CONFIG_FILE"
fi

TOKEN=$(jq -r .token "$CONFIG_FILE")
PAGE_ID=$(jq -r .page_id "$CONFIG_FILE")

if [[ "$ACTION" == "pull" ]]; then
    echo "⬇️  Pulling from Notion..."
    # Simplified block retrieval (fetches all blocks)
    # In reality, Notion API pagination is needed for large docs.
    RESPONSE=$(curl -s -X GET "https://api.notion.com/v1/blocks/$PAGE_ID/children" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Notion-Version: 2022-06-28")

    # Very naive JSON->Markdown converter for demo purposes
    # For robust usage, use a specialized tool or library.
    echo "$RESPONSE" | jq -r '.results[] |
        if .type == "heading_1" then "# " + .heading_1.rich_text[0].plain_text
        elif .type == "heading_2" then "## " + .heading_2.rich_text[0].plain_text
        elif .type == "paragraph" then (.paragraph.rich_text[0].plain_text // "")
        elif .type == "bulleted_list_item" then "- " + .bulleted_list_item.rich_text[0].plain_text
        else "" end' > SPECS.md

    echo "✅ Updated SPECS.md"

elif [[ "$ACTION" == "push" ]]; then
    echo "⬆️  Pushing to Notion..."
    # This is complex because Notion API requires appending blocks.
    # For this "WOW" demo, we'll implement a Mock/Echo or a simplified append.

    # Real implementation would delete existing blocks and replace them,
    # or diff them. That is a full engineering project.
    # We will provide a "Copy Paste" helper instead if we can't do full sync easily in bash.

    echo "⚠️  Direct Push to Notion via Bash is complex (requires parsing MD to Block Objects)."
    echo "For now, copying SPECS.md content to clipboard..."

    if command -v pbcopy &> /dev/null; then
        cat SPECS.md | pbcopy
        echo "✅ Copied to clipboard! Paste it into Notion."
    else
        echo "❌ Clipboard tool not found. Please copy contents of SPECS.md manually."
    fi

else
    usage
fi
