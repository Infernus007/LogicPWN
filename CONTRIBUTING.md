# Contributing to LogicPwn

Thank you for your interest in contributing to LogicPwn! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/logicpwn.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** your changes: `poetry run pytest`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+
- Poetry (for dependency management)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/logicpwn/logicpwn.git
cd logicpwn

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Activate virtual environment
poetry shell
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=logicpwn --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py

# Run async tests
poetry run pytest tests/test_async_runner.py
```

### Code Quality

```bash
# Run linting
poetry run flake8 logicpwn tests
poetry run black --check logicpwn tests
poetry run isort --check-only logicpwn tests

# Run type checking
poetry run mypy logicpwn

# Run security checks
poetry run bandit -r logicpwn
poetry run safety check
```

## 📋 Contribution Guidelines

### Code Style

We follow these coding standards:

- **PEP 8**: Python style guide
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Security Considerations

Since LogicPwn is a security tool, we have strict security requirements:

1. **No sensitive data in logs**: All sensitive data must be redacted
2. **Input validation**: All inputs must be validated
3. **Secure defaults**: Default configurations must be secure
4. **Error handling**: Errors must not expose sensitive information
5. **Authentication**: All authentication flows must be secure

### Testing Requirements

- **Test coverage**: Minimum 90% coverage required
- **Unit tests**: All new features must have unit tests
- **Integration tests**: Complex features need integration tests
- **Async tests**: Async functionality must be tested
- **Security tests**: Security features must be tested

### Documentation

- **Docstrings**: All functions must have docstrings
- **Type hints**: All functions must have type hints
- **Examples**: Complex features need usage examples
- **API docs**: New APIs must be documented

## 🏗️ Project Structure

```
logicpwn/
├── logicpwn/              # Main package
│   ├── core/             # Core functionality
│   ├── models/           # Pydantic models
│   ├── exceptions/       # Custom exceptions
│   ├── middleware/       # Middleware system
│   └── utils/            # Utility functions
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures
├── docs/                # Documentation
├── examples/            # Usage examples
└── scripts/             # Development scripts
```

## 🧪 Testing Guidelines

### Writing Tests

```python
import pytest
from logicpwn.core import send_request

def test_send_request_success():
    """Test successful request execution."""
    result = send_request(
        url="https://httpbin.org/get",
        method="GET"
    )
    assert result.status_code == 200
    assert result.success is True

@pytest.mark.asyncio
async def test_async_request():
    """Test async request execution."""
    from logicpwn.core import AsyncRequestRunner

    async with AsyncRequestRunner() as runner:
        result = await runner.send_request(
            url="https://httpbin.org/get",
            method="GET"
        )
        assert result.status_code == 200
```

### Test Categories

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **Security Tests**: Test security features
4. **Performance Tests**: Test performance characteristics
5. **Async Tests**: Test async functionality

## 🔒 Security Guidelines

### Secure Coding Practices

1. **Input Validation**: Always validate inputs
2. **Output Encoding**: Encode outputs to prevent injection
3. **Error Handling**: Don't expose sensitive information in errors
4. **Logging**: Redact sensitive data in logs
5. **Authentication**: Implement secure authentication flows

### Security Testing

```python
def test_sensitive_data_redaction():
    """Test that sensitive data is redacted in logs."""
    result = send_request(
        url="https://example.com/login",
        method="POST",
        data={"username": "admin", "password": "secret123"}
    )

    # Verify password is redacted in logs
    log_output = capture_logs()
    assert "secret123" not in log_output
    assert "***REDACTED***" in log_output
```

## 📝 Documentation Guidelines

### Docstring Format

```python
def authenticate_session(auth_config: AuthConfig) -> Session:
    """
    Authenticate with a target system and return a persistent session.

    Args:
        auth_config: Authentication configuration containing credentials and settings

    Returns:
        Session: Authenticated session for making requests

    Raises:
        AuthenticationError: If authentication fails
        ValidationError: If auth_config is invalid
        NetworkError: If network connection fails

    Example:
        >>> auth_config = AuthConfig(
        ...     login_url="https://target.com/login",
        ...     credentials={"username": "admin", "password": "secret"}
        ... )
        >>> session = authenticate_session(auth_config)
        >>> response = session.get("https://target.com/admin")
    """
```

### API Documentation

- Use clear, concise descriptions
- Include code examples
- Document all parameters and return values
- Include security considerations
- Provide usage patterns

## 🚀 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Security review completed
- [ ] Performance benchmarks pass
- [ ] Changelog is updated
- [ ] Version is bumped
- [ ] Release notes are written

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow security best practices
- Respect privacy and confidentiality

### Communication

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Security**: Report security issues privately
- **Pull Requests**: Provide clear descriptions and examples

## 📚 Resources

- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Security Best Practices](https://owasp.org/www-project-top-ten/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/)
- [Documentation Guidelines](https://www.sphinx-doc.org/en/master/)

## 🆘 Getting Help

- **Documentation**: [https://logicpwn.readthedocs.io/](https://logicpwn.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/logicpwn/logicpwn/issues)
- **Discussions**: [GitHub Discussions](https://github.com/logicpwn/logicpwn/discussions)
- **Security**: security@logicpwn.org

Thank you for contributing to LogicPwn! 🚀
