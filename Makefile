.PHONY: lint format check-imports fix-imports test clean install-dev

# Install development dependencies
install-dev:
	poetry install --with dev
	poetry run pre-commit install

# Format code
format:
	poetry run black --line-length=88 logicpwn tests examples
	poetry run isort --profile=black --line-length=88 logicpwn tests examples

# Remove unused imports and variables
fix-imports:
	poetry run autoflake --in-place --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --ignore-init-module-imports --recursive logicpwn tests examples

# Check code quality
lint:
	poetry run flake8 --config=.flake8 logicpwn tests examples
	poetry run isort --check-only --diff --profile=black --line-length=88 logicpwn tests examples
	poetry run black --check --line-length=88 logicpwn tests examples

# Security check
security:
	poetry run bandit -r logicpwn -f json -o bandit-report.json

# Run all checks
check: lint security
	@echo "All quality checks passed!"

# Fix all issues automatically
fix: fix-imports format
	@echo "Code formatting and import cleanup completed!"

# Run tests
test:
	poetry run pytest tests/ -v

# Run tests with coverage
test-cov:
	poetry run pytest tests/ --cov=logicpwn --cov-report=html --cov-report=term

# Clean build artifacts
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

# Run pre-commit on all files
pre-commit-all:
	poetry run pre-commit run --all-files

# Update pre-commit hooks
pre-commit-update:
	poetry run pre-commit autoupdate

# Development setup
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make check' to verify everything is working."

# CI pipeline simulation
ci: clean check test
	@echo "CI pipeline simulation completed successfully!"
