// Copyright 2025 Google LLC
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Minimal placeholder fuzzer that feeds arbitrary bytes into a CLI-like parser.
// Replace the parse logic with real gemini-cli parsing once upstream is linked.

function parseArgs(input) {
	// Very simple tokenizer to simulate CLI splitting
	const str = input.toString('utf8');
	// Split on whitespace while keeping quoted segments somewhat intact
	const tokens = [];
	let current = '';
	let inQuote = false;
	for (let i = 0; i < str.length; i++) {
		const ch = str[i];
		if (ch === '"') {
			inQuote = !inQuote;
			continue;
		}
		if (!inQuote && /\s/.test(ch)) {
			if (current.length > 0) tokens.push(current);
			current = '';
			continue;
		}
		current += ch;
	}
	if (current.length > 0) tokens.push(current);
	return tokens.slice(0, 64);
}

module.exports.fuzz = function (data) {
	if (!data || data.length === 0) return;
	const args = parseArgs(data);
	// Simulate option handling
	const options = new Map();
	for (const tok of args) {
		if (tok.startsWith('--')) {
			const [k, v] = tok.slice(2).split('=');
			options.set(k || '', v || '');
		}
	}
	// Trigger edge cases
	if (options.has('help') && options.get('help').length > 1000) {
		throw new Error('help overflow');
	}
	if (options.has('model') && /\u0000/.test(options.get('model'))) {
		throw new Error('NUL in model');
	}
};