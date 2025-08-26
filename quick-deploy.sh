#!/bin/bash
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

# Quick Deploy Script for OSS-Fuzz Master Compliance and Deployment
# Provides easy access to common deployment scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Quick Deploy Script for OSS-Fuzz Master Compliance and Deployment"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --full-deploy          Run complete compliance check, build validation, and deployment"
    echo "  --compliance-only      Run compliance checks only"
    echo "  --build-only           Run build validation only"
    echo "  --deploy-only          Run deployment only (skip compliance and build checks)"
    echo "  --dry-run              Show what would be deployed without actually deploying"
    echo "  --projects-dir DIR     Specify projects directory (default: projects)"
    echo "  --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --full-deploy                    # Complete deployment process"
    echo "  $0 --compliance-only                # Check compliance only"
    echo "  $0 --deploy-only --projects-dir custom_projects"
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if required Python packages are available
    python3 -c "import yaml, asyncio, json" 2>/dev/null || {
        print_error "Required Python packages missing. Please install: yaml, asyncio, json"
        exit 1
    }
    
    # Check if master deployment script exists
    if [ ! -f "master-compliance-deploy.py" ]; then
        print_error "master-compliance-deploy.py not found in current directory"
        exit 1
    fi
    
    # Check if deployment config exists
    if [ ! -f "deployment-config.yaml" ]; then
        print_warning "deployment-config.yaml not found, using defaults"
    fi
    
    print_success "Prerequisites check passed"
}

# Function to run compliance checks
run_compliance() {
    print_status "Running compliance checks..."
    python3 master-compliance-deploy.py --compliance-only --projects-dir "$PROJECTS_DIR"
    
    if [ $? -eq 0 ]; then
        print_success "Compliance checks completed successfully"
    else
        print_error "Compliance checks failed"
        exit 1
    fi
}

# Function to run build validation
run_build_validation() {
    print_status "Running build validation..."
    python3 master-compliance-deploy.py --build-only --projects-dir "$PROJECTS_DIR"
    
    if [ $? -eq 0 ]; then
        print_success "Build validation completed successfully"
    else
        print_error "Build validation failed"
        exit 1
    fi
}

# Function to run deployment
run_deployment() {
    print_status "Running deployment..."
    python3 master-compliance-deploy.py --deploy-only --projects-dir "$PROJECTS_DIR"
    
    if [ $? -eq 0 ]; then
        print_success "Deployment completed successfully"
    else
        print_error "Deployment failed"
        exit 1
    fi
}

# Function to run full deployment
run_full_deployment() {
    print_status "Starting full deployment process..."
    
    # Step 1: Compliance checks
    run_compliance
    
    # Step 2: Build validation
    run_build_validation
    
    # Step 3: Deployment
    run_deployment
    
    print_success "Full deployment process completed successfully!"
}

# Function to show deployment plan (dry run)
show_deployment_plan() {
    print_status "Showing deployment plan (dry run)..."
    
    # Discover projects and show what would be deployed
    python3 -c "
import asyncio
import sys
sys.path.append('.')
from master_compliance_deploy import MasterComplianceDeployer

async def show_plan():
    deployer = MasterComplianceDeployer('$PROJECTS_DIR')
    await deployer.discover_projects()
    await deployer.calculate_deployment_order()
    
    print('\\n=== DEPLOYMENT PLAN ===')
    print(f'Total projects discovered: {len(deployer.projects)}')
    print('\\nDeployment order:')
    for i, project_name in enumerate(deployer.deployment_order, 1):
        project = deployer.projects[project_name]
        print(f'  {i}. {project_name} (priority: {project.priority}, language: {project.language})')
        if project.dependencies:
            print(f'     Dependencies: {", ".join(project.dependencies)}')
    
    print('\\n=== COMPLIANCE CHECKS ===')
    print('Will check:')
    print('  - Google copyright headers')
    print('  - AI reference compliance')
    print('  - YAML syntax validation')
    print('  - Required file presence')
    
    print('\\n=== BUILD VALIDATION ===')
    print('Will validate:')
    print('  - project.yaml syntax')
    print('  - Dockerfile presence')
    print('  - build.sh script')
    print('  - fuzzers directory')
    
    print('\\n=== DEPLOYMENT ===')
    print('Will deploy projects in order with:')
    print('  - Git add/commit/push')
    print('  - Custom deployment scripts (if available)')
    print('  - Health checks')
    print('  - Rollback on failure')

asyncio.run(show_plan())
"
}

# Main script logic
PROJECTS_DIR="projects"
FULL_DEPLOY=false
COMPLIANCE_ONLY=false
BUILD_ONLY=false
DEPLOY_ONLY=false
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full-deploy)
            FULL_DEPLOY=true
            shift
            ;;
        --compliance-only)
            COMPLIANCE_ONLY=true
            shift
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --deploy-only)
            DEPLOY_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --projects-dir)
            PROJECTS_DIR="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if at least one option is specified
if [ "$FULL_DEPLOY" = false ] && [ "$COMPLIANCE_ONLY" = false ] && [ "$BUILD_ONLY" = false ] && [ "$DEPLOY_ONLY" = false ] && [ "$DRY_RUN" = false ]; then
    print_error "No deployment option specified"
    show_usage
    exit 1
fi

# Check prerequisites
check_prerequisites

# Execute based on options
if [ "$DRY_RUN" = true ]; then
    show_deployment_plan
elif [ "$FULL_DEPLOY" = true ]; then
    run_full_deployment
elif [ "$COMPLIANCE_ONLY" = true ]; then
    run_compliance
elif [ "$BUILD_ONLY" = true ]; then
    run_build_validation
elif [ "$DEPLOY_ONLY" = true ]; then
    run_deployment
fi

print_success "Quick deploy script completed!"
