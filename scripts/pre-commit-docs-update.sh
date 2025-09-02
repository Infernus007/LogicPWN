#!/bin/bash

# Pre-commit hook to update API documentation
# This script runs before commits to ensure documentation is up to date

set -e

echo "📚 Updating API documentation..."

# Check if we're on a protected branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    echo "⚠️  On protected branch ($CURRENT_BRANCH), skipping documentation update"
    exit 0
fi

# Check if we're on a valid branch (not detached HEAD)
if [[ "$CURRENT_BRANCH" == "" ]]; then
    echo "⚠️  Not on a valid branch, skipping documentation update"
    exit 0
fi

# Generate API documentation
echo "🔧 Generating API documentation..."
python3 scripts/generate_simple_api_docs.py

# Fix API documentation structure
echo "🔧 Fixing API documentation structure..."
python3 scripts/fix_api_docs.py

# Check for documentation changes
DOC_FILES=$(git diff --name-only | grep -E '\.(md|rst|html|css|js|yaml|yml|json)$' || true)

if [[ -n "$DOC_FILES" ]]; then
    echo "📝 Staging documentation changes..."
    echo "$DOC_FILES" | sed 's/^/  - /'

    # Stage all documentation files
    echo "$DOC_FILES" | xargs -r git add

    echo "✅ Documentation changes staged successfully"
    echo "💡 Changes will be auto-committed after the main commit completes"
else
    echo "ℹ️  No documentation changes detected"
fi

echo "✅ API documentation update completed!"
