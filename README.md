# LogicPWN 🔒

**Advanced Business Logic Security Testing Framework**

[![PyPI version](https://badge.fury.io/py/logicpwn.svg)](https://pypi.org/project/logicpwn/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LogicPWN represents a paradigm shift from traditional security testing toward intelligent, business-aware security automation. Its unique focus on business logic vulnerabilities, combined with enterprise-grade performance and comprehensive documentation, positions it as a leader in the next generation of security testing tools.

## 📦 Installation

**Latest Release**: [v0.3.0](https://pypi.org/project/logicpwn/) - Available on PyPI

```bash
# Install from PyPI
pip install logicpwn

# Or install with all features
pip install logicpwn[async,stress,reporting]
```

## ✨ Key Features

- **🔐 Advanced Authentication** - Session persistence, CSRF handling
- **⚡ Exploit Chaining** - Multi-step attack automation with state management
- **🏗️ Modular Architecture** - Install only the modules you need
- **📊 Enterprise Performance** - High-throughput testing with monitoring
- **🛡️ Comprehensive Security** - Business logic vulnerability detection
- **📝 Detailed Reporting** - Compliance-ready reports

## 🚀 Quick Start

### 🎯 Your First Security Test

Here's a complete example to get you started:

```python
from logicpwn.core.auth import authenticate_session, AuthConfig
from logicpwn.core.access import detect_idor_flaws
from logicpwn.core.runner import HttpRunner
from logicpwn.core.reporter import ReportConfig, ReportGenerator

# 1. Set up authentication
auth_config = AuthConfig(
    url="https://target.com/login",
    method="POST",
    credentials={
        "username": "testuser",
        "password": "password123"
    },
    success_indicators=["Welcome", "Dashboard"],
    failure_indicators=["Login failed", "Invalid credentials"]
)

# 2. Authenticate and get session
session = authenticate_session(auth_config)
print(f"✅ Authenticated successfully: {session.cookies}")

# 3. Use the new unified HttpRunner for requests
runner = HttpRunner()
response = runner.get("https://target.com/api/users/1")
print(f"📡 Response status: {response.status_code}")

# 4. Test for IDOR vulnerabilities
idor_results = detect_idor_flaws(
    session=session,
    endpoint_template="https://target.com/api/users/{id}",
    test_ids=["1", "2", "3", "admin"],
    success_indicators=["user_data", "profile"],
    failure_indicators=["access_denied", "unauthorized"]
)

# 5. Generate a security report
report_config = ReportConfig(
    target_url="https://target.com",
    report_title="Security Assessment Report"
)

generator = ReportGenerator(report_config)
report = generator.generate_report(
    findings=idor_results,
    include_recommendations=True
)

print(f"📊 Report generated: {len(report.findings)} findings")
```

### 🔍 Common Use Cases

#### **Enhanced HTTP Runner**
```python
from logicpwn.core.runner import HttpRunner

# Unified HTTP runner with sync/async support
runner = HttpRunner()

# Synchronous requests
response = runner.get("https://api.example.com/users")
response = runner.post("https://api.example.com/login", json_data={"user": "admin"})

# Asynchronous requests
async with runner:
    response = await runner.get_async("https://api.example.com/data")
    response = await runner.post_async("https://api.example.com/update", json_data={"id": 1})

# Batch processing
results = await runner.batch([
    {"url": "https://api.example.com/1", "method": "GET"},
    {"url": "https://api.example.com/2", "method": "POST", "json_data": {"key": "value"}}
])

# Convenient HTTP methods
runner.get("https://example.com")           # GET request
runner.post("https://example.com", data)    # POST request
runner.put("https://example.com", data)     # PUT request
runner.delete("https://example.com")         # DELETE request
```

#### **IDOR Vulnerability Testing**
```python
from logicpwn.core.access import detect_idor_flaws

# Test user enumeration
results = detect_idor_flaws(
    session=authenticated_session,
    endpoint_template="https://app.com/api/users/{id}",
    test_ids=["1", "2", "3", "admin", "test"],
    success_indicators=["user_data", "email", "profile"],
    failure_indicators=["access_denied", "not_found"]
)

for result in results:
    if result.vulnerability_detected:
        print(f"🚨 IDOR found: {result.endpoint_url}")
```

#### **Business Logic Testing**
```python
from logicpwn.core.validator import validate_business_logic

# Test price manipulation
logic_rules = [
    {
        "name": "price_validation",
        "condition": "response.json().get('price') > 0",
        "description": "Price must be positive"
    },
    {
        "name": "quantity_limit",
        "condition": "response.json().get('quantity') <= 100",
        "description": "Quantity cannot exceed 100"
    }
]

validation_result = validate_business_logic(
    response=response,
    rules=logic_rules
)

if not validation_result.is_valid:
    print(f"⚠️  Business logic violation: {validation_result.violations}")
```

#### **Performance & Stress Testing**
```python
from logicpwn.core.stress import StressTester, StressTestConfig

# Configure stress test
config = StressTestConfig(
    max_concurrent=50,
    duration=300,  # 5 minutes
    memory_monitoring=True,
    error_threshold=0.1  # 10% error rate
)

# Run stress test
async with StressTester(config) as tester:
    metrics = await tester.run_stress_test([
        {"url": "https://target.com/api/endpoint", "method": "GET"}
    ])

    print(f"📈 Requests/sec: {metrics.requests_per_second:.1f}")
    print(f"⚠️  Error rate: {metrics.error_rate:.2f}%")
```

## 🏗️ Architecture

LogicPWN is built with a modular, extensible architecture designed for enterprise security testing:

```
logicpwn/
├── core/
│   ├── auth/           # Authentication & session management
│   ├── access/         # IDOR & access control testing
│   ├── runner/         # HTTP request execution (sync/async)
│   ├── stress/         # Performance & stress testing
│   ├── validator/      # Response validation & analysis
│   ├── exploit_engine/ # Exploit chain execution
│   ├── reporter/       # Report generation & compliance
│   └── logging/        # Secure audit logging
├── models/             # Pydantic data models
├── exceptions/         # Custom exception hierarchy
└── middleware/         # Extensible request/response middleware
```

### Key Components

- **Enhanced HTTP Runner**: Unified sync/async HTTP client with user-friendly error messages
- **Authentication System**: Multi-protocol support (OAuth 2.0, SAML, JWT, form-based)
- **Access Control Testing**: Intelligent IDOR detection with pattern recognition
- **Performance Engine**: Async/concurrent execution for high-throughput testing
- **Exploit Engine**: Chain exploits and validate security controls
- **Reporting**: Generate detailed security reports with compliance mapping

## 📖 Documentation

Comprehensive documentation is available:

- **📚 [Full Documentation](https://logicpwn.github.io/)** - Complete guides and API reference
- **🚀 [Getting Started Guide](https://logicpwn.github.io/getting-started/)** - Quick start tutorials
- **💡 [Examples](https://github.com/Infernus007/LogicPWN/tree/main/examples)** - Real-world usage examples
- **📊 [Performance Benchmarks](https://pypi.org/project/logicpwn/)** - Performance analysis and optimization

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
make test

# Run specific test categories
poetry run pytest tests/unit/ -v
poetry run pytest tests/core/ -v
poetry run pytest tests/integration/ -v

# Run with coverage
poetry run pytest --cov=logicpwn tests/
```

## 🚀 Development

### Prerequisites

- Python 3.9+
- Poetry for dependency management
- Pre-commit hooks for code quality

### Setup

```bash
# Clone the repository
git clone https://github.com/Infernus007/LogicPWN.git
cd LogicPWN

# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install

# Run code quality checks
make check
make fix
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Security checks
make security

# Run all checks
make check
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](./docs/) folder
- **Issues**: [GitHub Issues](https://github.com/Infernus007/LogicPWN/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Infernus007/LogicPWN/discussions)

## 🔧 Troubleshooting

### Common Issues

#### **Import Errors**
```bash
# If you get import errors, try reinstalling
pip uninstall logicpwn
pip install logicpwn

# Or install with specific modules
pip install logicpwn[auth,runner,access]
```

#### **Authentication Issues**
```python
# Make sure your success/failure indicators are correct
auth_config = AuthConfig(
    url="https://target.com/login",
    method="POST",
    credentials={"username": "user", "password": "pass"},
    success_indicators=["Welcome", "Dashboard"],  # Text that appears on success
    failure_indicators=["Login failed", "Invalid"]  # Text that appears on failure
)
```

#### **Rate Limiting**
```python
# If you're getting blocked, use the reliability module
from logicpwn.core.reliability import AdaptiveRateLimiter

rate_limiter = AdaptiveRateLimiter("api_calls")
# The runner will automatically use this for rate limiting
```

#### **Session Persistence**
```python
# Sessions are automatically cached and reused
# If you need a fresh session:
from logicpwn.core.cache import clear_all_caches
clear_all_caches()
```

### Getting Help

1. **Check the documentation** in the [`docs/`](./docs/) folder
2. **Search existing issues** on GitHub
3. **Create a new issue** with:
   - Python version
   - LogicPWN version
   - Error message
   - Code example
   - Expected vs actual behavior

## 🔗 Links

- **📦 [PyPI Package](https://pypi.org/project/logicpwn/)** - Install from PyPI
- **📚 [Documentation](https://logicpwn.github.io/)** - Complete guides and API reference
- **🐙 [GitHub Repository](https://github.com/Infernus007/LogicPWN)** - Source code and issues
- **💬 [GitHub Discussions](https://github.com/Infernus007/LogicPWN/discussions)** - Community support

## 📊 Performance Benchmarks

Real-world performance metrics from comprehensive testing:

| Test Scenario           | Requests | Duration | Req/s | Memory  | CPU   | Error Rate |
| ----------------------- | -------- | -------- | ----- | ------- | ----- | ---------- |
| **Basic HTTP Requests** | 100      | 11.36s   | 8.8   | 62.2 MB | 12.2% | 0.0%       |
| **Async Concurrent**    | 100      | 24.82s   | 4.0   | 66.3 MB | 30.4% | 3.0%       |
| **IDOR Detection**      | 25       | 24.90s   | 1.0   | 68.8 MB | 50.0% | 0.0%       |
| **Stress Testing**      | 169      | 51.61s   | 3.3   | 73.5 MB | 12.5% | 0.0%       |

**Overall Averages:**
- **4.3 requests/second** average throughput
- **67.7 MB** average memory usage
- **26.2%** average CPU utilization
- **Excellent reliability** with minimal error rates

---

**Built with ❤️ for the security community**
