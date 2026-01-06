const fs = require('fs');
const path = require('path');

const filesToCheck = [
  'cli-tool/templates/marketing/examples/tribe-app/.gemini/agents/culture-code.md',
  'cli-tool/templates/marketing/examples/tribe-app/.gemini/agents/mvt-discovery.md',
  'cli-tool/templates/marketing/examples/tribe-app/.gemini/agents/brand-rituals.md',
  'cli-tool/templates/marketing/examples/tribe-app/.gemini/agents/linking-value.md',
  'docs/guides/tribal-marketing.html',
  'cli-tool/templates/marketing/examples/tribe-app/.gemini/commands/tribe-scout.md',
  'cli-tool/templates/marketing/examples/tribe-app/.gemini/commands/tribe-map.md',
  'cli-tool/templates/marketing/.gemini/settings.json'
];

let failed = false;

console.log('Verifying files...');

filesToCheck.forEach(file => {
  if (!fs.existsSync(file)) {
    console.error(`❌ Missing file: ${file}`);
    failed = true;
  } else {
    console.log(`✅ Found file: ${file}`);
    const content = fs.readFileSync(file, 'utf8');

    // Specific checks
    if (file.includes('tribe-scout.md')) {
        if (content.includes('brave-search')) {
            console.error(`❌ ${file} still contains brave-search`);
            failed = true;
        }
        if (!content.includes('Google Search')) {
            console.error(`❌ ${file} does not contain "Google Search"`);
            failed = true;
        }
    }

     if (file.includes('tribe-map.md')) {
        if (content.includes('puppeteer')) {
             console.error(`❌ ${file} still contains puppeteer`);
             failed = true;
        }
    }

    if (file.includes('settings.json')) {
        if (content.includes('brave-search') || content.includes('puppeteer')) {
            console.error(`❌ ${file} still contains brave/puppeteer config`);
            failed = true;
        }
    }
  }
});

if (fs.existsSync('cli-tool/templates/marketing/.mcp.json')) {
    console.error('❌ cli-tool/templates/marketing/.mcp.json should be deleted');
    failed = true;
}

if (failed) {
  console.error('Verification failed.');
  process.exit(1);
} else {
  console.log('Verification passed!');
}
