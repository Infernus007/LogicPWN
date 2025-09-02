#!/bin/bash

# Pre-commit hook to auto-commit documentation changes
# This script runs during pre-commit to handle documentation updates

set -e

echo "🤖 Pre-commit: Checking for documentation changes..."

# Get the current branch name
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check if we're on a valid branch (not detached HEAD)
if [[ "$CURRENT_BRANCH" == "" ]]; then
    echo "⚠️  Not on a valid branch, skipping auto-commit"
    exit 0
fi

# Check if we're on main/master branch (don't auto-commit to protected branches)
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    echo "⚠️  On protected branch ($CURRENT_BRANCH), skipping auto-commit"
    exit 0
fi

# Check if there are any unstaged documentation changes
DOC_FILES=$(git diff --name-only | grep -E '\.(md|rst|html|css|js|yaml|yml|json)$' || true)
SUBMODULE_CHANGES=$(git diff --name-only | grep -E '^(doks|docs)/' || true)

if [[ -n "$DOC_FILES" ]] || [[ -n "$SUBMODULE_CHANGES" ]]; then
    echo "📚 Documentation changes detected:"
    if [[ -n "$DOC_FILES" ]]; then
        echo "  - Direct documentation files:"
        echo "$DOC_FILES" | sed 's/^/    - /'
    fi
    if [[ -n "$SUBMODULE_CHANGES" ]]; then
        echo "  - Submodule changes:"
        echo "$SUBMODULE_CHANGES" | sed 's/^/    - /'
    fi

    # Stage all documentation changes
    if [[ -n "$DOC_FILES" ]]; then
        echo "📝 Staging documentation files..."
        echo "$DOC_FILES" | xargs -r git add
    fi

    if [[ -n "$SUBMODULE_CHANGES" ]]; then
        echo "📝 Staging submodule changes..."
        echo "$SUBMODULE_CHANGES" | xargs -r git add
    fi

    # Create commit message
    COMMIT_MSG="📚 Auto-update documentation

- Updated API documentation
- Generated latest docs from source code
- Auto-commit by pre-commit hook"

    if [[ -n "$DOC_FILES" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Files changed:
$(echo "$DOC_FILES" | sed 's/^/  - /')"
    fi

    if [[ -n "$SUBMODULE_CHANGES" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Submodule changes:
$(echo "$SUBMODULE_CHANGES" | sed 's/^/  - /')"
    fi

    COMMIT_MSG="$COMMIT_MSG

[skip ci]"

    # Commit the changes (bypass pre-commit hooks to avoid loops)
    git commit --no-verify -m "$COMMIT_MSG" || {
        echo "❌ Failed to commit documentation changes"
        exit 1
    }

    echo "✅ Documentation changes committed successfully"
    echo "💡 These changes will be included in the main commit"
else
    echo "ℹ️  No documentation changes to commit"
fi

echo "🎉 Pre-commit auto-commit process completed!"
