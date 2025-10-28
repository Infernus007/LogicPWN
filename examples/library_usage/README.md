# LogicPWN Library Usage Examples

Comprehensive examples demonstrating LogicPWN's capabilities and best practices.

## 📚 Examples Overview

### 🚀 Quick Start Examples

| Example | Description | Complexity | Use Case |
|---------|-------------|------------|----------|
| `01_minimal_idor_test.py` | Simplest IDOR test (5 lines) | ⭐ Beginner | Quick security checks |
| `02_authenticated_testing.py` | Testing with authentication | ⭐⭐ Intermediate | API security audits |
| `03_exploit_chain_execution.py` | Multi-step attack chains | ⭐⭐ Intermediate | Complex vulnerability testing |
| `04_batch_endpoint_testing.py` | Test multiple endpoints | ⭐⭐⭐ Advanced | Full API surface scans |
| `05_context_manager_usage.py` | Resource management | ⭐⭐ Intermediate | Production code |
| `06_result_export_and_reporting.py` | Generate reports | ⭐⭐ Intermediate | Compliance & CI/CD |

## 🎯 Running the Examples

### Prerequisites

```bash
# Install LogicPWN
pip install logicpwn

# Or install from source
pip install -e .
```

### Run an Example

```bash
# Navigate to examples directory
cd examples/library_usage

# Run any example
python 01_minimal_idor_test.py
```

### Modify for Your Target

Each example uses `https://api.example.com` as a placeholder. Replace with your actual target:

```python
# Change this
tester = SecurityTester("https://api.example.com")

# To your target
tester = SecurityTester("https://your-target.com")
```

## 📖 Example Details

### 01 - Minimal IDOR Test

**What it does:**
- Tests for IDOR vulnerabilities in 5 lines
- No authentication required
- Perfect for quick checks

**Key concepts:**
- `quick_idor_test()` function
- Basic result interpretation

**Run time:** < 5 seconds

```python
from logicpwn import quick_idor_test

results = quick_idor_test(
    "https://api.example.com",
    "/api/users/{id}",
    [1, 2, 3, "admin"]
)
print(results['summary'])
```

---

### 02 - Authenticated Testing

**What it does:**
- Authenticates to the target
- Tests multiple endpoints
- Checks for unauthorized access

**Key concepts:**
- `SecurityTester` class
- Authentication flow
- Testing protected resources

**Run time:** 10-30 seconds

```python
from logicpwn import SecurityTester

with SecurityTester("https://api.example.com") as tester:
    tester.authenticate("user", "pass")
    results = tester.test_idor("/api/users/{id}", [1, 2, 3])
```

---

### 03 - Exploit Chain Execution

**What it does:**
- Executes multi-step attack sequences
- Tests business logic flaws
- Validates each step's success

**Key concepts:**
- `ExploitChain` and `ExploitStep`
- YAML configuration
- Step-by-step validation

**Run time:** 30-60 seconds

```python
from logicpwn import quick_exploit_chain

results = quick_exploit_chain("exploit_chain.yaml")
print(f"Completed {len(results)} steps")
```

---

### 04 - Batch Endpoint Testing

**What it does:**
- Tests multiple resource types
- Scans entire API surfaces
- Aggregates results

**Key concepts:**
- Batch testing
- Result aggregation
- Performance optimization

**Run time:** 1-5 minutes (depending on API size)

```python
resources = {
    "users": [1, 2, 3],
    "orders": [100, 101, 102],
    "documents": ["doc1", "doc2"]
}

for resource_type, ids in resources.items():
    results = tester.test_idor(f"/api/{resource_type}/{{id}}", ids)
```

---

### 05 - Context Manager Usage

**What it does:**
- Demonstrates proper resource management
- Automatic cleanup
- Exception handling

**Key concepts:**
- Context managers (`with` statement)
- Resource lifecycle
- Best practices

**Run time:** < 10 seconds

```python
with SecurityTester("https://api.example.com") as tester:
    # Resources automatically cleaned up
    pass
```

---

### 06 - Result Export and Reporting

**What it does:**
- Exports results in multiple formats
- Generates compliance reports
- CI/CD integration examples

**Key concepts:**
- Report generation
- Multiple export formats
- CI/CD integration

**Run time:** 10-20 seconds

```python
result.export_json("report.json")
result.export_markdown("report.md")
result.export_csv("report.csv")
```

---

## 🎓 Learning Path

### Beginner Track
1. Start with `01_minimal_idor_test.py`
2. Move to `02_authenticated_testing.py`
3. Try `05_context_manager_usage.py`

### Intermediate Track
1. Study `03_exploit_chain_execution.py`
2. Practice with `04_batch_endpoint_testing.py`
3. Master `06_result_export_and_reporting.py`

### Advanced Track
1. Combine multiple examples
2. Create custom exploit chains
3. Build your own security testing workflows

## 🔧 Customization

### Modify Target URLs

```python
# Single target
tester = SecurityTester("https://your-api.com")

# Multiple targets
targets = ["https://api1.com", "https://api2.com"]
for target in targets:
    with SecurityTester(target) as tester:
        # Test each target
```

### Adjust Test IDs

```python
# Numeric IDs
test_ids = list(range(1, 100))

# String IDs
test_ids = ["user1", "user2", "admin"]

# Mixed
test_ids = [1, 2, 3, "admin", "guest", 100, 999]
```

### Custom Success Indicators

```python
results = tester.test_idor(
    "/api/users/{id}",
    [1, 2, 3],
    success_indicators=["email", "profile", "user_data", "username"]
)
```

## 📊 Output Examples

### Console Output

```
IDOR Vulnerability Scan Results:
  Target: https://api.example.com
  Total Tests: 10
  Vulnerabilities: 3 (30.0%)
  Secure: 7 (70.0%)
  Status: 🚨 VULNERABLE
```

### JSON Export

```json
{
  "test_type": "IDOR",
  "target_url": "https://api.example.com",
  "vulnerable_count": 3,
  "pass_rate": 70.0,
  "vulnerabilities": [...]
}
```

### Markdown Report

```markdown
# IDOR Security Test Report

**Target:** https://api.example.com
**Date:** 2025-01-15 10:30:00

## Vulnerabilities Found

### 1. /api/users/2
- **Status Code:** 200
- **Evidence:** User data exposed...
```

## 🚀 Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
- name: Run Security Tests
  run: |
    python examples/library_usage/01_minimal_idor_test.py
    if [ $? -ne 0 ]; then
      echo "Security vulnerabilities detected!"
      exit 1
    fi
```

### Python Script Integration

```python
from logicpwn import quick_idor_test

def security_check(api_url, endpoints):
    for endpoint in endpoints:
        results = quick_idor_test(api_url, endpoint, [1, 2, 3])
        if results['vulnerable_count'] > 0:
            send_alert(f"Vulnerability found in {endpoint}")
```

### Scheduled Testing (Cron)

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/examples && python 04_batch_endpoint_testing.py
```

## 🆘 Troubleshooting

### Common Issues

**Authentication fails:**
```python
# Enable debug output
from logicpwn.core.logging import log_debug
log_debug("Check authentication response")
```

**Connection errors:**
```python
# Increase timeout
tester = SecurityTester("https://api.example.com")
# Adjust timeouts in your requests
```

**Import errors:**
```bash
# Reinstall LogicPWN
pip uninstall logicpwn
pip install logicpwn
```

## 📚 Additional Resources

- [Main Documentation](../../README.md)
- [API Reference](../../docs/)
- [Exploit Chain Examples](../simple_exploit_corrected.yaml)
- [DVWA Examples](../dvwa_auth_example.py)

## 💡 Tips & Best Practices

1. **Always use context managers** for production code
2. **Export results** for documentation and compliance
3. **Test in staging** before production
4. **Rate limit** your tests to avoid DoS
5. **Document findings** immediately

## 🤝 Contributing

Have a useful example? Submit a PR!

1. Create your example file
2. Follow the existing naming convention
3. Add documentation
4. Submit pull request

---

**Happy Testing! 🔒**
