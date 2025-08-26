# Master Compliance and Deployment System for OSS-Fuzz

## Overview

This system provides automated compliance checking, build validation, and deployment orchestration for multiple OSS-Fuzz projects. It ensures all projects meet Google's compliance requirements and are deployed in the correct order based on dependencies.

## 🚀 Quick Start

### 1. Run Full Deployment
```bash
python master-compliance-deploy.py
```

### 2. Run Compliance Checks Only
```bash
python master-compliance-deploy.py --compliance-only
```

### 3. Run Build Validation Only
```bash
python master-compliance-deploy.py --build-only
```

### 4. Run Deployment Only
```bash
python master-compliance-deploy.py --deploy-only
```

### 5. Using the Quick Deploy Script
```bash
# Full deployment
./quick-deploy.sh --full-deploy

# Compliance checks only
./quick-deploy.sh --compliance-only

# Dry run to see what would be deployed
./quick-deploy.sh --dry-run
```

## 📁 System Components

### Core Files
- **`master-compliance-deploy.py`** - Main orchestration script
- **`deployment-config.yaml`** - Configuration for priorities, dependencies, and rules
- **`quick-deploy.sh`** - Convenience wrapper script
- **`compliance-report.json`** - Generated compliance report

### Generated Files
- **`master-compliance-deploy.log`** - Detailed execution log
- **`compliance-report.json`** - Comprehensive compliance status report

## 🔧 Configuration

### Project Priorities
Projects are deployed in priority order (lower number = higher priority):

```yaml
project_priorities:
  gemini_cli: 1          # Main Gemini CLI integration
  gemini-cli: 2          # Secondary Gemini CLI integration  
  model-transparency: 3  # AI/ML transparency project
  g-api-python-tasks: 4  # Google API integration
  bitcoin-core: 5        # Cryptocurrency security
  curl: 6                # Network security
  # ... more projects
```

### Dependencies
Projects can depend on other projects:

```yaml
project_dependencies:
  model-transparency:
    - gemini_cli
    - gemini-cli
  g-api-python-tasks:
    - gemini_cli
  bitcoin-core:
    - curl
```

## ✅ Compliance Rules

### Required Copyright Header
All source files must include:
```
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
```

### Forbidden AI References
The following terms are automatically replaced with pattern-based alternatives:
- `ai-powered` → `pattern-powered`
- `ai-assisted` → `pattern-assisted`
- `sentient core` → `pattern-based core`
- `tower of babel` → `universal plugin generator`

### File Types Requiring Copyright Headers
- `.py` (Python)
- `.js` (JavaScript)
- `.ts` (TypeScript)
- `.go` (Go)
- `.java` (Java)
- `.cpp` (C++)
- `.c` (C)
- `.h` (Header files)

### Excluded Files
These files are exempt from AI reference checks:
- `orchestrate-rollout.py`
- `rapid_expand.py`
- `automated-rollout.yml`
- `master-compliance-deploy.py`
- `deploy.sh`
- `build.sh`
- `deployment-config.yaml`

## 🏗️ Build Validation

### Required Files
Each project must have:
- `project.yaml` - OSS-Fuzz project configuration
- `Dockerfile` - Build container definition
- `build.sh` - Build script (must be executable)
- `fuzzers/` directory - Contains fuzzer implementations

### Validation Checks
- YAML syntax validation
- Required file presence
- Executable script permissions
- Directory structure validation

## 🚀 Deployment Process

### Deployment Order
1. **Discovery** - Find all OSS-Fuzz projects
2. **Priority Sorting** - Sort by configured priorities
3. **Dependency Resolution** - Use topological sort for dependencies
4. **Compliance Checks** - Validate all compliance rules
5. **Build Validation** - Verify build configuration
6. **Deployment** - Deploy projects in order

### Deployment Methods
- **Custom Scripts** - Uses `deploy.sh` if available
- **Standard Git** - `git add`, `commit`, `push` if no custom script
- **Health Checks** - Validates deployment success
- **Rollback** - Automatic rollback on failure

## 📊 Monitoring and Reporting

### Compliance Report
Generated `compliance-report.json` includes:
- Project status summary
- Individual project details
- Compliance issues
- Build validation issues
- Deployment status

### Logging
- **File Logging** - `master-compliance-deploy.log`
- **Console Output** - Real-time status updates
- **Error Tracking** - Detailed error information

## 🔍 Usage Examples

### Check Specific Project Directory
```bash
python master-compliance-deploy.py --projects-dir custom_projects
```

### Compliance Check for Your Projects Only
```bash
python master-compliance-deploy.py --compliance-only --projects-dir projects/gemini_cli
```

### Full Deployment with Custom Config
```bash
# Edit deployment-config.yaml first
python master-compliance-deploy.py
```

### Quick Deploy with Dry Run
```bash
./quick-deploy.sh --dry-run
```

## 🛠️ Troubleshooting

### Common Issues

#### Missing Dependencies
```bash
pip install pyyaml
```

#### Permission Issues
```bash
# On Unix/Linux
chmod +x quick-deploy.sh
chmod +x projects/*/build.sh
chmod +x projects/*/deploy.sh
```

#### Compliance Failures
1. Add Google copyright headers to source files
2. Replace AI references with pattern-based alternatives
3. Check excluded files list

#### Build Validation Failures
1. Ensure `project.yaml` has valid YAML syntax
2. Verify `Dockerfile` exists and is valid
3. Make `build.sh` executable
4. Create `fuzzers/` directory

### Debug Mode
```bash
# Enable verbose logging
export PYTHONPATH=.
python -u master-compliance-deploy.py --compliance-only
```

## 📈 Advanced Features

### Parallel Processing
- Configurable worker count
- Concurrent compliance checks
- Parallel build validation

### Caching
- Compliance check caching
- Build validation caching
- Performance optimization

### Security Scanning
- Hardcoded secret detection
- Vulnerability scanning
- Dependency analysis
- License compliance

### Performance Optimization
- Memory limits
- Timeout settings
- Resource management

## 🔄 Integration with Existing Workflows

### GitHub Actions
```yaml
- name: Run Master Deployment
  run: |
    python master-compliance-deploy.py --compliance-only
    python master-compliance-deploy.py --build-only
    python master-compliance-deploy.py --deploy-only
```

### CI/CD Pipelines
```bash
# Pre-commit hook
./quick-deploy.sh --compliance-only

# Deployment pipeline
./quick-deploy.sh --full-deploy
```

## 📋 Project Management

### Adding New Projects
1. Create project directory in `projects/`
2. Add `project.yaml` configuration
3. Update `deployment-config.yaml` with priorities/dependencies
4. Run compliance checks: `./quick-deploy.sh --compliance-only`

### Updating Existing Projects
1. Modify project files
2. Run compliance checks: `./quick-deploy.sh --compliance-only`
3. Deploy if compliant: `./quick-deploy.sh --deploy-only`

### Removing Projects
1. Remove project directory
2. Update `deployment-config.yaml` if needed
3. Run full deployment to verify: `./quick-deploy.sh --full-deploy`

## 🎯 Best Practices

### Compliance
- Always run compliance checks before deployment
- Use the provided copyright header template
- Replace AI references with pattern-based alternatives
- Keep excluded files list updated

### Deployment
- Test with dry run first: `--dry-run`
- Deploy in stages: compliance → build → deploy
- Monitor logs for issues
- Use rollback on failures

### Configuration
- Keep priorities logical and consistent
- Minimize circular dependencies
- Document project relationships
- Regular configuration reviews

## 📞 Support

### Logs
- Check `master-compliance-deploy.log` for detailed execution logs
- Review `compliance-report.json` for project status

### Common Commands
```bash
# Check system status
./quick-deploy.sh --dry-run

# Fix compliance issues
python master-compliance-deploy.py --compliance-only

# Deploy compliant projects
python master-compliance-deploy.py --deploy-only

# Full system check
./quick-deploy.sh --full-deploy
```

### Error Recovery
1. Check logs for specific error messages
2. Fix compliance issues first
3. Validate build configuration
4. Retry deployment
5. Use rollback if needed

---

**Note**: This system is designed for Google's OSS-Fuzz infrastructure and follows Google's compliance requirements. Ensure all projects meet these standards before deployment.
