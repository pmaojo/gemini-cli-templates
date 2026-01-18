#!/bin/bash
set -e

# Ralph Wiggum - VM Bootstrap Script
# Usage: curl -sL <url> | bash -s -- --repo <url> --task "<task>"

REPO_URL=""
TASK=""
VERIFY_CMD="npm test"
BRANCH="main"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --repo) REPO_URL="$2"; shift 2 ;;
    --task) TASK="$2"; shift 2 ;;
    --verify) VERIFY_CMD="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$TASK" ]]; then
  echo "Error: --task required"
  exit 1
fi

echo "🚀 Bootstrapping Ralph Wiggum Environment..."

# 1. Install Dependencies (Ubuntu/Debian assumed)
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y git nodejs npm curl
fi

# 2. Install Gemini CLI
if ! command -v gemini &> /dev/null; then
    echo "Installing Gemini CLI..."
    # Placeholder for actual installation command if it differs
    npm install -g @google/gemini-cli || echo "Warning: ensure gemini-cli is installed"
fi

# 3. Setup Workspace
WORK_DIR="$HOME/ralph-workspace"
if [[ -n "$REPO_URL" ]]; then
    if [[ -d "$WORK_DIR" ]]; then
        echo "Cleaning previous workspace..."
        rm -rf "$WORK_DIR"
    fi
    git clone "$REPO_URL" "$WORK_DIR"
    cd "$WORK_DIR"
    if [[ -f "package.json" ]]; then
        npm install
    fi
else
    # Current directory usage
    echo "Using current directory context..."
fi

# 4. Inject Ralph Script
# We download the ralph script from the repository (using raw link) or create it inline
# For this template, since we are creating the file in the repo, we can copy it if local,
# or cat it here for the standalone script.
# To be self-contained, I will embed a simplified ralph loop or fetch the full one.
# For "WOW", let's assume this script is running from the repo context OR fetch it.
# I'll create the ralph.sh locally in the VM.

cat > ralph.sh << 'EOF'
#!/bin/bash
# ... (Embedded content of ralph.sh to ensure portability without needing to fetch extra files)
# For brevity in this plan, I will just call the actual ralph.sh if present, or assume the user has the templates.
# But for a TRUE VM launch, we should download it.
# Let's assume we curl it from the repo "main" branch.
EOF

# For now, let's just make sure the user knows to have the script.
# In a real scenario, this script would `curl` the `ralph.sh` from GitHub.
# I will simulate that by checking if `ralph.sh` exists in relative path (if cloned repo) or warn.

if [[ ! -f "./scripts/ralph.sh" ]]; then
    echo "Downloading Ralph engine..."
    mkdir -p scripts
    # Replace with actual raw URL in production
    # curl -sL https://raw.githubusercontent.com/pmaojo/gemini-cli-templates/main/cli-tool/components/skills/development/ralph-wiggum/scripts/ralph.sh > scripts/ralph.sh
    # chmod +x scripts/ralph.sh
    echo "NOTE: In this dev environment, please ensure ralph.sh is available."
else
    chmod +x ./scripts/ralph.sh
fi

# 5. Launch
echo "Starting Ralph Loop..."
# If local script exists
if [[ -f "./scripts/ralph.sh" ]]; then
    ./scripts/ralph.sh --afk --verify "$VERIFY_CMD" "$TASK"
else
    echo "Ralph script not found. Please clone the full template repository."
fi
