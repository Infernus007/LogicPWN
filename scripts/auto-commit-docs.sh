#!/bin/bash

# Auto-commit and push documentation changes
# This script runs after pre-commit hooks to automatically commit and push docs

set -e

echo "🤖 Auto-committing documentation changes..."

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

# Check if there are any staged changes
if ! git diff --cached --quiet; then
    echo "📝 Found staged changes, committing documentation updates..."

    # Get list of changed documentation files
    DOC_FILES=$(git diff --cached --name-only | grep -E '\.(md|rst|html|css|js|yaml|yml|json)$' || true)

    if [[ -n "$DOC_FILES" ]]; then
        echo "📚 Documentation files changed:"
        echo "$DOC_FILES" | sed 's/^/  - /'

        # Create commit message
        COMMIT_MSG="📚 Auto-update documentation

        - Updated API documentation
        - Generated latest docs from source code
        - Auto-commit by pre-commit hook

        Files changed:
        $(echo "$DOC_FILES" | sed 's/^/  - /')

        [skip ci]"

        # Commit the changes
        git commit -m "$COMMIT_MSG" || {
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
        echo "ℹ️  No documentation files in staged changes"
    fi
else
    echo "ℹ️  No staged changes to commit"
fi

echo "🎉 Auto-commit process completed!"
