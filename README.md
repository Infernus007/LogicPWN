# LogicPWN 🔒

**Business Logic Exploitation & Exploit Chaining Automation Tool**

LogicPWN represents a paradigm shift from traditional security testing toward intelligent, business-aware security automation. Its unique focus on business logic vulnerabilities, combined with enterprise-grade performance and comprehensive documentation, positions it as a leader in the next generation of security testing tools.

## ✨ Key Features

- **🔐 Advanced Authentication** - Session persistence, CSRF handling
- **⚡ Exploit Chaining** - Multi-step attack automation with state management
- **🏗️ Modular Architecture** - Install only the modules you need
- **📊 Enterprise Performance** - High-throughput testing with monitoring
- **🛡️ Comprehensive Security** - Business logic vulnerability detection
- **📝 Detailed Reporting** - Compliance-ready reports

## 🚀 Quick Start

### Installation

LogicPWN offers flexible installation options to suit your needs:

```bash
# Full installation with all features (default)
pip install logicpwn

# Install with specific feature groups only (for minimal installations)
pip install logicpwn[auth]        # Authentication & session management
pip install logicpwn[runner]      # HTTP request execution & async support
pip install logicpwn[access]      # Access control & IDOR detection
pip install logicpwn[validator]   # Response validation & analysis
pip install logicpwn[reporter]    # Report generation & compliance
pip install logicpwn[performance] # Performance monitoring & profiling
pip install logicpwn[stress]      # Stress testing & load testing
pip install logicpwn[exploit]     # Exploit engine & payload generation
pip install logicpwn[reliability] # Circuit breakers & reliability features

# Development installation
git clone https://github.com/Infernus007/LogicPWN.git
cd LogicPWN
poetry install --with dev
poetry run pre-commit install
```

**Note**: The default `pip install logicpwn` includes all features. Use the optional extras (e.g., `[auth]`, `[runner]`) only if you want to install specific modules with minimal dependencies.

### 🎯 Your First Security Test

Here's a complete example to get you started:

```python
from logicpwn.core.auth import authenticate_session, AuthConfig
from logicpwn.core.access import detect_idor_flaws
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

# 3. Test for IDOR vulnerabilities
idor_results = detect_idor_flaws(
    session=session,
    endpoint_template="https://target.com/api/users/{id}",
    test_ids=["1", "2", "3", "admin"],
    success_indicators=["user_data", "profile"],
    failure_indicators=["access_denied", "unauthorized"]
)

# 4. Generate a security report
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

## 🏗️ Module Groups

LogicPWN is designed with a modular architecture. By default, `pip install logicpwn` installs everything. The optional extras below are for users who want to install only specific components:

### 🔐 Authentication Module (`[auth]`)
- Session management and persistence
- CSRF token handling
- MFA support (TOTP, SMS, Email)
- OAuth 2.0 and SAML integration
- JWT token management
- Identity provider integration

**Dependencies**: `requests`, `pydantic`, `loguru`, `cryptography`, `qrcode`

### 🚀 Runner Module (`[runner]`)
- HTTP request execution
- Async request support
- Rate limiting and throttling
- Session management
- Middleware support

**Dependencies**: `requests`, `pydantic`, `loguru`, `aiohttp`, `pytest-asyncio`

### 🔍 Access Detection Module (`[access]`)
- IDOR vulnerability detection
- Access control testing
- Privilege escalation testing
- Tenant isolation testing
- Smart ID generation

**Dependencies**: `requests`, `pydantic`, `loguru`

### ✅ Validator Module (`[validator]`)
- Response validation
- Business logic rule checking
- Vulnerability pattern detection
- Confidence scoring
- Custom validation presets

**Dependencies**: `requests`, `pydantic`, `loguru`, `jsonpath-ng`

### 📊 Reporter Module (`[reporter]`)
- Vulnerability reporting
- Compliance mapping
- Indian law enforcement support
- CVSS scoring
- Template rendering

**Dependencies**: `requests`, `pydantic`, `loguru`, `pyyaml`

### 📈 Performance Module (`[performance]`)
- Performance monitoring
- Memory profiling
- Benchmarking tools
- Async performance tracking

**Dependencies**: `requests`, `pydantic`, `loguru`, `psutil`

### 🧪 Stress Testing Module (`[stress]`)
- Load testing
- Concurrent exploit execution
- Performance metrics
- Error rate analysis

**Dependencies**: `requests`, `pydantic`, `loguru`, `psutil`, `aiohttp`, `pytest-asyncio`

### 💥 Exploit Engine (`[exploit]`)
- Exploit chain execution
- Payload generation
- Step validation
- Session state management

**Dependencies**: `requests`, `pydantic`, `loguru`, `pyyaml`

### 🛡️ Reliability Features (`[reliability]`)
- Circuit breakers
- Security metrics
- Adaptive rate limiting
- Event recording

**Dependencies**: `requests`, `pydantic`, `loguru`, `tenacity`

## 📖 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) folder:

- **API Reference** - Complete API documentation
- **Getting Started** - Quick start guides and tutorials
- **Case Studies** - Real-world usage examples
- **Performance Benchmarks** - Performance analysis and optimization
- **Compliance** - Indian law enforcement and compliance frameworks

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

- **Repository**: [https://github.com/Infernus007/LogicPWN](https://github.com/Infernus007/LogicPWN)
- **Documentation**: [docs/](./docs/) folder
- **PyPI**: [https://pypi.org/project/logicpwn/](https://pypi.org/project/logicpwn/)

---

**Built with ❤️ for the security community**
# Test comment for workflow demo
