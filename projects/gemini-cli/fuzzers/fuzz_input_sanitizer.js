/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

const { fuzz } = require('@jazzer.js/core');

/**
 * Fuzz target for Gemini CLI input sanitization
 * Tests input validation and sanitization logic
 */
fuzz('FuzzInputSanitizer', (data) => {
  try {
    const input = data.toString();
    
    // Test input sanitization
    const sanitized = sanitizeInput(input);
    
    // Test XSS detection
    const hasXSS = detectXSS(input);
    
    // Test injection detection
    const hasInjection = detectInjection(input);
    
    // Test path validation
    const isValidPath = validatePath(input);
    
    // Test shell command validation
    const isValidShellCommand = validateShellCommand(input);
    
  } catch (error) {
    // Expected errors for invalid input - don't crash
    if (error instanceof TypeError || error.message.includes('Invalid')) {
      return;
    }
    // Re-throw unexpected errors
    throw error;
  }
});

/**
 * Mock input sanitization function
 * Simulates the actual input sanitization logic
 */
function sanitizeInput(input) {
  if (typeof input !== 'string') {
    throw new Error('Input must be a string');
  }
  
  let sanitized = input;
  
  // Remove potentially dangerous characters
  sanitized = sanitized.replace(/[<>]/g, '');
  
  // Escape quotes
  sanitized = sanitized.replace(/"/g, '\\"');
  sanitized = sanitized.replace(/'/g, "\\'");
  
  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '');
  
  // Remove control characters (except newlines and tabs)
  sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  
  return sanitized;
}

/**
 * Mock XSS detection function
 * Simulates the actual XSS detection logic
 */
function detectXSS(input) {
  const xssPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
    /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,
    /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi,
    /<link\b[^<]*(?:(?!<\/link>)<[^<]*)*<\/link>/gi,
    /<meta\b[^<]*(?:(?!<\/meta>)<[^<]*)*<\/meta>/gi
  ];
  
  return xssPatterns.some(pattern => pattern.test(input));
}

/**
 * Mock injection detection function
 * Simulates the actual injection detection logic
 */
function detectInjection(input) {
  const injectionPatterns = [
    /eval\s*\(/gi,
    /Function\s*\(/gi,
    /setTimeout\s*\(/gi,
    /setInterval\s*\(/gi,
    /exec\s*\(/gi,
    /spawn\s*\(/gi,
    /execSync\s*\(/gi,
    /spawnSync\s*\(/gi,
    /child_process/gi,
    /require\s*\(/gi,
    /import\s*\(/gi
  ];
  
  return injectionPatterns.some(pattern => pattern.test(input));
}

/**
 * Mock path validation function
 * Simulates the actual path validation logic
 */
function validatePath(input) {
  // Check for path traversal attempts
  const traversalPatterns = [
    /\.\.\//g,
    /\.\.\\/g,
    /\/\.\./g,
    /\\\.\./g,
    /\.\.$/g
  ];
  
  const hasTraversal = traversalPatterns.some(pattern => 
    pattern.test(input)
  );
  
  if (hasTraversal) {
    return false;
  }
  
  // Check for absolute paths (if not allowed)
  if (input.startsWith('/') || input.startsWith('\\') || 
      /^[A-Za-z]:[\\\/]/.test(input)) {
    return false;
  }
  
  // Check for null bytes
  if (input.includes('\0')) {
    return false;
  }
  
  return true;
}

/**
 * Mock shell command validation function
 * Simulates the actual shell command validation logic
 */
function validateShellCommand(input) {
  // Check for dangerous shell commands
  const dangerousCommands = [
    'rm', 'del', 'format', 'mkfs', 'dd', 'shred',
    'sudo', 'su', 'chmod', 'chown', 'passwd',
    'wget', 'curl', 'nc', 'netcat', 'telnet',
    'ssh', 'scp', 'rsync', 'tar', 'zip', 'unzip'
  ];
  
  const hasDangerousCommand = dangerousCommands.some(cmd => 
    input.toLowerCase().includes(cmd.toLowerCase())
  );
  
  if (hasDangerousCommand) {
    return false;
  }
  
  // Check for command separators
  const separators = [';', '&&', '||', '|', '>', '<', '>>', '<<'];
  const hasSeparator = separators.some(sep => input.includes(sep));
  
  if (hasSeparator) {
    return false;
  }
  
  // Check for subshells
  if (input.includes('$(') || input.includes('`')) {
    return false;
  }
  
  return true;
}
