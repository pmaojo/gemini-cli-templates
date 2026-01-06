const fs = require('fs').promises;
const path = require('path');

const COMPONENTS_DIR = path.join(__dirname, '../cli-tool/components');

async function findMarkdownFiles(dir) {
  const files = [];
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        const subFiles = await findMarkdownFiles(fullPath);
        files.push(...subFiles);
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    if (error.code !== 'ENOENT') {
      console.error(`Error reading ${dir}: ${error.message}`);
    }
  }
  return files;
}

async function fixFrontmatter() {
  console.log(`Scanning ${COMPONENTS_DIR}...`);
  
  const files = await findMarkdownFiles(COMPONENTS_DIR);
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
    // const type = path.basename(path.dirname(dir)); // not used yet
    
    let name = filename;
    let description = '';
    
    // Try to extract from content
    const lines = content.split('\n');
    let titleFound = false;
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!titleFound && trimmed.startsWith('# ')) {
        const h1 = trimmed.substring(2).trim();
        if (h1.startsWith('/')) {
            name = h1.substring(1); 
        }
        titleFound = true;
      } else if (titleFound && trimmed.length > 0 && !trimmed.startsWith('#')) {
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
