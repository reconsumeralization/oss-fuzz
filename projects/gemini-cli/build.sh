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
# Phase 1: Basic Go fuzzing with 3 essential fuzz targets

echo "Building Gemini CLI foundation fuzzers (Phase 1)..."

# Move into project directory
cd /src/projects/gemini-cli

# Initialize Go module if needed
if [ ! -f gofuzz/go.mod ]; then
  echo "Initializing Go module..."
  cd gofuzz
  go mod init github.com/google-gemini/gemini-cli/gofuzz
  cd ..
fi

# Build foundation fuzz targets (Phase 1)
echo "Building foundation fuzz targets..."

cd gofuzz
go mod tidy
go mod download

# Foundation fuzz targets - minimal set for Phase 1
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzConfigParser fuzz_config_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzCLIParser fuzz_cli_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzInputSanitizer fuzz_input_sanitizer

cd ..

echo "Foundation fuzz targets built successfully!"

# Create basic seed corpora for foundation targets
echo "Creating foundation seed corpora..."

mkdir -p seeds/foundation

# Config parser seeds
echo '{"api_key": "test_key", "model": "gemini-pro"}' > seeds/foundation/config_valid.json
echo '{}' > seeds/foundation/config_empty.json

# CLI parser seeds
echo 'gemini chat "Hello world"' > seeds/foundation/cli_valid.txt
echo 'gemini --help' > seeds/foundation/cli_help.txt

# Input sanitizer seeds
echo 'normal_input' > seeds/foundation/input_normal.txt
echo '<script>alert("xss")</script>' > seeds/foundation/input_xss.txt

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
  "gemini-pro-vision": "string"
}
EOF

cat > $OUT/fuzz_cli_parser.dict << 'EOF'
{
  "gemini": "string",
  "chat": "string",
  "help": "string",
  "--": "string"
}
EOF

cat > $OUT/fuzz_input_sanitizer.dict << 'EOF'
{
  "<script>": "string",
  "javascript:": "string",
  "onerror=": "string",
  "onload=": "string"
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
