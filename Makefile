.PHONY: lint format check-imports fix-imports test clean install-dev docs-update auto-commit docs-workflow

install-dev:
	poetry install --with dev
	poetry run pre-commit install

format:
	poetry run black --line-length=88 logicpwn tests examples
	poetry run isort --profile=black --line-length=88 logicpwn tests examples

fix-imports:
	poetry run autoflake --in-place --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --ignore-init-module-imports --recursive logicpwn tests examples

lint:
	poetry run isort --check-only --diff --profile=black --line-length=88 logicpwn tests examples
	poetry run black --check-only --diff --line-length=88 logicpwn tests examples

check: lint
	@echo "All quality checks passed!"

fix: fix-imports format
	@echo "Code formatting and import cleanup completed!"

test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ --cov=logicpwn --cov-report=html --cov-report=term

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

pre-commit-all:
	poetry run pre-commit run --all-files

pre-commit-update:
	poetry run pre-commit autoupdate

docs-update:
	@echo "📚 Updating API documentation..."
	./scripts/pre-commit-docs-update.sh

auto-commit:
	@echo "🤖 Running auto-commit for documentation changes..."
	./scripts/auto-commit-docs.sh

docs-workflow:
	@echo "🚀 Running comprehensive documentation workflow..."
	./scripts/docs-workflow.sh

dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make check' to verify everything is working."

ci: clean check test
	@echo "CI pipeline simulation completed successfully!"
