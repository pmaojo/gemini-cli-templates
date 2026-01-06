import requests
from bs4 import BeautifulSoup
import json
import os
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def infer_category(name, description, tags):
    text = (name + " " + description + " " + " ".join(tags)).lower()

    if any(x in text for x in ['database', 'sql', 'mongo', 'redis', 'postgres', 'db']):
        return 'database'
    if any(x in text for x in ['cloud', 'aws', 'gcp', 'azure', 'kubernetes', 'terraform', 'deploy']):
        return 'cloud'
    if any(x in text for x in ['security', 'auth', 'secret', 'vault']):
        return 'security'
    if any(x in text for x in ['ai', 'ml', 'llm', 'model', 'inference', 'vision', 'speech']):
        return 'ai-ml'
    if any(x in text for x in ['debug', 'test', 'git', 'github', 'gitlab', 'code', 'dev']):
        return 'devtools'
    if any(x in text for x in ['monitor', 'log', 'trace', 'observability']):
        return 'observability'
    if any(x in text for x in ['productivity', 'task', 'note', 'email', 'calendar']):
        return 'productivity'

    return 'community'

import sys

def main():
    # Allow batching via command line args: python script.py [offset] [limit]
    offset = 0
    limit = 50
    if len(sys.argv) > 1:
        offset = int(sys.argv[1])
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])

    url = "https://geminicli.com/extensions"
    print(f"Fetching {url}...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Failed to fetch URL: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')

    install_texts = soup.find_all(string=re.compile("Install this extension"))

    print(f"Found {len(install_texts)} extension entries.")

    # Aggregate all extensions into a single list
    all_extensions = []

    base_dir = "cli-tool/components/extensions"
    os.makedirs(base_dir, exist_ok=True)

    print(f"Processing {len(install_texts)} extension entries.")

    for install_text in install_texts:
        try:
            # The structure likely groups these.
            # Let's traverse up to a container.
            card = install_text.find_parent('div')
            if not card:
                continue

            # Go up a few levels until we capture the name and description
            # This is heuristic.
            container = card.parent
            if not container:
                continue

            text_content = container.get_text(separator="\n")
            lines = [l.strip() for l in text_content.split('\n') if l.strip()]

            # Find the install command line
            install_cmd_idx = -1
            for i, line in enumerate(lines):
                if "gemini extensions install" in line:
                    install_cmd_idx = i
                    break

            if install_cmd_idx == -1:
                continue

            install_command = lines[install_cmd_idx]
            repo_url = install_command.replace("gemini extensions install", "").strip()

            # Name usually at the top or near
            # We can parse the repo url to get the name
            parts = repo_url.split('/')
            if len(parts) >= 2:
                repo_name = parts[-1]
                owner = parts[-2]
            else:
                repo_name = "unknown"
                owner = "unknown"

            name = repo_name.replace('.git', '')

            # Find the index of "Install this extension"
            install_prompt_idx = -1
            for i, line in enumerate(lines):
                if "Install this extension" in line:
                    install_prompt_idx = i
                    break

            description = ""
            if install_prompt_idx > 2:
                # Assuming structure: Name, Author, Description..., Install...
                description = " ".join(lines[2:install_prompt_idx])

            if not description:
                description = f"Gemini CLI extension: {name}"

            category = infer_category(name, description, [])

            extension_data = {
                "name": name,
                "displayName": name.replace('-', ' ').title(),
                "description": description,
                "repository": repo_url,
                "author": owner,
                "category": category,
                "tags": [category, name],
                "installCommand": f"npx gemini-cli-templates@latest --extension={name}" # Adapting to our CLI
            }

            all_extensions.append(extension_data)

        except Exception as e:
            print(f"Error processing entry: {e}")
            continue

    # Save all to a single file
    output_file = os.path.join(base_dir, "extensions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_extensions, f, indent=2)

    print(f"Saved {len(all_extensions)} extensions to {output_file}")

if __name__ == "__main__":
    main()
