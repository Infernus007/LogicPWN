# LogicPWN

**Advanced Business Logic Security Testing Framework**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/logicpwn/logicpwn/workflows/tests/badge.svg)](https://github.com/logicpwn/logicpwn/actions)

A comprehensive Python framework for advanced business logic vulnerability testing, IDOR detection, and multi-step security exploitation. Built for penetration testers, security researchers, and bug bounty hunters.

## 🚀 Features

- **🔍 IDOR Detection**: Intelligent enumeration and cross-user testing
- **⚡ Multi-Step Exploit Chains**: Automated complex attack scenarios
- **🚀 High-Performance Async**: Concurrent testing with intelligent rate limiting
- **🔐 Enterprise Authentication**: OAuth 2.0, SAML, JWT, MFA support
- **💪 Stress Testing**: Performance validation with security monitoring
- **📊 Rich Reporting**: Comprehensive vulnerability analysis and documentation
- **🤖 Auto-Documentation**: Automatic API documentation generation and updates
- **🔄 CI/CD Integration**: Pre-commit hooks and automated workflows

## 🚀 Quick Start

```bash
# Install LogicPWN
pip install logicpwn

# Or install with all features
pip install logicpwn[async,stress,reporting]

# Development installation
git clone https://github.com/Infernus007/LogicPWN.git
cd LogicPWN
poetry install --with dev
poetry run pre-commit install
```

### 🔧 Basic Usage

```python
from logicpwn.core.auth import AuthConfig, authenticate_session
from logicpwn.core.access import detect_idor_flaws

# Configure authentication
auth_config = AuthConfig(
    url="https://target.com/login",
    credentials={"username": "testuser", "password": "password"},
    success_indicators=["dashboard", "welcome"]
)

# Get authenticated session
session = authenticate_session(auth_config)

# Test for IDOR vulnerabilities
results = detect_idor_flaws(
    session=session,
    endpoint_template="https://target.com/api/users/{id}",
    test_ids=["user1", "user2", "admin"],
    success_indicators=["profile_data"],
    failure_indicators=["access_denied", "unauthorized"]
)

# Check results
for result in results:
    if result.vulnerability_detected:
        print(f"🚨 IDOR found: {result.test_url}")
```

### ⚡ Async Testing

```python
import asyncio
from logicpwn.core.runner import AsyncRequestRunner

async def test_endpoints():
    async with AsyncRequestRunner() as runner:
        results = await runner.send_request(
            url="https://target.com/api/data",
            method="GET"
        )
        print(f"Response: {results.status_code}")

asyncio.run(test_endpoints())
```

### 💪 Stress Testing

```python
from logicpwn.core.stress import StressTester, StressTestConfig

async def run_stress_test():
    config = StressTestConfig(
        max_concurrent=25,
        duration=30,
        memory_monitoring=True
    )

    async with StressTester(config) as tester:
        metrics = await tester.run_stress_test([
            {"url": "https://target.com/api/endpoint", "method": "GET"}
        ])

    print(f"Requests/sec: {metrics.requests_per_second:.1f}")
    print(f"Error rate: {metrics.error_rate:.1f}%")

asyncio.run(run_stress_test())
```

## 📊 Performance Benchmarks

Real-world performance metrics from comprehensive testing:

| Test Scenario | Requests | Duration | Req/s | Memory | CPU | Error Rate |
|---------------|----------|----------|-------|--------|-----|------------|
| **Basic HTTP Requests** | 100 | 11.36s | 8.8 | 62.2 MB | 12.2% | 0.0% |
| **Async Concurrent** | 100 | 24.82s | 4.0 | 66.3 MB | 30.4% | 3.0% |
| **IDOR Detection** | 25 | 24.90s | 1.0 | 68.8 MB | 50.0% | 0.0% |
| **Stress Testing** | 169 | 51.61s | 3.3 | 73.5 MB | 12.5% | 0.0% |

**Overall Averages:**
- **4.3 requests/second** average throughput
- **67.7 MB** average memory usage
- **26.2%** average CPU utilization
- **Excellent reliability** with minimal error rates

*Benchmarks performed against public test endpoints with real network conditions.*

## 🏗️ Architecture

LogicPWN is built with a modular, extensible architecture:

```
logicpwn/
├── core/
│   ├── auth/           # Authentication & session management
│   ├── access/         # IDOR & access control testing
│   ├── runner/         # HTTP request execution (sync/async)
│   ├── stress/         # Performance & stress testing
│   ├── validator/      # Response validation & analysis
│   ├── reporter/       # Vulnerability reporting & compliance
│   └── logging/        # Secure audit logging
├── models/             # Pydantic data models
├── exceptions/         # Custom exception hierarchy
├── middleware/         # Extensible request/response middleware
└── exporters/          # Report export formats (HTML, Markdown, JSON)
```

## 🔧 Key Components

### 🔐 Authentication System
- **Multi-protocol support**: OAuth 2.0, SAML, JWT, form-based
- **Session persistence**: Automatic token refresh and CSRF handling
- **MFA integration**: TOTP, SMS verification support
- **Enterprise SSO**: Active Directory, LDAP integration

### 🚪 Access Control Testing
- **Intelligent IDOR detection** with pattern recognition
- **Cross-tenant isolation** testing for SaaS applications
- **Privilege escalation** path discovery and validation
- **Role-based access control** testing

### ⚡ Performance Engine
- **Async/concurrent execution** for high-throughput testing
- **Adaptive rate limiting** to respect application constraints
- **Memory-efficient** processing for large-scale assessments
- **Circuit breaker patterns** for fault tolerance

### 📊 Reporting & Compliance
- **Multiple export formats**: HTML, Markdown, JSON
- **Compliance frameworks**: SOC 2, ISO 27001, GDPR
- **Indian compliance**: CERT-In, RBI guidelines
- **Automated documentation**: API docs generation and updates

## 🚀 Auto-Documentation Workflow

LogicPWN includes an advanced auto-documentation system:

```bash
# Generate API documentation
make docs-update

# Auto-commit and push documentation changes
make auto-commit-push

# Complete documentation workflow
make docs-workflow
```

**Features:**
- 🔄 **Automatic API documentation** generation from source code
- 🤖 **Pre-commit hooks** for code quality and documentation
- 📝 **Auto-commit** of documentation changes
- 🚀 **Auto-push** to remote repositories
- 📚 **Submodule handling** for documentation management

## 📚 Documentation

- **[API Reference](doks/purple-atmosphere/src/content/docs/api-reference/)** - Complete API documentation
- **[User Guide](doks/purple-atmosphere/src/content/docs/)** - Comprehensive usage guide
- **[Examples](examples/)** - Real-world usage examples
- **[Performance Analysis](doks/purple-atmosphere/src/content/docs/)** - Detailed benchmark results

## 🧪 Testing

```bash
# Run test suite
make test

# Run with coverage
make test-coverage

# Run code quality checks
make check

# Format code
make format

# Run performance benchmarks
poetry run python tests/benchmarks/performance_benchmarks.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### 🛠️ Development Setup

```bash
git clone https://github.com/Infernus007/LogicPWN.git
cd LogicPWN
poetry install --with dev
poetry run pre-commit install
make check  # Verify everything is working
```

### 📋 Pre-commit Hooks

LogicPWN uses pre-commit hooks for code quality:

- **Code formatting**: Black, isort, autoflake
- **Linting**: pyupgrade, prettier
- **Documentation**: Auto-generation and updates
- **Auto-commit**: Documentation changes

## 🔒 Security

LogicPWN is designed for **authorized security testing only**. Please:

- ✅ Obtain proper authorization before testing any systems
- ✅ Follow responsible disclosure practices
- ✅ Respect privacy and confidentiality
- ✅ Comply with applicable laws and regulations
- ✅ Use only for educational and authorized testing purposes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built by the security community for security professionals. Special thanks to:

- **OWASP** for business logic vulnerability research
- **The bug bounty community** for real-world testing feedback
- **Open source contributors** and security researchers
- **GitHub** for hosting and CI/CD infrastructure

---

**⭐ Star us on GitHub if LogicPWN helps secure your applications!**

**🔗 Repository**: [https://github.com/Infernus007/LogicPWN](https://github.com/Infernus007/LogicPWN)

**📧 Support**: Open an issue on GitHub for questions and support
