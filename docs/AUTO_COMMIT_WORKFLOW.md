# Auto-Commit Documentation Workflow

This guide explains how to use the new auto-commit functionality that automatically commits and pushes documentation changes after they are generated.

## 🚀 Overview

The auto-commit workflow automatically:
1. **Generates** API documentation from your source code
2. **Stages** documentation changes
3. **Runs** pre-commit hooks for code quality
4. **Commits** changes with descriptive messages
5. **Pushes** to the remote repository

## 📋 Prerequisites

- Git repository with remote origin configured
- Poetry environment with pre-commit hooks installed
- Write access to the remote repository

## 🔧 Installation

1. **Install pre-commit hooks:**
   ```bash
   make install-dev
   ```

2. **Verify the hooks are installed:**
   ```bash
   poetry run pre-commit install
   ```

## 🎯 Usage

### Option 1: Complete Workflow (Recommended)

Run the complete documentation workflow:

```bash
make docs-workflow
```

This will:
- Generate documentation
- Run all quality checks
- Auto-commit and push changes

### Option 2: Individual Steps

Run individual steps as needed:

```bash
# Generate documentation only
make docs-update

# Commit and push only (if docs are already staged)
make auto-commit

# Run pre-commit hooks
make pre-commit-all
```

### Option 3: Manual Pre-commit

The hooks run automatically when you commit, but you can also run them manually:

```bash
# Run all pre-commit hooks
poetry run pre-commit run --all-files

# Run specific hooks
poetry run pre-commit run black
poetry run pre-commit run isort
```

## 🔄 How It Works

### 1. Pre-commit Stage
When you make changes to Python files and try to commit:

1. **Documentation Generation Hook** (`docs-update`):
   - Detects changes in `logicpwn/` or `scripts/` directories
   - Runs API documentation generation scripts
   - Stages generated documentation files

2. **Code Quality Hooks**:
   - Black formatting
   - isort import sorting
   - Autoflake cleanup
   - Other quality checks

### 2. Post-commit Stage
After successful commit:

1. **Auto-commit Hook** (`auto-commit`):
   - Detects staged documentation changes
   - Creates descriptive commit message
   - Commits changes automatically
   - Pushes to remote repository

## 📝 Commit Messages

Auto-commits use descriptive messages like:

```
📚 Auto-update documentation

- Updated API documentation
- Generated latest docs from source code
- Auto-commit by pre-commit hook

Files changed:
  - docs/api-reference/access.mdx
  - docs/api-reference/auth.mdx
  - docs/api-reference/runner.mdx

[skip ci]
```

## 🛡️ Safety Features

### Protected Branches
The workflow automatically skips auto-commit on protected branches:
- `main`
- `master`

### Branch Validation
- Only works on valid feature branches
- Skips detached HEAD states
- Validates remote origin exists

### Retry Logic
- Automatic retry on push failures
- Maximum 3 retry attempts
- Helpful error messages

## 📁 File Structure

```
scripts/
├── auto-commit-docs.sh          # Auto-commit and push script
├── docs-workflow.sh             # Complete workflow script
├── pre-commit-docs-update.sh    # Documentation generation hook
└── generate_simple_api_docs.py  # API docs generator

docs/
└── AUTO_COMMIT_WORKFLOW.md      # This guide

.pre-commit-config.yaml          # Pre-commit configuration
Makefile                         # Build commands
```

## 🚨 Troubleshooting

### Common Issues

1. **"Not in a git repository"**
   - Ensure you're in the project root directory
   - Check if `.git` directory exists

2. **"On protected branch"**
   - Switch to a feature branch
   - Use `git checkout -b feature-branch-name`

3. **"No remote origin found"**
   - Configure remote: `git remote add origin <url>`
   - Check remote: `git remote -v`

4. **"Push failed"**
   - Check network connectivity
   - Verify write permissions
   - Manual push: `git push origin <branch>`

### Debug Mode

Run with verbose output:

```bash
# Verbose pre-commit
poetry run pre-commit run --all-files --verbose

# Verbose workflow
./scripts/docs-workflow.sh
```

## 🔧 Configuration

### Customizing Commit Messages

Edit `scripts/auto-commit-docs.sh` to modify commit message format.

### Adding New Documentation Types

Update the file pattern matching in the scripts:

```bash
# Current patterns
\.(md|rst|html|css|js|yaml|yml|json)$

# Add new patterns as needed
\.(md|rst|html|css|js|yaml|yml|json|txt|xml)$
```

### Modifying Hook Behavior

Edit `.pre-commit-config.yaml` to:
- Change hook execution order
- Modify file patterns
- Adjust hook parameters

## 📚 Examples

### Example 1: Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/new-auth-module

# 2. Make code changes
# ... edit Python files ...

# 3. Run complete workflow
make docs-workflow

# 4. Create pull request
# ... via GitHub/GitLab UI ...
```

### Example 2: Documentation Only

```bash
# 1. Switch to docs branch
git checkout -b docs/update-api-reference

# 2. Generate docs
make docs-update

# 3. Review changes
git status
git diff --cached

# 4. Auto-commit and push
make auto-commit
```

### Example 3: Manual Workflow

```bash
# 1. Generate documentation
./scripts/pre-commit-docs-update.sh

# 2. Run quality checks
poetry run pre-commit run --all-files

# 3. Manual commit if needed
git add .
git commit -m "Update documentation"

# 4. Push manually
git push origin feature-branch
```

## 🎉 Benefits

- **Automated**: No manual documentation commits needed
- **Consistent**: Standardized commit messages and workflow
- **Safe**: Protected branch detection and validation
- **Efficient**: Single command for complete workflow
- **Reliable**: Retry logic and error handling
- **Transparent**: Clear logging and status messages

## 🤝 Contributing

To improve the auto-commit workflow:

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** the workflow
5. **Submit** a pull request

## 📞 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review the script logs
3. Check pre-commit hook status
4. Open an issue with details

---

**Happy documenting! 🚀📚**
