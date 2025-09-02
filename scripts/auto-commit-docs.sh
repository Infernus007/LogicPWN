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

# Check if there are any unstaged or staged documentation changes
DOC_FILES=$(git diff --name-only | grep -E '\.(md|rst|html|css|js|yaml|yml|json)$' || true)
SUBMODULE_CHANGES=$(git diff --name-only | grep -E '^(doks|docs)/' || true)
SUBMODULE_DIR=$(git diff --name-only | grep -E '^(doks|docs)$' || true)

# Also check staged changes
STAGED_DOC_FILES=$(git diff --cached --name-only | grep -E '\.(md|rst|html|css|js|yaml|yml|json)$' || true)
STAGED_SUBMODULE_CHANGES=$(git diff --cached --name-only | grep -E '^(doks|docs)/' || true)
STAGED_SUBMODULE_DIR=$(git diff --cached --name-only | grep -E '^(doks|docs)$' || true)

if [[ -n "$DOC_FILES" ]] || [[ -n "$SUBMODULE_CHANGES" ]] || [[ -n "$SUBMODULE_DIR" ]] || \
   [[ -n "$STAGED_DOC_FILES" ]] || [[ -n "$STAGED_SUBMODULE_CHANGES" ]] || [[ -n "$STAGED_SUBMODULE_DIR" ]]; then

    echo "📚 Documentation changes detected:"
    if [[ -n "$DOC_FILES" ]]; then
        echo "  - Unstaged documentation files:"
        echo "$DOC_FILES" | sed 's/^/    - /'
    fi
    if [[ -n "$SUBMODULE_CHANGES" ]]; then
        echo "  - Unstaged submodule file changes:"
        echo "$SUBMODULE_CHANGES" | sed 's/^/    - /'
    fi
    if [[ -n "$SUBMODULE_DIR" ]]; then
        echo "  - Unstaged submodule directory changes:"
        echo "$SUBMODULE_DIR" | sed 's/^/    - /'
    fi
    if [[ -n "$STAGED_DOC_FILES" ]]; then
        echo "  - Staged documentation files:"
        echo "$STAGED_DOC_FILES" | sed 's/^/    - /'
    fi
    if [[ -n "$STAGED_SUBMODULE_CHANGES" ]]; then
        echo "  - Staged submodule file changes:"
        echo "$STAGED_SUBMODULE_CHANGES" | sed 's/^/    - /'
    fi
    if [[ -n "$STAGED_SUBMODULE_DIR" ]]; then
        echo "  - Staged submodule directory changes:"
        echo "$STAGED_SUBMODULE_DIR" | sed 's/^/    - /'
    fi

    # Handle unstaged submodule changes first
    if [[ -n "$SUBMODULE_DIR" ]]; then
        echo "📝 Handling unstaged submodule changes..."
        for submodule in $SUBMODULE_DIR; do
            if [[ -d "$submodule" ]] && [[ -f "$submodule/.git" ]]; then
                echo "  - Processing submodule: $submodule"

                # Go into submodule and commit changes
                cd "$submodule"
                if git diff --quiet; then
                    echo "    - No changes in $submodule"
                    cd ..
                    continue
                fi

                # Stage all changes in submodule
                git add .

                # Commit changes in submodule
                SUBMODULE_COMMIT_MSG="📚 Auto-update documentation from main repository

- Generated latest API documentation
- Auto-commit by pre-commit hook
- [skip ci]"

                git commit --no-verify -m "$SUBMODULE_COMMIT_MSG" || {
                    echo "❌ Failed to commit changes in submodule $submodule"
                    cd ..
                    exit 1
                }

                echo "    - ✅ Committed changes in $submodule"
                cd ..
            fi
        done
    fi

    # Stage all remaining documentation changes in main repository
    if [[ -n "$DOC_FILES" ]]; then
        echo "📝 Staging unstaged documentation files..."
        echo "$DOC_FILES" | xargs -r git add
    fi

    if [[ -n "$SUBMODULE_CHANGES" ]]; then
        echo "📝 Staging unstaged submodule file changes..."
        echo "$SUBMODULE_CHANGES" | xargs -r git add
    fi

    if [[ -n "$SUBMODULE_DIR" ]]; then
        echo "📝 Staging unstaged submodule directory changes..."
        echo "$SUBMODULE_DIR" | xargs -r git add
    fi

    # Create commit message for main repository
    COMMIT_MSG="📚 Auto-update documentation

- Updated API documentation
- Generated latest docs from source code
- Auto-commit by pre-commit hook"

    if [[ -n "$DOC_FILES" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Unstaged files changed:
$(echo "$DOC_FILES" | sed 's/^/  - /')"
    fi

    if [[ -n "$SUBMODULE_CHANGES" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Unstaged submodule file changes:
$(echo "$SUBMODULE_CHANGES" | sed 's/^/  - /')"
    fi

    if [[ -n "$SUBMODULE_DIR" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Unstaged submodule directory changes:
$(echo "$SUBMODULE_DIR" | sed 's/^/  - /')"
    fi

    if [[ -n "$STAGED_DOC_FILES" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Already staged files:
$(echo "$STAGED_DOC_FILES" | sed 's/^/  - /')"
    fi

    if [[ -n "$STAGED_SUBMODULE_CHANGES" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Already staged submodule file changes:
$(echo "$STAGED_SUBMODULE_CHANGES" | sed 's/^/  - /')"
    fi

    if [[ -n "$STAGED_SUBMODULE_DIR" ]]; then
        COMMIT_MSG="$COMMIT_MSG

Already staged submodule directory changes:
$(echo "$STAGED_SUBMODULE_DIR" | sed 's/^/  - /')"
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

    echo "💡 These changes will be included in the main commit"
else
    echo "ℹ️  No documentation changes to commit"
fi

echo "🎉 Pre-commit auto-commit process completed!"
