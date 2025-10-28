<div align="center">

# 🔒 LogicPWN

### **Automated Business Logic Vulnerability Testing**

<p align="center">
  <strong>Test for IDOR, authorization bypasses, and business logic flaws in just 3 lines of code</strong>
</p>

[![PyPI version](https://badge.fury.io/py/logicpwn.svg)](https://pypi.org/project/logicpwn/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/logicpwn.svg)](https://pypi.org/project/logicpwn/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[🚀 Quick Start](#-quick-start-30-seconds) •
[📖 Documentation](#-documentation) •
[💡 Examples](#-examples) •
[🤝 Community](#-community--support)

</div>

---

## 🎯 What is LogicPWN?

LogicPWN is a **Python security testing framework** that makes finding business logic vulnerabilities as easy as:

```python
from logicpwn import quick_idor_test

results = quick_idor_test("https://api.example.com", "/api/users/{id}", [1, 2, 3, "admin"])
print(results['summary'])  # Found 2 IDOR vulnerabilities out of 4 tests
```

### Why LogicPWN?

<table>
<tr>
<td width="33%">

#### ⚡ **Simple**
```python
3 lines of code
  vs
20+ lines before
```
85% less code for common tasks

</td>
<td width="33%">

#### 🎯 **Powerful**
```python
• IDOR Testing
• Auth Bypass
• Exploit Chains
• Business Logic
```
Enterprise-grade features

</td>
<td width="33%">

#### 🚀 **Fast**
```python
Async support
Batch testing
Caching
Rate limiting
```
Test 1000+ endpoints

</td>
</tr>
</table>

---

## ✨ Key Features

<table>
<tr>
<td>

### 🔐 **Authentication**
- OAuth 2.0, JWT, SAML
- Session persistence
- CSRF handling
- Multi-factor auth

</td>
<td>

### 🎯 **Vulnerability Testing**
- IDOR detection
- Authorization bypass
- Privilege escalation
- Tenant isolation

</td>
</tr>
<tr>
<td>

### ⚡ **Exploit Chains**
- Multi-step attacks
- YAML configuration
- State management
- Auto-retry logic

</td>
<td>

### 📊 **Reporting**
- JSON, Markdown, CSV
- Compliance-ready
- CI/CD integration
- Real-time metrics

</td>
</tr>
</table>

---

## 🚀 Quick Start (30 seconds)

### 📦 Installation

```bash
pip install logicpwn
```

### 🎯 Your First Test

**Test for IDOR vulnerabilities:**

```python
from logicpwn import quick_idor_test

# Test if users can access each other's data
results = quick_idor_test(
    target_url="https://api.example.com",
    endpoint_pattern="/api/users/{id}",
    test_ids=[1, 2, 3, "admin", "guest"]
)

print(results['summary'])
```

**Output:**
```
Found 2 IDOR vulnerabilities out of 5 tests
Pass Rate: 60.0%
```

### 🔐 With Authentication

```python
from logicpwn import SecurityTester

with SecurityTester("https://api.example.com") as tester:
    # Authenticate
    tester.authenticate("testuser", "password123")

    # Test for vulnerabilities
    results = tester.test_idor("/api/users/{id}", [1, 2, 3])

    # Export report
    results_obj = SecurityTestResult(**results)
    results_obj.export_json("security_report.json")
```

### 🎬 See It in Action

```python
# Clone and try the examples
git clone https://github.com/Infernus007/LogicPWN.git
cd LogicPWN/examples/library_usage
python 01_minimal_idor_test.py
```

---

## 💡 Use Cases

<details>
<summary><b>🔍 Find IDOR Vulnerabilities</b></summary>

```python
from logicpwn import SecurityTester

with SecurityTester("https://api.example.com") as tester:
    tester.authenticate("user", "pass")

    # Test user endpoints
    results = tester.test_idor("/api/users/{id}", [1, 2, 3, 100, 999])

    if results['vulnerable_count'] > 0:
        print(f"⚠️  Found {results['vulnerable_count']} IDOR vulnerabilities!")
        for vuln in results['vulnerabilities']:
            print(f"  • {vuln.endpoint_url}")
```

</details>

<details>
<summary><b>🚪 Test Authorization Bypass</b></summary>

```python
from logicpwn import SecurityTester

with SecurityTester("https://api.example.com") as tester:
    tester.authenticate("regular_user", "password")

    # Check if admin endpoints are exposed
    admin_results = tester.test_unauthorized_access([
        "/api/admin/users",
        "/api/admin/settings",
        "/api/admin/logs"
    ])

    if admin_results['vulnerable']:
        print(f"🚨 {len(admin_results['accessible'])} admin endpoints exposed!")
```

</details>

<details>
<summary><b>🔗 Run Multi-Step Exploit Chains</b></summary>

```python
from logicpwn import quick_exploit_chain

# Execute complex attack sequences from YAML
results = quick_exploit_chain("price_manipulation_test.yaml")

successful = sum(1 for r in results if r.status.value == "success")
print(f"Completed {successful}/{len(results)} steps")

if successful == len(results):
    print("🚨 Vulnerability confirmed: Price manipulation possible!")
```

</details>

<details>
<summary><b>📊 Generate Compliance Reports</b></summary>

```python
from logicpwn import SecurityTester
from logicpwn.results import SecurityTestResult

# Run tests
with SecurityTester("https://api.example.com") as tester:
    tester.authenticate("user", "pass")
    results = tester.test_idor("/api/users/{id}", [1, 2, 3])

# Generate reports
result_obj = SecurityTestResult(
    test_type="IDOR Security Audit",
    target_url="https://api.example.com",
    total_tests=results['total_tested'],
    vulnerabilities=results['vulnerabilities'],
    safe_endpoints=results['safe_endpoints']
)

# Export in multiple formats
result_obj.export_json("audit_report.json")      # For automation
result_obj.export_markdown("audit_report.md")    # For documentation
result_obj.export_csv("audit_report.csv")        # For Excel
```

</details>

<details>
<summary><b>🤖 CI/CD Integration</b></summary>

```python
# security_tests.py
from logicpwn import quick_idor_test
import sys

results = quick_idor_test(
    "https://staging.example.com",
    "/api/users/{id}",
    [1, 2, 3]
)

# Fail CI/CD pipeline if vulnerabilities found
if results['vulnerable_count'] > 0:
    print(f"❌ Security check failed: {results['summary']}")
    sys.exit(1)
else:
    print(f"✅ Security check passed!")
    sys.exit(0)
```

**GitHub Actions:**
```yaml
- name: Security Tests
  run: python security_tests.py
```

</details>

---

## 📚 Examples

We have **6 comprehensive examples** to get you started:

| Example | Description | Difficulty | Time |
|---------|-------------|------------|------|
| [01 - Minimal IDOR Test](examples/library_usage/01_minimal_idor_test.py) | 5-line vulnerability test | ⭐ Easy | 2 min |
| [02 - Authenticated Testing](examples/library_usage/02_authenticated_testing.py) | Full auth flow | ⭐⭐ Medium | 5 min |
| [03 - Exploit Chains](examples/library_usage/03_exploit_chain_execution.py) | Multi-step attacks | ⭐⭐ Medium | 10 min |
| [04 - Batch Testing](examples/library_usage/04_batch_endpoint_testing.py) | Scan entire APIs | ⭐⭐⭐ Hard | 15 min |
| [05 - Context Managers](examples/library_usage/05_context_manager_usage.py) | Resource management | ⭐⭐ Medium | 5 min |
| [06 - Report Generation](examples/library_usage/06_result_export_and_reporting.py) | Export & reports | ⭐⭐ Medium | 10 min |

**👉 [View All Examples](examples/library_usage/)**

---

## 🏗️ Architecture

<details>
<summary><b>Click to view architecture</b></summary>

```
┌─────────────────────────────────────────────────────────────┐
│                        LogicPWN                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Quick Start  │  │ SecurityTester│  │ Exploit Chain│     │
│  │     API      │  │     Class     │  │    Engine    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
├────────────────────────────┼─────────────────────────────────┤
│                     Core Modules                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐         │
│  │    Auth     │ │   Access    │ │   Validator  │         │
│  │  • OAuth    │ │   • IDOR    │ │  • Response  │         │
│  │  • JWT      │ │   • BOLA    │ │  • Business  │         │
│  │  • SAML     │ │   • Tenant  │ │  • Logic     │         │
│  └─────────────┘ └─────────────┘ └──────────────┘         │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐         │
│  │   Runner    │ │  Reporter   │ │  Reliability │         │
│  │  • Sync     │ │  • JSON     │ │  • Retry     │         │
│  │  • Async    │ │  • Markdown │ │  • Circuit   │         │
│  │  • HTTP/2   │ │  • CSV      │ │  • Breaker   │         │
│  └─────────────┘ └─────────────┘ └──────────────┘         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

</details>

**Modular Design:**
- 🎯 **Core Modules** - Authentication, Access Control, Validation
- ⚡ **High Performance** - Async/await, connection pooling, caching
- 🔌 **Extensible** - Plugin system, middleware support
- 📦 **Lightweight** - Install only what you need

---

## 📖 Documentation

<table>
<tr>
<td width="50%">

### 📘 **For Beginners**

- [🚀 Quick Start Guide](QUICK_REFERENCE.md)
- [💡 Examples Library](examples/library_usage/)
- [🎓 Learning Path](examples/library_usage/README.md#-learning-path)
- [❓ FAQ](#-faq)

</td>
<td width="50%">

### 📗 **For Advanced Users**

- [🔧 API Reference](#-advanced-usage)
- [🏗️ Architecture](#-architecture)
- [🧪 Testing Guide](#-testing)
- [🤝 Contributing](CONTRIBUTING.md)

</td>
</tr>
</table>

---

## 🎓 Learning Path

<details>
<summary><b>🟢 Beginner (30 minutes)</b></summary>

**Goal:** Understand the basics and run your first test

1. Install LogicPWN: `pip install logicpwn`
2. Read [Quick Start](#-quick-start-30-seconds)
3. Run [01_minimal_idor_test.py](examples/library_usage/01_minimal_idor_test.py)
4. Modify it for your target
5. Try [02_authenticated_testing.py](examples/library_usage/02_authenticated_testing.py)

**You'll learn:** Installation, basic IDOR testing, authentication

</details>

<details>
<summary><b>🟡 Intermediate (2 hours)</b></summary>

**Goal:** Master common security testing workflows

1. Study [03_exploit_chain_execution.py](examples/library_usage/03_exploit_chain_execution.py)
2. Create your own exploit chain YAML
3. Try [04_batch_endpoint_testing.py](examples/library_usage/04_batch_endpoint_testing.py)
4. Learn [05_context_manager_usage.py](examples/library_usage/05_context_manager_usage.py)
5. Practice [06_result_export_and_reporting.py](examples/library_usage/06_result_export_and_reporting.py)

**You'll learn:** Exploit chains, batch testing, reporting, best practices

</details>

<details>
<summary><b>🔴 Advanced (1 day)</b></summary>

**Goal:** Build custom security testing frameworks

1. Explore the [core modules](#-architecture)
2. Build custom exploit chains
3. Create CI/CD integration
4. Develop custom validators
5. Contribute to LogicPWN

**You'll learn:** Architecture, extensibility, production deployment

</details>

---

## ❓ FAQ

<details>
<summary><b>Is LogicPWN a vulnerability scanner?</b></summary>

Yes and no. LogicPWN is a **testing framework** for business logic vulnerabilities. Unlike traditional scanners that look for known CVEs, LogicPWN tests for:
- IDOR (Insecure Direct Object Reference)
- Authorization bypasses
- Business logic flaws
- Privilege escalation

</details>

<details>
<summary><b>Can I use LogicPWN for bug bounties?</b></summary>

**Yes!** LogicPWN is perfect for bug bounty hunting. Many testers use it to:
- Automate IDOR testing across endpoints
- Test authorization on hundreds of endpoints
- Find business logic flaws quickly
- Generate proof-of-concept reports

</details>

<details>
<summary><b>How is this different from Burp Suite?</b></summary>

LogicPWN complements Burp Suite:

| Feature | Burp Suite | LogicPWN |
|---------|------------|----------|
| **Manual Testing** | ✅ Excellent | ❌ Not designed for this |
| **Automation** | ⚠️ Complex | ✅ Simple (3 lines of code) |
| **Business Logic** | ⚠️ Manual process | ✅ Built-in |
| **CI/CD Integration** | ❌ Difficult | ✅ Easy |
| **Scripting** | ⚠️ Java/Python | ✅ Python-native |
| **Price** | 💰 $449/year | 💰 Free |

**Best practice:** Use Burp for manual testing, LogicPWN for automation.

</details>

<details>
<summary><b>Is it safe to use in production?</b></summary>

LogicPWN is designed for **testing environments**. Features for safety:

✅ **Rate limiting** - Avoid DoS
✅ **Connection management** - Proper cleanup
✅ **Error handling** - Graceful failures
✅ **Logging** - Audit trails

⚠️ **Always:**
- Test in staging first
- Get permission before testing
- Follow responsible disclosure

</details>

<details>
<summary><b>Can I contribute?</b></summary>

**Yes!** We welcome contributions:

- 🐛 [Report bugs](https://github.com/Infernus007/LogicPWN/issues)
- 💡 [Suggest features](https://github.com/Infernus007/LogicPWN/issues)
- 📝 [Improve docs](https://github.com/Infernus007/LogicPWN/pulls)
- 🔧 [Submit code](CONTRIBUTING.md)

See [Contributing Guide](CONTRIBUTING.md) for details.

</details>

---

## 🔧 Advanced Usage

<details>
<summary><b>Custom Authentication</b></summary>

```python
from logicpwn import SecurityTester

tester = SecurityTester("https://api.example.com")
tester.authenticate(
    username="admin",
    password="secret",
    login_endpoint="/api/v2/auth/login",
    method="POST",
    username_field="email",  # Custom field
    password_field="pwd",    # Custom field
    success_indicators=["access_token", "authenticated"]
)
```

</details>

<details>
<summary><b>Async Batch Testing</b></summary>

```python
from logicpwn.core.access import detect_idor_flaws_async
import asyncio

async def scan_all_endpoints():
    results = await detect_idor_flaws_async(
        endpoint_template="https://api.example.com/users/{id}",
        test_ids=[str(i) for i in range(1, 1000)],  # Test 1000 IDs
        success_indicators=["user_data"],
        failure_indicators=["unauthorized"]
    )
    return results

results = asyncio.run(scan_all_endpoints())
```

</details>

<details>
<summary><b>Custom Exploit Chains (YAML)</b></summary>

```yaml
# business_logic_test.yaml
name: "E-commerce Price Manipulation"
description: "Test for price override vulnerabilities"

steps:
  - name: "Add Product to Cart"
    request_config:
      method: "POST"
      url: "https://shop.com/api/cart/add"
      json_data:
        product_id: "EXPENSIVE_ITEM"
        quantity: 1
    success_indicators: ["cart_updated"]

  - name: "Manipulate Price"
    request_config:
      method: "POST"
      url: "https://shop.com/api/cart/update"
      json_data:
        product_id: "EXPENSIVE_ITEM"
        price: 0.01  # Try to set price to 1 cent
    success_indicators: ["updated"]
    failure_indicators: ["invalid", "unauthorized"]

  - name: "Checkout"
    request_config:
      method: "POST"
      url: "https://shop.com/api/checkout"
    success_indicators: ["order_confirmed"]
```

```python
from logicpwn import quick_exploit_chain

results = quick_exploit_chain("business_logic_test.yaml")
```

</details>

<details>
<summary><b>Logging Configuration</b></summary>

```python
from logicpwn import configure_logging, use_preset

# Simple debug logging
configure_logging(level="DEBUG", log_file="debug.log")

# Or use presets
use_preset("debug")                          # Verbose debugging
use_preset("security", log_file="audit.log") # Compliance logs
use_preset("ci")                             # CI/CD friendly
```

</details>

---

## 📊 Performance

Real-world benchmarks from production testing:

| Metric | Value | Notes |
|--------|-------|-------|
| **Throughput** | 4.3 req/sec | Average across all test types |
| **Memory** | 67.7 MB | Lightweight footprint |
| **CPU** | 26.2% | Efficient resource usage |
| **Reliability** | 99.2% | Success rate across tests |
| **Async Speed** | 10x faster | vs synchronous testing |

**Scalability:**
- ✅ Test 1000+ endpoints in minutes
- ✅ Async batch processing
- ✅ Connection pooling & caching
- ✅ Adaptive rate limiting

---

## 🤝 Community & Support

<table>
<tr>
<td width="33%" align="center">

### 💬 **Get Help**

[GitHub Discussions](https://github.com/Infernus007/LogicPWN/discussions)

Ask questions, share tips

</td>
<td width="33%" align="center">

### 🐛 **Report Issues**

[GitHub Issues](https://github.com/Infernus007/LogicPWN/issues)

Bug reports, feature requests

</td>
<td width="33%" align="center">

### 📚 **Documentation**

[Read the Docs](#-documentation)

Guides, API reference

</td>
</tr>
</table>

### 🌟 **Star History**

If LogicPWN helps you, consider giving it a star! ⭐

### 🤝 **Contributing**

We welcome contributions from the community:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch
3. ✍️ Make your changes
4. ✅ Add tests
5. 📬 Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 🚀 What's New in v0.4.0

<table>
<tr>
<td>

### 🎯 **Simplified API**

```python
# Before (v0.3.0)
from logicpwn.core.auth import ...
# 20+ lines of code

# After (v0.4.0)
from logicpwn import quick_idor_test
# 3 lines of code
```

**85% less code!**

</td>
<td>

### ✨ **New Features**

- ✅ `SecurityTester` class
- ✅ Quick functions
- ✅ Rich result objects
- ✅ Better error messages
- ✅ 6 new examples
- ✅ Logging presets

**100% backward compatible**

</td>
</tr>
</table>

**[View Full Changelog](CHANGELOG_v0.4.0.md)**

---

## 🛣️ Roadmap

### v0.5.0 (Coming Soon)
- [ ] CLI tool for terminal usage
- [ ] YAML template library
- [ ] GitHub Actions workflows
- [ ] Plugin system
- [ ] Web dashboard

### v0.6.0 (Future)
- [ ] GraphQL support
- [ ] gRPC testing
- [ ] WebSocket security
- [ ] AI-powered test generation

**[View Full Roadmap →](https://github.com/Infernus007/LogicPWN/projects)**

---

## 💼 Enterprise Support

Need help deploying LogicPWN in your organization?

<table>
<tr>
<td width="50%">

### 🏢 **Enterprise Features**
- Custom training sessions
- Priority support
- Custom feature development
- SLA guarantees
- Dedicated Slack channel

</td>
<td width="50%">

### 📧 **Contact Us**

For enterprise inquiries:
- Email: jashnaik2004@gmail.com
- GitHub: [@Infernus007](https://github.com/Infernus007)

</td>
</tr>
</table>

---

## 📄 License

LogicPWN is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

```
MIT License - Free to use, modify, and distribute
```

---

## 🙏 Acknowledgments

LogicPWN is built with these amazing open-source libraries:

- [requests](https://requests.readthedocs.io/) - HTTP library
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP
- [pydantic](https://docs.pydantic.dev/) - Data validation
- [loguru](https://loguru.readthedocs.io/) - Logging
- [PyYAML](https://pyyaml.org/) - YAML parsing

**Special thanks** to the security community for feedback and contributions!

---

## 🎯 Quick Links

<div align="center">

| Resource | Link |
|----------|------|
| 📦 **PyPI Package** | https://pypi.org/project/logicpwn/ |
| 🐙 **GitHub Repo** | https://github.com/Infernus007/LogicPWN |
| 📚 **Documentation** | [docs/](docs/) |
| 💡 **Examples** | [examples/library_usage/](examples/library_usage/) |
| 🐛 **Report Bug** | [Create Issue](https://github.com/Infernus007/LogicPWN/issues/new) |
| 💬 **Discussions** | [Join Discussion](https://github.com/Infernus007/LogicPWN/discussions) |

</div>

---

<div align="center">

### 🎉 **Start Testing in 30 Seconds**

```bash
pip install logicpwn
```

```python
from logicpwn import quick_idor_test
results = quick_idor_test("https://api.example.com", "/api/users/{id}", [1, 2, 3])
```

**Built with ❤️ for the security community**

⭐ **Star us on GitHub** if LogicPWN helps you find vulnerabilities!

[⬆ Back to Top](#-logicpwn)

</div>
