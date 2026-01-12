/**
 * Extension Pattern Generator
 *
 * Analyzes available extensions from website dump and generates file patterns for auto-detection.
 */

const path = require('path');
const fs = require('fs');

// Define pattern mappings based on tags and categories
const TAG_PATTERNS = {
  'python': ['**/*.py', 'requirements.txt', 'Pipfile', 'pyproject.toml'],
  'javascript': ['**/*.js', 'package.json'],
  'typescript': ['**/*.ts', 'tsconfig.json'],
  'react': ['**/*.jsx', '**/*.tsx'],
  'vue': ['**/*.vue'],
  'angular': ['angular.json'],
  'flutter': ['**/*.dart', 'pubspec.yaml'],
  'dart': ['**/*.dart', 'pubspec.yaml'],
  'terraform': ['**/*.tf', '**/*.tfvars'],
  'docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
  'kubernetes': ['**/*.k8s.yaml', '**/*.k8s.yml', 'helm/**/*.yaml'],
  'mongodb': ['**/*.bson'], // Heuristic
  'sql': ['**/*.sql'],
  'postgres': ['**/*.sql'],
  'mysql': ['**/*.sql'],
  'redis': ['**/*.rdb'], // Unlikely to be in repo but okay
  'json': ['**/*.json'],
  'yaml': ['**/*.yaml', '**/*.yml'],
  'xml': ['**/*.xml'],
  'markdown': ['**/*.md'],
  'voice': ['**/*.mp3', '**/*.wav', '**/*.ogg'],
  'audio': ['**/*.mp3', '**/*.wav', '**/*.ogg'],
  'image': ['**/*.png', '**/*.jpg', '**/*.jpeg', '**/*.svg'],
  'video': ['**/*.mp4', '**/*.mov'],
  'figma': ['.figma'], // conceptual
  'graphql': ['**/*.graphql', '**/*.gql'],
  'prisma': ['schema.prisma'],
  'java': ['**/*.java', 'pom.xml', 'build.gradle'],
  'kotlin': ['**/*.kt', '**/*.kts'],
  'swift': ['**/*.swift'],
  'csharp': ['**/*.cs', '**/*.csproj'],
  'go': ['**/*.go', 'go.mod'],
  'rust': ['**/*.rs', 'Cargo.toml'],
  'php': ['**/*.php', 'composer.json'],
  'ruby': ['**/*.rb', 'Gemfile'],
  'shell': ['**/*.sh'],
  'bash': ['**/*.sh'],
  'snyk': ['.snyk'],
  'github': ['.github/**/*'],
  'gitlab': ['.gitlab-ci.yml'],
  'firebase': ['firebase.json'],
  'gcloud': ['app.yaml'],
  'vertex': ['**/*vertex*'], // Weak heuristic
  'wandb': ['wandb/**/*'],
  'stripe': ['**/*stripe*'],
  'shopify': ['**/*shopify*'],
  'wordpress': ['wp-config.php', 'style.css'],
  'notion': ['**/*notion*'],
  'jira': ['**/*jira*'],
  'slack': ['**/*slack*'],
  'telegram': ['**/*telegram*'],
  'discord': ['**/*discord*'],
  'aws': ['**/*.aws'],
  'azure': ['**/*.azure'],
  'google': ['**/*.google']
};

// Patterns based on extension name (if no tags match)
const NAME_PATTERNS = {
  'postman': ['**/*.postman_collection.json'],
  'gitlab': ['.gitlab-ci.yml'],
  'github': ['.github/**/*'],
  'docker': ['Dockerfile'],
  'kubernetes': ['**/*.yaml'],
  'k8s': ['**/*.yaml'],
  'aws': ['**/*.tf'],
  'azure': ['**/*.tf'],
  'gcp': ['**/*.tf'],
  'google': ['**/*.tf'],
  'terraform': ['**/*.tf'],
  'ansible': ['**/*.yml'],
  'jenkins': ['Jenkinsfile'],
  'circleci': ['.circleci/config.yml'],
  'travis': ['.travis.yml'],
  'grafana': ['**/*.json'],
  'prometheus': ['prometheus.yml'],
  'datadog': ['datadog.yaml'],
  'sentry': ['.sentryclirc'],
  'sonarqube': ['sonar-project.properties'],
  'eslint': ['.eslintrc*'],
  'prettier': ['.prettierrc*'],
  'jest': ['jest.config.js'],
  'mocha': ['.mocharc*'],
  'cypress': ['cypress.json'],
  'playwright': ['playwright.config.ts'],
  'vitest': ['vitest.config.ts'],
  'vite': ['vite.config.ts'],
  'webpack': ['webpack.config.js'],
  'rollup': ['rollup.config.js'],
  'babel': ['.babelrc*'],
  'next': ['next.config.js'],
  'nuxt': ['nuxt.config.js'],
  'svelte': ['svelte.config.js'],
  'tailwind': ['tailwind.config.js'],
  'bootstrap': ['bootstrap.config.js'],
  'sass': ['**/*.scss'],
  'less': ['**/*.less'],
  'stylus': ['**/*.styl'],
  'css': ['**/*.css'],
  'html': ['**/*.html'],
  'android': ['AndroidManifest.xml'],
  'ios': ['Info.plist'],
  'xcode': ['**/*.xcodeproj'],
  'gradle': ['build.gradle'],
  'maven': ['pom.xml'],
  'ant': ['build.xml'],
  'cmake': ['CMakeLists.txt'],
  'make': ['Makefile'],
  'julia': ['**/*.jl'],
  'haskell': ['**/*.hs'],
  'scala': ['**/*.scala'],
  'clojure': ['**/*.clj'],
  'elixir': ['**/*.ex'],
  'erlang': ['**/*.erl'],
  'lua': ['**/*.lua'],
  'perl': ['**/*.pl'],
  'tcl': ['**/*.tcl'],
  'vb': ['**/*.vb'],
  'fsharp': ['**/*.fs'],
  'ocaml': ['**/*.ml'],
  'lisp': ['**/*.lisp'],
  'scheme': ['**/*.scm'],
  'prolog': ['**/*.pl'],
  'fortran': ['**/*.f'],
  'cobol': ['**/*.cbl'],
  'pascal': ['**/*.pas'],
  'ada': ['**/*.adb'],
  'assembly': ['**/*.asm'],
  'verilog': ['**/*.v'],
  'vhdl': ['**/*.vhd'],
  'arduino': ['**/*.ino'],
  'raspberry': ['**/*.py'],
  'solidity': ['**/*.sol'],
  'vyper': ['**/*.vy'],
  'move': ['**/*.move'],
  'cairo': ['**/*.cairo'],
  'rust': ['**/*.rs']
};

function parseExtensionsFromHtml(htmlPath) {
  if (!fs.existsSync(htmlPath)) {
    console.error(`Error: File ${htmlPath} not found.`);
    return [];
  }

  const html = fs.readFileSync(htmlPath, 'utf8');
  const extensions = [];

  // Split by gcli-dialog to isolate extension blocks
  const chunks = html.split('<gcli-dialog');

  // Skip the first chunk (header/intro)
  for (let i = 1; i < chunks.length; i++) {
    const chunk = chunks[i];

    // Extract Name
    const nameMatch = chunk.match(/data-title="([^"]+)"/);
    if (!nameMatch) continue;
    const name = nameMatch[1];

    // Extract Repo/Install URL
    const repoMatch = chunk.match(/gemini extensions install\s+(https?:\/\/[^ <]+)/);
    const repo = repoMatch ? repoMatch[1] : '';

    // Extract Tags (look for badge-text spans)
    const tags = [];
    const tagRegex = /<span class="badge-text [^"]+">([^<]+)<\/span>/g;
    let tagMatch;
    while ((tagMatch = tagRegex.exec(chunk)) !== null) {
      tags.push(tagMatch[1].trim());
    }

    // Also try to find description for better context matching (optional)
    const descMatch = chunk.match(/class="extension-dialog__description[^"]*">\s*([^<]+)\s*<\/div>/);
    const description = descMatch ? descMatch[1].trim() : '';

    extensions.push({
      id: name, // Using name as ID
      name: name,
      repository: repo,
      tags: tags,
      description: description,
      // Attempt to infer category from tags or description
      category: tags.includes('MCP') ? 'mcp' : 'general'
    });
  }

  return extensions;
}

function generatePatterns() {
  const htmlPath = path.join(process.cwd(), 'extensions.html');
  console.log(`🔍 Scanning extensions from ${htmlPath}...`);

  const extensions = parseExtensionsFromHtml(htmlPath);
  console.log(`✅ Found ${extensions.length} extensions.`);

  const extensionPatterns = {};

  for (const ext of extensions) {
    const patterns = new Set();

    // 1. Check Tags
    if (ext.tags) {
      for (const tag of ext.tags) {
        const lowerTag = tag.toLowerCase();

        // Direct tag match
        if (TAG_PATTERNS[lowerTag]) {
          TAG_PATTERNS[lowerTag].forEach(p => patterns.add(p));
        }

        // Partial tag match (e.g. "context file" -> "context" is not mapped, but maybe relevant?)
        // Heuristic: check if any key in TAG_PATTERNS is part of the tag
        for (const key of Object.keys(TAG_PATTERNS)) {
          if (lowerTag.includes(key)) {
             TAG_PATTERNS[key].forEach(p => patterns.add(p));
          }
        }
      }
    }

    // 2. Check Name (if no patterns found yet, or to augment)
    const lowerName = ext.name.toLowerCase();

    // Direct name match in TAG_PATTERNS
    if (TAG_PATTERNS[lowerName]) {
       TAG_PATTERNS[lowerName].forEach(p => patterns.add(p));
    }

    // Check NAME_PATTERNS
    if (NAME_PATTERNS[lowerName]) {
      NAME_PATTERNS[lowerName].forEach(p => patterns.add(p));
    }

    // Partial name match - strictly for longer keys or word boundaries
    for (const key of Object.keys(TAG_PATTERNS)) {
      if (key.length <= 3) {
        // For short keys, require exact word match
        const regex = new RegExp(`\\b${key}\\b`);
        if (regex.test(lowerName)) {
           TAG_PATTERNS[key].forEach(p => patterns.add(p));
        }
      } else if (lowerName.includes(key)) {
         TAG_PATTERNS[key].forEach(p => patterns.add(p));
      }
    }
    for (const key of Object.keys(NAME_PATTERNS)) {
      if (key.length <= 3) {
        // For short keys, require exact word match
        const regex = new RegExp(`\\b${key}\\b`);
        if (regex.test(lowerName)) {
           NAME_PATTERNS[key].forEach(p => patterns.add(p));
        }
      } else if (lowerName.includes(key)) {
         NAME_PATTERNS[key].forEach(p => patterns.add(p));
      }
    }

    if (patterns.size > 0) {
      extensionPatterns[ext.id] = {
        name: ext.name,
        // If repo is available, use it as ID for installation
        id: ext.repository || ext.id,
        category: ext.category,
        patterns: Array.from(patterns)
      };
    }
  }

  const outputPath = path.join(__dirname, '../components/extension-patterns.json');
  fs.writeFileSync(outputPath, JSON.stringify(extensionPatterns, null, 2));
  console.log(`✨ Generated patterns for ${Object.keys(extensionPatterns).length} extensions.`);
  console.log(`💾 Saved to ${outputPath}`);
}

generatePatterns();
