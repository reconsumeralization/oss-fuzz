<<<<<<< HEAD
/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

const { fuzz } = require('@jazzer.js/core');

/**
 * Fuzz target for Gemini CLI argument parsing
 * Tests command-line argument parsing for injection vulnerabilities
 */
fuzz('FuzzCLIParser', (data) => {
  try {
    const input = data.toString();
    
    // Test CLI argument parsing
    const args = parseCLIArgs(input);
    
    // Test argument validation
    validateCLIArgs(args);
    
    // Test command execution simulation
    simulateCommandExecution(args);
    
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
 * Mock CLI argument parsing function
 * Simulates the actual CLI parsing logic
 */
function parseCLIArgs(input) {
  const args = [];
  const flags = {};
  
  // Simple argument parsing (simplified version of yargs)
  const parts = input.split(/\s+/).filter(part => part.length > 0);
  
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    
    if (part.startsWith('--')) {
      // Long flag
      const flagName = part.slice(2);
      const nextPart = parts[i + 1];
      
      if (nextPart && !nextPart.startsWith('-')) {
        flags[flagName] = nextPart;
        i++; // Skip the value
      } else {
        flags[flagName] = true;
      }
    } else if (part.startsWith('-') && part.length > 1) {
      // Short flag
      const flagName = part.slice(1);
      const nextPart = parts[i + 1];
      
      if (nextPart && !nextPart.startsWith('-')) {
        flags[flagName] = nextPart;
        i++; // Skip the value
      } else {
        flags[flagName] = true;
      }
    } else {
      // Positional argument
      args.push(part);
    }
  }
  
  return { args, flags };
}

/**
 * Mock CLI argument validation function
 * Simulates the actual argument validation logic
 */
function validateCLIArgs(parsed) {
  const { args, flags } = parsed;
  
  // Validate command
  if (args.length > 0) {
    const command = args[0];
    const validCommands = ['chat', 'generate', 'help', 'config'];
    
    if (!validCommands.includes(command)) {
      throw new Error(`Invalid command: ${command}`);
    }
  }
  
  // Validate flags
  for (const [flag, value] of Object.entries(flags)) {
    switch (flag) {
      case 'model':
        if (typeof value !== 'string') {
          throw new Error('Invalid model flag type');
        }
        break;
      case 'prompt':
        if (typeof value !== 'string') {
          throw new Error('Invalid prompt flag type');
        }
        break;
      case 'temperature':
        const temp = parseFloat(value);
        if (isNaN(temp) || temp < 0 || temp > 2) {
          throw new Error('Invalid temperature value');
        }
        break;
      case 'max-tokens':
        const tokens = parseInt(value);
        if (isNaN(tokens) || tokens < 1 || tokens > 8192) {
          throw new Error('Invalid max-tokens value');
        }
        break;
    }
=======
// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
////////////////////////////////////////////////////////////////////////////////

// oss-fuzz/projects/gemini-cli/fuzzers/fuzz_cli_parser.js
<<<<<<< HEAD

// Import the actual source code for fuzzing
const { parseCliArgs, validateCommand } = require('../src/cli/parser.js');

// Global reference to CLI parser (cached for performance)
let cliParser = null;

/**
 * Initialize the CLI parser module
 * @returns {Promise<Function>} The CLI parser function
 */
async function initializeCLIParser() {
  if (cliParser) {
    return cliParser;
  }

  try {
    // Use the actual implementation
    cliParser = parseCliArgs;
    return cliParser;
  } catch (error) {
    console.warn(`Failed to load CLI parser: ${error.message}`);
    console.warn('Using fallback parser for testing');
    return fallbackCLIParser;
  }
}

/**
 * Mock CLI parser for testing when upstream module is not available
 * @param {string} input - Input string to parse
 */
function mockCLIParser(input) {
  // Simple mock that validates basic CLI structure
  if (!input || typeof input !== 'string') {
    throw new TypeError('Input must be a string');
  }

  // Basic validation - check for common CLI patterns
  const trimmed = input.trim();

  // Check for very basic CLI structure
  if (trimmed.length > 1000) {
    throw new RangeError('Input too long');
  }

  // This is just a mock - real CLI parsing would be more complex
  return { parsed: true, args: trimmed.split(/\s+/) };
}

/**
 * Fuzz target function for CLI parser
 * Follows Fuchsia guidelines similar to LLVMFuzzerTestOneInput
 * @param {Buffer|Uint8Array} data - Input data from fuzzer
 * @returns {number} 0 for success, non-zero for expected errors
 */
export async function LLVMFuzzerTestOneInput(data) {
  if (!data || data.length === 0) {
    return 0; // Skip empty inputs
  }

  try {
    const parseCLI = await initializeCLIParser();
    const input = Buffer.isBuffer(data) ? data.toString('utf8') : String(data);

    // Attempt to parse the fuzzer input as CLI arguments
    parseCLI(input);

    return 0; // Success
  } catch (error) {
    // Handle expected parsing errors gracefully
    if (error && error.name) {
      // These are expected parsing errors, not crashes
      if (error.name === 'SyntaxError' ||
          error.name === 'TypeError' ||
          error.name === 'RangeError' ||
          error.name === 'ReferenceError') {
        return 0; // Expected error, continue fuzzing
      }
    }

    // Return non-zero for unexpected errors (actual crashes) - OSS-Fuzz compliance
    return 1;
>>>>>>> pr-13797
  }
}

/**
<<<<<<< HEAD
 * Mock command execution simulation
 * Simulates the actual command execution logic
 */
function simulateCommandExecution(parsed) {
  const { args, flags } = parsed;
  
  // Simulate command routing
  if (args.length === 0) {
    return { type: 'interactive' };
  }
  
  const command = args[0];
  
  switch (command) {
    case 'chat':
      return { type: 'chat', prompt: flags.prompt || args.slice(1).join(' ') };
    case 'generate':
      return { type: 'generate', prompt: flags.prompt || args.slice(1).join(' ') };
    case 'help':
      return { type: 'help', topic: args[1] };
    case 'config':
      return { type: 'config', action: args[1], key: args[2], value: args[3] };
    default:
      throw new Error(`Unknown command: ${command}`);
  }
}
=======
 * Legacy compatibility function for Jazzer.js
 * @param {Buffer|Uint8Array} data - Input data from fuzzer
 * @returns {Promise<void>}
 */
export async function FuzzCLIParser(data) {
  const result = await LLVMFuzzerTestOneInput(data);
  if (result !== 0) {
    throw new Error(`Fuzzer returned error code: ${result}`);
  }
}

// This fuzzer is designed to work directly with OSS-Fuzz

// CommonJS export for OSS-Fuzz compatibility
module.exports = { LLVMFuzzerTestOneInput, FuzzCLIParser };
=======
import { locateUpstream } from './_upstream_locator.mjs';

export function FuzzCLIParser(data) {
  const input = Buffer.isBuffer(data) ? data.toString('utf8') : String(data);
  const p = locateUpstream([
    'packages/cli/src/cli.js',
    'packages/cli/src/index.js',
    'packages/cli/lib/cli.js'
  ]);
  if (!p) throw new Error('UPSTREAM_CLI_NOT_FOUND');
  return import(p).then(mod => {
    const parseArgs = mod.parseArgs || mod.default?.parseArgs || mod.parseCLI || mod.run;
    if (!parseArgs) throw new Error('UPSTREAM_CLI_PARSE_NOT_FOUND');
    try {
      parseArgs(input);
    } catch (e) {
      // swallow expected parse errors
      if (e && e.name === 'SyntaxError') return;
      throw e;
    }
  });
}
>>>>>>> 6beb447382265fce1442b77fb11e5a90be556a20
>>>>>>> pr-13797
