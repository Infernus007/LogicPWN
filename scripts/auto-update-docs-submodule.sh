#!/bin/bash

# Auto-update docs folder script
# This script updates the docs folder and commits the changes

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

# Function to check if docs folder exists
check_docs_folder() {
    if [ ! -d "docs" ]; then
        print_message "${RED}❌ Error: docs directory not found${NC}"
        exit 1
    fi

    print_message "${BLUE}ℹ️  Docs is a regular folder in the main repository${NC}"
}

# Function to update docs folder
update_docs_folder() {
    print_message "${BLUE}🔄 Checking docs folder...${NC}"

    # Check if docs folder has any changes
    if git diff --quiet docs/; then
        print_message "${GREEN}✅ Docs folder is up to date${NC}"
        return 0
    else
        print_message "${BLUE}📝 Changes detected in docs folder${NC}"
        return 1
    fi
}

# Function to check if docs folder has changes
check_docs_changes() {
    if git diff --quiet docs/; then
        print_message "${YELLOW}ℹ️  No changes in docs folder${NC}"
        return 1
    else
        print_message "${BLUE}📝 Changes detected in docs folder${NC}"
        return 0
    fi
}

# Function to commit docs changes
commit_docs_changes() {
    local commit_message="$1"

    print_message "${BLUE}📦 Staging docs folder changes...${NC}"
    git add docs/

    print_message "${BLUE}💾 Committing docs folder changes...${NC}"
    git commit -m "$commit_message"

    print_message "${GREEN}✅ Docs folder changes committed${NC}"
}

# Function to show docs status
show_docs_status() {
    print_message "${BLUE}📊 Docs folder status:${NC}"
    git status --porcelain docs/ || true
}

# Main function
main() {
    print_message "${BLUE}🚀 Starting docs folder auto-update...${NC}"

    # Check prerequisites
    check_git_repo
    check_docs_folder

    # Show current status
    show_docs_status

    # Update docs folder
    update_docs_folder

    # Check for changes
    if check_docs_changes; then
        # Generate commit message
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local commit_message="docs: Auto-update docs folder - $timestamp"

        # Commit changes
        commit_docs_changes "$commit_message"

        print_message "${GREEN}🎉 Docs folder auto-update completed successfully!${NC}"
    else
        print_message "${GREEN}✅ Docs folder is already up to date${NC}"
    fi

    # Show final status
    show_docs_status
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
            echo "This script automatically updates the docs folder and commits changes."
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
