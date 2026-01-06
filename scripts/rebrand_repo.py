import os
import re

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {filepath}")
        return

    original_content = content

    # 1. Replace username
    content = content.replace('davila7', 'pmaojo')

    # 2. Replace npm package references with GitHub repo
    # This regex looks for npm install commands or package.json dependencies
    # It's a heuristic and might need adjustment.

    # Example: npm install claude-code-templates -> npm install github:pmaojo/gemini-cli-templates
    # Example: "claude-code-templates": "^1.0.0" -> "claude-code-templates": "github:pmaojo/gemini-cli-templates"

    # Replace the package name in simple contexts if it appears as a direct npm install argument
    # (This is tricky because the package name might be 'claude-code-templates' or 'gemini-cli-templates')
    # Based on memory, the package name is 'claude-code-templates' in some places and 'gemini-cli-templates' in others.

    # Let's target the "official npm package" instruction specifically.
    # "npm install -g claude-code-templates" -> "npm install -g github:pmaojo/gemini-cli-templates"
    # "npx claude-code-templates" -> "npx github:pmaojo/gemini-cli-templates"

    # Regex for npm install/npx
    content = re.sub(r'npm install (?:-g )?claude-code-templates', 'npm install -g github:pmaojo/gemini-cli-templates', content)
    content = re.sub(r'npm install (?:-g )?gemini-cli-templates', 'npm install -g github:pmaojo/gemini-cli-templates', content)

    content = re.sub(r'npx claude-code-templates', 'npx github:pmaojo/gemini-cli-templates', content)
    content = re.sub(r'npx gemini-cli-templates', 'npx github:pmaojo/gemini-cli-templates', content)

    # Also replace direct links to npmjs
    content = re.sub(r'https://www.npmjs.com/package/claude-code-templates', 'https://github.com/pmaojo/gemini-cli-templates', content)
    content = re.sub(r'https://www.npmjs.com/package/gemini-cli-templates', 'https://github.com/pmaojo/gemini-cli-templates', content)

    if content != original_content:
        print(f"Updating {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    exclude_dirs = {'.git', 'node_modules', 'dist', 'build', '.next'}
    exclude_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.pyc'}

    for root, dirs, files in os.walk('.'):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in exclude_extensions):
                continue

            # Skip the script itself
            if file == 'rebrand_repo.py':
                continue

            filepath = os.path.join(root, file)
            replace_in_file(filepath)

if __name__ == "__main__":
    main()
