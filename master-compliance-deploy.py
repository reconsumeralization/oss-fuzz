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
Master Compliance and Deployment Script for OSS-Fuzz Projects
Maintains compliance across multiple projects and brings them online in correct order
"""

import asyncio
import json
import subprocess
import sys
import time
import yaml
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import logging
import argparse
import shutil
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master-compliance-deploy.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ProjectStatus(Enum):
    PENDING = "pending"
    COMPLIANCE_CHECK = "compliance_check"
    BUILD_VALIDATION = "build_validation"
    DEPLOYMENT_READY = "deployment_ready"
    DEPLOYING = "deploying"
    ONLINE = "online"
    FAILED = "failed"

@dataclass
class ProjectConfig:
    name: str
    path: Path
    priority: int
    dependencies: List[str]
    language: str
    status: ProjectStatus
    compliance_issues: List[str]
    build_issues: List[str]
    deployment_issues: List[str]

class MasterComplianceDeployer:
    """Master orchestrator for multi-project compliance and deployment"""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects: Dict[str, ProjectConfig] = {}
        self.deployment_order: List[str] = []
        self.compliance_cache: Dict[str, Dict] = {}
        self.build_cache: Dict[str, Dict] = {}
        
        # Compliance patterns
        self.google_copyright_pattern = re.compile(
            r'Copyright 2025 Google LLC',
            re.IGNORECASE
        )
        
        self.ai_reference_patterns = [
            re.compile(r'ai-powered', re.IGNORECASE),
            re.compile(r'ai-assisted', re.IGNORECASE),
            re.compile(r'sentient core', re.IGNORECASE),
            re.compile(r'tower of babel', re.IGNORECASE),
        ]
        
        # Files to exclude from AI reference checks
        self.excluded_files = {
            'orchestrate-rollout.py',
            'rapid_expand.py', 
            'automated-rollout.yml',
            'master-compliance-deploy.py',
            'deploy.sh',
            'build.sh'
        }
        
        # Project dependencies and priorities
        self.project_priorities = {
            'gemini_cli': 1,      # Highest priority - main integration
            'gemini-cli': 2,      # Secondary integration
            'model-transparency': 3,  # Related AI/ML project
            'g-api-python-tasks': 4,  # Google API integration
        }
        
    async def discover_projects(self) -> None:
        """Discover all OSS-Fuzz projects in the directory"""
        logging.info("Discovering OSS-Fuzz projects...")
        
        if not self.projects_dir.exists():
            logging.error(f"Projects directory not found: {self.projects_dir}")
            return
            
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
                
            project_name = project_dir.name
            project_yaml = project_dir / "project.yaml"
            
            if not project_yaml.exists():
                continue
                
            # Determine priority
            priority = self.project_priorities.get(project_name, 999)
            
            # Read project configuration
            try:
                with open(project_yaml, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                language = config.get('language', 'unknown')
                homepage = config.get('homepage', '')
                
                # Determine dependencies based on project relationships
                dependencies = self._determine_dependencies(project_name, config)
                
                self.projects[project_name] = ProjectConfig(
                    name=project_name,
                    path=project_dir,
                    priority=priority,
                    dependencies=dependencies,
                    language=language,
                    status=ProjectStatus.PENDING,
                    compliance_issues=[],
                    build_issues=[],
                    deployment_issues=[]
                )
                
                logging.info(f"Discovered project: {project_name} (priority: {priority}, language: {language})")
                
            except Exception as e:
                logging.error(f"Error reading project {project_name}: {e}")
                
        logging.info(f"Discovered {len(self.projects)} projects")
        
    def _determine_dependencies(self, project_name: str, config: Dict) -> List[str]:
        """Determine project dependencies based on configuration"""
        dependencies = []
        
        # Gemini CLI projects depend on each other
        if 'gemini' in project_name.lower():
            for other_project in self.projects:
                if other_project != project_name and 'gemini' in other_project.lower():
                    dependencies.append(other_project)
                    
        # Model transparency depends on Gemini CLI
        if project_name == 'model-transparency':
            dependencies.extend(['gemini_cli', 'gemini-cli'])
            
        # G-API projects depend on Google infrastructure
        if 'g-api' in project_name.lower():
            dependencies.extend(['gemini_cli'])
            
        return dependencies
        
    async def calculate_deployment_order(self) -> None:
        """Calculate the correct deployment order based on dependencies"""
        logging.info("Calculating deployment order...")
        
        # Sort by priority first
        sorted_projects = sorted(
            self.projects.values(),
            key=lambda p: p.priority
        )
        
        # Build dependency graph
        dependency_graph = {}
        for project in sorted_projects:
            dependency_graph[project.name] = project.dependencies.copy()
            
        # Topological sort
        self.deployment_order = self._topological_sort(dependency_graph)
        
        logging.info(f"Deployment order: {self.deployment_order}")
        
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort for dependency resolution"""
        in_degree = {node: 0 for node in graph}
        
        # Calculate in-degrees
        for node, dependencies in graph.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
                    
        # Find nodes with no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort by priority
            queue.sort(key=lambda x: self.projects[x].priority if x in self.projects else 999)
            node = queue.pop(0)
            result.append(node)
            
            # Update in-degrees
            for dep in graph.get(node, []):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)
                        
        return result
        
    async def run_compliance_checks(self) -> bool:
        """Run compliance checks on all projects"""
        logging.info("Running compliance checks on all projects...")
        
        all_compliant = True
        
        for project_name in self.deployment_order:
            project = self.projects[project_name]
            logging.info(f"Checking compliance for {project_name}...")
            
            project.status = ProjectStatus.COMPLIANCE_CHECK
            project.compliance_issues = []
            
            # Run compliance checks
            compliant = await self._check_project_compliance(project)
            
            if not compliant:
                all_compliant = False
                project.status = ProjectStatus.FAILED
                logging.error(f"Compliance check failed for {project_name}")
            else:
                logging.info(f"Compliance check passed for {project_name}")
                
        return all_compliant
        
    async def _check_project_compliance(self, project: ProjectConfig) -> bool:
        """Check compliance for a single project"""
        issues = []
        
        # Check project.yaml
        project_yaml = project.path / "project.yaml"
        if not await self._check_file_compliance(project_yaml, project.name):
            issues.append("project.yaml compliance issues")
            
        # Check all Python files
        for py_file in project.path.rglob("*.py"):
            if not await self._check_file_compliance(py_file, project.name):
                issues.append(f"Python file compliance: {py_file.name}")
                
        # Check all JavaScript files
        for js_file in project.path.rglob("*.js"):
            if not await self._check_file_compliance(js_file, project.name):
                issues.append(f"JavaScript file compliance: {js_file.name}")
                
        # Check all TypeScript files
        for ts_file in project.path.rglob("*.ts"):
            if not await self._check_file_compliance(ts_file, project.name):
                issues.append(f"TypeScript file compliance: {ts_file.name}")
                
        # Check YAML files
        for yaml_file in project.path.rglob("*.yml"):
            if not await self._check_file_compliance(yaml_file, project.name):
                issues.append(f"YAML file compliance: {yaml_file.name}")
                
        for yaml_file in project.path.rglob("*.yaml"):
            if not await self._check_file_compliance(yaml_file, project.name):
                issues.append(f"YAML file compliance: {yaml_file.name}")
                
        project.compliance_issues = issues
        return len(issues) == 0
        
    async def _check_file_compliance(self, file_path: Path, project_name: str) -> bool:
        """Check compliance for a single file"""
        if not file_path.exists():
            return True
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip excluded files
            if file_path.name in self.excluded_files:
                return True
                
            # Check for Google copyright header
            if file_path.suffix in ['.py', '.js', '.ts', '.go', '.java']:
                if not self.google_copyright_pattern.search(content):
                    logging.warning(f"Missing Google copyright header: {file_path}")
                    return False
                    
            # Check for AI references (except in excluded files)
            for pattern in self.ai_reference_patterns:
                if pattern.search(content):
                    logging.warning(f"AI reference found in {file_path}: {pattern.pattern}")
                    return False
                    
            return True
            
        except Exception as e:
            logging.error(f"Error checking compliance for {file_path}: {e}")
            return False
            
    async def run_build_validation(self) -> bool:
        """Run build validation on all projects"""
        logging.info("Running build validation on all projects...")
        
        all_valid = True
        
        for project_name in self.deployment_order:
            project = self.projects[project_name]
            
            if project.status == ProjectStatus.FAILED:
                continue
                
            logging.info(f"Validating build for {project_name}...")
            
            project.status = ProjectStatus.BUILD_VALIDATION
            project.build_issues = []
            
            # Run build validation
            valid = await self._validate_project_build(project)
            
            if not valid:
                all_valid = False
                project.status = ProjectStatus.FAILED
                logging.error(f"Build validation failed for {project_name}")
            else:
                project.status = ProjectStatus.DEPLOYMENT_READY
                logging.info(f"Build validation passed for {project_name}")
                
        return all_valid
        
    async def _validate_project_build(self, project: ProjectConfig) -> bool:
        """Validate build for a single project"""
        issues = []
        
        # Check for required files
        required_files = ['project.yaml', 'Dockerfile']
        for required_file in required_files:
            if not (project.path / required_file).exists():
                issues.append(f"Missing required file: {required_file}")
                
        # Check for build script
        build_script = project.path / "build.sh"
        if not build_script.exists():
            issues.append("Missing build.sh script")
        elif not os.access(build_script, os.X_OK):
            issues.append("build.sh not executable")
            
        # Check for fuzzers directory
        fuzzers_dir = project.path / "fuzzers"
        if not fuzzers_dir.exists():
            issues.append("Missing fuzzers directory")
            
        # Validate project.yaml syntax
        project_yaml = project.path / "project.yaml"
        if project_yaml.exists():
            try:
                with open(project_yaml, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                issues.append(f"Invalid YAML in project.yaml: {e}")
                
        project.build_issues = issues
        return len(issues) == 0
        
    async def deploy_projects(self) -> bool:
        """Deploy projects in the correct order"""
        logging.info("Starting deployment of projects...")
        
        all_deployed = True
        
        for project_name in self.deployment_order:
            project = self.projects[project_name]
            
            if project.status == ProjectStatus.FAILED:
                logging.warning(f"Skipping failed project: {project_name}")
                continue
                
            logging.info(f"Deploying {project_name}...")
            
            project.status = ProjectStatus.DEPLOYING
            
            # Deploy project
            success = await self._deploy_project(project)
            
            if success:
                project.status = ProjectStatus.ONLINE
                logging.info(f"Successfully deployed {project_name}")
            else:
                project.status = ProjectStatus.FAILED
                all_deployed = False
                logging.error(f"Failed to deploy {project_name}")
                
        return all_deployed
        
    async def _deploy_project(self, project: ProjectConfig) -> bool:
        """Deploy a single project"""
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project.path)
            
            # Check if there's a custom deployment script
            deploy_script = project.path / "deploy.sh"
            if deploy_script.exists() and os.access(deploy_script, os.X_OK):
                # Run custom deployment script
                result = subprocess.run(
                    [str(deploy_script)],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if result.returncode != 0:
                    logging.error(f"Deployment script failed: {result.stderr}")
                    return False
                    
            else:
                # Use standard OSS-Fuzz deployment
                result = subprocess.run(
                    ['git', 'add', '.'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if result.returncode != 0:
                    logging.error(f"Git add failed: {result.stderr}")
                    return False
                    
                result = subprocess.run(
                    ['git', 'commit', '-m', f'Deploy {project.name} to OSS-Fuzz'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if result.returncode != 0:
                    logging.error(f"Git commit failed: {result.stderr}")
                    return False
                    
                result = subprocess.run(
                    ['git', 'push'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if result.returncode != 0:
                    logging.error(f"Git push failed: {result.stderr}")
                    return False
                    
            # Restore original directory
            os.chdir(original_cwd)
            
            return True
            
        except Exception as e:
            logging.error(f"Error deploying {project.name}: {e}")
            return False
            
    async def generate_compliance_report(self) -> None:
        """Generate a comprehensive compliance report"""
        logging.info("Generating compliance report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_projects': len(self.projects),
                'deployed': len([p for p in self.projects.values() if p.status == ProjectStatus.ONLINE]),
                'failed': len([p for p in self.projects.values() if p.status == ProjectStatus.FAILED]),
                'pending': len([p for p in self.projects.values() if p.status == ProjectStatus.PENDING])
            },
            'projects': {}
        }
        
        for project_name, project in self.projects.items():
            report['projects'][project_name] = {
                'status': project.status.value,
                'priority': project.priority,
                'language': project.language,
                'dependencies': project.dependencies,
                'compliance_issues': project.compliance_issues,
                'build_issues': project.build_issues,
                'deployment_issues': project.deployment_issues
            }
            
        # Write report
        with open('compliance-report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logging.info("Compliance report written to compliance-report.json")
        
    async def run_full_deployment(self) -> bool:
        """Run the complete compliance and deployment process"""
        logging.info("Starting full compliance and deployment process...")
        
        try:
            # Step 1: Discover projects
            await self.discover_projects()
            
            if not self.projects:
                logging.error("No projects discovered")
                return False
                
            # Step 2: Calculate deployment order
            await self.calculate_deployment_order()
            
            # Step 3: Run compliance checks
            if not await self.run_compliance_checks():
                logging.error("Compliance checks failed")
                await self.generate_compliance_report()
                return False
                
            # Step 4: Run build validation
            if not await self.run_build_validation():
                logging.error("Build validation failed")
                await self.generate_compliance_report()
                return False
                
            # Step 5: Deploy projects
            if not await self.deploy_projects():
                logging.error("Deployment failed")
                await self.generate_compliance_report()
                return False
                
            # Step 6: Generate final report
            await self.generate_compliance_report()
            
            logging.info("Full deployment completed successfully!")
            return True
            
        except Exception as e:
            logging.error(f"Deployment process failed: {e}")
            await self.generate_compliance_report()
            return False

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Master Compliance and Deployment Script')
    parser.add_argument('--projects-dir', default='projects', help='Projects directory')
    parser.add_argument('--compliance-only', action='store_true', help='Run compliance checks only')
    parser.add_argument('--build-only', action='store_true', help='Run build validation only')
    parser.add_argument('--deploy-only', action='store_true', help='Run deployment only')
    
    args = parser.parse_args()
    
    deployer = MasterComplianceDeployer(args.projects_dir)
    
    if args.compliance_only:
        await deployer.discover_projects()
        await deployer.calculate_deployment_order()
        success = await deployer.run_compliance_checks()
        await deployer.generate_compliance_report()
        return success
        
    elif args.build_only:
        await deployer.discover_projects()
        await deployer.calculate_deployment_order()
        success = await deployer.run_build_validation()
        await deployer.generate_compliance_report()
        return success
        
    elif args.deploy_only:
        await deployer.discover_projects()
        await deployer.calculate_deployment_order()
        success = await deployer.deploy_projects()
        await deployer.generate_compliance_report()
        return success
        
    else:
        return await deployer.run_full_deployment()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
