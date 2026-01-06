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

async function fixIncompleteFrontmatter() {
  console.log(`Scanning ${COMPONENTS_DIR} for incomplete frontmatter...`);
  
  const files = await findMarkdownFiles(COMPONENTS_DIR);
  let fixedCount = 0;
  
  for (const file of files) {
    const content = await fs.readFile(file, 'utf8');
    const filename = path.basename(file, '.md');
    
    // Check if it has frontmatter
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    
    if (frontmatterMatch) {
      const frontmatter = frontmatterMatch[1];
      if (!frontmatter.includes('name:')) {
        console.log(`Fixing missing name in frontmatter: ${path.relative(process.cwd(), file)}`);
        
        // Add name field
        const newFrontmatter = `name: "${filename}"\n${frontmatter}`;
        const newContent = content.replace(frontmatter, newFrontmatter);
        
        await fs.writeFile(file, newContent);
        fixedCount++;
      }
    }
  }
  
  console.log(`\nFixed ${fixedCount} files.`);
}

fixIncompleteFrontmatter().catch(console.error);
