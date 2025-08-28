#!/bin/bash

# LogicPwn API Documentation Update Script
# 
# This script automatically updates the API documentation in your Astro site
# by extracting docstrings and signatures from the Python codebase.

set -e

echo "🚀 LogicPwn API Documentation Generator"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📂 Project Root: ${PROJECT_ROOT}${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo -e "${RED}❌ Error: pyproject.toml not found. Are you in the LogicPwn project root?${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found. Please install Python 3.${NC}"
    exit 1
fi

# Set up paths
API_DOCS_DIR="$PROJECT_ROOT/doks/purple-atmosphere/src/content/docs/api-reference"
GENERATOR_SCRIPT="$SCRIPT_DIR/generate_simple_api_docs.py"

echo -e "${BLUE}📖 API Docs Directory: ${API_DOCS_DIR}${NC}"
echo -e "${BLUE}🔧 Generator Script: ${GENERATOR_SCRIPT}${NC}"
echo ""

# Check if generator script exists
if [ ! -f "$GENERATOR_SCRIPT" ]; then
    echo -e "${RED}❌ Error: Generator script not found at ${GENERATOR_SCRIPT}${NC}"
    exit 1
fi

# Backup existing docs if they exist
if [ -d "$API_DOCS_DIR" ]; then
    echo -e "${YELLOW}📋 Backing up existing API docs...${NC}"
    BACKUP_DIR="$API_DOCS_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    cp -r "$API_DOCS_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✅ Backup created: ${BACKUP_DIR}${NC}"
    echo ""
fi

# Change to project root
cd "$PROJECT_ROOT"

# Install/update dependencies if needed
echo -e "${YELLOW}📦 Checking Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt --quiet
elif [ -f "pyproject.toml" ]; then
    if command -v poetry &> /dev/null; then
        poetry install --quiet
    else
        echo -e "${YELLOW}⚠️  Poetry not found, trying pip install -e .${NC}"
        python3 -m pip install -e . --quiet
    fi
fi
echo ""

# Run the API documentation generator
echo -e "${YELLOW}🔄 Generating API documentation...${NC}"
echo ""

if python3 "$GENERATOR_SCRIPT"; then
    echo ""
    echo -e "${GREEN}✅ API documentation generated successfully!${NC}"
    echo ""
    
    # Count generated files
    if [ -d "$API_DOCS_DIR" ]; then
        FILE_COUNT=$(find "$API_DOCS_DIR" -name "*.mdx" | wc -l)
        echo -e "${GREEN}📄 Generated ${FILE_COUNT} MDX files${NC}"
        
        # List main sections
        echo -e "${BLUE}📚 Generated sections:${NC}"
        find "$API_DOCS_DIR" -maxdepth 1 -name "*.mdx" -exec basename {} .mdx \; | sort | sed 's/^/  - /'
        
        if [ -d "$API_DOCS_DIR/auth" ]; then
            echo -e "${BLUE}🔐 Auth modules:${NC}"
            find "$API_DOCS_DIR/auth" -name "*.mdx" -exec basename {} .mdx \; | sort | sed 's/^/  - auth\//'
        fi
        
        if [ -d "$API_DOCS_DIR/access" ]; then
            echo -e "${BLUE}🔒 Access modules:${NC}"
            find "$API_DOCS_DIR/access" -name "*.mdx" -exec basename {} .mdx \; | sort | sed 's/^/  - access\//'
        fi
        
        if [ -d "$API_DOCS_DIR/reporter" ]; then
            echo -e "${BLUE}📊 Reporter modules:${NC}"
            find "$API_DOCS_DIR/reporter" -name "*.mdx" -exec basename {} .mdx \; | sort | sed 's/^/  - reporter\//'
        fi
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Documentation update complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Review the generated documentation"
    echo "  2. Commit the changes to your repository"
    echo "  3. Deploy your Astro site to see the updates"
    echo ""
    echo -e "${BLUE}💡 Tip: Add this script to your CI/CD pipeline to auto-update docs!${NC}"
    
else
    echo ""
    echo -e "${RED}❌ Error: API documentation generation failed${NC}"
    
    # Restore backup if it exists
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}🔄 Restoring backup...${NC}"
        rm -rf "$API_DOCS_DIR"
        mv "$BACKUP_DIR" "$API_DOCS_DIR"
        echo -e "${GREEN}✅ Backup restored${NC}"
    fi
    
    exit 1
fi
