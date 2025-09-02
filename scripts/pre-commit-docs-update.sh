#!/bin/bash

# Pre-commit documentation update script
# This script generates API documentation and stages the changes

set -e

echo "📚 Generating API documentation..."

# Change to project root
cd "$(dirname "$0")/.."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check if we're on a protected branch
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    echo "⚠️  On protected branch ($CURRENT_BRANCH), skipping documentation generation"
    exit 0
fi

# Generate API documentation
echo "🔧 Running API documentation generation..."

# Run the documentation generation script if it exists
if [[ -f "scripts/generate_simple_api_docs.py" ]]; then
    echo "📖 Generating simple API docs..."
    python3 scripts/generate_simple_api_docs.py
fi

# Run any other documentation generation commands
if [[ -f "scripts/fix_api_docs.py" ]]; then
    echo "🔧 Fixing API docs structure..."
    python3 scripts/fix_api_docs.py
fi

# Check if there are any documentation files to stage
DOC_FILES=$(git status --porcelain | grep -E '\.(md|rst|html|css|js|yaml|yml|json)$' | awk '{print $2}' || true)

if [[ -n "$DOC_FILES" ]]; then
    echo "📝 Staging documentation changes..."
    echo "$DOC_FILES" | sed 's/^/  - /'

    # Stage all documentation files
    echo "$DOC_FILES" | xargs -r git add

    echo "✅ Documentation changes staged successfully"
    echo "💡 Changes will be auto-committed after pre-commit hooks complete"
else
    echo "ℹ️  No documentation changes to stage"
fi

echo "🎉 Documentation generation completed!"
