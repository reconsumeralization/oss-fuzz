#!/bin/bash

# OSS-Fuzz Foundation Validation Script
# Run this before submitting PR to ensure everything is correct

echo "🔍 Validating OSS-Fuzz Foundation Setup..."

# Check required files exist
echo "📁 Checking required files..."
required_files=("project.yaml" "Dockerfile" "build.sh" ".gitignore" "README.md" "PR_STRATEGY.md")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
        exit 1
    fi
done

# Validate project.yaml
echo "📋 Validating project.yaml..."
if grep -q "language: go" project.yaml; then
    echo "  ✅ Language set to Go"
else
    echo "  ❌ Language not set to Go"
    exit 1
fi

if grep -q "FuzzConfigParser\|FuzzCLIParser\|FuzzInputSanitizer" project.yaml; then
    echo "  ✅ Foundation fuzz targets listed"
else
    echo "  ❌ Foundation fuzz targets missing"
    exit 1
fi

# Validate build.sh
echo "🔨 Validating build.sh..."
if grep -q "compile_go_fuzzer.*FuzzConfigParser" build.sh; then
    echo "  ✅ FuzzConfigParser compilation found"
else
    echo "  ❌ FuzzConfigParser compilation missing"
    exit 1
fi

if grep -q "compile_go_fuzzer.*FuzzCLIParser" build.sh; then
    echo "  ✅ FuzzCLIParser compilation found"
else
    echo "  ❌ FuzzCLIParser compilation missing"
    exit 1
fi

if grep -q "compile_go_fuzzer.*FuzzInputSanitizer" build.sh; then
    echo "  ✅ FuzzInputSanitizer compilation found"
else
    echo "  ❌ FuzzInputSanitizer compilation missing"
    exit 1
fi

# Validate .gitignore
echo "🚫 Validating .gitignore..."
if grep -q "node_modules/" .gitignore; then
    echo "  ✅ node_modules excluded"
else
    echo "  ❌ node_modules not excluded"
    exit 1
fi

# Check for DCO compliance
echo "📝 Checking DCO compliance..."
if git log --grep="Signed-off-by" --oneline | head -1; then
    echo "  ✅ DCO sign-off found"
else
    echo "  ⚠️  No DCO sign-off found - use 'git commit -s' for future commits"
fi

# Summary
echo ""
echo "🎉 Foundation validation complete!"
echo "📋 Files to submit:"
echo "  - project.yaml"
echo "  - Dockerfile" 
echo "  - build.sh"
echo "  - .gitignore"
echo "  - README.md"
echo "  - PR_STRATEGY.md"
echo ""
echo "📤 Ready for PR submission!"
echo "💡 Remember to use the PR description template from PR_SUBMISSION_GUIDE.md"
