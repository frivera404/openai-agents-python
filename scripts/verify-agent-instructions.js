#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.join(__dirname, '..');
const serverTs = path.join(root, 'server.ts');

if (!fs.existsSync(serverTs)) {
  console.error('server.ts not found at', serverTs);
  process.exit(2);
}

const content = fs.readFileSync(serverTs, 'utf8');
const marker = 'const agentInstructions';
const idx = content.indexOf(marker);
if (idx === -1) {
  console.error('Could not find "const agentInstructions" in server.ts');
  process.exit(2);
}

// Find the opening '{' after the '=' sign and parse until matching '}'
let eq = content.indexOf('=', idx);
if (eq === -1) eq = content.indexOf('{', idx);
const braceStart = content.indexOf('{', eq);
if (braceStart === -1) {
  console.error('Could not find opening brace for agentInstructions');
  process.exit(2);
}

let i = braceStart;
let depth = 0;
let inSingle = false;
let inDouble = false;
let inTemplate = false;
let escaped = false;
let endIndex = -1;

for (; i < content.length; i++) {
  const ch = content[i];
  if (escaped) { escaped = false; continue; }
  if (ch === '\\') { escaped = true; continue; }
  if (inSingle) {
    if (ch === "'") inSingle = false;
    continue;
  }
  if (inDouble) {
    if (ch === '"') inDouble = false;
    continue;
  }
  if (inTemplate) {
    if (ch === '`') inTemplate = false;
    continue;
  }
  if (ch === "'") { inSingle = true; continue; }
  if (ch === '"') { inDouble = true; continue; }
  if (ch === '`') { inTemplate = true; continue; }
  if (ch === '{') { depth++; continue; }
  if (ch === '}') { depth--; if (depth === 0) { endIndex = i; break; } }
}

if (endIndex === -1) {
  console.error('Failed to locate end of agentInstructions object');
  process.exit(2);
}

const objText = content.slice(braceStart, endIndex + 1);

// Evaluate the object literal in a safe VM context
let agentInstructions;
try {
  // Wrap in parentheses to make it an expression
  agentInstructions = vm.runInNewContext('(' + objText + ')', {}, { timeout: 1000 });
} catch (err) {
  console.error('Failed to evaluate agentInstructions object:', err);
  process.exit(2);
}

const keys = Object.keys(agentInstructions || {});
console.log('Found agentInstructions keys:', keys.join(', '));
console.log('Count:', keys.length);

// Save a snapshot for inspection
const outPath = path.join(root, 'scripts', 'agentInstructions.snapshot.json');
fs.writeFileSync(outPath, JSON.stringify({ keys, instructions: agentInstructions }, null, 2), 'utf8');
console.log('Snapshot written to', outPath);

// Print a short preview of each instruction (first 120 chars)
for (const k of keys) {
  const v = agentInstructions[k];
  const preview = typeof v === 'string' ? v.replace(/\s+/g, ' ').slice(0, 120) : String(v);
  console.log(`- ${k}: ${preview}${preview.length >= 120 ? '…' : ''}`);
}

console.log('VERIFY: agentInstructions object validated successfully.');
