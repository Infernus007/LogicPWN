# LogicPwn Documentation Automation Scripts

This directory contains scripts to automate the documentation verification and build process for LogicPwn.

## Scripts

### `fix_docs.sh` - Quick Fix Script
A targeted script that specifically fixes common Sphinx build issues:

- **Section underline problems**: Automatically corrects underlines to match title length
- **Docstring formatting**: Fixes common docstring formatting issues
- **Build verification**: Attempts to build documentation after fixes

**Usage:**
```bash
./scripts/fix_docs.sh
```

### `verify_docs.sh` - Comprehensive Verification Script
A comprehensive script that performs full documentation verification:

- **Environment checks**: Verifies Python and Poetry installation
- **Dependency installation**: Installs required Sphinx packages
- **Structure verification**: Checks for required documentation files
- **Formatting fixes**: Applies comprehensive formatting corrections
- **Build testing**: Attempts to build documentation
- **Issue detection**: Identifies common problems
- **Report generation**: Creates a detailed report

**Usage:**
```bash
./scripts/verify_docs.sh
```

## Common Issues Fixed

### 1. Section Underline Problems
- **Problem**: Sphinx reports "Title underline too short"
- **Solution**: Scripts automatically correct underlines to match title length exactly

### 2. Docstring Formatting Issues
- **Problem**: Invalid indentation or missing blank lines in docstrings
- **Solution**: Scripts fix indentation and add required blank lines

### 3. Example Formatting
- **Problem**: "Example:" instead of "Examples::" in docstrings
- **Solution**: Scripts convert to proper Sphinx format

## Output

Both scripts provide colored output:
- 🔵 **Blue**: Information messages
- 🟢 **Green**: Success messages
- 🔴 **Red**: Error messages

## Files Modified

The scripts may modify:
- `docs/source/*.rst` - Documentation source files
- `logicpwn/core/*.py` - Python source files with docstrings

## Backup Files

The `fix_docs.sh` script creates backup files (`.backup`) before making changes and cleans them up after successful builds.

## Troubleshooting

### Script fails to run
- Ensure you're in the LogicPwn project root directory
- Verify Python 3 and Poetry are installed
- Check that `pyproject.toml` exists

### Documentation still fails to build
- Check the Sphinx error output for specific issues
- Manual fixes may be required for complex formatting problems
- Consider using a text editor that shows invisible characters

### Permission denied
- Make scripts executable: `chmod +x scripts/*.sh`

## Integration

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Verify Documentation
  run: |
    chmod +x scripts/verify_docs.sh
    ./scripts/verify_docs.sh
```

## Manual Override

If automated fixes don't work, you can manually fix issues:

1. **Section underlines**: Ensure underline length matches title length exactly
2. **Docstring formatting**: Add blank lines after Args/Returns/Raises sections
3. **Code blocks**: Use proper indentation (8 spaces for code blocks)
4. **Examples**: Use "Examples::" instead of "Example:" 