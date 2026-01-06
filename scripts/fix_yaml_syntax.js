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

async function fixYamlSyntax() {
  console.log(`Scanning ${COMPONENTS_DIR} for YAML syntax errors...`);
  
  const files = await findMarkdownFiles(COMPONENTS_DIR);
  let fixedCount = 0;
  
  for (const file of files) {
    const content = await fs.readFile(file, 'utf8');
    
    // Check for argument-hint with unquoted brackets/pipes
    // Regex matches: argument-hint: [text] with optional pipes/flags following, unquoted
    // match 'argument-hint: ' followed by something starting with [ or < not starting with "
    const argHintMatch = content.match(/^argument-hint: ([^"\n]+)$/m);
    
    if (argHintMatch) {
      const val = argHintMatch[1].trim();
      // If it has spaces, brackets, or pipes, and is NOT quoted
      if ((val.includes('[') || val.includes('|') || val.includes('<')) && !val.startsWith('"')) {
        console.log(`Fixing argument-hint in: ${path.relative(process.cwd(), file)}`);
        
        // Escape existing quotes if any (unlikely if we matched safe regex, but good practice)
        const escapedVal = val.replace(/"/g, '\\"');
        const newVal = `argument-hint: "${escapedVal}"`;
        
        const newContent = content.replace(argHintMatch[0], newVal);
        await fs.writeFile(file, newContent);
        fixedCount++;
      }
    }
  }
  
  console.log(`\nFixed ${fixedCount} files.`);
}

fixYamlSyntax().catch(console.error);
