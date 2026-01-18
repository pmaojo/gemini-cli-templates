#!/bin/bash
set -u

# Architect - The Spec Interviewer
# Uses Gemini to interview the user and generate SPECS.md

GEMINI_BIN="gemini"
PERSONA_FILE="$(dirname "$0")/../commands/spec-architect.md"
OUTPUT_FILE="SPECS.md"

echo -e "\033[1;34m🤖 Architect initialized.\033[0m"
echo -e "I will help you define your software specifications."
echo -e "Let's start an interview session to build your '${OUTPUT_FILE}'."
echo ""

# Check if we have the persona file
if [[ ! -f "$PERSONA_FILE" ]]; then
    echo "Error: Persona file not found at $PERSONA_FILE"
    exit 1
fi

# We use a temporary file to store the "conversation state" or just rely on the CLI's chat history if interactive.
# Since standard 'gemini' CLI might be one-shot, we simulate a loop or use an interactive flag if available.
# For this template, we assume standard one-shot but we will run a loop where we append history.
# However, a simpler way for the "WOW" demo is to launch Gemini in REPL mode if supported,
# OR just run a single big prompt that says "Interview me".

# Let's try the "Interactive Loop" approach using bash read.

HISTORY_FILE=".gemini/architect-history.txt"
mkdir -p .gemini
echo "" > "$HISTORY_FILE"

# Initial prompt
SYSTEM_PROMPT=$(cat "$PERSONA_FILE")
CURRENT_INPUT="Hello! I want to build a new piece of software. Please interview me."

while true; do
    # 1. User Input (already set for first turn, or read from stdin)

    # 2. Call Gemini
    # We combine System Prompt + History + New Input
    # Note: This naive history appending might hit context limits eventually, but fine for a spec interview.

    FULL_PROMPT="$SYSTEM_PROMPT

    --- CONVERSATION HISTORY ---
    $(cat "$HISTORY_FILE")

    --- USER INPUT ---
    $CURRENT_INPUT

    (Reply to the user. If you have enough info to write the SPECS.md, output the markdown content inside a code block tagged with 'FILE:SPECS.md')"

    echo -e "\033[1;33mThinking...\033[0m"
    RESPONSE=$($GEMINI_BIN "$FULL_PROMPT")

    # Display Response
    echo -e "\033[1;32mArchitect:\033[0m"
    echo "$RESPONSE"

    # Save to history
    echo "User: $CURRENT_INPUT" >> "$HISTORY_FILE"
    echo "Architect: $RESPONSE" >> "$HISTORY_FILE"

    # Check for File Generation Signal
    # A robust implementation would parse the response.
    # Here we look for the marker we asked for.
    if echo "$RESPONSE" | grep -q "FILE:SPECS.md"; then
        # Extract content (simplified extraction logic)
        # Assuming the AI puts the content between ```markdown and ``` blocks
        # This is a bit brittle in bash, but sufficient for the template proof-of-concept.

        echo "$RESPONSE" | sed -n '/FILE:SPECS.md/,/```/p' | sed '1d;$d' > "$OUTPUT_FILE"
        # Cleanup potential markers if regex was sloppy
        # Ideally, use a proper tool or the 'write_file' tool if the agent was running in a tool-use environment.

        # Fallback: Just ask the user if they want to save it manually if extraction fails?
        # Better: The agent (in a real tool env) would call `write_file`.
        # Since we are wrapping the CLI, we simulate it.

        echo -e "\n\033[1;35m✨ Draft detected!\033[0m"
        echo "I've attempted to extract the spec to '$OUTPUT_FILE'."
        echo "Please review it."
        break
    fi

    echo ""
    echo -e "\033[1;34mYou (leave empty to finish/force draft):\033[0m"
    read -r USER_REPLY

    if [[ -z "$USER_REPLY" ]]; then
        CURRENT_INPUT="Please finalize the SPECS.md file based on what we discussed. Output it with the FILE:SPECS.md tag."
    else
        CURRENT_INPUT="$USER_REPLY"
    fi
done

echo "Architect session finished."
