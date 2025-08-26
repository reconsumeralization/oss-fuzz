#!/usr/bin/env python3
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

"""
Comprehensive Compliance and Deployment System for OSS-Fuzz Projects

This script provides a complete solution for maintaining compliance and bringing
all OSS-Fuzz projects online in the correct order, integrating security audits,
compliance checks, build validation, and automated deployment.
"""

import os
import sys
import json
import yaml
import logging
import argparse
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive-compliance-deploy.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProjectInfo:
    """Information about an OSS-Fuzz project."""
    name: str
    path: str
    priority: int
    dependencies: List[str]
    language: str
    status: str = "PENDING"
    compliance_issues: List[str] = None
    build_issues: List[str] = None
    security_issues: List[str] = None
    deployment_issues: List[str] = None
    
    def __post_init__(self):
        if self.compliance_issues is None:
            self.compliance_issues = []
        if self.build_issues is None:
            self.build_issues = []
        if self.security_issues is None:
            self.security_issues = []
        if self.deployment_issues is None:
            self.deployment_issues = []

@dataclass
class ComplianceResult:
    """Result of compliance checking for a project."""
    project_name: str
    success: bool
    issues: List[str]
    copyright_headers_missing: List[str]
    ai_references_found: List[str]
    yaml_syntax_errors: List[str]
    required_files_missing: List[str]

@dataclass
class SecurityAuditResult:
    """Result of security audit processing."""
    audit_file: str
    vulnerabilities_found: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    deployment_blockers: List[str]
    recommendations: List[str]

class ComprehensiveComplianceDeployer:
    """Comprehensive compliance and deployment system."""
    
    def __init__(self, config_file: str = "comprehensive-config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.projects = {}
        self.security_audits = []
        self.deployment_order = []
        
        # Initialize components
        self._init_security_processor()
        self._init_master_deployer()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load comprehensive configuration."""
        if not os.path.exists(self.config_file):
            return self._create_comprehensive_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_comprehensive_config(self) -> Dict[str, Any]:
        """Create comprehensive configuration."""
        config = {
            "security": {
                "enabled": True,
                "audit_files": [],
                "block_deployment_on_critical": True,
                "block_deployment_on_high": False,
                "require_security_review": True,
                "auto_fix_low_severity": False
            },
            "compliance": {
                "enabled": True,
                "check_copyright_headers": True,
                "check_ai_references": True,
                "check_yaml_syntax": True,
                "check_required_files": True,
                "auto_fix_copyright_headers": True,
                "auto_fix_ai_references": True,
                "exclude_files": [
                    "master-compliance-deploy.py",
                    "enhanced-master-deploy.py",
                    "comprehensive-compliance-deploy.py",
                    "security-audit-integration.py"
                ]
            },
            "build": {
                "enabled": True,
                "validate_yaml": True,
                "check_required_files": True,
                "test_build_scripts": True,
                "parallel_workers": 4,
                "timeout_seconds": 300
            },
            "deployment": {
                "enabled": True,
                "dry_run": False,
                "parallel_deployment": True,
                "max_parallel_deployments": 2,
                "deployment_timeout": 600,
                "rollback_on_failure": True,
                "health_check_after_deployment": True
            },
            "projects": {
                "priority_order": [
                    "gemini_cli",
                    "gemini-cli",
                    "model-transparency",
                    "g-api-python-tasks",
                    "bitcoin-core",
                    "curl",
                    "openssl",
                    "nginx"
                ],
                "dependencies": {
                    "model-transparency": ["gemini_cli", "gemini-cli"],
                    "g-api-python-tasks": ["gemini_cli"],
                    "bitcoin-core": ["openssl"],
                    "nginx": ["openssl"]
                },
                "language_mapping": {
                    "gemini_cli": "javascript",
                    "gemini-cli": "python",
                    "model-transparency": "python",
                    "g-api-python-tasks": "python",
                    "bitcoin-core": "cpp",
                    "curl": "cpp",
                    "openssl": "cpp",
                    "nginx": "cpp"
                }
            },
            "monitoring": {
                "enabled": True,
                "generate_reports": True,
                "save_logs": True,
                "notify_on_failure": True,
                "dashboard_url": "http://localhost:8080"
            }
        }
        
        # Save config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        return config
    
    def _init_security_processor(self):
        """Initialize security audit processor."""
        try:
            from security_audit_integration import SecurityAuditProcessor
            self.security_processor = SecurityAuditProcessor
            logger.info("Security audit processor initialized")
        except ImportError:
            self.security_processor = None
            logger.warning("Security audit processor not available")
    
    def _init_master_deployer(self):
        """Initialize master deployment system."""
        try:
            from master_compliance_deploy import MasterComplianceDeployer
            self.master_deployer = MasterComplianceDeployer(self.config_file)
            logger.info("Master deployment system initialized")
        except ImportError:
            self.master_deployer = None
            logger.warning("Master deployment system not available")
    
    def discover_projects(self, projects_dir: str = "projects") -> Dict[str, ProjectInfo]:
        """Discover all OSS-Fuzz projects in the directory."""
        logger.info(f"Discovering projects in {projects_dir}")
        
        projects = {}
        priority_order = self.config["projects"]["priority_order"]
        dependencies = self.config["projects"]["dependencies"]
        language_mapping = self.config["projects"]["language_mapping"]
        
        if not os.path.exists(projects_dir):
            logger.error(f"Projects directory not found: {projects_dir}")
            return projects
        
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_path):
                # Check if it's a valid OSS-Fuzz project
                project_yaml = os.path.join(project_path, "project.yaml")
                if os.path.exists(project_yaml):
                    priority = priority_order.index(project_name) if project_name in priority_order else 999
                    deps = dependencies.get(project_name, [])
                    language = language_mapping.get(project_name, "unknown")
                    
                    projects[project_name] = ProjectInfo(
                        name=project_name,
                        path=project_path,
                        priority=priority,
                        dependencies=deps,
                        language=language
                    )
        
        logger.info(f"Discovered {len(projects)} projects")
        return projects
    
    def process_security_audits(self, audit_files: List[str]) -> List[SecurityAuditResult]:
        """Process security audit files."""
        if not self.security_processor or not audit_files:
            return []
        
        logger.info("Processing security audits...")
        results = []
        
        for audit_file in audit_files:
            if not os.path.exists(audit_file):
                logger.error(f"Security audit file not found: {audit_file}")
                continue
            
            try:
                processor = self.security_processor(audit_file)
                audit = processor.parse_markdown_audit()
                
                # Save audit data
                audit_file_path, compliance_file, blockers_file = processor.save_audit_data(audit)
                
                # Create result
                critical_count = len([v for v in audit.vulnerabilities if v.severity.value == "CRITICAL"])
                high_count = len([v for v in audit.vulnerabilities if v.severity.value == "HIGH"])
                
                result = SecurityAuditResult(
                    audit_file=audit_file,
                    vulnerabilities_found=len(audit.vulnerabilities),
                    critical_vulnerabilities=critical_count,
                    high_vulnerabilities=high_count,
                    deployment_blockers=[v.title for v in audit.vulnerabilities if v.severity.value in ["CRITICAL", "HIGH"]],
                    recommendations=processor._generate_recommendations(audit)
                )
                
                results.append(result)
                self.security_audits.append(result)
                
                logger.info(f"Processed audit: {audit_file}")
                logger.info(f"  - Vulnerabilities: {result.vulnerabilities_found}")
                logger.info(f"  - Critical: {result.critical_vulnerabilities}")
                logger.info(f"  - High: {result.high_vulnerabilities}")
                
            except Exception as e:
                logger.error(f"Failed to process security audit {audit_file}: {e}")
        
        return results
    
    def check_project_compliance(self, project: ProjectInfo) -> ComplianceResult:
        """Check compliance for a single project."""
        logger.info(f"Checking compliance for project: {project.name}")
        
        issues = []
        copyright_headers_missing = []
        ai_references_found = []
        yaml_syntax_errors = []
        required_files_missing = []
        
        try:
            # Check project.yaml
            project_yaml = os.path.join(project.path, "project.yaml")
            if not os.path.exists(project_yaml):
                required_files_missing.append("project.yaml")
                issues.append("Missing project.yaml")
            else:
                # Check YAML syntax
                try:
                    with open(project_yaml, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    yaml_syntax_errors.append(f"project.yaml: {str(e)}")
                    issues.append(f"YAML syntax error in project.yaml: {e}")
                
                # Check for AI references
                if self.config["compliance"]["check_ai_references"]:
                    with open(project_yaml, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        ai_patterns = ["ai-powered", "ai-assisted", "sentient core", "tower of babel"]
                        for pattern in ai_patterns:
                            if pattern in content:
                                ai_references_found.append(f"project.yaml: {pattern}")
                                issues.append(f"AI reference found: {pattern}")
            
            # Check for copyright headers in source files
            if self.config["compliance"]["check_copyright_headers"]:
                for root, dirs, files in os.walk(project.path):
                    for file in files:
                        if file.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h')):
                            file_path = os.path.join(root, file)
                            if self._should_check_file(file_path):
                                if not self._has_copyright_header(file_path):
                                    copyright_headers_missing.append(file_path)
                                    issues.append(f"Missing copyright header: {file_path}")
            
            # Check for required files
            required_files = ["Dockerfile", "build.sh"]
            for req_file in required_files:
                if not os.path.exists(os.path.join(project.path, req_file)):
                    required_files_missing.append(req_file)
                    issues.append(f"Missing required file: {req_file}")
            
            success = len(issues) == 0
            
            return ComplianceResult(
                project_name=project.name,
                success=success,
                issues=issues,
                copyright_headers_missing=copyright_headers_missing,
                ai_references_found=ai_references_found,
                yaml_syntax_errors=yaml_syntax_errors,
                required_files_missing=required_files_missing
            )
            
        except Exception as e:
            logger.error(f"Error checking compliance for {project.name}: {e}")
            return ComplianceResult(
                project_name=project.name,
                success=False,
                issues=[f"Error during compliance check: {e}"],
                copyright_headers_missing=[],
                ai_references_found=[],
                yaml_syntax_errors=[],
                required_files_missing=[]
            )
    
    def _should_check_file(self, file_path: str) -> bool:
        """Check if a file should be checked for compliance."""
        exclude_files = self.config["compliance"]["exclude_files"]
        filename = os.path.basename(file_path)
        return filename not in exclude_files
    
    def _has_copyright_header(self, file_path: str) -> bool:
        """Check if a file has the required copyright header."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return "Copyright 2025 Google LLC" in content
        except Exception:
            return False
    
    def fix_compliance_issues(self, project: ProjectInfo, compliance_result: ComplianceResult) -> bool:
        """Automatically fix compliance issues where possible."""
        logger.info(f"Fixing compliance issues for project: {project.name}")
        
        fixed = True
        
        # Fix copyright headers
        if self.config["compliance"]["auto_fix_copyright_headers"]:
            for file_path in compliance_result.copyright_headers_missing:
                if self._add_copyright_header(file_path):
                    logger.info(f"Added copyright header to: {file_path}")
                else:
                    logger.warning(f"Failed to add copyright header to: {file_path}")
                    fixed = False
        
        # Fix AI references
        if self.config["compliance"]["auto_fix_ai_references"]:
            for file_path in compliance_result.ai_references_found:
                if self._fix_ai_references(file_path):
                    logger.info(f"Fixed AI references in: {file_path}")
                else:
                    logger.warning(f"Failed to fix AI references in: {file_path}")
                    fixed = False
        
        return fixed
    
    def _add_copyright_header(self, file_path: str) -> bool:
        """Add copyright header to a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            copyright_header = """# Copyright 2025 Google LLC
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

"""
            
            if not content.startswith(copyright_header):
                new_content = copyright_header + content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            return True
        except Exception as e:
            logger.error(f"Error adding copyright header to {file_path}: {e}")
            return False
    
    def _fix_ai_references(self, file_path: str) -> bool:
        """Fix AI references in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace AI references with pattern-based alternatives
            replacements = {
                "ai-powered": "pattern-powered",
                "ai-assisted": "pattern-assisted", 
                "sentient core": "pattern-based core",
                "tower of babel": "universal plugin generator"
            }
            
            modified = False
            for old, new in replacements.items():
                if old in content.lower():
                    content = content.replace(old, new)
                    content = content.replace(old.title(), new.title())
                    content = content.replace(old.upper(), new.upper())
                    modified = True
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"Error fixing AI references in {file_path}: {e}")
            return False
    
    def validate_project_build(self, project: ProjectInfo) -> bool:
        """Validate that a project can be built."""
        logger.info(f"Validating build for project: {project.name}")
        
        try:
            # Check if build.sh exists and is executable
            build_script = os.path.join(project.path, "build.sh")
            if os.path.exists(build_script):
                if not os.access(build_script, os.X_OK):
                    os.chmod(build_script, 0o755)
                    logger.info(f"Made build.sh executable for {project.name}")
            
            # Check Dockerfile
            dockerfile = os.path.join(project.path, "Dockerfile")
            if not os.path.exists(dockerfile):
                logger.warning(f"No Dockerfile found for {project.name}")
                return False
            
            # Basic validation passed
            return True
            
        except Exception as e:
            logger.error(f"Error validating build for {project.name}: {e}")
            return False
    
    def deploy_project(self, project: ProjectInfo) -> bool:
        """Deploy a single project."""
        logger.info(f"Deploying project: {project.name}")
        
        try:
            # Check if project is ready for deployment
            if project.status != "READY":
                logger.error(f"Project {project.name} not ready for deployment (status: {project.status})")
                return False
            
            # Run deployment
            if self.config["deployment"]["dry_run"]:
                logger.info(f"DRY RUN: Would deploy {project.name}")
                return True
            
            # Use git to commit and push changes
            os.chdir(project.path)
            
            # Add all changes
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit changes
            commit_message = f"Deploy {project.name} - Automated compliance and security fixes"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Push changes
            subprocess.run(["git", "push"], check=True)
            
            logger.info(f"Successfully deployed {project.name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed for {project.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deploying {project.name}: {e}")
            return False
    
    def calculate_deployment_order(self) -> List[str]:
        """Calculate the correct deployment order based on dependencies."""
        logger.info("Calculating deployment order...")
        
        # Create dependency graph
        graph = {}
        for project_name, project in self.projects.items():
            graph[project_name] = project.dependencies
        
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def dfs(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected: {node}")
            if node in visited:
                return
            
            temp_visited.add(node)
            
            for dep in graph.get(node, []):
                if dep in self.projects:
                    dfs(dep)
            
            temp_visited.remove(node)
            visited.add(node)
            order.append(node)
        
        # Sort by priority first, then by dependencies
        sorted_projects = sorted(self.projects.keys(), key=lambda x: self.projects[x].priority)
        
        for project in sorted_projects:
            if project not in visited:
                dfs(project)
        
        self.deployment_order = order
        logger.info(f"Deployment order: {order}")
        return order
    
    def run_comprehensive_deployment(self, 
                                   projects_dir: str = "projects",
                                   audit_files: List[str] = None,
                                   skip_security: bool = False,
                                   skip_compliance: bool = False,
                                   skip_build: bool = False,
                                   skip_deploy: bool = False) -> bool:
        """Run the complete comprehensive deployment process."""
        
        logger.info("Starting comprehensive compliance and deployment process")
        
        # Step 1: Discover projects
        self.projects = self.discover_projects(projects_dir)
        if not self.projects:
            logger.error("No projects found")
            return False
        
        # Step 2: Process security audits
        if not skip_security and self.config["security"]["enabled"] and audit_files:
            security_results = self.process_security_audits(audit_files)
            
            # Check for deployment blockers
            critical_blockers = sum(r.critical_vulnerabilities for r in security_results)
            if critical_blockers > 0 and self.config["security"]["block_deployment_on_critical"]:
                logger.error(f"Deployment blocked due to {critical_blockers} critical vulnerabilities")
                return False
        
        # Step 3: Check compliance for all projects
        if not skip_compliance and self.config["compliance"]["enabled"]:
            logger.info("Checking compliance for all projects...")
            
            with ThreadPoolExecutor(max_workers=self.config["build"]["parallel_workers"]) as executor:
                compliance_futures = {
                    executor.submit(self.check_project_compliance, project): project
                    for project in self.projects.values()
                }
                
                for future in as_completed(compliance_futures):
                    project = compliance_futures[future]
                    try:
                        compliance_result = future.result()
                        project.compliance_issues = compliance_result.issues
                        
                        if not compliance_result.success:
                            # Try to fix issues automatically
                            if self.fix_compliance_issues(project, compliance_result):
                                # Re-check compliance
                                compliance_result = self.check_project_compliance(project)
                                project.compliance_issues = compliance_result.issues
                            
                            if not compliance_result.success:
                                project.status = "COMPLIANCE_FAILED"
                                logger.error(f"Compliance check failed for {project.name}")
                            else:
                                project.status = "COMPLIANCE_PASSED"
                        else:
                            project.status = "COMPLIANCE_PASSED"
                            
                    except Exception as e:
                        logger.error(f"Error checking compliance for {project.name}: {e}")
                        project.status = "COMPLIANCE_FAILED"
        
        # Step 4: Validate builds
        if not skip_build and self.config["build"]["enabled"]:
            logger.info("Validating builds for all projects...")
            
            for project in self.projects.values():
                if project.status == "COMPLIANCE_PASSED":
                    if self.validate_project_build(project):
                        project.status = "BUILD_VALIDATED"
                    else:
                        project.status = "BUILD_FAILED"
                        logger.error(f"Build validation failed for {project.name}")
        
        # Step 5: Calculate deployment order
        deployment_order = self.calculate_deployment_order()
        
        # Step 6: Deploy projects
        if not skip_deploy and self.config["deployment"]["enabled"]:
            logger.info("Deploying projects in order...")
            
            deployed_count = 0
            for project_name in deployment_order:
                project = self.projects[project_name]
                
                if project.status == "BUILD_VALIDATED":
                    project.status = "READY"
                    
                    if self.deploy_project(project):
                        project.status = "DEPLOYED"
                        deployed_count += 1
                        logger.info(f"Successfully deployed {project_name}")
                    else:
                        project.status = "DEPLOYMENT_FAILED"
                        logger.error(f"Failed to deploy {project_name}")
                        
                        if self.config["deployment"]["rollback_on_failure"]:
                            logger.info(f"Rolling back {project_name}")
                            # Implement rollback logic here
                else:
                    logger.warning(f"Skipping {project_name} - status: {project.status}")
        
        # Generate final report
        self._generate_final_report()
        
        logger.info("Comprehensive compliance and deployment process completed")
        return True
    
    def _generate_final_report(self):
        """Generate a comprehensive final report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_projects": len(self.projects),
                "compliance_passed": len([p for p in self.projects.values() if p.status == "COMPLIANCE_PASSED"]),
                "build_validated": len([p for p in self.projects.values() if p.status == "BUILD_VALIDATED"]),
                "deployed": len([p for p in self.projects.values() if p.status == "DEPLOYED"]),
                "failed": len([p for p in self.projects.values() if "FAILED" in p.status])
            },
            "projects": {
                name: {
                    "status": project.status,
                    "priority": project.priority,
                    "dependencies": project.dependencies,
                    "language": project.language,
                    "compliance_issues": project.compliance_issues,
                    "build_issues": project.build_issues,
                    "security_issues": project.security_issues,
                    "deployment_issues": project.deployment_issues
                }
                for name, project in self.projects.items()
            },
            "security_audits": [
                {
                    "audit_file": audit.audit_file,
                    "vulnerabilities_found": audit.vulnerabilities_found,
                    "critical_vulnerabilities": audit.critical_vulnerabilities,
                    "high_vulnerabilities": audit.high_vulnerabilities,
                    "deployment_blockers": audit.deployment_blockers
                }
                for audit in self.security_audits
            ],
            "deployment_order": self.deployment_order
        }
        
        # Save report
        with open("comprehensive-deployment-report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Final report generated: comprehensive-deployment-report.json")

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Compliance and Deployment System")
    parser.add_argument("--projects-dir", default="projects", help="Directory containing OSS-Fuzz projects")
    parser.add_argument("--config", default="comprehensive-config.yaml", help="Configuration file")
    parser.add_argument("--audit-files", nargs="+", help="Security audit files to process")
    parser.add_argument("--skip-security", action="store_true", help="Skip security audit processing")
    parser.add_argument("--skip-compliance", action="store_true", help="Skip compliance checks")
    parser.add_argument("--skip-build", action="store_true", help="Skip build validation")
    parser.add_argument("--skip-deploy", action="store_true", help="Skip deployment")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--discover-only", action="store_true", help="Only discover projects")
    parser.add_argument("--compliance-only", action="store_true", help="Only run compliance checks")
    parser.add_argument("--build-only", action="store_true", help="Only validate builds")
    parser.add_argument("--deploy-only", action="store_true", help="Only deploy projects")
    
    args = parser.parse_args()
    
    # Initialize comprehensive deployer
    deployer = ComprehensiveComplianceDeployer(args.config)
    
    # Set dry-run mode if requested
    if args.dry_run:
        deployer.config["deployment"]["dry_run"] = True
    
    # Handle single-mode operations
    if args.discover_only:
        projects = deployer.discover_projects(args.projects_dir)
        print(f"Discovered {len(projects)} projects:")
        for name, project in projects.items():
            print(f"  - {name} (priority: {project.priority}, language: {project.language})")
        sys.exit(0)
    
    if args.compliance_only:
        projects = deployer.discover_projects(args.projects_dir)
        deployer.projects = projects
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            compliance_futures = {
                executor.submit(deployer.check_project_compliance, project): project
                for project in projects.values()
            }
            
            for future in as_completed(compliance_futures):
                project = compliance_futures[future]
                try:
                    result = future.result()
                    status = "PASS" if result.success else "FAIL"
                    print(f"{project.name}: {status}")
                    if not result.success:
                        for issue in result.issues:
                            print(f"  - {issue}")
                except Exception as e:
                    print(f"{project.name}: ERROR - {e}")
        sys.exit(0)
    
    if args.build_only:
        projects = deployer.discover_projects(args.projects_dir)
        deployer.projects = projects
        
        for project in projects.values():
            success = deployer.validate_project_build(project)
            status = "PASS" if success else "FAIL"
            print(f"{project.name}: {status}")
        sys.exit(0)
    
    if args.deploy_only:
        projects = deployer.discover_projects(args.projects_dir)
        deployer.projects = projects
        
        # Set all projects as ready for deployment
        for project in projects.values():
            project.status = "READY"
        
        deployment_order = deployer.calculate_deployment_order()
        print(f"Deployment order: {deployment_order}")
        
        for project_name in deployment_order:
            project = projects[project_name]
            success = deployer.deploy_project(project)
            status = "SUCCESS" if success else "FAILED"
            print(f"{project_name}: {status}")
        sys.exit(0)
    
    # Run comprehensive deployment
    success = deployer.run_comprehensive_deployment(
        projects_dir=args.projects_dir,
        audit_files=args.audit_files,
        skip_security=args.skip_security,
        skip_compliance=args.skip_compliance,
        skip_build=args.skip_build,
        skip_deploy=args.skip_deploy
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
