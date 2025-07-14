#!/bin/bash

# LogicPwn Documentation Fix Script
# This script specifically fixes common Sphinx build issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to fix section underlines in RST files
fix_rst_underlines() {
    local file="$1"
    print_status "Fixing underlines in $file"
    
    # Create backup
    cp "$file" "$file.backup"
    
    # Use sed to fix common underline issues
    # Fix main title underlines
    sed -i 's/^Async Request Execution$/Async Request Execution\n=======================/' "$file"
    sed -i 's/^Getting Started with LogicPwn$/Getting Started with LogicPwn\n============================/' "$file"
    sed -i 's/^API Reference$/API Reference\n=============/' "$file"
    sed -i 's/^LogicPwn Documentation$/LogicPwn Documentation\n====================/' "$file"
    
    # Fix section underlines - replace existing underlines with correct length
    sed -i 's/^Why Use Async?$/Why Use Async?\n~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^AsyncRequestRunner$/AsyncRequestRunner\n------------------/' "$file"
    sed -i 's/^Basic Usage$/Basic Usage\n-----------/' "$file"
    sed -i 's/^Configuration$/Configuration\n------------/' "$file"
    sed -i 's/^Batch Requests$/Batch Requests\n--------------/' "$file"
    sed -i 's/^Request Types$/Request Types\n------------/' "$file"
    sed -i 's/^Error Handling$/Error Handling\n--------------/' "$file"
    sed -i 's/^AsyncSessionManager$/AsyncSessionManager\n-------------------/' "$file"
    sed -i 's/^Authentication Configuration$/Authentication Configuration\n----------------------------/' "$file"
    sed -i 's/^Session Methods$/Session Methods\n--------------/' "$file"
    sed -i 's/^Exploit Chaining$/Exploit Chaining\n----------------/' "$file"
    sed -i 's/^Convenience Functions$/Convenience Functions\n--------------------/' "$file"
    sed -i 's/^Single Async Request$/Single Async Request\n--------------------/' "$file"
    sed -i 's/^Batch Async Requests$/Batch Async Requests\n--------------------/' "$file"
    sed -i 's/^Async Context Manager$/Async Context Manager\n--------------------/' "$file"
    sed -i 's/^Advanced Usage$/Advanced Usage\n--------------/' "$file"
    sed -i 's/^Rate Limiting$/Rate Limiting\n------------/' "$file"
    sed -i 's/^Connection Pooling$/Connection Pooling\n------------------/' "$file"
    sed -i 's/^Performance Monitoring$/Performance Monitoring\n----------------------/' "$file"
    sed -i 's/^Error Recovery$/Error Recovery\n--------------/' "$file"
    sed -i 's/^Best Practices$/Best Practices\n--------------/' "$file"
    sed -i 's/^Troubleshooting$/Troubleshooting\n---------------/' "$file"
    
    # Fix API reference section underlines
    sed -i 's/^Authentication Module$/Authentication Module\n~~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Request Runner Module$/Request Runner Module\n~~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Response Validator Module$/Response Validator Module\n~~~~~~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Async Runner Module$/Async Runner Module\n~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Performance Module$/Performance Module\n~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Cache Module$/Cache Module\n~~~~~~~~~~~~/' "$file"
    sed -i 's/^Configuration Module$/Configuration Module\n~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Utilities Module$/Utilities Module\n~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Logging Module$/Logging Module\n~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Stress Testing Module$/Stress Testing Module\n~~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Request Result Model$/Request Result Model\n~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Request Config Model$/Request Config Model\n~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Models Package$/Models Package\n~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Core Module Refactoring$/Core Module Refactoring\n~~~~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Performance \& Caching$/Performance \& Caching\n~~~~~~~~~~~~~~~~~~~~~~/' "$file"
    sed -i 's/^Async Execution$/Async Execution\n~~~~~~~~~~~~~~~/' "$file"
    
    print_success "Fixed underlines in $file"
}

# Function to fix docstring formatting
fix_docstring_formatting() {
    local file="$1"
    print_status "Fixing docstring formatting in $file"
    
    # Create backup
    cp "$file" "$file.backup"
    
    # Fix common docstring issues
    sed -i 's/Example:/Examples::/g' "$file"
    sed -i 's/Example: /Examples::\n\n/g' "$file"
    
    # Ensure proper indentation for code blocks
    sed -i 's/^        # /            # /g' "$file"
    sed -i 's/^        /            /g' "$file"
    
    # Add blank lines after definition lists
    sed -i '/^    Args:$/a\' "$file"
    sed -i '/^    Returns:$/a\' "$file"
    sed -i '/^    Raises:$/a\' "$file"
    
    print_success "Fixed docstring formatting in $file"
}

# Function to clean up backup files
cleanup_backups() {
    print_status "Cleaning up backup files..."
    find . -name "*.backup" -delete
    print_success "Backup files cleaned up"
}

# Function to build documentation
build_docs() {
    print_status "Building documentation..."
    
    # Clean previous build
    if [[ -d "docs/build" ]]; then
        rm -rf docs/build
    fi
    
    # Build with warnings as errors
    if poetry run sphinx-build -b html docs/source docs/build/html -W; then
        print_success "Documentation built successfully!"
        echo "Documentation is available at: docs/build/html/index.html"
    else
        print_error "Documentation build failed"
        return 1
    fi
}

# Main function
main() {
    echo "=========================================="
    echo "LogicPwn Documentation Fix Script"
    echo "=========================================="
    echo ""
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        print_error "This script must be run from the LogicPwn project root"
        exit 1
    fi
    
    # Fix RST files
    for file in docs/source/*.rst; do
        if [[ -f "$file" ]]; then
            fix_rst_underlines "$file"
        fi
    done
    
    # Fix Python docstrings
    for file in logicpwn/core/*.py; do
        if [[ -f "$file" ]]; then
            fix_docstring_formatting "$file"
        fi
    done
    
    # Build documentation
    if build_docs; then
        cleanup_backups
        print_success "All fixes applied and documentation built successfully!"
    else
        print_error "Documentation build failed after fixes"
        exit 1
    fi
}

# Run main function
main "$@" 