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
Enhanced Master Compliance and Deployment System with Security Audit Integration

This script extends the master compliance and deployment system to include
security audit processing, ensuring that security vulnerabilities are addressed
before deployment.
"""

import os
import sys
import json
import yaml
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the security audit integration module
try:
    from security_audit_integration import SecurityAuditProcessor, Severity
except ImportError:
    print("Warning: security_audit_integration module not found. Security audit features will be disabled.")
    SecurityAuditProcessor = None

# Import the original master deployment module
try:
    from master_compliance_deploy import MasterComplianceDeployer
except ImportError:
    print("Warning: master_compliance_deploy module not found. Using basic functionality.")
    MasterComplianceDeployer = None

class EnhancedMasterDeployer:
    """Enhanced master deployment system with security audit integration."""
    
    def __init__(self, config_file: str = "deployment-config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.security_audits = []
        self.deployment_blockers = []
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced-master-deploy.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.master_deployer = MasterComplianceDeployer(config_file) if MasterComplianceDeployer else None
        self.security_processor = SecurityAuditProcessor if SecurityAuditProcessor else None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration."""
        if not os.path.exists(self.config_file):
            return self._create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration if none exists."""
        config = {
            "security_audit": {
                "enabled": True,
                "audit_files": [],
                "block_deployment_on_critical": True,
                "block_deployment_on_high": False,
                "require_security_review": True
            },
            "compliance": {
                "enabled": True,
                "check_copyright_headers": True,
                "check_ai_references": True,
                "exclude_files": [
                    "master-compliance-deploy.py",
                    "enhanced-master-deploy.py",
                    "security-audit-integration.py"
                ]
            },
            "deployment": {
                "enabled": True,
                "dry_run": False,
                "parallel_workers": 4,
                "timeout_seconds": 300
            },
            "projects": {
                "priority_order": [
                    "gemini_cli",
                    "gemini-cli", 
                    "model-transparency",
                    "g-api-python-tasks"
                ],
                "dependencies": {
                    "model-transparency": ["gemini_cli", "gemini-cli"],
                    "g-api-python-tasks": ["gemini_cli"]
                }
            }
        }
        
        # Save default config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        return config
    
    def process_security_audits(self, audit_files: List[str]) -> bool:
        """Process security audit files and check for deployment blockers."""
        if not self.security_processor:
            self.logger.warning("Security audit processing not available")
            return True
        
        self.logger.info("Processing security audits...")
        
        for audit_file in audit_files:
            if not os.path.exists(audit_file):
                self.logger.error(f"Security audit file not found: {audit_file}")
                continue
            
            try:
                processor = self.security_processor(audit_file)
                audit = processor.parse_markdown_audit()
                
                # Save audit data
                audit_file_path, compliance_file, blockers_file = processor.save_audit_data(audit)
                
                # Check for deployment blockers
                blockers = processor.create_deployment_blockers(audit)
                self.deployment_blockers.extend(blockers)
                
                self.logger.info(f"Processed audit: {audit_file}")
                self.logger.info(f"  - Vulnerabilities: {len(audit.vulnerabilities)}")
                self.logger.info(f"  - Deployment blockers: {len(blockers)}")
                
                # Check if deployment should be blocked
                if self.config["security_audit"]["block_deployment_on_critical"]:
                    critical_blockers = [b for b in blockers if b["severity"] == "CRITICAL"]
                    if critical_blockers:
                        self.logger.error(f"Deployment blocked due to {len(critical_blockers)} critical vulnerabilities")
                        return False
                
                if self.config["security_audit"]["block_deployment_on_high"]:
                    high_blockers = [b for b in blockers if b["severity"] == "HIGH"]
                    if high_blockers:
                        self.logger.error(f"Deployment blocked due to {len(high_blockers)} high severity vulnerabilities")
                        return False
                
            except Exception as e:
                self.logger.error(f"Failed to process security audit {audit_file}: {e}")
                if self.config["security_audit"]["require_security_review"]:
                    return False
        
        return True
    
    def run_compliance_checks(self, projects_dir: str = "projects") -> bool:
        """Run compliance checks using the master deployer."""
        if not self.master_deployer:
            self.logger.warning("Master compliance deployer not available")
            return True
        
        self.logger.info("Running compliance checks...")
        
        try:
            # Run compliance checks
            result = self.master_deployer.check_compliance(projects_dir)
            
            if not result["success"]:
                self.logger.error("Compliance checks failed")
                return False
            
            self.logger.info("Compliance checks passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            return False
    
    def run_build_validation(self, projects_dir: str = "projects") -> bool:
        """Run build validation using the master deployer."""
        if not self.master_deployer:
            self.logger.warning("Master compliance deployer not available")
            return True
        
        self.logger.info("Running build validation...")
        
        try:
            # Run build validation
            result = self.master_deployer.validate_builds(projects_dir)
            
            if not result["success"]:
                self.logger.error("Build validation failed")
                return False
            
            self.logger.info("Build validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Build validation failed: {e}")
            return False
    
    def deploy_projects(self, projects_dir: str = "projects") -> bool:
        """Deploy projects using the master deployer."""
        if not self.master_deployer:
            self.logger.warning("Master compliance deployer not available")
            return True
        
        if self.config["deployment"]["dry_run"]:
            self.logger.info("DRY RUN: Would deploy projects")
            return True
        
        self.logger.info("Deploying projects...")
        
        try:
            # Deploy projects
            result = self.master_deployer.deploy_projects(projects_dir)
            
            if not result["success"]:
                self.logger.error("Deployment failed")
                return False
            
            self.logger.info("Deployment completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "security_audits_processed": len(self.security_audits),
            "deployment_blockers": len(self.deployment_blockers),
            "blocker_details": self.deployment_blockers,
            "recommendations": []
        }
        
        # Add recommendations based on blockers
        if self.deployment_blockers:
            critical_count = len([b for b in self.deployment_blockers if b["severity"] == "CRITICAL"])
            high_count = len([b for b in self.deployment_blockers if b["severity"] == "HIGH"])
            
            if critical_count > 0:
                report["recommendations"].append(f"Address {critical_count} critical vulnerabilities before deployment")
            
            if high_count > 0:
                report["recommendations"].append(f"Review {high_count} high severity vulnerabilities")
        
        return report
    
    def run_full_deployment(self, 
                          projects_dir: str = "projects",
                          audit_files: List[str] = None,
                          skip_security: bool = False,
                          skip_compliance: bool = False,
                          skip_build: bool = False,
                          skip_deploy: bool = False) -> bool:
        """Run the complete enhanced deployment process."""
        
        self.logger.info("Starting enhanced master deployment process")
        
        # Step 1: Process security audits
        if not skip_security and self.config["security_audit"]["enabled"]:
            if audit_files:
                if not self.process_security_audits(audit_files):
                    self.logger.error("Security audit processing failed - deployment blocked")
                    return False
            else:
                self.logger.info("No security audit files provided - skipping security checks")
        
        # Step 2: Run compliance checks
        if not skip_compliance and self.config["compliance"]["enabled"]:
            if not self.run_compliance_checks(projects_dir):
                self.logger.error("Compliance checks failed - deployment blocked")
                return False
        
        # Step 3: Run build validation
        if not skip_build and self.config["deployment"]["enabled"]:
            if not self.run_build_validation(projects_dir):
                self.logger.error("Build validation failed - deployment blocked")
                return False
        
        # Step 4: Deploy projects
        if not skip_deploy and self.config["deployment"]["enabled"]:
            if not self.deploy_projects(projects_dir):
                self.logger.error("Deployment failed")
                return False
        
        # Generate final report
        security_report = self.generate_security_report()
        
        # Save final report
        with open("enhanced-deployment-report.json", 'w', encoding='utf-8') as f:
            json.dump(security_report, f, indent=2)
        
        self.logger.info("Enhanced master deployment process completed successfully")
        return True

def main():
    parser = argparse.ArgumentParser(description="Enhanced Master Compliance and Deployment System")
    parser.add_argument("--projects-dir", default="projects", help="Directory containing OSS-Fuzz projects")
    parser.add_argument("--config", default="deployment-config.yaml", help="Configuration file")
    parser.add_argument("--audit-files", nargs="+", help="Security audit files to process")
    parser.add_argument("--skip-security", action="store_true", help="Skip security audit processing")
    parser.add_argument("--skip-compliance", action="store_true", help="Skip compliance checks")
    parser.add_argument("--skip-build", action="store_true", help="Skip build validation")
    parser.add_argument("--skip-deploy", action="store_true", help="Skip deployment")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--security-only", action="store_true", help="Only process security audits")
    parser.add_argument("--compliance-only", action="store_true", help="Only run compliance checks")
    parser.add_argument("--build-only", action="store_true", help="Only run build validation")
    parser.add_argument("--deploy-only", action="store_true", help="Only deploy projects")
    
    args = parser.parse_args()
    
    # Initialize enhanced deployer
    deployer = EnhancedMasterDeployer(args.config)
    
    # Set dry-run mode if requested
    if args.dry_run:
        deployer.config["deployment"]["dry_run"] = True
    
    # Handle single-mode operations
    if args.security_only:
        if args.audit_files:
            success = deployer.process_security_audits(args.audit_files)
            sys.exit(0 if success else 1)
        else:
            print("Error: --security-only requires --audit-files")
            sys.exit(1)
    
    if args.compliance_only:
        success = deployer.run_compliance_checks(args.projects_dir)
        sys.exit(0 if success else 1)
    
    if args.build_only:
        success = deployer.run_build_validation(args.projects_dir)
        sys.exit(0 if success else 1)
    
    if args.deploy_only:
        success = deployer.deploy_projects(args.projects_dir)
        sys.exit(0 if success else 1)
    
    # Run full deployment
    success = deployer.run_full_deployment(
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
