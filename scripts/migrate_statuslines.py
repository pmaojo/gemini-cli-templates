import os
import json

directory = '/Users/pelayo/proyectos/Gemini-cli-templates/cli-tool/components/settings/statusline/'

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if 'statusLine' in data and 'ui' not in data:
                print(f"Migrating {filename}...")
                data['ui'] = {'statusLine': data['statusLine']}
                del data['statusLine']
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                print(f"Skipping {filename} (already migrated or no statusLine)")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
