#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const MESSAGES_DIR = path.join(__dirname, '..', 'messages');
const LANGUAGES = ['en']; // Add more languages as needed

// Function to escape strings for PO files
function escapePoString(str) {
  return str
    .replace(/\\/g, '\\\\')  // Escape backslashes
    .replace(/"/g, '\\"')    // Escape quotes
    .replace(/\n/g, '\\n')   // Escape newlines
    .replace(/\t/g, '\\t');  // Escape tabs
}

// Create messages directory if it doesn't exist
if (!fs.existsSync(MESSAGES_DIR)) {
  fs.mkdirSync(MESSAGES_DIR, { recursive: true });
}

// Process each language
LANGUAGES.forEach(lang => {
  const langDir = path.join(MESSAGES_DIR, lang);
  const jsonFile = path.join(langDir, 'translations.json');
  const poFile = path.join(langDir, 'messages.po');

  // Create language directory if it doesn't exist
  if (!fs.existsSync(langDir)) {
    fs.mkdirSync(langDir, { recursive: true });
  }

  if (fs.existsSync(jsonFile)) {
    try {
      // Read the JSON file
      const translations = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));

      if (!translations || typeof translations !== 'object') {
        console.error(`Invalid JSON structure in ${jsonFile}. Expected an object with key/value pairs.`);
        return;
      }

      // Create a temporary file with msgid/msgstr pairs
      const tempFile = path.join(langDir, 'temp.po');
      let poContent = `msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Language: ${lang}\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"\\n"

`;

      // Add each translation
      Object.entries(translations).forEach(([key, value]) => {
        poContent += `msgid "${escapePoString(key)}"\n`;
        poContent += `msgstr "${escapePoString(value)}"\n\n`;
      });

      // Write the temporary file
      fs.writeFileSync(tempFile, poContent);

      // Use msgfmt to validate and format the PO file
      try {
        execSync(`msgfmt -o /dev/null ${tempFile}`);
        fs.renameSync(tempFile, poFile);
        console.log(`Successfully created ${poFile}`);
      } catch (error) {
        console.error(`Error validating PO file for ${lang}:`, error.message);
        fs.unlinkSync(tempFile);
      }
    } catch (error) {
      console.error(`Error processing ${jsonFile}:`, error.message);
    }
  } else {
    console.warn(`No JSON file found for ${lang}`);
  }
});