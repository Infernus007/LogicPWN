#!/bin/bash

# Auto-update docs submodule script
# This script updates the doks submodule and commits the changes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "$1"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_message "${RED}❌ Error: Not in a git repository${NC}"
        exit 1
    fi
}

# Function to check if docs submodule exists
check_docs_submodule() {
    if [ ! -d "docs" ]; then
        print_message "${RED}❌ Error: docs directory not found${NC}"
        exit 1
    fi

    # Check if docs is a git repository (either submodule or nested repo)
    if [ ! -d "docs/.git" ]; then
        print_message "${RED}❌ Error: docs is not a git repository${NC}"
        exit 1
    fi

    # Check if it's a submodule or nested repo
    if git submodule status docs > /dev/null 2>&1; then
        print_message "${BLUE}ℹ️  Docs is configured as a git submodule${NC}"
    else
        print_message "${BLUE}ℹ️  Docs is a nested git repository${NC}"
    fi
}

# Function to update docs submodule
update_docs_submodule() {
    print_message "${BLUE}🔄 Updating docs submodule...${NC}"

    # Go into docs directory
    cd docs

    # Check if this is a local nested git repo (no remote)
    if ! git remote | grep -q origin; then
        print_message "${BLUE}ℹ️  Docs is a local nested git repository (no remote origin)${NC}"
        print_message "${GREEN}✅ Local docs repository is up to date${NC}"
        cd ..
        return 0
    fi

    # Check if remote repository exists
    if ! git ls-remote origin > /dev/null 2>&1; then
        print_message "${YELLOW}⚠️  Remote repository not found or not accessible${NC}"
        print_message "${YELLOW}   Docs is working as a local repository${NC}"
        cd ..
        return 0
    fi

    # For nested git repos with remote, try to fetch and pull
    git fetch origin

    # Check if we're ahead of origin (local commits not pushed)
    if git status --porcelain=v1 | grep -q "ahead"; then
        print_message "${YELLOW}ℹ️  Docs submodule has local commits ahead of origin${NC}"
        print_message "${YELLOW}   Consider pushing local changes first${NC}"
    fi

    # Try to pull latest changes
    if git pull origin main; then
        print_message "${GREEN}✅ Docs submodule updated from remote${NC}"
    else
        print_message "${YELLOW}⚠️  Could not pull from remote, keeping local changes${NC}"
    fi

    cd ..
    print_message "${GREEN}✅ Docs submodule update completed${NC}"
}

# Function to check if submodule has changes
check_submodule_changes() {
    if git diff --quiet docs; then
        print_message "${YELLOW}ℹ️  No changes in docs submodule${NC}"
        return 1
    else
        print_message "${BLUE}📝 Changes detected in docs submodule${NC}"
        return 0
    fi
}

# Function to commit submodule changes
commit_submodule_changes() {
    local commit_message="$1"

    print_message "${BLUE}📦 Staging docs submodule changes...${NC}"
    git add docs

    print_message "${BLUE}💾 Committing docs submodule changes...${NC}"
    git commit -m "$commit_message"

    print_message "${GREEN}✅ Docs submodule changes committed${NC}"
}

# Function to show submodule status
show_submodule_status() {
    print_message "${BLUE}📊 Docs repository status:${NC}"
    if git submodule status docs > /dev/null 2>&1; then
        git submodule status docs
    else
        cd docs
        print_message "  Current commit: $(git rev-parse --short HEAD)"
        print_message "  Branch: $(git branch --show-current)"
        cd ..
    fi
}

# Main function
main() {
    print_message "${BLUE}🚀 Starting docs submodule auto-update...${NC}"

    # Check prerequisites
    check_git_repo
    check_docs_submodule

    # Show current status
    show_submodule_status

    # Update submodule
    update_docs_submodule

    # Check for changes
    if check_submodule_changes; then
        # Generate commit message
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local commit_message="docs: Auto-update doks submodule - $timestamp"

        # Commit changes
        commit_submodule_changes "$commit_message"

        print_message "${GREEN}🎉 Doks submodule auto-update completed successfully!${NC}"
    else
        print_message "${GREEN}✅ Doks submodule is already up to date${NC}"
    fi

    # Show final status
    show_submodule_status
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --help, -h     Show this help message"
            echo "  --dry-run      Show what would be done without making changes"
            echo "  --force        Force update even if no changes detected"
            echo ""
            echo "This script automatically updates the doks submodule and commits changes."
            exit 0
            ;;
        --dry-run)
            print_message "${YELLOW}🔍 Dry run mode - no changes will be made${NC}"
            # TODO: Implement dry run logic
            exit 0
            ;;
        --force)
            FORCE_UPDATE=true
            shift
            ;;
        *)
            print_message "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main
