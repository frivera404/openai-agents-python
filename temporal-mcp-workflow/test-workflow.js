#!/usr/bin/env node

/**
 * Temporal MCP Workflow Test Script
 *
 * This script demonstrates the MCP Scaffold Deploy Workflow
 * Make sure Temporal server is running and worker is started
 */

const { execSync } = require('child_process');
const path = require('path');

console.log('🚀 Temporal MCP Workflow Test');
console.log('==============================\n');

// Check if dist directory exists
const distDir = path.join(__dirname, 'dist');
const fs = require('fs');

if (!fs.existsSync(distDir)) {
  console.log('❌ Build output not found. Run "npm run build" first.');
  process.exit(1);
}

console.log('✅ Build artifacts found');

// Check for required environment variables
const requiredEnvVars = ['OPENAI_API_KEY'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.log('⚠️  Missing environment variables:');
  missingVars.forEach(varName => console.log(`   - ${varName}`));
  console.log('   Using .env.runlimited or set manually\n');
} else {
  console.log('✅ Environment variables configured');
}

// Instructions for running
console.log('📋 To test the workflow:');
console.log('');
console.log('1. Start Temporal server (if not running):');
console.log('   temporal server start-dev');
console.log('');
console.log('2. Start the worker in another terminal:');
console.log('   npm run start:worker');
console.log('');
console.log('3. Run the client to start a workflow:');
console.log('   npm run start:client');
console.log('');
console.log('4. Monitor workflow progress:');
console.log('   npm run query:status -- --workflow-id <workflow-id>');
console.log('   npm run query:logs -- --workflow-id <workflow-id>');
console.log('');
console.log('5. Control workflow (optional):');
console.log('   npm run signal:cancel -- --workflow-id <workflow-id>');
console.log('   npm run signal:update -- --workflow-id <workflow-id> --input \'{"lang":"node"}\'');
console.log('');

console.log('🎯 Workflow will:');
console.log('   • Plan MCP server specifications');
console.log('   • Scaffold repository structure');
console.log('   • Implement requested tools (get_status, openai_chat, list_files)');
console.log('   • Wire OpenAI integration');
console.log('   • Run smoke tests');
console.log('   • Package Docker image');
console.log('   • Deploy to Cloud Run (if configured)');
console.log('   • Record deployment metadata');
console.log('');

console.log('📁 Generated MCP server will be created in: /workspace/mcp');
console.log('🔧 Tools implemented: get_status, openai_chat, list_files');
console.log('🏗️  Languages supported: Python, Node.js');
console.log('');

console.log('✨ Ready to deploy MCP servers at scale!');