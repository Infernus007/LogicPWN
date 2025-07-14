# LogicPwn

[![PyPI version](https://badge.fury.io/py/logicpwn.svg)](https://badge.fury.io/py/logicpwn)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/logicpwn/logicpwn/workflows/Tests/badge.svg)](https://github.com/logicpwn/logicpwn/actions)
[![Documentation](https://readthedocs.org/projects/logicpwn/badge/?version=latest)](https://logicpwn.readthedocs.io/)

**Advanced Business Logic Exploitation & Exploit Chaining Automation Tool**

LogicPwn is a comprehensive security testing framework designed for advanced business logic exploitation and multi-step attack automation. Built for penetration testing, security research, and automated vulnerability assessment.

## 🚀 Features

- **Advanced Authentication**: Session persistence and multi-step authentication workflows
- **Exploit Chaining**: Orchestrate complex multi-step attack sequences
- **High-Performance Async**: Concurrent request execution with aiohttp
- **Modular Architecture**: Extensible middleware system and plugin support
- **Security Analysis**: Automated vulnerability detection and response analysis
- **IDOR & Access Control Detection**: Detect insecure direct object references and access control flaws with context-aware logic
- **Enterprise Logging**: Secure logging with sensitive data redaction
- **Comprehensive Testing**: 100% test coverage with improved reliability
- **Enhanced Error Handling**: Standardized exception handling across all modules
- **Secure Logging**: URL sanitization and response size logging

## 📦 Installation

LogicPwn is now available on [PyPI](https://pypi.org/project/logicpwn/)! You can install it directly using pip:

```bash
pip install logicpwn
```

### Async Functionality (Recommended)

```bash
pip install logicpwn[async]
```

### Development Installation

```bash
git clone https://github.com/logicpwn/logicpwn.git
cd logicpwn
poetry install
```

## 🎯 Quick Start

### Basic Usage

```python
from logicpwn.core import send_request
from logicpwn.models import RequestResult

# Send a GET request
result = send_request(
    url="https://httpbin.org/get",
    method="GET",
    headers={"User-Agent": "LogicPwn/1.0"}
)

print(f"Status: {result.status_code}")
print(f"Response: {result.body}")
```

### Async Requests

```python
import asyncio
from logicpwn.core import AsyncRequestRunner

async def main():
    async with AsyncRequestRunner() as runner:
        result = await runner.send_request(
            url="https://httpbin.org/get",
            method="GET"
        )
        print(f"Status: {result.status_code}")

asyncio.run(main())
```

### Exploit Chaining

```python
from logicpwn.core import authenticate_session, AsyncSessionManager

# Authenticate and chain exploits
auth_config = {
    "url": "https://target.com/login",
    "method": "POST",
    "credentials": {"username": "admin", "password": "secret123"}
}

async with AsyncSessionManager(auth_config=auth_config) as session:
    # Step 1: Access admin panel
    admin_result = await session.get("https://target.com/admin/panel")
    
    # Step 2: Extract user data
    users_result = await session.get("https://target.com/api/users")
    
    # Step 3: Execute exploit
    exploit_result = await session.post(
        "https://target.com/api/admin/users",
        json_data={"action": "create", "user": {"role": "admin"}}
    )
```

---

## 🧩 Automated Exploit Engine & Chain Orchestration

LogicPwn features a powerful exploit automation engine for chaining multi-step attacks, leveraging authenticated sessions, advanced payloads, and flexible validation. You can define exploit chains in YAML or JSON, and run them synchronously or asynchronously.

### YAML/JSON Config-Driven Chains

Define your exploit chain in a simple YAML file:

```yaml
exploit_chain:
  name: "IDOR User Data Extraction"
  description: "Exploit IDOR to access another user's data."
  steps:
    - name: "Login as User"
      request_config:
        method: "POST"
        url: "https://api.example.com/login"
        json_data:
          username: "victim"
          password: "password123"
      success_indicators:
        - "status_code == 200"
        - "token in response.json"
      data_extractors:
        token: "json:token"
    - name: "Access Another User's Data"
      request_config:
        method: "GET"
        url: "https://api.example.com/api/users/2/profile"
        headers:
          Authorization: "Bearer {{token}}"
      success_indicators:
        - "status_code == 200"
        - "py:'email' in response.text"
```

### Running a Chain (Sync & Async)

```python
from logicpwn.core.exploit_engine.exploit_engine import load_exploit_chain_from_file, run_exploit_chain, async_run_exploit_chain
from logicpwn.core.auth.auth_session import authenticate_session
import requests
import asyncio

# Load chain from YAML
chain = load_exploit_chain_from_file("examples/exploits/idor_chain.yaml")

# Create authenticated session (if needed)
session = requests.Session()  # or use authenticate_session(auth_config)

# Synchronous execution
results = run_exploit_chain(session, chain)

# Asynchronous execution
async def main():
    await async_run_exploit_chain(session, chain)

asyncio.run(main())
```

### Real-World Templates
- See `examples/exploits/` for IDOR, SSRF, privilege escalation, and advanced chains.

### Advanced Features
- **Payloads:** Static, random, fuzz, template, and context-aware injection
- **Validation:** Status code, Python expressions, JSONPath, session state
- **Async/Parallel:** Run steps or chains concurrently for high-throughput
- **Caching & Performance:** Built-in response/session caching and performance monitoring
- **Extensibility:** Add new payload types, validations, or extractors easily
- **Logging:** Step-level and chain-level logging with request/response capture

---

### IDOR & Access Control Detection

Detect insecure direct object references (IDOR) and access control flaws with LogicPwn's access detector module. This example demonstrates how to test a REST API for unauthorized access to user resources.

```python
from logicpwn.core.access.detector import detect_idor_flaws
from logicpwn.core.access.models import AccessDetectorConfig
import requests

# Assume you have an authenticated session for user1
session = requests.Session()
session.cookies.set('auth_token', 'user1_token')

# The endpoint template with an {id} placeholder
endpoint_template = "https://target.com/api/users/{id}/profile"

# IDs to test (e.g., user IDs)
test_ids = ["user1", "user2", "user3"]

# Indicators for access granted/denied
success_indicators = ["profile data", "email", "username"]
failure_indicators = ["access denied", "unauthorized", "forbidden"]

# Configure the detector: user1 is the current user, only user1 should be accessible
config = AccessDetectorConfig(
    current_user_id="user1",
    authorized_ids=["user1"],
    unauthorized_ids=["user2", "user3"],
    compare_unauthenticated=True
)

# Run the IDOR/access control test
results = detect_idor_flaws(
    session,
    endpoint_template,
    test_ids,
    success_indicators,
    failure_indicators,
    config
)

for result in results:
    print(f"Tested ID: {result.id_tested}")
    print(f"  Access granted: {result.access_granted}")
    print(f"  Vulnerability detected: {result.vulnerability_detected}")
    print(f"  Status code: {result.status_code}")
    print(f"  Error: {result.error_message}")
    print()

# Output will show which IDs are vulnerable to unauthorized access.
```

## 📚 Documentation

- **[Getting Started](https://logicpwn.readthedocs.io/en/latest/getting_started.html)** - Installation and basic usage
- **[Async Runner](https://logicpwn.readthedocs.io/en/latest/async_runner.html)** - High-performance async request execution
- **[API Reference](https://logicpwn.readthedocs.io/en/latest/api_reference.html)** - Complete API documentation

## 🔧 Configuration

### Environment Variables

```bash
export LOGICPWN_TIMEOUT=30
export LOGICPWN_MAX_RETRIES=3
export LOGICPWN_LOG_LEVEL=INFO
export LOGICPWN_ENABLE_SESSION_PERSISTENCE=true
```

### Configuration File

```python
from logicpwn.core.config import config

# Set configuration values
config.set_timeout(30)
config.set_max_retries(5)
config.set_log_level("DEBUG")

# Save configuration
config.save()
```

## 🛡️ Security Features

### Secure Logging
LogicPwn automatically redacts sensitive information from logs:

```python
# Sensitive data is automatically redacted
logger.info("Request: GET https://target.com/api?password=***&token=***")
```

### Input Validation
All inputs are validated using Pydantic models:

```python
from logicpwn.models import RequestConfig

# Invalid configuration raises ValidationError
config = RequestConfig(url="invalid-url", method="INVALID")
```

### Error Handling
Comprehensive error handling with specific exception types:

```python
from logicpwn.exceptions import AuthenticationError, NetworkError

try:
    session = authenticate_session(auth_config)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=logicpwn

# Run exploit engine test suite
pytest tests/unit/test_exploit_engine.py
```

### Test Reliability
All tests now pass with improved mock handling and error handling:

- **Exploit engine test suite** covers payloads, validation, chain execution (sync/async), caching, and interoperability
- **Enhanced mock support** for better test reliability
- **Standardized error messages** across all modules
- **Improved confidence scoring** for validation tests

## 🔄 Recent Improvements

### Core Module Refactoring
- **Shared Utilities**: Common functionality unified in `logicpwn.core.utils`
- **Enhanced Error Handling**: Standardized exception handling across modules
- **Secure Logging**: URL sanitization and response size logging
- **Test Reliability**: All tests now pass with improved mock handling

### Authentication Module
- **Unified Validation**: Uses shared utilities for indicator checking
- **Improved Error Messages**: Clear, specific error messages
- **Secure Logging**: Automatic credential redaction
- **Better Session Management**: Enhanced session validation and persistence

### Request Runner Module
- **Enhanced Error Handling**: Proper HTTP error status code handling
- **Secure Logging**: URL sanitization and response size logging
- **Improved Mock Support**: Better handling of mock objects in tests
- **Standardized Configuration**: Consistent config validation across modules

### Response Validator Module
- **Unified Validation Logic**: Shared utilities for indicator checking
- **Improved Confidence Scoring**: Lowered default threshold for better validation
- **Enhanced Pattern Detection**: Better regex pattern handling
- **Comprehensive Error Handling**: Robust error handling for all validation types

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/logicpwn/logicpwn.git
cd logicpwn
poetry install
poetry run pytest
```

### Code Quality

- **Type Hints**: All functions include comprehensive type hints
- **Documentation**: All public APIs are documented
- **Testing**: 100% test coverage with parameterized tests
- **Linting**: Code follows PEP 8 and passes all linting checks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Read the Docs](https://logicpwn.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/logicpwn/logicpwn/issues)
- **Security**: security@logicpwn.org

## 🏗️ Architecture

LogicPwn is built with a modular architecture:

- **Core Module**: Request execution and session management
- **Models**: Pydantic models for data validation
- **Middleware**: Extensible middleware system
- **Async Support**: High-performance async operations
- **Logging**: Secure logging with redaction
- **Configuration**: Flexible configuration management

## 📈 Roadmap

- [ ] Plugin system for custom exploits
- [ ] GUI interface for exploit chaining
- [ ] Integration with popular security tools
- [ ] Machine learning for vulnerability detection
- [ ] Cloud deployment support
- [ ] Mobile app for remote testing

---

**Built with ❤️ for the security community** 