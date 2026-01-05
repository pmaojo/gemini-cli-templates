const path = require('path');
const { getCommandsForLanguageAndFramework } = require('./command-scanner');

const TEMPLATES_CONFIG = {
  'common': {
    name: 'Common (Language-agnostic)',
    description: 'Universal configuration for any project',
    files: [
      { source: 'common/GEMINI.md', destination: 'GEMINI.md' }
    ]
  },
  'javascript-typescript': {
    name: 'JavaScript/TypeScript',
    description: 'Optimized for modern JS/TS development',
    files: [
      { source: 'javascript-typescript/GEMINI.md', destination: 'GEMINI.md' },
      { source: 'javascript-typescript/.gemini', destination: '.gemini' },
      { source: 'javascript-typescript/.gemini/settings.json', destination: '.gemini/settings.json' },
      { source: 'javascript-typescript/.mcp.json', destination: '.mcp.json' }
    ],
    frameworks: {
      'react': {
        name: 'React',
        additionalFiles: [
          { source: 'javascript-typescript/examples/react-app/.gemini/commands', destination: '.gemini/commands' }
        ]
      },
      'vue': {
        name: 'Vue.js',
        additionalFiles: [
          { source: 'javascript-typescript/examples/vue-app/.gemini/commands', destination: '.gemini/commands' }
        ]
      },
      'angular': {
        name: 'Angular',
        additionalFiles: [
          { source: 'javascript-typescript/examples/angular-app/.gemini/commands', destination: '.gemini/commands' }
        ]
      },
      'node': {
        name: 'Node.js',
        additionalFiles: [
          { source: 'javascript-typescript/examples/node-api/.gemini/commands', destination: '.gemini/commands' }
        ]
      }
    }
  },
  'python': {
    name: 'Python',
    description: 'Optimized for Python development',
    files: [
      { source: 'python/GEMINI.md', destination: 'GEMINI.md' },
      { source: 'python/.gemini', destination: '.gemini' },
      { source: 'python/.gemini/settings.json', destination: '.gemini/settings.json' },
      { source: 'python/.mcp.json', destination: '.mcp.json' }
    ],
    frameworks: {
      'django': {
        name: 'Django',
        additionalFiles: [
          { source: 'python/examples/django-app/.gemini/commands', destination: '.gemini/commands' },
          { source: 'python/examples/django-app/GEMINI.md', destination: 'GEMINI.md' }
        ]
      },
      'flask': {
        name: 'Flask',
        additionalFiles: [
          { source: 'python/examples/flask-app/.gemini/commands', destination: '.gemini/commands' }
        ]
      },
      'fastapi': {
        name: 'FastAPI',
        additionalFiles: [
          { source: 'python/examples/fastapi-app/.gemini/commands', destination: '.gemini/commands' }
        ]
      }
    }
  },
  'ruby': {
    name: 'Ruby',
    description: 'Optimized for Ruby development with modern tools',
    files: [
      { source: 'ruby/GEMINI.md', destination: 'GEMINI.md' },
      { source: 'ruby/.gemini', destination: '.gemini' },
      { source: 'ruby/.gemini/settings.json', destination: '.gemini/settings.json' },
      { source: 'ruby/.mcp.json', destination: '.mcp.json' }
    ],
    frameworks: {
      'rails': {
        name: 'Ruby on Rails 8',
        additionalFiles: [
          { source: 'ruby/examples/rails-app/.gemini/commands', destination: '.gemini/commands' },
          { source: 'ruby/examples/rails-app/GEMINI.md', destination: 'GEMINI.md' }
        ]
      },
      'sinatra': {
        name: 'Sinatra',
        additionalFiles: [
          { source: 'ruby/examples/sinatra-app/.gemini/commands', destination: '.gemini/commands' }
        ]
      }
    }
  },
  'rust': {
    name: 'Rust',
    description: 'Optimized for Rust development',
    comingSoon: true,
    files: [
      { source: 'rust/.mcp.json', destination: '.mcp.json' }
    ]
  },
  'go': {
    name: 'Go',
    description: 'Optimized for Go development', 
    comingSoon: true,
    files: [
      { source: 'go/.mcp.json', destination: '.mcp.json' }
    ]
  },
  'marketing': {
    name: 'Tribal Marketing',
    description: 'Seth Godin\'s framework for building a Minimum Viable Audience',
    files: [
      { source: 'marketing/GEMINI.md', destination: 'GEMINI.md' },
      { source: 'marketing/.gemini', destination: '.gemini' },
      { source: 'marketing/.gemini/settings.json', destination: '.gemini/settings.json' },
      { source: 'marketing/.mcp.json', destination: '.mcp.json' }
    ],
    frameworks: {
      'tribe-app': {
        name: 'Tribe App (Agents & Commands)',
        additionalFiles: [
          { source: 'marketing/examples/tribe-app/.gemini/commands', destination: '.gemini/commands' },
          { source: 'marketing/examples/tribe-app/.gemini/agents', destination: '.gemini/agents' }
        ]
      }
    }
  }
};

function getAvailableLanguages() {
  return Object.keys(TEMPLATES_CONFIG).map(key => ({
    value: key,
    name: TEMPLATES_CONFIG[key].name,
    description: TEMPLATES_CONFIG[key].description,
    disabled: TEMPLATES_CONFIG[key].comingSoon ? 'Coming Soon' : false
  }));
}

function getFrameworksForLanguage(language) {
  const config = TEMPLATES_CONFIG[language];
  if (!config || !config.frameworks) return [];
  
  return Object.keys(config.frameworks).map(key => ({
    value: key,
    name: config.frameworks[key].name
  }));
}

function getTemplateConfig(selections) {
  const { language, framework, commands = [] } = selections;
  const baseConfig = TEMPLATES_CONFIG[language];
  
  if (!baseConfig) {
    throw new Error(`Unknown language template: ${language}`);
  }
  
  let files = [...baseConfig.files];
  
  // Add framework-specific files
  if (framework && framework !== 'none' && baseConfig.frameworks && baseConfig.frameworks[framework]) {
    const frameworkConfig = baseConfig.frameworks[framework];
    if (frameworkConfig.additionalFiles) {
      files = files.concat(frameworkConfig.additionalFiles);
    }
  }
  
  // Handle command selection
  let selectedCommands = [];
  if (commands && commands.length > 0) {
    const availableCommands = getCommandsForLanguageAndFramework(language, framework);
    selectedCommands = availableCommands.filter(cmd => commands.includes(cmd.name));
  }
  
  return {
    language,
    framework,
    files,
    selectedCommands,
    config: baseConfig
  };
}

module.exports = {
  TEMPLATES_CONFIG,
  getAvailableLanguages,
  getFrameworksForLanguage,
  getTemplateConfig
};