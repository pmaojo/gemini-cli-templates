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
    // ignore
  }
  return files;
}

async function fixYamlDescriptions() {
  console.log('Fixing YAML description syntax errors...');
  const files = await findMarkdownFiles(COMPONENTS_DIR);
  let fixedCount = 0;
  
  for (const file of files) {
    let content = await fs.readFile(file, 'utf8');
    
    // Regex to find description: value where value contains : and is NOT quoted
    // We look for the frontmatter block
    const frontmatterRegex = /^---\n([\s\S]*?)\n---/m;
    const match = content.match(frontmatterRegex);
    
    if (match) {
      let fmContent = match[1];
      let fmChanged = false;
      
      // Check description line
      // This is a naive regex, but might catch the specific case we saw
      // Validation: description: has content, content has : or special chars, and is not wrapped in quotes
      const descriptionMatch = fmContent.match(/^description: (.*)$/m);
      if (descriptionMatch) {
        const val = descriptionMatch[1].trim();
        const hasSpecialChars = val.includes(':') || val.includes('#') || val.includes('[') || val.includes('{') || val.includes('<');
        const isQuoted = val.startsWith('"') || val.startsWith("'");
        
        if (hasSpecialChars && !isQuoted) {
          console.log(`Fixing description in: ${path.relative(process.cwd(), file)}`);
          const escapedVal = val.replace(/"/g, '\\"');
          const newVal = `description: "${escapedVal}"`;
          fmContent = fmContent.replace(descriptionMatch[0], newVal);
          fmChanged = true;
        }
      }

      if (fmChanged) {
        content = content.replace(match[1], fmContent);
        await fs.writeFile(file, content);
        fixedCount++;
      }
    }
  }
  
  console.log(`Fixed ${fixedCount} files.`);
}

fixYamlDescriptions().catch(console.error);
