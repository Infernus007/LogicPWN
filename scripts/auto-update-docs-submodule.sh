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

# Function to check if doks submodule exists
check_doks_submodule() {
    if [ ! -d "doks" ]; then
        print_message "${RED}❌ Error: doks submodule not found${NC}"
        exit 1
    fi

    if ! git submodule status doks > /dev/null 2>&1; then
        print_message "${RED}❌ Error: doks is not a git submodule${NC}"
        exit 1
    fi
}

# Function to update doks submodule
update_doks_submodule() {
    print_message "${BLUE}🔄 Updating doks submodule...${NC}"

    # Go into doks directory and pull latest changes
    cd doks
    git fetch origin
    git checkout main
    git pull origin main
    cd ..

    print_message "${GREEN}✅ Doks submodule updated${NC}"
}

# Function to check if submodule has changes
check_submodule_changes() {
    if git diff --quiet doks; then
        print_message "${YELLOW}ℹ️  No changes in doks submodule${NC}"
        return 1
    else
        print_message "${BLUE}📝 Changes detected in doks submodule${NC}"
        return 0
    fi
}

# Function to commit submodule changes
commit_submodule_changes() {
    local commit_message="$1"

    print_message "${BLUE}📦 Staging doks submodule changes...${NC}"
    git add doks

    print_message "${BLUE}💾 Committing doks submodule changes...${NC}"
    git commit -m "$commit_message"

    print_message "${GREEN}✅ Doks submodule changes committed${NC}"
}

# Function to show submodule status
show_submodule_status() {
    print_message "${BLUE}📊 Doks submodule status:${NC}"
    git submodule status doks
}

# Main function
main() {
    print_message "${BLUE}🚀 Starting doks submodule auto-update...${NC}"

    # Check prerequisites
    check_git_repo
    check_doks_submodule

    # Show current status
    show_submodule_status

    # Update submodule
    update_doks_submodule

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
