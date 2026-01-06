const SemanticValidator = require('../cli-tool/src/validation/validators/SemanticValidator');
const fs = require('fs');
const path = require('path');

const filesToTest = [
  'cli-tool/components/commands/testing/test-coverage.md',
  'cli-tool/components/commands/testing/test-quality-analyzer.md',
  'cli-tool/components/commands/testing/testing_plan_integration.md',
  'cli-tool/components/commands/testing/write-tests.md',
  'cli-tool/components/commands/utilities/code-review.md',
  'cli-tool/components/commands/utilities/debug-error.md'
];

async function runDebug() {
  const validator = new SemanticValidator();
  
  for (const filePath of filesToTest) {
    const fullPath = path.join(process.cwd(), filePath);
    console.log(`\n=== ${filePath} ===`);
    
    if (!fs.existsSync(fullPath)) {
      console.log('File not found');
      continue;
    }
    
    const content = fs.readFileSync(fullPath, 'utf8');
    const result = await validator.validate({
      content,
      path: filePath,
      type: 'command'
    });
    
    if (result.errors.length > 0) {
      result.errors.forEach(e => {
        console.log(`  [${e.code}] ${e.message}`);
        if (e.metadata && e.metadata.examples) {
          e.metadata.examples.forEach(ex => {
            console.log(`    Match: "${ex.text}"`);
          });
        }
      });
    } else {
      console.log('  ✅ No errors');
    }
  }
}

runDebug();
