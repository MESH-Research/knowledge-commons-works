#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const LANGUAGES = ['en'];
const MESSAGES_DIR = path.join(__dirname, '..', 'messages');
const POT_FILE = path.join(__dirname, '..', 'translations.pot');

// Create messages directory if it doesn't exist
if (!fs.existsSync(MESSAGES_DIR)) {
  fs.mkdirSync(MESSAGES_DIR, { recursive: true });
}

// Process each language
LANGUAGES.forEach(lang => {
  const langDir = path.join(MESSAGES_DIR, lang);
  const poFile = path.join(langDir, 'messages.po');

  // Create language directory if it doesn't exist
  if (!fs.existsSync(langDir)) {
    fs.mkdirSync(langDir, { recursive: true });
  }

  // Initialize .po file from .pot
  if (fs.existsSync(POT_FILE)) {
    try {
      execSync(`msginit --no-translator -i ${POT_FILE} -o ${poFile} -l ${lang}`);
      console.log(`Successfully initialized ${lang} translations`);
    } catch (error) {
      console.error(`Error initializing ${lang} translations:`, error);
    }
  } else {
    console.warn('No .pot file found. Please run extract_messages first.');
  }
});