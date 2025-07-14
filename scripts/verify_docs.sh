#!/bin/bash

# LogicPwn Documentation Verification and Build Script
# This script automates the process of verifying, fixing, and building documentation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to fix section underlines in RST files
fix_section_underlines() {
    local file="$1"
    print_status "Fixing section underlines in $file"
    
    # Create a temporary file
    local temp_file=$(mktemp)
    
    # Process the file line by line
    local in_section=0
    local current_title=""
    local title_length=0
    
    while IFS= read -r line; do
        # Check if this is a section title (ends with : or is followed by underline)
        if [[ $line =~ ^[A-Za-z0-9\ \-\_\?\!]+:$ ]] || [[ $line =~ ^[A-Za-z0-9\ \-\_\?\!]+$ ]]; then
            # This might be a section title
            current_title="$line"
            title_length=${#line}
            in_section=1
            echo "$line" >> "$temp_file"
        elif [[ $in_section -eq 1 ]] && [[ $line =~ ^[=\-\~\^]+$ ]]; then
            # This is an underline, fix it to match title length
            local underline_char="${line:0:1}"
            local new_underline=""
            for ((i=0; i<title_length; i++)); do
                new_underline+="$underline_char"
            done
            echo "$new_underline" >> "$temp_file"
            in_section=0
        else
            # Regular line, just copy it
            echo "$line" >> "$temp_file"
            in_section=0
        fi
    done < "$file"
    
    # Replace original file with fixed version
    mv "$temp_file" "$file"
    print_success "Fixed section underlines in $file"
}

# Function to fix docstring formatting issues
fix_docstring_formatting() {
    local file="$1"
    print_status "Fixing docstring formatting in $file"
    
    # Fix common docstring issues
    sed -i 's/Example:/Examples::/g' "$file"
    sed -i 's/Example: /Examples::\n\n/g' "$file"
    
    # Ensure proper indentation for code blocks in docstrings
    sed -i 's/^        # /            # /g' "$file"
    sed -i 's/^        /            /g' "$file"
    
    # Fix definition list formatting
    sed -i '/^    Args:$/a\' "$file"
    sed -i '/^    Returns:$/a\' "$file"
    sed -i '/^    Raises:$/a\' "$file"
    
    print_success "Fixed docstring formatting in $file"
}

# Function to clean up temporary files
cleanup() {
    print_status "Cleaning up temporary files..."
    rm -f /tmp/doc_*.rst
    print_success "Cleanup completed"
}

# Function to check Python environment
check_python_env() {
    print_status "Checking Python environment..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command_exists poetry; then
        print_error "Poetry is not installed"
        exit 1
    fi
    
    print_success "Python environment is ready"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Install Sphinx and related packages
    poetry add --group dev sphinx@^7.2.0 sphinx-rtd-theme sphinx-autodoc-typehints@^1.22.0
    
    print_success "Dependencies installed"
}

# Function to verify documentation structure
verify_doc_structure() {
    print_status "Verifying documentation structure..."
    
    local required_files=(
        "docs/source/index.rst"
        "docs/source/getting_started.rst"
        "docs/source/api_reference.rst"
        "docs/source/async_runner.rst"
        "docs/source/conf.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required documentation file missing: $file"
            exit 1
        fi
    done
    
    print_success "Documentation structure verified"
}

# Function to fix common formatting issues
fix_formatting_issues() {
    print_status "Fixing common formatting issues..."
    
    # Fix section underlines in all RST files
    for file in docs/source/*.rst; do
        if [[ -f "$file" ]]; then
            fix_section_underlines "$file"
        fi
    done
    
    # Fix docstring formatting in Python files
    for file in logicpwn/core/*.py; do
        if [[ -f "$file" ]]; then
            fix_docstring_formatting "$file"
        fi
    done
    
    print_success "Formatting issues fixed"
}

# Function to build documentation
build_documentation() {
    print_status "Building documentation..."
    
    # Clean previous build
    if [[ -d "docs/build" ]]; then
        rm -rf docs/build
    fi
    
    # Build documentation with warnings as errors
    if poetry run sphinx-build -b html docs/source docs/build/html -W; then
        print_success "Documentation built successfully"
    else
        print_error "Documentation build failed"
        return 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if poetry run pytest tests/ -v; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed"
        return 1
    fi
}

# Function to check for common issues
check_common_issues() {
    print_status "Checking for common issues..."
    
    # Check for invalid escape sequences
    local escape_issues=$(grep -r "invalid escape sequence" docs/build/html/ 2>/dev/null || true)
    if [[ -n "$escape_issues" ]]; then
        print_warning "Found escape sequence issues:"
        echo "$escape_issues"
    fi
    
    # Check for missing files
    local missing_files=$(find docs/source -name "*.rst" -exec basename {} \; | while read file; do
        if ! grep -q "$file" docs/source/index.rst; then
            echo "$file"
        fi
    done)
    
    if [[ -n "$missing_files" ]]; then
        print_warning "Files not included in index.rst:"
        echo "$missing_files"
    fi
    
    print_success "Common issues check completed"
}

# Function to generate documentation report
generate_report() {
    print_status "Generating documentation report..."
    
    local report_file="docs/build/documentation_report.txt"
    
    {
        echo "LogicPwn Documentation Report"
        echo "============================"
        echo "Generated: $(date)"
        echo ""
        
        echo "Documentation Files:"
        echo "-------------------"
        find docs/source -name "*.rst" -exec basename {} \;
        echo ""
        
        echo "Build Status:"
        echo "-------------"
        if [[ -d "docs/build/html" ]]; then
            echo "✓ HTML documentation built successfully"
            echo "  - Location: docs/build/html/"
            echo "  - Files: $(find docs/build/html -name "*.html" | wc -l)"
        else
            echo "✗ HTML documentation build failed"
        fi
        echo ""
        
        echo "Test Status:"
        echo "------------"
        if poetry run pytest tests/ --tb=no -q >/dev/null 2>&1; then
            echo "✓ All tests passed"
        else
            echo "✗ Some tests failed"
        fi
        
    } > "$report_file"
    
    print_success "Report generated: $report_file"
}

# Main function
main() {
    echo "=========================================="
    echo "LogicPwn Documentation Verification Script"
    echo "=========================================="
    echo ""
    
    # Set up trap for cleanup
    trap cleanup EXIT
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]] || [[ ! -d "logicpwn" ]]; then
        print_error "This script must be run from the LogicPwn project root"
        exit 1
    fi
    
    # Run all verification steps
    check_python_env
    install_dependencies
    verify_doc_structure
    fix_formatting_issues
    
    # Try to build documentation
    if build_documentation; then
        check_common_issues
        generate_report
        print_success "Documentation verification completed successfully!"
        echo ""
        echo "Documentation is available at: docs/build/html/index.html"
        echo "Report generated at: docs/build/documentation_report.txt"
    else
        print_error "Documentation verification failed"
        exit 1
    fi
}

# Run main function
main "$@" 