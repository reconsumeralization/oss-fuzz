#!/bin/bash
# OSS-Fuzz Critical Compliance Implementation Script
# Implements the most critical security improvements immediately

set -e

echo "🔐 OSS-Fuzz Critical Compliance Implementation"
echo "============================================="

# Detect OSS-Fuzz root
if [ -z "$OSS_FUZZ_ROOT" ]; then
    if [ -f "infra/helper.py" ] && [ -d "projects" ]; then
        export OSS_FUZZ_ROOT="$(pwd)"
        echo "📍 Auto-detected OSS-Fuzz root: $OSS_FUZZ_ROOT"
    else
        echo "❌ Please run from OSS-Fuzz root directory"
        exit 1
    fi
fi

cd "$OSS_FUZZ_ROOT"

echo ""
echo "1️⃣ Creating Security Policy..."
# Create SECURITY.md if it doesn't exist
if [ ! -f "SECURITY.md" ]; then
    cat > SECURITY.md << 'EOF'
# Security Policy

## Supported Versions
| Version | Supported          |
| ------- | ------------------ |
| Latest  | ✅ Yes             |
| < 1.0   | ❌ No              |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report vulnerabilities to: **oss-fuzz-team@google.com**

### Response Timeline
- **Initial Response:** 48 hours
- **Triage Completion:** 7 days  
- **Fix Timeline:** 30 days (critical), 90 days (others)

### Disclosure Policy
We follow coordinated disclosure principles:
1. Private reporting and investigation
2. Fix development and testing  
3. Coordinated public disclosure
4. Credit attribution to researchers

## Security Best Practices
When contributing to OSS-Fuzz:
- Follow secure coding practices
- Test security-relevant changes thoroughly
- Report potential vulnerabilities privately first
- Keep dependencies up to date

## Contact
For security-related questions: oss-fuzz-team@google.com
EOF
    echo "✅ Created SECURITY.md"
else
    echo "✅ SECURITY.md already exists"
fi

echo ""
echo "2️⃣ Setting up GitHub Security Features..."

# Create .github directory if it doesn't exist
mkdir -p .github/workflows

# Create dependency scanning workflow
cat > .github/workflows/dependency-scan.yml << 'EOF'
name: Dependency Security Scan
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
      
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        if [ -f infra/ci/requirements.txt ]; then pip install -r infra/ci/requirements.txt; fi
    
    - name: Run Safety to check Python dependencies
      run: |
        pip install safety
        safety check --json --output safety-report.json || true
    
    - name: Run Bandit security scan
      run: |
        pip install bandit
        bandit -r . -f json -o bandit-report.json || true
    
    - name: Upload security scan results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-scan-results
        path: |
          safety-report.json
          bandit-report.json
        retention-days: 30
    
    - name: Check for critical vulnerabilities
      run: |
        if [ -f safety-report.json ]; then
          if grep -q '"vulnerabilities":' safety-report.json && [ "$(jq '.vulnerabilities | length' safety-report.json)" -gt 0 ]; then
            echo "⚠️ Vulnerabilities found in dependencies:"
            jq -r '.vulnerabilities[] | "- \(.advisory): \(.package_name) \(.analyzed_version)"' safety-report.json
          else
            echo "✅ No vulnerabilities found in dependencies"
          fi
        fi
EOF

echo "✅ Created dependency scanning workflow"

# Create Dependabot configuration
cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"
    commit-message:
      prefix: "deps"
      include: "scope"
    
  - package-ecosystem: "pip" 
    directory: "/infra/ci"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "infra"

  - package-ecosystem: "docker"
    directory: "/infra/base-images/base-builder"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 3
    labels:
      - "dependencies"
      - "docker"
      
  - package-ecosystem: "docker"
    directory: "/infra/base-images/base-runner"
    schedule:
      interval: "weekly"  
    open-pull-requests-limit: 3
    labels:
      - "dependencies"
      - "docker"
EOF

echo "✅ Created Dependabot configuration"

# Create container security scanning workflow
cat > .github/workflows/container-security.yml << 'EOF'
name: Container Security Scan
on:
  push:
    paths: 
      - 'infra/base-images/**'
      - '**/Dockerfile'
  pull_request:
    paths:
      - 'infra/base-images/**'
      - '**/Dockerfile'

jobs:
  container-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
      
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Build base-builder image
      run: |
        docker build -t oss-fuzz-base-builder infra/base-images/base-builder/
    
    - name: Build base-runner image  
      run: |
        docker build -t oss-fuzz-base-runner infra/base-images/base-runner/
    
    - name: Run Trivy vulnerability scanner on base-builder
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'oss-fuzz-base-builder'
        format: 'sarif'
        output: 'trivy-base-builder.sarif'
    
    - name: Run Trivy vulnerability scanner on base-runner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'oss-fuzz-base-runner'
        format: 'sarif'
        output: 'trivy-base-runner.sarif'
        
    - name: Upload Trivy scan results for base-builder
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-base-builder.sarif'
        category: 'base-builder-security'
        
    - name: Upload Trivy scan results for base-runner
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-base-runner.sarif' 
        category: 'base-runner-security'
    
    - name: Check scan results
      run: |
        echo "🔍 Container security scan completed"
        if [ -f trivy-base-builder.sarif ]; then
          echo "📊 Base-builder scan results available"
        fi
        if [ -f trivy-base-runner.sarif ]; then
          echo "📊 Base-runner scan results available"  
        fi
EOF

echo "✅ Created container security scanning workflow"

echo ""
echo "3️⃣ Creating compliance monitoring tools..."

# Create compliance tools directory
mkdir -p tools/compliance

# Create basic compliance checker
cat > tools/compliance/compliance_checker.py << 'EOF'
#!/usr/bin/env python3
"""
OSS-Fuzz Compliance Checker
Basic compliance validation tool
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ComplianceChecker:
    def __init__(self, oss_fuzz_root: str):
        self.root = Path(oss_fuzz_root)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_score': 0.0,
            'recommendations': []
        }
    
    def check_security_policy(self) -> Dict[str, Any]:
        """Check if security policy exists and is comprehensive."""
        security_file = self.root / 'SECURITY.md'
        
        if not security_file.exists():
            return {
                'status': 'fail',
                'score': 0,
                'message': 'SECURITY.md file missing'
            }
        
        content = security_file.read_text()
        required_sections = [
            'reporting',
            'vulnerability',
            'response',
            'disclosure'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)
        
        if missing_sections:
            return {
                'status': 'partial',
                'score': 50,
                'message': f'Security policy exists but missing: {", ".join(missing_sections)}'
            }
        
        return {
            'status': 'pass',
            'score': 100,
            'message': 'Comprehensive security policy found'
        }
    
    def check_license_compliance(self) -> Dict[str, Any]:
        """Check license file and compliance."""
        license_file = self.root / 'LICENSE'
        
        if not license_file.exists():
            return {
                'status': 'fail', 
                'score': 0,
                'message': 'LICENSE file missing'
            }
        
        content = license_file.read_text()
        if 'Apache License' in content and '2.0' in content:
            return {
                'status': 'pass',
                'score': 100,
                'message': 'Apache 2.0 license found'
            }
        
        return {
            'status': 'partial',
            'score': 75,
            'message': 'License file exists but type unclear'
        }
    
    def check_contributing_guidelines(self) -> Dict[str, Any]:
        """Check contributing guidelines."""
        contributing_file = self.root / 'CONTRIBUTING.md'
        
        if not contributing_file.exists():
            return {
                'status': 'fail',
                'score': 0, 
                'message': 'CONTRIBUTING.md file missing'
            }
        
        content = contributing_file.read_text()
        required_elements = ['CLA', 'review', 'code']
        
        found_elements = sum(1 for element in required_elements 
                           if element.lower() in content.lower())
        
        score = (found_elements / len(required_elements)) * 100
        
        return {
            'status': 'pass' if score >= 80 else 'partial',
            'score': score,
            'message': f'Contributing guidelines found with {found_elements}/{len(required_elements)} key elements'
        }
    
    def check_dependency_files(self) -> Dict[str, Any]:
        """Check for dependency management files."""
        dep_files = [
            'requirements.txt',
            'infra/ci/requirements.txt',
            '.github/dependabot.yml'
        ]
        
        found_files = []
        for dep_file in dep_files:
            if (self.root / dep_file).exists():
                found_files.append(dep_file)
        
        score = (len(found_files) / len(dep_files)) * 100
        
        return {
            'status': 'pass' if score >= 60 else 'partial',
            'score': score,
            'message': f'Dependency management: {len(found_files)}/{len(dep_files)} files found'
        }
    
    def check_security_workflows(self) -> Dict[str, Any]:
        """Check for security-related GitHub workflows."""
        workflow_dir = self.root / '.github' / 'workflows'
        
        if not workflow_dir.exists():
            return {
                'status': 'fail',
                'score': 0,
                'message': 'No GitHub workflows directory found'
            }
        
        security_workflows = []
        for workflow_file in workflow_dir.glob('*.yml'):
            content = workflow_file.read_text()
            if any(keyword in content.lower() for keyword in 
                  ['security', 'vulnerability', 'trivy', 'snyk', 'safety', 'bandit']):
                security_workflows.append(workflow_file.name)
        
        if len(security_workflows) >= 2:
            return {
                'status': 'pass',
                'score': 100,
                'message': f'Security workflows found: {", ".join(security_workflows)}'
            }
        elif len(security_workflows) == 1:
            return {
                'status': 'partial',
                'score': 70,
                'message': f'One security workflow found: {security_workflows[0]}'
            }
        else:
            return {
                'status': 'fail',
                'score': 0,
                'message': 'No security workflows found'
            }
    
    def check_maintainers(self) -> Dict[str, Any]:
        """Check maintainers file."""
        maintainers_file = self.root / 'infra' / 'MAINTAINERS.csv'
        
        if not maintainers_file.exists():
            return {
                'status': 'fail',
                'score': 0,
                'message': 'MAINTAINERS.csv file missing'
            }
        
        content = maintainers_file.read_text()
        lines = content.strip().split('\n')
        
        # Count maintainers (excluding header)
        maintainer_count = len(lines) - 1 if len(lines) > 1 else 0
        
        if maintainer_count >= 3:
            return {
                'status': 'pass',
                'score': 100,
                'message': f'{maintainer_count} maintainers listed'
            }
        elif maintainer_count >= 1:
            return {
                'status': 'partial', 
                'score': 70,
                'message': f'Only {maintainer_count} maintainers listed'
            }
        else:
            return {
                'status': 'fail',
                'score': 0,
                'message': 'No maintainers found'
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all compliance checks."""
        checks = {
            'security_policy': self.check_security_policy(),
            'license_compliance': self.check_license_compliance(),
            'contributing_guidelines': self.check_contributing_guidelines(),
            'dependency_management': self.check_dependency_files(),
            'security_workflows': self.check_security_workflows(),
            'maintainers': self.check_maintainers()
        }
        
        self.results['checks'] = checks
        
        # Calculate overall score
        total_score = sum(check['score'] for check in checks.values())
        self.results['overall_score'] = total_score / len(checks)
        
        # Generate recommendations
        for check_name, check_result in checks.items():
            if check_result['status'] != 'pass':
                self.results['recommendations'].append({
                    'area': check_name,
                    'priority': 'high' if check_result['score'] < 50 else 'medium',
                    'message': check_result['message']
                })
        
        return self.results
    
    def print_report(self):
        """Print compliance report."""
        print("🔍 OSS-Fuzz Compliance Check Report")
        print("=" * 50)
        print(f"Overall Score: {self.results['overall_score']:.1f}/100")
        print()
        
        for check_name, result in self.results['checks'].items():
            status_icon = "✅" if result['status'] == 'pass' else "⚠️" if result['status'] == 'partial' else "❌"
            print(f"{status_icon} {check_name.replace('_', ' ').title()}: {result['score']:.0f}/100")
            print(f"   {result['message']}")
            print()
        
        if self.results['recommendations']:
            print("💡 Recommendations:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡"
                print(f"   {i}. {priority_icon} {rec['area'].replace('_', ' ').title()}: {rec['message']}")
            print()
        
        print(f"Report generated: {self.results['timestamp']}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        oss_fuzz_root = sys.argv[1]
    else:
        oss_fuzz_root = os.getcwd()
    
    if not Path(oss_fuzz_root).exists():
        print(f"❌ Directory not found: {oss_fuzz_root}")
        sys.exit(1)
    
    checker = ComplianceChecker(oss_fuzz_root)
    results = checker.run_all_checks()
    checker.print_report()
    
    # Save results to file
    results_file = Path(oss_fuzz_root) / 'compliance-report.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Detailed results saved to: {results_file}")
    
    # Exit with non-zero code if significant issues found
    if results['overall_score'] < 70:
        print("⚠️ Compliance score below 70%. Please address critical issues.")
        sys.exit(1)
    else:
        print("✅ Compliance check completed successfully!")

if __name__ == "__main__":
    main()
EOF

chmod +x tools/compliance/compliance_checker.py
echo "✅ Created compliance checker tool"

echo ""
echo "4️⃣ Creating SBOM generation script..."

cat > tools/compliance/generate_sbom.py << 'EOF'
#!/usr/bin/env python3
"""
Simple SBOM (Software Bill of Materials) Generator for OSS-Fuzz
Creates basic dependency inventory
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def get_python_dependencies() -> List[Dict]:
    """Get Python dependencies from pip."""
    try:
        result = subprocess.run(['pip', 'list', '--format=json'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []

def get_system_info() -> Dict:
    """Get system information."""
    try:
        result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
        system_info = result.stdout.strip() if result.returncode == 0 else 'Unknown'
    except:
        system_info = 'Unknown'
    
    return {
        'system': system_info,
        'python_version': sys.version.split()[0]
    }

def generate_sbom(output_file: str = 'oss-fuzz-sbom.json'):
    """Generate basic SBOM."""
    
    print("🔍 Generating Software Bill of Materials (SBOM)...")
    
    # Get dependencies
    python_deps = get_python_dependencies()
    system_info = get_system_info()
    
    # Create SBOM structure
    sbom = {
        'bomFormat': 'CycloneDX',
        'specVersion': '1.4',
        'serialNumber': f'urn:uuid:oss-fuzz-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
        'version': 1,
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'tools': [
                {
                    'vendor': 'OSS-Fuzz',
                    'name': 'SBOM Generator',
                    'version': '1.0'
                }
            ],
            'component': {
                'type': 'application',
                'name': 'OSS-Fuzz',
                'version': 'latest',
                'description': 'Continuous fuzzing service for open source software',
                'licenses': [
                    {
                        'license': {
                            'id': 'Apache-2.0'
                        }
                    }
                ]
            }
        },
        'components': []
    }
    
    # Add Python dependencies
    for dep in python_deps:
        component = {
            'type': 'library',
            'name': dep['name'],
            'version': dep['version'],
            'purl': f"pkg:pypi/{dep['name']}@{dep['version']}",
            'scope': 'required'
        }
        sbom['components'].append(component)
    
    # Add system information as metadata
    sbom['metadata']['properties'] = [
        {
            'name': 'system_info',
            'value': system_info['system']
        },
        {
            'name': 'python_version', 
            'value': system_info['python_version']
        }
    ]
    
    # Save SBOM
    with open(output_file, 'w') as f:
        json.dump(sbom, f, indent=2)
    
    print(f"✅ SBOM generated: {output_file}")
    print(f"   Components: {len(sbom['components'])}")
    print(f"   Python dependencies: {len(python_deps)}")
    
    return output_file

def main():
    """Main function."""
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'oss-fuzz-sbom.json'
    generate_sbom(output_file)

if __name__ == "__main__":
    main()
EOF

chmod +x tools/compliance/generate_sbom.py
echo "✅ Created SBOM generator"

echo ""
echo "5️⃣ Running initial compliance check..."

# Run the compliance checker
python3 tools/compliance/compliance_checker.py "$OSS_FUZZ_ROOT"

echo ""
echo "6️⃣ Generating initial SBOM..."

# Generate SBOM
python3 tools/compliance/generate_sbom.py oss-fuzz-initial-sbom.json

echo ""
echo "🎉 Critical compliance implementation completed!"
echo ""
echo "📋 What was implemented:"
echo "   ✅ Security policy (SECURITY.md)"
echo "   ✅ Automated dependency scanning"
echo "   ✅ Container security scanning" 
echo "   ✅ Dependabot configuration"
echo "   ✅ Compliance checker tool"
echo "   ✅ SBOM generation capability"
echo ""
echo "🚀 Next steps:"
echo "   1. Review and customize the security workflows"
echo "   2. Enable GitHub Security features in repository settings"
echo "   3. Configure Dependabot alerts and pull requests"
echo "   4. Run compliance checker regularly: ./tools/compliance/compliance_checker.py"
echo "   5. Generate SBOM for releases: ./tools/compliance/generate_sbom.py"
echo ""
echo "📊 Monitor compliance status:"
echo "   - Check GitHub Security tab for alerts"
echo "   - Review Dependabot pull requests weekly"
echo "   - Run compliance checker before releases"
echo "   - Update security policy as needed"
echo ""
echo "✅ OSS-Fuzz compliance significantly enhanced!"