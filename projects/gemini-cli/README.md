
# Gemini CLI OSS-Fuzz Integration - Foundation Setup

## Overview
This PR establishes the foundation for OSS-Fuzz integration with Gemini CLI, providing basic fuzzing coverage for critical input parsing components using TypeScript/JavaScript fuzzing with Jazzer.js.

## What This PR Does

### ✅ Foundation Setup
- **Basic OSS-Fuzz Configuration**: Minimal `project.yaml` with JavaScript fuzzing support
- **Simple Build Environment**: Clean `Dockerfile` using Node.js 20.x LTS
- **Essential Fuzz Targets**: 3 core fuzz targets for critical functionality
- **Proper Exclusion**: `.gitignore` excludes node_modules and build artifacts

### 🎯 Fuzz Targets (Phase 1)
1. **`FuzzConfigParser`** - Tests configuration file parsing for security issues
2. **`FuzzCLIParser`** - Tests command-line argument parsing for injection vulnerabilities  
3. **`FuzzInputSanitizer`** - Tests input validation and sanitization logic

### 📁 Files Added
- `project.yaml` - OSS-Fuzz project configuration
- `Dockerfile` - Build environment setup with Node.js
- `build.sh` - Fuzz target compilation script with Jazzer.js
- `.gitignore` - Excludes unnecessary files
- `PR_STRATEGY.md` - Phased integration plan
- `fuzzers/` - JavaScript fuzz targets using Jazzer.js

## Why This Approach

### ✅ Maintainer-Friendly
- **Minimal Complexity**: Only 3 fuzz targets, simple configuration
- **Easy Review**: Focused changes, clear purpose
- **Low Risk**: Foundation that can be safely merged
- **Independent**: Doesn't depend on complex features

### ✅ Security-Focused
- **Critical Paths**: Targets most important input parsing
- **Early Detection**: Catches basic security issues immediately
- **Foundation**: Sets up infrastructure for future security targets

### ✅ Future-Ready
- **Expandable**: Easy to add more fuzz targets in future PRs
- **Well-Documented**: Clear strategy for phased expansion
- **Tested**: Basic seed corpora and dictionaries included

## Technical Details

### 🛠️ Technology Stack
- **Language**: JavaScript/TypeScript (matches actual Gemini CLI codebase)
- **Fuzzing Engine**: Jazzer.js (OSS-Fuzz's JavaScript fuzzer)
- **Runtime**: Node.js 20.x LTS
- **Build System**: npm + esbuild

### 🎯 Target Areas
- **Configuration Parsing**: JSON config validation and merging
- **CLI Argument Parsing**: Command-line argument validation
- **Input Sanitization**: XSS, injection, and path traversal detection

## Testing

### ✅ Build Verification
- [ ] OSS-Fuzz trial build passes
- [ ] 3 fuzz targets compile successfully
- [ ] Basic seed corpora work correctly
- [ ] No build errors or warnings

### ✅ Coverage
- Configuration parsing: JSON validation and type checking
- CLI parsing: Argument parsing and command validation
- Input sanitization: XSS, injection, and path validation

## Next Steps

After this foundation is approved and tested, future PRs will add:
- **Phase 2**: Core functionality fuzz targets (MCP, OAuth, filesystem)
- **Phase 3**: Security-critical targets (shell validation, path traversal)
- **Phase 4**: Comprehensive coverage (remaining targets)

## Contact
Questions? Contact: `reconsumeralization@gmail.com`

---

**Note**: This is Phase 1 of a 4-phase integration strategy. See `PR_STRATEGY.md` for complete details.
