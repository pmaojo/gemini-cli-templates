/**
 * Extension Scanner Module
 * Dynamically loads and manages Gemini CLI extensions from JSON files
 */

const fs = require('fs');
const path = require('path');

const EXTENSIONS_DIR = path.join(__dirname, '../components/extensions');

/**
 * Get all available extension categories
 * @returns {string[]} Array of category names
 */
function getExtensionCategories() {
  if (!fs.existsSync(EXTENSIONS_DIR)) {
    return [];
  }
  
  return fs.readdirSync(EXTENSIONS_DIR)
    .filter(item => {
      const itemPath = path.join(EXTENSIONS_DIR, item);
      return fs.statSync(itemPath).isDirectory();
    });
}

/**
 * Load all extensions from a specific category
 * @param {string} category - Category name (e.g., 'productivity', 'database')
 * @returns {Object[]} Array of extension objects
 */
function getExtensionsByCategory(category) {
  const categoryPath = path.join(EXTENSIONS_DIR, category);
  
  if (!fs.existsSync(categoryPath)) {
    return [];
  }
  
  const extensions = [];
  const files = fs.readdirSync(categoryPath).filter(f => f.endsWith('.json'));
  
  for (const file of files) {
    try {
      const content = fs.readFileSync(path.join(categoryPath, file), 'utf8');
      const extension = JSON.parse(content);
      extension.id = path.basename(file, '.json');
      extension.category = category;
      extensions.push(extension);
    } catch (error) {
      console.error(`Error loading extension ${file}:`, error.message);
    }
  }
  
  return extensions;
}

/**
 * Get all available extensions
 * @returns {Object[]} Array of all extension objects
 */
function getAllExtensions() {
  const categories = getExtensionCategories();
  let allExtensions = [];
  
  for (const category of categories) {
    const extensions = getExtensionsByCategory(category);
    allExtensions = allExtensions.concat(extensions);
  }
  
  return allExtensions;
}

/**
 * Get recommended extensions (for default installation)
 * @returns {Object[]} Array of recommended extension objects
 */
function getRecommendedExtensions() {
  return getAllExtensions().filter(ext => ext.recommended === true);
}

/**
 * Search extensions by query (matches name, displayName, description, or tags)
 * @param {string} query - Search query
 * @returns {Object[]} Array of matching extension objects
 */
function searchExtensions(query) {
  const lowerQuery = query.toLowerCase();
  
  return getAllExtensions().filter(ext => {
    const searchableText = [
      ext.name,
      ext.displayName,
      ext.description,
      ...(ext.tags || [])
    ].join(' ').toLowerCase();
    
    return searchableText.includes(lowerQuery);
  });
}

/**
 * Get extension by ID
 * @param {string} id - Extension ID (filename without .json)
 * @returns {Object|null} Extension object or null if not found
 */
function getExtensionById(id) {
  const categories = getExtensionCategories();
  
  for (const category of categories) {
    const filePath = path.join(EXTENSIONS_DIR, category, `${id}.json`);
    if (fs.existsSync(filePath)) {
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const extension = JSON.parse(content);
        extension.id = id;
        extension.category = category;
        return extension;
      } catch (error) {
        return null;
      }
    }
  }
  
  return null;
}

/**
 * Get extensions formatted for inquirer checkbox prompt
 * @param {Object} options - Options for filtering
 * @param {string} [options.category] - Filter by category
 * @param {boolean} [options.recommendedOnly] - Only show recommended extensions
 * @returns {Object[]} Array of inquirer choice objects
 */
function getExtensionsForPrompt(options = {}) {
  let extensions = options.category 
    ? getExtensionsByCategory(options.category)
    : getAllExtensions();
  
  if (options.recommendedOnly) {
    extensions = extensions.filter(ext => ext.recommended);
  }
  
  // Sort: recommended first, then alphabetically
  extensions.sort((a, b) => {
    if (a.recommended && !b.recommended) return -1;
    if (!a.recommended && b.recommended) return 1;
    return a.displayName.localeCompare(b.displayName);
  });
  
  return extensions.map(ext => ({
    name: `${ext.displayName} - ${ext.description}`,
    value: ext.repository,
    checked: ext.recommended,
    short: ext.displayName
  }));
}

/**
 * Get extension count by category
 * @returns {Object} Object with category names as keys and counts as values
 */
function getExtensionStats() {
  const categories = getExtensionCategories();
  const stats = {
    total: 0,
    recommended: 0,
    byCategory: {}
  };
  
  for (const category of categories) {
    const extensions = getExtensionsByCategory(category);
    stats.byCategory[category] = extensions.length;
    stats.total += extensions.length;
    stats.recommended += extensions.filter(e => e.recommended).length;
  }
  
  return stats;
}

module.exports = {
  getExtensionCategories,
  getExtensionsByCategory,
  getAllExtensions,
  getRecommendedExtensions,
  searchExtensions,
  getExtensionById,
  getExtensionsForPrompt,
  getExtensionStats,
  EXTENSIONS_DIR
};
