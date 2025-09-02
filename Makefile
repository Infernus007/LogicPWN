.PHONY: help install install-dev check lint format fix test test-coverage clean docs-update auto-commit docs-workflow auto-commit-push

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

docs-update: ## Update API documentation
	@echo "📚 Updating API documentation..."
	./scripts/pre-commit-docs-update.sh

auto-commit: ## Auto-commit documentation changes
	@echo "🤖 Running auto-commit for documentation changes..."
	./scripts/auto-commit-docs.sh

auto-commit-push: ## Auto-commit and push documentation changes
	@echo "🚀 Running auto-commit and push for documentation changes..."
	./scripts/auto-commit-docs.sh

docs-workflow: ## Complete documentation workflow
	@echo "🚀 Running comprehensive documentation workflow..."
	./scripts/docs-workflow.sh
