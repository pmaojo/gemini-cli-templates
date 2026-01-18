#!/bin/bash
set -uo pipefail

# Ralph Wiggum - Agentic Loop Engine
# "I'm doing agentic engineering!"

# Colors and formatting
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Defaults
MAX_ITERATIONS=10
VERIFY_CMD="npm test" # Default, but should be overridden
MODE="HITL" # HITL or AFK
STATE_FILE=".gemini/ralph-progress.md"
LOG_FILE=".gemini/ralph-last-run.log"
INITIAL_PROMPT=""
GEMINI_BIN="gemini" # Assumes 'gemini' is in PATH

usage() {
  echo -e "${BOLD}Ralph Wiggum - Agentic Loop${NC}"
  echo "Usage: $0 [options] \"<prompt>\""
  echo ""
  echo "Options:"
  echo "  --verify <cmd>   Command to verify success (default: 'npm test')"
  echo "  --max-iter <n>   Maximum iterations (default: 10)"
  echo "  --afk            Run in AFK mode (no human confirmation)"
  echo "  --help           Show this help"
  echo ""
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --verify)
      VERIFY_CMD="$2"
      shift 2
      ;;
    --max-iter)
      MAX_ITERATIONS="$2"
      shift 2
      ;;
    --afk)
      MODE="AFK"
      shift
      ;;
    --help)
      usage
      ;;
    *)
      if [[ -z "$INITIAL_PROMPT" ]]; then
        INITIAL_PROMPT="$1"
        shift
      else
        echo "Error: Unknown argument '$1'"
        usage
      fi
      ;;
  esac
done

if [[ -z "$INITIAL_PROMPT" ]]; then
  echo -e "${RED}Error: No prompt provided.${NC}"
  usage
fi

# Ensure .gemini directory exists
mkdir -p .gemini

# Initialize
CURRENT_ITERATION=1
CURRENT_PROMPT="$INITIAL_PROMPT"

echo -e "${BLUE}=======================================${NC}"
echo -e "${BOLD}🤖 Ralph Wiggum Initialized${NC}"
echo -e "   Mode: ${YELLOW}$MODE${NC}"
echo -e "   Task: $INITIAL_PROMPT"
echo -e "   Verify: $VERIFY_CMD"
echo -e "   Max Iter: $MAX_ITERATIONS"
echo -e "${BLUE}=======================================${NC}"

# Log start
echo "# Ralph Wiggum Session - $(date)" > "$STATE_FILE"
echo "Task: $INITIAL_PROMPT" >> "$STATE_FILE"
echo "" >> "$STATE_FILE"

while [[ $CURRENT_ITERATION -le $MAX_ITERATIONS ]]; do
  echo -e "\n${CYAN}🔄 Iteration $CURRENT_ITERATION / $MAX_ITERATIONS${NC}"

  # 1. Run the Agent
  echo -e "${BOLD}Thinking...${NC}"

  # Prepare input for Gemini
  # We construct a wrapper prompt to enforce the persona
  FULL_PROMPT="You are Ralph, an agentic engineer. Your goal is to pass the verification command: '$VERIFY_CMD'.

  Current Task context:
  $CURRENT_PROMPT

  Please implement the necessary changes to the codebase. Do not ask for permission, just write the code."

  if [[ "$MODE" == "HITL" ]]; then
     echo -e "${YELLOW}HITL Mode: Press Enter to run this iteration (or Ctrl+C to stop)...${NC}"
     read -r
  fi

  # Call Gemini CLI
  # We pipe the prompt to gemini and capture output to ensure it ran
  # Assuming standard input usage or arguments.
  # Note: Adjust command based on actual Gemini CLI syntax available in environment
  $GEMINI_BIN "$FULL_PROMPT"

  GEMINI_EXIT_CODE=$?
  if [[ $GEMINI_EXIT_CODE -ne 0 ]]; then
      echo -e "${RED}❌ Gemini crashed or failed to run.${NC}"
      exit 1
  fi

  # 2. Verify
  echo -e "${BOLD}Verifying work ($VERIFY_CMD)...${NC}"
  set +e # Allow verify command to fail
  eval "$VERIFY_CMD" > "$LOG_FILE" 2>&1
  VERIFY_EXIT_CODE=$?
  set -e

  if [[ $VERIFY_EXIT_CODE -eq 0 ]]; then
    # SUCCESS
    echo -e "${GREEN}✅ Verification Passed!${NC}"

    # Commit
    git add .
    git commit -m "Ralph: Task completed (Iter $CURRENT_ITERATION)"

    echo -e "## Iteration $CURRENT_ITERATION: ${GREEN}SUCCESS${NC}" >> "$STATE_FILE"
    echo "Work committed."
    exit 0
  else
    # FAILURE
    echo -e "${RED}❌ Verification Failed${NC}"

    # Extract error log (tail last 20 lines for brevity in prompt, but maybe full log is better)
    ERROR_LOG=$(cat "$LOG_FILE")

    echo -e "## Iteration $CURRENT_ITERATION: ${RED}FAILED${NC}" >> "$STATE_FILE"
    echo "\`\`\`" >> "$STATE_FILE"
    tail -n 10 "$LOG_FILE" >> "$STATE_FILE"
    echo "\`\`\`" >> "$STATE_FILE"

    # Construct next prompt
    CURRENT_PROMPT="The previous iteration failed the verification check ($VERIFY_CMD).

    Here is the output log:

    \`\`\`
    $ERROR_LOG
    \`\`\`

    Please analyze the error, fix the code, and try again."

    # 3. Git checkpointing (optional strategy: revert or commit broken state?)
    # Ralph article suggests: "Commit after each feature".
    # But if it's broken, maybe we don't commit yet?
    # Or we commit with "WIP: Failed attempt" so the agent sees history?
    # Let's commit as WIP to preserve history for the agent.
    git add .
    git commit -m "Ralph: WIP - Verification failed (Iter $CURRENT_ITERATION)" || true # Ignore empty commit errors

  fi

  CURRENT_ITERATION=$((CURRENT_ITERATION + 1))
done

echo -e "${RED}🛑 Max iterations reached without success.${NC}"
echo "Check $STATE_FILE for details."
exit 1
