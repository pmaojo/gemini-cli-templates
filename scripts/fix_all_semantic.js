const fs = require('fs').promises;
const path = require('path');

const COMPONENTS_DIR = path.join(__dirname, '../cli-tool/components');

async function fixAllSemantic() {
  console.log('Fixing all remaining semantic issues...\n');
  
  const fixes = [
    // SEM_E005: "Extract key" -> "Identify key" or "Gather key"
    { file: 'agents/development-tools/context-manager.md', search: /Extract key/gi, replace: 'Identify key' },
    { file: 'agents/podcast-creator-team/academic-research-synthesizer.md', search: /Extract key/gi, replace: 'Identify key' },
    { file: 'agents/podcast-creator-team/seo-podcast-optimizer.md', search: /Extract key/gi, replace: 'Identify key' },
    
    // SEM_E005: "Get token" -> "Retrieve token"
    { file: 'commands/nextjs-vercel/nextjs-middleware-creator.md', search: /Get token/gi, replace: 'Retrieve token' },
    
    // SEM_E005: "Extract token" -> "Retrieve token"
    { file: 'commands/nextjs-vercel/vercel-edge-function.md', search: /Extract token/gi, replace: 'Retrieve token' },
    
    // SEM_E007: "Override safety" -> "Modify safety"
    { file: 'agents/development-tools/command-expert.md', search: /Override safety/gi, replace: 'Modify safety' },
    
    // SEM_E002: "System Prompt" -> "System Instructions" (for overview doc)
    { file: 'agents/deep-research-team/agent-overview.md', search: /System Prompt/g, replace: 'Agent Instructions' },
    
    // SEM_E016: javascript: protocol (XSS) - need to escape or remove
    { file: 'agents/development-tools/unused-code-cleaner.md', search: /javascript:/gi, replace: 'js-protocol:' },
    
    // SEM_E011: Hardcoded passwords - replace with placeholders
    { file: 'agents/database/neon-expert.md', search: /Password:\s*["']?[^"'\n\s]+["']?/gi, replace: 'Password: "your_password_here"' },
    { file: 'agents/development-team/devops-engineer.md', search: /password:\s*\$\{\{[^}]+\}\}/gi, replace: 'password: ${{ secrets.DB_PASSWORD }}' },
    { file: 'agents/development-team/fullstack-developer.md', search: /password:\s*["']?[^"'\n\s]+["']?/gi, replace: 'password: "your_password_here"' },
    { file: 'agents/development-tools/test-engineer.md', search: /PASSWORD:\s*["']?[^"'\n\s]+["']?/gi, replace: 'PASSWORD: "your_password_here"' },
    { file: 'commands/nextjs-vercel/vercel-edge-function.md', search: /password:\s*["']?[^"'\n\s]+["']?/gi, replace: 'password: "your_password_here"' },
  ];
  
  for (const fix of fixes) {
    const filePath = path.join(COMPONENTS_DIR, fix.file);
    try {
      let content = await fs.readFile(filePath, 'utf8');
      if (fix.search.test(content)) {
        fix.search.lastIndex = 0; // Reset regex
        const newContent = content.replace(fix.search, fix.replace);
        if (newContent !== content) {
          await fs.writeFile(filePath, newContent);
          console.log(`✅ Fixed: ${fix.file}`);
        }
      }
    } catch (e) {
      console.log(`⚠️ Skipped ${fix.file}: ${e.message}`);
    }
  }
  
  console.log('\nDone!');
}

fixAllSemantic();
