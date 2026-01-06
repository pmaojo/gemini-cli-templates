const fs = require('fs');
const path = require('path');

const dir = 'cli-tool/components/agents/deep-research-team';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));

for (const file of files) {
  const filePath = path.join(dir, file);
  let content = fs.readFileSync(filePath, 'utf8');

  // Handle files without frontmatter
  if (!content.startsWith('---')) {
    console.log(`Adding frontmatter to ${file}`);
    const name = file.replace('.md', '');
    const title = name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    content = `---\nname: ${name}\ndescription: ${title} agent part of the Deep Research Team.\n---\n\n` + content;
    fs.writeFileSync(filePath, content);
    continue;
  }

  // Extract frontmatter
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) continue;

  let frontmatterStr = match[1];
  const rest = content.slice(match[0].length);

  // Check if description needs fixing (contains \n or is very long)
  if (frontmatterStr.includes('description:') && frontmatterStr.includes('\\n')) {
    console.log(`Fixing description in ${file}`);
    
    // Find description line
    const lines = frontmatterStr.split('\n');
    const descIndex = lines.findIndex(l => l.startsWith('description:'));
    
    if (descIndex !== -1) {
      const descLine = lines[descIndex];
      const descValue = descLine.slice('description:'.length).trim();
      
      // Convert to block scalar
      const cleanedValue = descValue
        .replace(/^["']/, '')
        .replace(/["']$/, '')
        .replace(/\\n/g, '\n    ');
      
      lines[descIndex] = `description: |\n    ${cleanedValue}`;
      frontmatterStr = lines.join('\n');
      
      const newContent = `---\n${frontmatterStr}\n---${rest}`;
      fs.writeFileSync(filePath, newContent);
    }
  }
}
