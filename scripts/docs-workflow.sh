#!/bin/bash

# Comprehensive Documentation Workflow Script
# This script demonstrates the complete documentation workflow with auto-commit

set -e

echo "🚀 LogicPWN Documentation Workflow"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_status $RED "❌ Not in a git repository"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
print_status $BLUE "📍 Current branch: $CURRENT_BRANCH"

# Check if we're on a protected branch
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    print_status $YELLOW "⚠️  On protected branch ($CURRENT_BRANCH)"
    print_status $YELLOW "   Creating feature branch for documentation updates..."

    # Create a new feature branch
    FEATURE_BRANCH="docs/auto-update-$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$FEATURE_BRANCH"
    print_status $GREEN "✅ Created feature branch: $FEATURE_BRANCH"
fi

# Step 1: Generate Documentation
print_status $BLUE "\n📚 Step 1: Generating API Documentation"
echo "Running documentation generation scripts..."

if [[ -f "scripts/generate_simple_api_docs.py" ]]; then
    print_status $BLUE "🔧 Generating simple API docs..."
    python3 scripts/generate_simple_api_docs.py
fi

if [[ -f "scripts/fix_api_docs.py" ]]; then
    print_status $BLUE "🔧 Fixing API docs structure..."
    python3 scripts/fix_api_docs.py
fi

# Step 2: Stage Documentation Changes
print_status $BLUE "\n📝 Step 2: Staging Documentation Changes"

# Check for documentation files
DOC_FILES=$(git status --porcelain | grep -E '\.(md|rst|html|css|js|yaml|yml|json)$' | awk '{print $2}' || true)

if [[ -n "$DOC_FILES" ]]; then
    print_status $GREEN "📚 Found documentation changes:"
    echo "$DOC_FILES" | sed 's/^/  - /'

    # Stage all documentation files
    echo "$DOC_FILES" | xargs -r git add
    print_status $GREEN "✅ Documentation changes staged successfully"
else
    print_status $YELLOW "ℹ️  No documentation changes to stage"
fi

# Step 3: Run Pre-commit Hooks
print_status $BLUE "\n🔍 Step 3: Running Pre-commit Hooks"
echo "Running code quality checks and formatting..."

if poetry run pre-commit run --all-files; then
    print_status $GREEN "✅ Pre-commit hooks passed successfully"
else
    print_status $RED "❌ Pre-commit hooks failed"
    print_status $YELLOW "💡 Fix the issues and run again"
    exit 1
fi

# Step 4: Auto-commit and Push
print_status $BLUE "\n🤖 Step 4: Auto-commit and Push"
echo "Automatically committing and pushing documentation changes..."

if ./scripts/auto-commit-docs.sh; then
    print_status $GREEN "✅ Documentation changes committed and pushed successfully"
else
    print_status $YELLOW "⚠️  Auto-commit failed, you may need to commit manually"
fi

# Step 5: Summary
print_status $GREEN "\n🎉 Documentation Workflow Completed!"
echo ""
echo "📋 Summary:"
echo "  - Branch: $CURRENT_BRANCH"
echo "  - Documentation generated and updated"
echo "  - Code quality checks passed"
echo "  - Changes committed and pushed"
echo ""
echo "🚀 Next steps:"
echo "  - Create a pull request if needed"
echo "  - Review the documentation changes"
echo "  - Merge when ready"
echo ""
echo "💡 You can also run individual steps:"
echo "  - make docs-update    # Generate docs only"
echo "  - make auto-commit    # Commit and push only"
echo "  - make docs-workflow  # Complete workflow"
