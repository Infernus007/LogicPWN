#!/bin/bash

# Documentation Update Hook
# This script runs when documentation-related files change

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Pre-commit: Checking for documentation updates...${NC}"

# Check if any Python files in logicpwn/ have changed
CHANGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^logicpwn/.*\.py$' || true)
CHANGED_SCRIPT_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^scripts/.*\.py$' || true)

if [[ -n "$CHANGED_PY_FILES" ]] || [[ -n "$CHANGED_SCRIPT_FILES" ]]; then
    echo -e "${YELLOW}📝 Python files changed, updating API documentation...${NC}"

    # Run the documentation update script
    if ./scripts/update_api_docs.sh --quiet; then
        echo -e "${GREEN}✅ Documentation updated successfully${NC}"

        # Check if documentation files were generated/changed
        GENERATED_DOCS=$(git status --porcelain doks/purple-atmosphere/src/content/docs/api-reference/ 2>/dev/null || true)

        if [[ -n "$GENERATED_DOCS" ]]; then
            echo -e "${BLUE}📄 Generated documentation files:${NC}"
            echo "$GENERATED_DOCS" | sed 's/^/  /'

            # Add the generated files to the commit
            cd doks
            git add purple-atmosphere/src/content/docs/api-reference/

            # Commit docs changes in the submodule if needed
            if ! git diff --cached --quiet; then
                git commit -m "Auto-update API documentation from main repository changes"
                echo -e "${GREEN}✅ Documentation changes committed to submodule${NC}"
            fi
            cd ..

            # Update the submodule reference in the main repo
            git add doks
            if ! git diff --cached --quiet doks; then
                git commit -m "Update docs submodule after API docs generation"
                echo -e "${GREEN}✅ Submodule reference committed in main repo${NC}"
            else
                echo -e "${BLUE}ℹ️ No submodule reference changes to commit${NC}"
            fi
        else
            echo -e "${BLUE}ℹ️ No documentation changes generated${NC}"
        fi
    else
        echo -e "${RED}❌ Documentation update failed${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}ℹ️ No Python files changed, skipping documentation update${NC}"
fi

echo -e "${GREEN}✅ Documentation check completed${NC}"
