import os
import re
import json
import sys
import yaml

LIMIT = 40

# Load report
try:
    with open('cli-tool/security-report.json', 'r') as f:
        report = json.load(f)
except FileNotFoundError:
    print("Report not found.")
    sys.exit(1)

def get_failed_files(code):
    files = []
    for c in report['components']:
        if not c['overall']['valid']:
            for v in c['validators'].values():
                if 'errors' in v:
                    for e in v['errors']:
                        if e['code'] == code:
                            files.append(c['component']['path'])
    return list(set(files))

files_missing_frontmatter = get_failed_files('STRUCT_E001')
files_invalid_yaml = get_failed_files('STRUCT_E002')
files_missing_field = get_failed_files('STRUCT_E006')

def fix_frontmatter_missing(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError: return False

    if content.startswith('---'): return False

    filename = os.path.basename(filepath)
    name = os.path.splitext(filename)[0]
    name = re.sub(r'[^a-zA-Z0-9-]', '-', name).lower()

    # Simple description extraction
    lines = content.split('\n')
    description = "No description provided."
    for i, line in enumerate(lines):
        if line.startswith('# '):
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].strip() and not lines[j].startswith('#'):
                    description = lines[j].strip().replace('"', '\\"')
                    break
            break

    is_agent = 'agents/' in filepath
    fm = "---\n"
    fm += f"name: {name}\n"
    fm += f"description: \"{description}\"\n"
    if is_agent:
        fm += "tools: [Read]\n"
    fm += "---\n\n"

    with open(filepath, 'w') as f:
        f.write(fm + content)
    return True

def is_valid_yaml_value(val):
    try:
        yaml.safe_load(f"key: {val}")
        return True
    except:
        return False

def fix_yaml_syntax(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError: return False

    match = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not match: return False

    fm_text = match.group(1)
    lines = fm_text.split('\n')
    new_lines = []
    modified = False

    for line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            val = parts[1].strip()

            needs_quoting = False
            # Quote if unquoted and looks like invalid YAML or specific problematic patterns
            if val and not (val.startswith('"') or val.startswith("'") or val.startswith('|') or val.startswith('>')):
                 if not is_valid_yaml_value(val):
                     needs_quoting = True
                 elif val.startswith('[') and '|' in val:
                     needs_quoting = True
                 elif ':' in val and not (val.startswith('{') or val.startswith('[')):
                     needs_quoting = True

            if needs_quoting:
                if '\\n' in val:
                     val = val.replace('\\n', '\n  ')
                     new_lines.append(f"{key}: |\n  {val}")
                else:
                    val = val.replace('"', '\\"')
                    new_lines.append(f'{key}: "{val}"')
                modified = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if modified:
        new_fm_text = '\n'.join(new_lines)
        new_content = content.replace(f"---\n{fm_text}\n---", f"---\n{new_fm_text}\n---", 1)
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

def fix_missing_field(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError: return False

    match = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not match: return False
    fm_text = match.group(1)

    modified = False
    new_fm_text = fm_text

    # Check Name
    if not re.search(r'^name:', fm_text, re.MULTILINE):
        name = os.path.splitext(os.path.basename(filepath))[0]
        new_fm_text = f"name: {name}\n" + new_fm_text
        modified = True

    # Check Tools (for agents)
    if 'agents/' in filepath and not re.search(r'^tools:', fm_text, re.MULTILINE):
        new_fm_text = new_fm_text + "tools: [Read]\n"
        modified = True

    if modified:
        new_content = content.replace(f"---\n{fm_text}\n---", f"---\n{new_fm_text}\n---", 1)
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

processed = 0
changed_files = []

# Order: Frontmatter missing, then YAML syntax, then missing fields.
# Check if file already modified to avoid double counting
def process_file(path, func):
    global processed
    full_path = os.path.join('cli-tool', path)
    if full_path in changed_files: return # Already touched

    if func(full_path):
        changed_files.append(full_path)
        processed += 1
        print(f"Fixed: {path}")
        return True
    return False

print("Processing missing frontmatter...")
for path in files_missing_frontmatter:
    if processed >= LIMIT: break
    process_file(path, fix_frontmatter_missing)

if processed < LIMIT:
    print("Processing invalid YAML...")
    for path in files_invalid_yaml:
        if processed >= LIMIT: break
        process_file(path, fix_yaml_syntax)

if processed < LIMIT:
    print("Processing missing fields...")
    for path in files_missing_field:
        if processed >= LIMIT: break
        process_file(path, fix_missing_field)

print(f"Total processed: {processed}")
