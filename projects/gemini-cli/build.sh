#!/bin/bash -eu
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################

# Build script for OSS-Fuzz - Gemini CLI Foundation Setup
# Phase 1: Basic TypeScript/JavaScript fuzzing with Jazzer.js

echo "Building Gemini CLI foundation fuzzers (Phase 1)..."

# Move into project directory
cd /src/gemini-cli

# Install dependencies
echo "Installing dependencies..."
npm install

# Install Jazzer.js for fuzzing
echo "Installing Jazzer.js..."
npm install --save-dev @jazzer.js/core

# Build TypeScript code
echo "Building TypeScript code..."
npm run build

# Build foundation fuzz targets (Phase 1)
echo "Building foundation fuzz targets..."

# Create fuzzers directory if it doesn't exist
mkdir -p fuzzers

# Build foundation fuzz targets - TypeScript/JavaScript
compile_javascript_fuzzer fuzzers fuzz_config_parser.js --sync
compile_javascript_fuzzer fuzzers fuzz_cli_parser.js --sync
compile_javascript_fuzzer fuzzers fuzz_input_sanitizer.js --sync

echo "Foundation fuzz targets built successfully!"

# Create basic seed corpora for foundation targets
echo "Creating foundation seed corpora..."

mkdir -p seeds/foundation

# Config parser seeds
echo '{"api_key": "test_key", "model": "gemini-pro"}' > seeds/foundation/config_valid.json
echo '{}' > seeds/foundation/config_empty.json
echo '{"invalid": "json", "missing": "quote}' > seeds/foundation/config_invalid.json

# CLI parser seeds
echo 'gemini chat "Hello world"' > seeds/foundation/cli_valid.txt
echo 'gemini --help' > seeds/foundation/cli_help.txt
echo 'gemini --invalid-flag' > seeds/foundation/cli_invalid.txt

# Input sanitizer seeds
echo 'normal_input' > seeds/foundation/input_normal.txt
echo '<script>alert("xss")</script>' > seeds/foundation/input_xss.txt
echo 'javascript:alert("injection")' > seeds/foundation/input_injection.txt

# Package seed corpora
if [ -d "seeds" ]; then
  echo "Packaging foundation seed corpora..."
  cp -r seeds/* $OUT/
fi

# Create basic dictionary for foundation targets
echo "Creating foundation dictionary..."
cat > $OUT/fuzz_config_parser.dict << 'EOF'
{
  "api_key": "string",
  "model": "string",
  "gemini-pro": "string",
  "gemini-pro-vision": "string",
  "temperature": "number",
  "max_tokens": "number"
}
EOF

cat > $OUT/fuzz_cli_parser.dict << 'EOF'
{
  "gemini": "string",
  "chat": "string",
  "help": "string",
  "--": "string",
  "--model": "string",
  "--prompt": "string"
}
EOF

cat > $OUT/fuzz_input_sanitizer.dict << 'EOF'
{
  "<script>": "string",
  "javascript:": "string",
  "onerror=": "string",
  "onload=": "string",
  "eval(": "string"
}
EOF

# Create basic options files
echo "Creating foundation options files..."
cat > $OUT/fuzz_config_parser.options << 'EOF'
[libfuzzer]
max_len = 1024
EOF

cat > $OUT/fuzz_cli_parser.options << 'EOF'
[libfuzzer]
max_len = 512
EOF

cat > $OUT/fuzz_input_sanitizer.options << 'EOF'
[libfuzzer]
max_len = 2048
EOF

echo "Foundation setup complete! Ready for Phase 2 expansion."
