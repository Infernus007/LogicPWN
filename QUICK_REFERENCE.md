# LogicPWN v0.4.0 - Quick Reference Guide

## 🚀 Installation

```bash
pip install logicpwn==0.4.0
```

---

## ⚡ Quick Start (Copy & Paste Ready)

### 1. Test for IDOR in 3 Lines

```python
from logicpwn import quick_idor_test

results = quick_idor_test("https://api.example.com", "/api/users/{id}", [1, 2, 3, "admin"])
print(results['summary'])
```

### 2. Authenticated Testing

```python
from logicpwn import SecurityTester

with SecurityTester("https://api.example.com") as tester:
    tester.authenticate("admin", "password123")
    results = tester.test_idor("/api/users/{id}", [1, 2, 3])
    print(results['summary'])
```

### 3. Run Exploit Chain

```python
from logicpwn import quick_exploit_chain

results = quick_exploit_chain("exploit_chain.yaml")
print(f"Completed {len(results)} steps")
```

---

## 📚 Common Patterns

### Test Multiple Endpoints

```python
from logicpwn import SecurityTester

with SecurityTester("https://api.example.com") as tester:
    tester.authenticate("user", "pass")

    # Test users
    user_results = tester.test_idor("/api/users/{id}", [1, 2, 3])

    # Test documents
    doc_results = tester.test_idor("/api/documents/{id}", ["doc1", "doc2"])

    # Test admin access
    admin_results = tester.test_unauthorized_access([
        "/api/admin/users",
        "/api/admin/settings"
    ])
```

### Export Results

```python
from logicpwn import SecurityTester
from logicpwn.results import SecurityTestResult

with SecurityTester("https://api.example.com") as tester:
    tester.authenticate("user", "pass")
    results = tester.test_idor("/api/users/{id}", [1, 2, 3])

    # Create rich result object
    result_obj = SecurityTestResult(
        test_type="IDOR",
        target_url="https://api.example.com",
        total_tests=results['total_tested'],
        vulnerabilities=results['vulnerabilities'],
        safe_endpoints=results['safe_endpoints']
    )

    # Export in multiple formats
    result_obj.export_json("report.json")
    result_obj.export_markdown("report.md")
    result_obj.export_csv("report.csv")
```

### Configure Logging

```python
from logicpwn import configure_logging, use_preset

# Simple
configure_logging(level="DEBUG", log_file="test.log")

# Or use preset
use_preset("debug")                                    # Verbose
use_preset("security", log_file="audit.log")          # Compliance
use_preset("ci")                                       # CI/CD friendly
```

---

## 🎯 API Quick Reference

### SecurityTester Methods

```python
tester = SecurityTester("https://api.example.com")

# Authentication
tester.authenticate(username, password, login_endpoint="/login")

# IDOR Testing
results = tester.test_idor(endpoint_pattern, test_ids, success_indicators=None)

# Unauthorized Access Testing
results = tester.test_unauthorized_access(protected_endpoints, expected_status=403)

# Exploit Chains
results = tester.run_exploit_chain(yaml_file)

# Cleanup
tester.close()  # Or use context manager (with statement)
```

### Quick Functions

```python
# Quick IDOR test
quick_idor_test(target_url, endpoint_pattern, test_ids, username=None, password=None)

# Quick auth test
quick_auth_test(login_url, username, password, success_indicators=None)

# Quick exploit chain
quick_exploit_chain(yaml_file, runner=None)
```

### SecurityTestResult Properties & Methods

```python
result = SecurityTestResult(...)

# Properties
result.is_vulnerable          # bool
result.pass_rate             # float (0-100)
result.vulnerable_count      # int
result.safe_count           # int

# Methods
result.summary()             # str: Human-readable summary
result.detailed_summary()    # str: With vulnerability details
result.to_dict()            # dict: For JSON serialization

# Export
result.export_json(filename)
result.export_markdown(filename)
result.export_csv(filename)

# Analysis
result.get_critical_vulnerabilities()  # list
result.get_high_vulnerabilities()      # list
```

---

## 🔧 Configuration Examples

### Custom Authentication

```python
tester.authenticate(
    username="admin",
    password="password123",
    login_endpoint="/api/auth/login",
    method="POST",
    username_field="email",  # Custom field name
    password_field="pwd",    # Custom field name
    success_indicators=["token", "authenticated", "success"]
)
```

### Custom IDOR Test

```python
results = tester.test_idor(
    endpoint_pattern="/api/users/{id}",
    test_ids=[1, 2, 3, "admin", 100, 999],
    success_indicators=["email", "user_data", "profile"],
    method="GET"  # or "POST", "PUT", "DELETE"
)
```

### Custom Logging

```python
from logicpwn import configure_logging

configure_logging(
    level="INFO",                    # DEBUG, INFO, WARNING, ERROR
    log_file="security_test.log",   # Optional
    colorize=True,                   # Colored output
    rotation="10 MB",                # Rotate at 10MB
    retention="1 week",              # Keep for 1 week
    compression="zip"                # Compress old logs
)
```

---

## 📊 Result Interpretation

### IDOR Test Results

```python
results = {
    'total_tested': 5,           # Total IDs tested
    'vulnerable_count': 2,       # Number of vulnerable endpoints
    'vulnerabilities': [...],     # List of vulnerable endpoints
    'safe_endpoints': [...],      # List of secure endpoints
    'summary': "Found 2 IDOR vulnerabilities out of 5 tests",
    'pass_rate': 60.0           # Percentage secure (60%)
}

# Check if vulnerable
if results['vulnerable_count'] > 0:
    print("⚠️  Vulnerabilities found!")
    for vuln in results['vulnerabilities']:
        print(f"  - {vuln.endpoint_url}")
```

### Unauthorized Access Results

```python
results = {
    'accessible': [...],         # Improperly accessible endpoints
    'blocked': [...],           # Properly blocked endpoints
    'errors': [...],            # Endpoints with errors
    'vulnerable': True,         # True if any accessible
    'summary': "2 endpoints improperly accessible, 3 properly secured",
    'pass_rate': 60.0          # Percentage properly secured
}
```

---

## 🐛 Common Issues & Solutions

### Authentication Fails

```python
# Problem: Authentication not working
# Solution: Enable debug logging to see response
from logicpwn import configure_logging
configure_logging(level="DEBUG")

# Then check success_indicators match actual response
tester.authenticate(
    "user", "pass",
    success_indicators=["token", "success", "logged in"]  # Must match response text
)
```

### Import Errors

```bash
# Problem: Cannot import SecurityTester
# Solution: Reinstall
pip uninstall logicpwn
pip install logicpwn==0.4.0
```

### SSL Errors

```python
# Problem: SSL certificate verification fails
# Solution: Disable SSL verification (testing only!)
tester = SecurityTester("https://api.example.com", verify_ssl=False)
```

---

## 📁 File Structure

```
logicpwn/
├── __init__.py              # Main exports
├── quickstart.py            # High-level API (SecurityTester)
├── results.py               # Rich result objects
├── logging_config.py        # Logging configuration
├── exceptions/
│   └── enhanced_exceptions.py  # Better error messages
├── core/
│   ├── auth/               # Authentication
│   ├── access/             # IDOR detection
│   ├── exploit_engine/     # Exploit chains
│   ├── runner/             # HTTP requests
│   └── validator/          # Response validation
└── examples/
    └── library_usage/      # 6 comprehensive examples
```

---

## 🎓 Learning Path

### Beginner
1. Run `examples/library_usage/01_minimal_idor_test.py`
2. Modify it for your target
3. Try `02_authenticated_testing.py`

### Intermediate
1. Study `03_exploit_chain_execution.py`
2. Create your own exploit chain YAML
3. Try `04_batch_endpoint_testing.py`

### Advanced
1. Combine multiple testing methods
2. Build custom security testing workflows
3. Integrate with CI/CD pipelines

---

## 📖 More Resources

- **Examples:** `examples/library_usage/README.md`
- **Full Changelog:** `CHANGELOG_v0.4.0.md`
- **GitHub:** https://github.com/Infernus007/LogicPWN
- **PyPI:** https://pypi.org/project/logicpwn/

---

## 💡 Pro Tips

1. **Always use context managers** for automatic cleanup:
   ```python
   with SecurityTester(...) as tester:
       # Your code here
   # Automatically cleaned up
   ```

2. **Export results** for documentation:
   ```python
   result_obj.export_markdown("report.md")
   ```

3. **Enable debug logging** when troubleshooting:
   ```python
   use_preset("debug")
   ```

4. **Test in staging** before production

5. **Use batch testing** for efficiency:
   ```python
   for resource in ["users", "orders", "documents"]:
       results = tester.test_idor(f"/api/{resource}/{{id}}", ids)
   ```

---

**Happy Testing! 🔒**

For detailed examples, see `examples/library_usage/`
