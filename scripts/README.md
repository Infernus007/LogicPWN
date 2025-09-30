# LogicPwn Documentation Automation Scripts

This directory contains scripts to automate the API documentation generation
and maintenance for LogicPwn.

## Scripts

### `generate_simple_api_docs.py` - Main API Documentation Generator

The primary script that generates API documentation from Python source code:

- **Module extraction**: Extracts docstrings, type hints, and signatures
- **MDX generation**: Creates Astro-compatible MDX files
- **Structure organization**: Organizes modules by category
- **Cross-referencing**: Generates proper navigation and links

**Usage:**

```bash
# Using poetry (recommended)
poetry run python3 scripts/generate_simple_api_docs.py

# Or directly
python3 scripts/generate_simple_api_docs.py
```

### `update_api_docs.sh` - Documentation Update Script

A wrapper script that automates the documentation update process:

- **Optional backup creation**: Creates backups before updates (disabled by default)
- **Dependency check**: Ensures required packages are installed
- **Documentation generation**: Runs the API generator
- **Status reporting**: Shows generated files and stats

**Usage:**

```bash
# Default: no backup creation
./scripts/update_api_docs.sh

# With backup creation
./scripts/update_api_docs.sh --backup

# Quiet mode (no backup)
./scripts/update_api_docs.sh --quiet

# Quiet mode with backup
./scripts/update_api_docs.sh --quiet --backup
```

### `fix_api_docs.py` - Documentation Post-Processor

Fixes and enhances generated documentation:

- **Content cleanup**: Removes redundant sections
- **Example updates**: Updates code examples with current patterns
- **Format improvements**: Enhances readability and structure

**Usage:**

```bash
# Using poetry (recommended)
poetry run python3 scripts/fix_api_docs.py

# Or directly
python3 scripts/fix_api_docs.py
```

### `verify_api_docs_structure.py` - Documentation Validator

Verifies the integrity of generated documentation:

- **Link validation**: Checks for broken internal links
- **Structure verification**: Ensures consistent formatting
- **Navigation check**: Validates sidebar structure
- **Report generation**: Provides detailed issue reports

**Usage:**

```bash
# Using poetry (recommended)
poetry run python3 scripts/verify_api_docs_structure.py

# Or directly
python3 scripts/verify_api_docs_structure.py
```

## Configuration

### `api_docs_config.yaml` - API Documentation Configuration

Configuration file for the API documentation generator:

- **Module inclusion/exclusion**: Controls which modules to document
- **Category organization**: Defines how modules are grouped
- **Template settings**: Customizes output format and structure
- **Navigation settings**: Controls sidebar and cross-references

## Automation

### Pre-commit Integration

These scripts can be integrated with pre-commit hooks to automatically update
documentation when code changes.

### CI/CD Integration

Example GitHub Actions integration:

```yaml
- name: Update API Documentation
  run: |
    chmod +x scripts/update_api_docs.sh
    ./scripts/update_api_docs.sh
```

## Output

All scripts provide colored output:

- 🔵 **Blue**: Information messages
- 🟢 **Green**: Success messages
- 🔴 **Red**: Error messages
- 🟡 **Yellow**: Warning messages

## Files Generated

The scripts generate:

- `docs/src/content/docs/api-reference/*.mdx` - API docs
- Organized directory structure matching module hierarchy
- Navigation-ready MDX files with proper frontmatter

## Troubleshooting

### Script fails to run

- Ensure you're in the LogicPwn project root directory
- Verify Python 3 is installed and accessible
- Check that required dependencies are installed

### Documentation generation issues

- Check module import paths in the generator script
- Verify that the target modules have proper docstrings
- Ensure output directory has write permissions

### Permission denied

- Make shell scripts executable: `chmod +x scripts/*.sh`
