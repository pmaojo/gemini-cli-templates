const chalk = require('chalk');
const { execSync } = require('child_process');

/**
 * Install a list of extensions
 * @param {string[]} extensions - List of extension URLs to install
 * @param {Object} options - Installation options
 */
function installExtensions(extensions, options = {}) {
  if (!extensions || extensions.length === 0) {
    return;
  }

  console.log(chalk.yellow('🧩 Installing recommended extensions...'));
  
  // Check if gemini command exists
  let geminiAvailable = false;
  try {
    execSync('which gemini', { stdio: 'ignore' });
    geminiAvailable = true;
  } catch (e) {
    console.log(chalk.yellow('  ⚠️  Gemini CLI not found in PATH. Skipping auto-installation of extensions.'));
    console.log(chalk.gray('  To install them manually, run: gemini extensions install <url>'));
  }

  if (geminiAvailable) {
    for (const extensionUrl of extensions) {
      try {
        console.log(chalk.gray(`  Installing ${extensionUrl.split('/').pop()}...`));
        // If the command requires interaction, stdio: inherit allows the user to interact
        execSync(`gemini extensions install ${extensionUrl}`, { stdio: 'inherit' });
      } catch (error) {
        console.log(chalk.yellow(`  ⚠️  Could not auto-install extension: ${error.message.split('\n')[0]}`));
        console.log(chalk.gray(`  Please install manually: gemini extensions install ${extensionUrl}`));
      }
    }
  }
}

module.exports = {
  installExtensions
};
