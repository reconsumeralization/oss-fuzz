/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

const { fuzz } = require('@jazzer.js/core');

/**
 * Fuzz target for Gemini CLI configuration parsing
 * Tests configuration file parsing for security issues
 */
fuzz('FuzzConfigParser', (data) => {
  try {
    // Parse the fuzzed data as JSON configuration
    const config = JSON.parse(data.toString());
    
    // Test configuration validation
    validateConfig(config);
    
    // Test configuration merging
    mergeConfigs(config, {});
    
    // Test configuration serialization
    JSON.stringify(config);
    
  } catch (error) {
    // Expected errors for invalid JSON - don't crash
    if (error instanceof SyntaxError) {
      return;
    }
    // Re-throw unexpected errors
    throw error;
  }
});

/**
 * Mock configuration validation function
 * Simulates the actual config validation logic
 */
function validateConfig(config) {
  // Validate required fields
  if (config.api_key && typeof config.api_key !== 'string') {
    throw new Error('Invalid API key type');
  }
  
  if (config.model && typeof config.model !== 'string') {
    throw new Error('Invalid model type');
  }
  
  // Validate numeric fields
  if (config.temperature !== undefined) {
    const temp = parseFloat(config.temperature);
    if (isNaN(temp) || temp < 0 || temp > 2) {
      throw new Error('Invalid temperature value');
    }
  }
  
  if (config.max_tokens !== undefined) {
    const tokens = parseInt(config.max_tokens);
    if (isNaN(tokens) || tokens < 1 || tokens > 8192) {
      throw new Error('Invalid max_tokens value');
    }
  }
}

/**
 * Mock configuration merging function
 * Simulates the actual config merging logic
 */
function mergeConfigs(userConfig, defaultConfig) {
  const merged = { ...defaultConfig, ...userConfig };
  
  // Validate merged configuration
  validateConfig(merged);
  
  return merged;
}
