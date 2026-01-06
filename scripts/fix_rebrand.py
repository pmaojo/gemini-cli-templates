import os
import re

def fix_rebrand_syntax(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {filepath}")
        return

    original_content = content

    # Replace invalid syntax:
    # "github:pmaojo/gemini-cli-templates@latest" -> "github:pmaojo/gemini-cli-templates"

    # We need to be careful not to replace it if it's already correct, but the pattern is specific enough.
    # The error is appending @latest to a github: protocol url.

    content = content.replace('github:pmaojo/gemini-cli-templates@latest', 'github:pmaojo/gemini-cli-templates')

    if content != original_content:
        print(f"Fixing syntax in {filepath}")
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

            # Skip the scripts themselves
            if file == 'rebrand_repo.py' or file == 'fix_rebrand.py':
                continue

            filepath = os.path.join(root, file)
            fix_rebrand_syntax(filepath)

if __name__ == "__main__":
    main()
