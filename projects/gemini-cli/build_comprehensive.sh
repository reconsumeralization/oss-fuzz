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
# Comprehensive build script for Gemini CLI OSS-Fuzz integration
# Dual-language approach: TypeScript/JavaScript (primary) + Go (enhanced security)
################################################################################

set -euxo pipefail

echo "=== Gemini CLI Comprehensive OSS-Fuzz Build ==="
echo "Building dual-language fuzzers with advanced security focus"

# Environment setup
export CGO_ENABLED=1
export GOPROXY=https://proxy.golang.org,direct
export GOSUMDB=sum.golang.org

# Verify environment
echo "Build environment:"
echo "  SRC=$SRC"
echo "  OUT=$OUT"
echo "  CC=$CC"
echo "  CXX=$CXX"
echo "  CFLAGS=$CFLAGS"
echo "  CXXFLAGS=$CXXFLAGS"
echo "  LIB_FUZZING_ENGINE=$LIB_FUZZING_ENGINE"

# Navigate to project directory
cd "$SRC/gemini-cli"

# Phase 1: Build TypeScript/JavaScript fuzzers (Primary)
echo "=== Phase 1: Building TypeScript/JavaScript Fuzzers ==="

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install
npm install --save-dev @jazzer.js/core

# Build TypeScript code
echo "Building TypeScript code..."
npm run build

# Create fuzzers directory if it doesn't exist
mkdir -p fuzzers

# Build foundation fuzz targets (Phase 1)
echo "Building foundation fuzz targets..."
compile_javascript_fuzzer fuzzers fuzz_config_parser.js --sync
compile_javascript_fuzzer fuzzers fuzz_cli_parser.js --sync
compile_javascript_fuzzer fuzzers fuzz_input_sanitizer.js --sync

# Build enhanced fuzz targets (Phase 2)
echo "Building enhanced fuzz targets..."
compile_javascript_fuzzer fuzzers fuzz_env_parser.js --sync
compile_javascript_fuzzer fuzzers fuzz_file_path_handler.js --sync
compile_javascript_fuzzer fuzzers fuzz_http_request_parser.js --sync
compile_javascript_fuzzer fuzzers fuzz_mcp_request.js --sync
compile_javascript_fuzzer fuzzers fuzz_mcp_response.js --sync
compile_javascript_fuzzer fuzzers fuzz_oauth_token_request.js --sync
compile_javascript_fuzzer fuzzers fuzz_oauth_token_response.js --sync
compile_javascript_fuzzer fuzzers fuzz_response_parser.js --sync
compile_javascript_fuzzer fuzzers fuzz_url_parser.js --sync

echo "TypeScript/JavaScript fuzzers built successfully!"

# Phase 2: Build Go fuzzers (Enhanced Security)
echo "=== Phase 2: Building Go Fuzzers (Enhanced Security) ==="

# Initialize Go module if needed
if [ ! -f gofuzz/go.mod ]; then
  echo "Initializing Go module..."
  cd gofuzz
  go mod init github.com/google-gemini/gemini-cli/gofuzz
  cd ..
fi

cd gofuzz
go mod tidy
go mod download

# Security-critical fuzz targets (Priority 1 - Issue #1121)
echo "Building security-critical fuzz targets..."
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzSymlinkValidation fuzz_symlink_validation
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzPathValidation fuzz_path_validation
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzContextFileParser fuzz_context_file_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzShellValidation fuzz_shell_validation

# Core functionality fuzz targets (Priority 2)
echo "Building core functionality fuzz targets..."
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzFileSystemOperations fuzz_file_system_operations
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzMCPDecoder fuzz_mcp_decoder
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzCryptoOperations fuzz_crypto_operations
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzSlashCommands fuzz_slash_commands

cd ..

echo "Go fuzzers built successfully!"

# Phase 3: Create comprehensive seed corpora
echo "=== Phase 3: Creating Comprehensive Seed Corpora ==="

mkdir -p seeds/comprehensive

# Config parser seeds
echo '{"api_key": "test_key", "model": "gemini-pro"}' > seeds/comprehensive/config_valid.json
echo '{}' > seeds/comprehensive/config_empty.json
echo '{"invalid": "json", "missing": "quote}' > seeds/comprehensive/config_invalid.json
echo '{"api_key": "test", "model": "gemini-pro", "temperature": 0.7, "max_tokens": 1000}' > seeds/comprehensive/config_complete.json

# CLI parser seeds
echo 'gemini chat "Hello world"' > seeds/comprehensive/cli_valid.txt
echo 'gemini --help' > seeds/comprehensive/cli_help.txt
echo 'gemini --invalid-flag' > seeds/comprehensive/cli_invalid.txt
echo 'gemini --model gemini-pro --prompt "Test prompt"' > seeds/comprehensive/cli_with_flags.txt

# Input sanitizer seeds
echo 'normal_input' > seeds/comprehensive/input_normal.txt
echo '<script>alert("xss")</script>' > seeds/comprehensive/input_xss.txt
echo 'javascript:alert("injection")' > seeds/comprehensive/input_injection.txt
echo '../../../etc/passwd' > seeds/comprehensive/input_path_traversal.txt

# Environment parser seeds
echo 'API_KEY=test_key' > seeds/comprehensive/env_valid.txt
echo 'MODEL=gemini-pro' > seeds/comprehensive/env_model.txt
echo 'INVALID_ENV' > seeds/comprehensive/env_invalid.txt
echo 'PATH=../../../etc' > seeds/comprehensive/env_path_traversal.txt

# MCP seeds
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {}}' > seeds/comprehensive/mcp_valid.json
echo '{"jsonrpc": "2.0", "method": "invalid", "params": null}' > seeds/comprehensive/mcp_invalid.json

# OAuth seeds
echo '{"access_token": "test_token", "token_type": "Bearer"}' > seeds/comprehensive/oauth_valid.json
echo '{"error": "invalid_grant"}' > seeds/comprehensive/oauth_error.json

# Package seed corpora
echo "Packaging comprehensive seed corpora..."

# Copy seed files if they exist
if [ -d "seeds" ]; then
  echo "Packaging comprehensive seed corpora..."
  cp -r seeds/* $OUT/
fi

# Phase 4: Create comprehensive dictionaries
echo "=== Phase 4: Creating Comprehensive Dictionaries ==="

# Config parser dictionary
cat > $OUT/fuzz_config_parser.dict << 'EOF'
{
  "api_key": "string",
  "model": "string",
  "gemini-pro": "string",
  "gemini-pro-vision": "string",
  "temperature": "number",
  "max_tokens": "number",
  "top_p": "number",
  "top_k": "number"
}
EOF

# CLI parser dictionary
cat > $OUT/fuzz_cli_parser.dict << 'EOF'
{
  "gemini": "string",
  "chat": "string",
  "help": "string",
  "--": "string",
  "--model": "string",
  "--prompt": "string",
  "--temperature": "string",
  "--max-tokens": "string"
}
EOF

# Input sanitizer dictionary
cat > $OUT/fuzz_input_sanitizer.dict << 'EOF'
{
  "<script>": "string",
  "javascript:": "string",
  "onerror=": "string",
  "onload=": "string",
  "eval(": "string",
  "../": "string",
  "..\\": "string"
}
EOF

# Environment parser dictionary
cat > $OUT/fuzz_env_parser.dict << 'EOF'
{
  "API_KEY": "string",
  "MODEL": "string",
  "TEMPERATURE": "string",
  "MAX_TOKENS": "string",
  "=": "string",
  "PATH": "string",
  "HOME": "string"
}
EOF

# MCP dictionary
cat > $OUT/fuzz_mcp_request.dict << 'EOF'
{
  "jsonrpc": "string",
  "2.0": "string",
  "method": "string",
  "params": "string",
  "id": "string",
  "initialize": "string",
  "request": "string"
}
EOF

# OAuth dictionary
cat > $OUT/fuzz_oauth_token_request.dict << 'EOF'
{
  "access_token": "string",
  "token_type": "string",
  "Bearer": "string",
  "expires_in": "string",
  "refresh_token": "string",
  "error": "string"
}
EOF

# Security-critical dictionaries
cat > $OUT/fuzz_symlink_validation.dict << 'EOF'
{
  "../": "string",
  "..\\": "string",
  "/etc/": "string",
  "/proc/": "string",
  "/sys/": "string",
  "symlink": "string",
  "ln -s": "string"
}
EOF

cat > $OUT/fuzz_path_validation.dict << 'EOF'
{
  "../": "string",
  "..\\": "string",
  "/etc/passwd": "string",
  "/etc/shadow": "string",
  "C:\\Windows\\": "string",
  "path": "string",
  "traversal": "string"
}
EOF

# Phase 5: Create comprehensive options files
echo "=== Phase 5: Creating Comprehensive Options Files ==="

# Create options files for all fuzzers
for fuzzer in fuzz_config_parser fuzz_cli_parser fuzz_input_sanitizer fuzz_env_parser fuzz_file_path_handler fuzz_http_request_parser fuzz_mcp_request fuzz_mcp_response fuzz_oauth_token_request fuzz_oauth_token_response fuzz_response_parser fuzz_url_parser fuzz_symlink_validation fuzz_path_validation fuzz_context_file_parser fuzz_shell_validation fuzz_file_system_operations fuzz_mcp_decoder fuzz_crypto_operations fuzz_slash_commands; do
  cat > $OUT/$fuzzer.options << 'EOF'
[libfuzzer]
max_len = 8192
timeout = 60
max_total_time = 3600
close_fd_mask = 3
detect_leaks = 1
use_value_profile = 1
shrink = 1
reduce_inputs = 1
EOF
done

# Phase 6: Build validation and summary
echo "=== Phase 6: Build Validation and Summary ==="

# Count built fuzzers
total_fuzzers=$(ls -1 $OUT/fuzz_* 2>/dev/null | grep -v -E '\.(dict|options|zip)$' | wc -l)
total_corpora=$(ls -1 $OUT/*_seed_corpus.zip 2>/dev/null | wc -l)
total_dicts=$(ls -1 $OUT/*.dict 2>/dev/null | wc -l)

echo "Comprehensive Build Summary:"
echo "  Total fuzz targets: $total_fuzzers"
echo "  Total seed corpora: $total_corpora"
echo "  Total dictionaries: $total_dicts"

# List all built fuzzers
echo "Built fuzzers:"
ls -1 $OUT/fuzz_* | grep -v -E '\.(dict|options|zip)$' | while read fuzzer; do
  echo "  - $(basename $fuzzer)"
done

# Verify critical security fuzzers
echo "=== Verifying Critical Security Fuzzers ==="
critical_fuzzers="fuzz_symlink_validation fuzz_path_validation fuzz_context_file_parser fuzz_shell_validation"
for fuzzer in $critical_fuzzers; do
  if [ -f "$OUT/$fuzzer" ]; then
    echo "✓ $fuzzer built successfully"
  else
    echo "✗ WARNING: Critical fuzzer $fuzzer not found!"
  fi
done

# Verify foundation fuzzers
echo "=== Verifying Foundation Fuzzers ==="
foundation_fuzzers="fuzz_config_parser fuzz_cli_parser fuzz_input_sanitizer"
for fuzzer in $foundation_fuzzers; do
  if [ -f "$OUT/$fuzzer" ]; then
    echo "✓ $fuzzer built successfully"
  else
    echo "✗ WARNING: Foundation fuzzer $fuzzer not found!"
  fi
done

echo "=== Comprehensive build completed successfully! ==="
echo "Advanced system ready for OSS-Fuzz integration."
echo "Focus on Issue #1121 (symlink traversal) and comprehensive security coverage."
