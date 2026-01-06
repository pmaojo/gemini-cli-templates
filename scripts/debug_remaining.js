const SemanticValidator = require('../cli-tool/src/validation/validators/SemanticValidator');
const fs = require('fs');
const path = require('path');

const filesToTest = [
  'cli-tool/components/agents/database/neon-expert.md',
  'cli-tool/components/agents/deep-research-team/agent-overview.md',
  'cli-tool/components/agents/development-team/devops-engineer.md',
  'cli-tool/components/agents/development-team/fullstack-developer.md',
  'cli-tool/components/agents/development-tools/command-expert.md',
  'cli-tool/components/agents/development-tools/context-manager.md',
  'cli-tool/components/agents/development-tools/test-engineer.md',
  'cli-tool/components/agents/development-tools/unused-code-cleaner.md',
  'cli-tool/components/agents/podcast-creator-team/academic-research-synthesizer.md',
  'cli-tool/components/agents/podcast-creator-team/seo-podcast-optimizer.md',
  'cli-tool/components/commands/nextjs-vercel/nextjs-middleware-creator.md',
  'cli-tool/components/commands/nextjs-vercel/vercel-edge-function.md'
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
      type: filePath.includes('/agents/') ? 'agent' : 'command'
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
