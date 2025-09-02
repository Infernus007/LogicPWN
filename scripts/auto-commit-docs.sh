#!/bin/bash

# Post-commit hook to auto-commit and push documentation changes
# This script runs after commits to handle documentation updates

set -e

echo "🤖 Post-commit: Auto-committing documentation changes..."

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
- Auto-commit by post-commit hook"

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

    # Check if remote exists and push
    if git remote get-url origin >/dev/null 2>&1; then
        echo "🚀 Pushing documentation changes to remote..."

        # Push with retry logic
        MAX_RETRIES=3
        RETRY_COUNT=0

        while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
            if git push origin "$CURRENT_BRANCH"; then
                echo "✅ Documentation changes pushed successfully to origin/$CURRENT_BRANCH"
                break
            else
                RETRY_COUNT=$((RETRY_COUNT + 1))
                if [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; then
                    echo "⚠️  Push failed, retrying in 5 seconds... (attempt $RETRY_COUNT/$MAX_RETRIES)"
                    sleep 5
                else
                    echo "❌ Failed to push after $MAX_RETRIES attempts"
                    echo "💡 You can manually push with: git push origin $CURRENT_BRANCH"
                    exit 1
                fi
            fi
        done
    else
        echo "⚠️  No remote origin found, skipping push"
    fi
else
    echo "ℹ️  No documentation changes to commit"
fi

echo "🎉 Post-commit auto-commit process completed!"
