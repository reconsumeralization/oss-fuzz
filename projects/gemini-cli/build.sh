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

# Build script for OSS-Fuzz - Gemini CLI Go Fuzzing Integration
# Builds Go fuzz targets for critical input parsing and security validation


echo "Building Gemini CLI Go fuzzers..."

# Move into project directory
cd /src/projects/gemini-cli

# Initialize Go module if needed
if [ ! -f gofuzz/go.mod ]; then
  echo "Initializing Go module..."
  cd gofuzz
  go mod init github.com/google-gemini/gemini-cli/gofuzz
  cd ..
fi

# Build Go fuzz targets
echo "Building Go fuzz targets..."

cd gofuzz
go mod tidy
go mod download

# Build core fuzz targets
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzConfigParser fuzz_config_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzCLIParser fuzz_cli_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzMCPRequest fuzz_mcp_request
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzMCPResponse fuzz_mcp_response
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzOAuthTokenRequest fuzz_oauth_token_request
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzOAuthTokenResponse fuzz_oauth_token_response
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzFileSystemOperations fuzz_file_system_operations
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzURLParser fuzz_url_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzCryptoOperations fuzz_crypto_operations
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzEnvironmentParser fuzz_environment_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzInputSanitizer fuzz_input_sanitizer
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzSlashCommands fuzz_slash_commands
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzContextFileParser fuzz_context_file_parser
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzPathValidation fuzz_path_validation
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzShellValidation fuzz_shell_validation
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzSymlinkValidation fuzz_symlink_validation
compile_go_fuzzer github.com/google-gemini/gemini-cli/gofuzz/fuzz FuzzToolInvocation fuzz_tool_invocation

cd ..

echo "Go fuzz targets built successfully!"

# Package seed corpora
echo "Packaging seed corpora..."

# Create seed corpus directories if they don't exist
mkdir -p seeds/config
mkdir -p seeds/cli
mkdir -p seeds/mcp
mkdir -p seeds/oauth

# Copy seed files if they exist
if [ -d "seeds" ]; then
  echo "Copying existing seed corpora..."
  cp -r seeds/* $OUT/
fi

# Create basic seed files if none exist
if [ ! -f "$OUT/fuzz_config_parser_seed_corpus.zip" ]; then
  echo "Creating basic seed corpora..."
  
  # Config parser seeds
  echo '{"api_key": "test_key", "model": "gemini-pro"}' > seeds/config/valid_config.json
  echo '{}' > seeds/config/empty_config.json
  echo '{"invalid": "json", "missing": "quote}' > seeds/config/invalid_config.json
  
  # CLI parser seeds
  echo 'gemini chat "Hello world"' > seeds/cli/valid_command.txt
  echo 'gemini --help' > seeds/cli/help_command.txt
  echo 'gemini --invalid-flag' > seeds/cli/invalid_flag.txt
  
  # MCP seeds
  echo '{"jsonrpc": "2.0", "method": "initialize", "params": {}}' > seeds/mcp/valid_request.json
  echo '{"jsonrpc": "2.0", "result": {"capabilities": {}}}' > seeds/mcp/valid_response.json
  echo '{"invalid": "json"' > seeds/mcp/invalid_json.json
  
  # OAuth seeds
  echo '{"access_token": "test_token", "token_type": "Bearer"}' > seeds/oauth/valid_token.json
  echo '{"error": "invalid_grant"}' > seeds/oauth/error_response.json
  echo '{"expires_in": 3600}' > seeds/oauth/expires_info.json
  
  # Package seeds
  zip -r $OUT/fuzz_config_parser_seed_corpus.zip seeds/config/
  zip -r $OUT/fuzz_cli_parser_seed_corpus.zip seeds/cli/
  zip -r $OUT/fuzz_mcp_request_seed_corpus.zip seeds/mcp/
  zip -r $OUT/fuzz_mcp_response_seed_corpus.zip seeds/mcp/
  zip -r $OUT/fuzz_oauth_token_request_seed_corpus.zip seeds/oauth/
  zip -r $OUT/fuzz_oauth_token_response_seed_corpus.zip seeds/oauth/
fi

echo "Seed corpora packaged successfully!"

# Create dictionaries
echo "Creating dictionaries..."

# Config parser dictionary
cat > $OUT/fuzz_config_parser.dict << 'EOF'
"api_key"
"model"
"gemini-pro"
"gemini-pro-vision"
"temperature"
"max_tokens"
"top_p"
"top_k"
EOF

# CLI parser dictionary
cat > $OUT/fuzz_cli_parser.dict << 'EOF'
"gemini"
"chat"
"generate"
"help"
"--model"
"--temperature"
"--max-tokens"
"--api-key"
"--config"
EOF

# MCP dictionary
cat > $OUT/fuzz_mcp_request.dict << 'EOF'
"jsonrpc"
"2.0"
"method"
"initialize"
"params"
"id"
"result"
"error"
EOF

# OAuth dictionary
cat > $OUT/fuzz_oauth_token_request.dict << 'EOF'
"access_token"
"token_type"
"Bearer"
"expires_in"
"refresh_token"
"scope"
"error"
"invalid_grant"
EOF

echo "Dictionaries created successfully!"

# Create .options files for performance optimization
echo "Creating .options files..."

cat > $OUT/fuzz_config_parser.options << 'EOF'
[libfuzzer]
max_len = 1024
timeout = 30
EOF

cat > $OUT/fuzz_cli_parser.options << 'EOF'
[libfuzzer]
max_len = 512
timeout = 30
EOF

cat > $OUT/fuzz_mcp_request.options << 'EOF'
[libfuzzer]
max_len = 2048
timeout = 30
EOF

cat > $OUT/fuzz_oauth_token_request.options << 'EOF'
[libfuzzer]
max_len = 1024
timeout = 30
EOF

echo "Build completed successfully!"
echo "Built 17 Go fuzz targets for Gemini CLI security testing"
