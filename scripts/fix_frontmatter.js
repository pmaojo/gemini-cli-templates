const fs = require('fs-extra');
const path = require('path');
const glob = require('glob');

const COMPONENTS_DIR = path.join(__dirname, '../cli-tool/components');

async function fixFrontmatter() {
  console.log(`Scanning ${COMPONENTS_DIR}...`);
  
  // Find all .md files
  const files = glob.sync(`${COMPONENTS_DIR}/**/*.md`);
  let fixedCount = 0;
  
  for (const file of files) {
    const content = await fs.readFile(file, 'utf8');
    
    // Check if it has frontmatter
    if (content.trim().startsWith('---')) {
      continue;
    }
    
    console.log(`Fixing missing frontmatter: ${path.relative(process.cwd(), file)}`);
    
    // Extract info
    const filename = path.basename(file, '.md');
    const dir = path.dirname(file);
    const category = path.basename(dir);
    const type = path.basename(path.dirname(dir)); // agents, commands, etc. (singularize later)
    
    let name = filename;
    let description = '';
    
    // Try to extract from content
    const lines = content.split('\n');
    let titleFound = false;
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!titleFound && trimmed.startsWith('# ')) {
        // Extract name from H1 if it looks like a command name (e.g. "/scope:name" or "Name")
        const h1 = trimmed.substring(2).trim();
        if (h1.startsWith('/')) {
            name = h1.substring(1); // Remove leading slash
        } else {
            // Keep filename as name for consistency, or use H1?
            // Existing structure suggests filename is usually the ID.
            // Let's stick to filename as 'name' metadata for safety, or H1 if it looks like technical ID.
        }
        titleFound = true;
      } else if (titleFound && trimmed.length > 0 && !trimmed.startsWith('#')) {
        // First non-empty line after title is description
        description = trimmed;
        break;
      }
    }
    
    if (!description) {
      description = `${name} component for Gemini CLI`;
    }
    
    // Escape description quotes
    description = description.replace(/"/g, '\\"');
    
    // Construct frontmatter
    const frontmatter = `---
name: "${name}"
description: "${description}"
author: "Gemini CLI Templates"
version: "1.0.0"
category: "${category}"
---

`;
    
    // Write back
    await fs.writeFile(file, frontmatter + content);
    fixedCount++;
  }
  
  console.log(`\nFixed ${fixedCount} files.`);
}

fixFrontmatter().catch(console.error);
