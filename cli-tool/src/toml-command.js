/**
 * Minimal reader for Gemini CLI custom command files (.toml).
 * Commands only use two string fields, `description` and `prompt`, so a full
 * TOML parser is not needed.
 */

const COMMAND_EXTENSION = '.toml';

function unescapeBasicString(value) {
  return value.replace(/\\(["\\nt])/g, (_, ch) => (ch === 'n' ? '\n' : ch === 't' ? '\t' : ch));
}

/**
 * @param {string} content - Raw .toml command content
 * @returns {{description: string|null, prompt: string|null}}
 */
function parseCommandToml(content) {
  const result = { description: null, prompt: null };

  const descMatch = content.match(/^description\s*=\s*"((?:[^"\\\n]|\\.)*)"/m);
  if (descMatch) {
    try {
      result.description = JSON.parse(`"${descMatch[1]}"`);
    } catch (error) {
      result.description = unescapeBasicString(descMatch[1]);
    }
  }

  const multiBasic = content.match(/^prompt\s*=\s*"""\n?([\s\S]*?)"""\s*$/m);
  const multiLiteral = content.match(/^prompt\s*=\s*'''\n?([\s\S]*?)'''\s*$/m);
  const singleLine = content.match(/^prompt\s*=\s*"((?:[^"\\\n]|\\.)*)"/m);

  if (multiBasic) {
    result.prompt = unescapeBasicString(multiBasic[1]);
  } else if (multiLiteral) {
    result.prompt = multiLiteral[1];
  } else if (singleLine) {
    result.prompt = unescapeBasicString(singleLine[1]);
  }

  return result;
}

module.exports = { COMMAND_EXTENSION, parseCommandToml };
