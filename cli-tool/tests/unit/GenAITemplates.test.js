
const path = require('path');
const fs = require('fs-extra');
const { TEMPLATES_CONFIG } = require('../../src/templates');
const { getAvailableAgents } = require('../../src/agents');

describe('GenAI Templates', () => {
  it('should have genai category in TEMPLATES_CONFIG', () => {
    expect(TEMPLATES_CONFIG.genai).toBeDefined();
    expect(TEMPLATES_CONFIG.genai.name).toContain('GenAI Native');
  });

  it('should have genai frameworks configured', () => {
    const frameworks = TEMPLATES_CONFIG.genai.frameworks;
    expect(frameworks.general).toBeDefined();
    expect(frameworks.autonomous).toBeDefined();
    expect(frameworks.architect).toBeDefined();
  });

  it('should find the new agents', () => {
    // We need to mock fs or ensure the path resolution works in test environment
    // For this integration test, we rely on the actual file system since we created the files

    // Check if the directories exist
    const genaiPath = path.join(__dirname, '../../templates/genai');
    expect(fs.existsSync(genaiPath)).toBe(true);

    const autonomousAgentPath = path.join(genaiPath, 'examples/autonomous/agents/autonomous-developer.md');
    expect(fs.existsSync(autonomousAgentPath)).toBe(true);
  });

  it('getAvailableAgents should discover the new agents', () => {
    const agents = getAvailableAgents();
    const autonomousDev = agents.find(a => a.name === 'autonomous-developer');
    const systemArchitect = agents.find(a => a.name === 'system-architect');
    const legacyModernizer = agents.find(a => a.name === 'legacy-modernizer');

    expect(autonomousDev).toBeDefined();
    expect(autonomousDev.language).toBe('genai');
    expect(autonomousDev.framework).toBe('autonomous');

    expect(systemArchitect).toBeDefined();
    expect(systemArchitect.language).toBe('genai');
    expect(systemArchitect.framework).toBe('architect');

    expect(legacyModernizer).toBeDefined();
    expect(legacyModernizer.language).toBe('genai');
    expect(legacyModernizer.framework).toBe('general');
  });
});
