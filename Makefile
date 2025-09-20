.PHONY: help install install-dev check lint format fix test test-coverage clean clean-backups docs-update docs-update-backup docs-force-backup auto-commit docs-workflow auto-commit-push pre-commit-check pre-commit-fix commit-safe docs-force update-docs-submodule docs-submodule-status

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	poetry install --only main

install-dev: ## Install development dependencies
	poetry install

check: lint ## Run all checks (linting only)

lint: ## Run linting checks
	poetry run black --check-only --diff .
	poetry run isort --check-only --diff .

format: ## Format code
	poetry run black .
	poetry run isort .

fix: format ## Format code (alias for format)

test: ## Run tests
	poetry run pytest -v

test-coverage: ## Run tests with coverage
	poetry run pytest --cov=logicpwn --cov-report=html --cov-report=term

clean: ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-backups: ## Clean up API documentation backup folders
	@echo "🧹 Cleaning up API documentation backup folders..."
	find . -name "*.backup.*" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Backup folders cleaned up!"

# Pre-commit workflow commands
pre-commit-check: ## Check if pre-commit hooks pass (dry run)
	@echo "🔍 Running pre-commit hooks check..."
	pre-commit run --all-files

pre-commit-fix: ## Run pre-commit hooks and fix formatting issues
	@echo "🔧 Running pre-commit hooks to fix formatting..."
	pre-commit run --all-files
	@echo "✅ Pre-commit hooks completed. Run 'git add .' to stage any modified files."

commit-safe: ## Safe commit workflow - format first, then commit
	@echo "🚀 Starting safe commit workflow..."
	@echo "📦 Adding all changes..."
	git add .
	@echo "🔧 Running pre-commit hooks to format code..."
	pre-commit run --all-files || (echo "⚠️  Pre-commit hooks modified files, re-adding..." && git add .)
	@echo "🔍 Final pre-commit check..."
	pre-commit run --all-files || (echo "❌ Pre-commit hooks still failing. Please fix manually." && exit 1)
	@echo "✅ All checks passed! Now you can commit with:"
	@echo "   git commit -m \"your message\""

# Documentation commands
docs-update: ## Update API documentation (no backup, respects branch restrictions)
	@echo "📚 Updating API documentation (no backup)..."
	./scripts/pre-commit-docs-update.sh

docs-update-backup: ## Update API documentation with backup (respects branch restrictions)
	@echo "📚 Updating API documentation with backup..."
	@echo "🔧 Generating API documentation with backup..."
	./scripts/update_api_docs.sh --backup
	@echo "🔧 Fixing API documentation structure..."
	python3 scripts/fix_api_docs.py
	@echo "✅ Documentation generated successfully with backup!"

docs-force: ## Force update API documentation (no backup, ignores branch restrictions)
	@echo "🚀 Force updating API documentation (no backup)..."
	@echo "🔧 Generating API documentation..."
	./scripts/update_api_docs.sh
	@echo "🔧 Fixing API documentation structure..."
	python3 scripts/fix_api_docs.py
	@echo "✅ Documentation generated successfully!"

docs-force-backup: ## Force update API documentation with backup (ignores branch restrictions)
	@echo "🚀 Force updating API documentation with backup..."
	@echo "🔧 Generating API documentation with backup..."
	./scripts/update_api_docs.sh --backup
	@echo "🔧 Fixing API documentation structure..."
	python3 scripts/fix_api_docs.py
	@echo "✅ Documentation generated successfully with backup!"

auto-commit: ## Auto-commit documentation changes
	@echo "🤖 Running auto-commit for documentation changes..."
	./scripts/auto-commit-docs.sh

auto-commit-push: ## Auto-commit and push documentation changes
	@echo "🚀 Running auto-commit and push for documentation changes..."
	./scripts/auto-commit-docs.sh

docs-workflow: ## Complete documentation workflow
	@echo "🚀 Running comprehensive documentation workflow..."
	./scripts/docs-workflow.sh

update-docs-submodule: ## Update doks submodule and commit changes
	@echo "🔄 Updating doks submodule..."
	./scripts/auto-update-docs-submodule.sh

docs-submodule-status: ## Show doks repository status
	@echo "📊 Doks repository status:"
	@if git submodule status doks > /dev/null 2>&1; then \
		git submodule status doks; \
	else \
		cd doks && echo "  Current commit: $$(git rev-parse --short HEAD)" && echo "  Branch: $$(git branch --show-current)" && cd ..; \
	fi
