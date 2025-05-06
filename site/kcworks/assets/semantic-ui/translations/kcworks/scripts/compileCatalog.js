#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const LANGUAGES = ['en'];
const MESSAGES_DIR = path.join(__dirname, '..', 'messages');

// Create messages directory if it doesn't exist
if (!fs.existsSync(MESSAGES_DIR)) {
  fs.mkdirSync(MESSAGES_DIR, { recursive: true });
}

// Process each language
LANGUAGES.forEach(lang => {
  const langDir = path.join(MESSAGES_DIR, lang);
  const poFile = path.join(langDir, 'messages.po');
  const jsonFile = path.join(langDir, 'translations.json');

  // Create language directory if it doesn't exist
  if (!fs.existsSync(langDir)) {
    fs.mkdirSync(langDir, { recursive: true });
  }

  // Convert .po to .json
  if (fs.existsSync(poFile)) {
    try {
      execSync(`i18next-conv -l ${lang} -s ${poFile} -t ${jsonFile}`);
      console.log(`Successfully compiled ${lang} translations`);
    } catch (error) {
      console.error(`Error compiling ${lang} translations:`, error);
    }
  } else {
    console.warn(`No .po file found for ${lang}`);
  }
});