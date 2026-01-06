const SemanticValidator = require('../cli-tool/src/validation/validators/SemanticValidator');
const fs = require('fs');
const path = require('path');

const filesToTest = [
  'cli-tool/components/commands/marketing/publisher-linkedin.md',
  'cli-tool/components/agents/mcp-dev-team/mcp-security-auditor.md',
  'cli-tool/components/agents/development-team/devops-engineer.md',
  'cli-tool/components/commands/deployment/deployment-monitoring.md'
];

async function runDebug() {
  const validator = new SemanticValidator();
  
  for (const filePath of filesToTest) {
    const fullPath = path.join(process.cwd(), filePath);
    console.log(`\nAnalyzing ${filePath}...`);
    
    if (!fs.existsSync(fullPath)) {
      console.log('File not found');
      continue;
    }
    
    const content = fs.readFileSync(fullPath, 'utf8');
    const result = await validator.validate({
      content,
      path: filePath,
      type: filePath.includes('/agents/') ? 'agent' : 'command'
    });
    
    if (result.errors.length > 0) {
      console.log('❌ Errors:');
      result.errors.forEach(e => {
        console.log(`  [${e.code}] ${e.message}`);
        if (e.metadata.examples) {
          e.metadata.examples.forEach(ex => {
            console.log(`    - Match: "${ex.text}"`);
            console.log(`    - Context: "${ex.context}"`);
          });
        }
      });
    } else {
      console.log('✅ No errors found.');
    }
    
    if (result.warnings.length > 0) {
      console.log('⚠️ Warnings:');
      result.warnings.forEach(w => {
        console.log(`  [${w.code}] ${w.message}`);
         if (w.metadata.examples) {
          w.metadata.examples.forEach(ex => {
            console.log(`    - Match: "${ex.text}"`);
          });
        }
      });
    }
  }
}

runDebug();
