const fs = require('fs').promises;
const path = require('path');

const COMPONENTS_DIR = path.join(__dirname, '../cli-tool/components');

async function fixBrokenArgumentHint() {
  console.log('Fixing broken argument-hint in YAML frontmatter...');
  
  const filesToFix = [
    'commands/testing/test-coverage.md',
    'commands/testing/test-quality-analyzer.md',
    'commands/testing/testing_plan_integration.md',
    'commands/testing/write-tests.md',
    'commands/utilities/code-review.md'
  ];
  
  for (const relPath of filesToFix) {
    const filePath = path.join(COMPONENTS_DIR, relPath);
    try {
      let content = await fs.readFile(filePath, 'utf8');
      
      // Fix broken argument-hint where it spans 2 lines
      // Pattern: argument-hint: "|"\n  [actual-content]
      const brokenPattern = /argument-hint:\s*"\|"\n\s*(.+)\n/g;
      
      if (brokenPattern.test(content)) {
        brokenPattern.lastIndex = 0;
        content = content.replace(brokenPattern, (match, actualContent) => {
          // Combine into a single properly quoted line
          const combined = actualContent.trim();
          console.log(`Fixing ${relPath}: "${combined}"`);
          return `argument-hint: "${combined}"\n`;
        });
        await fs.writeFile(filePath, content);
      }
    } catch (e) {
      console.log(`Error with ${relPath}: ${e.message}`);
    }
  }
  
  console.log('Done!');
}

fixBrokenArgumentHint();
