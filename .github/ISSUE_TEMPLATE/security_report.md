---
name: Security report
about: Report a security vulnerability in LogicPwn
title: '[SECURITY] '
labels: ['security']
assignees: ''
---

**Security Vulnerability Report**

**Vulnerability Type**
- [ ] Authentication bypass
- [ ] Information disclosure
- [ ] Code injection
- [ ] Privilege escalation
- [ ] Denial of service
- [ ] Other (please specify)

**Severity**
- [ ] Critical
- [ ] High
- [ ] Medium
- [ ] Low

**Description**
A clear and concise description of the security vulnerability.

**Steps to reproduce**
1. Install LogicPwn version '...'
2. Run the following code '...'
3. Observe the security issue

**Proof of concept**
```python
# Please provide a minimal proof of concept
# DO NOT include real credentials or sensitive data
from logicpwn.core import send_request

# Example that demonstrates the vulnerability
result = send_request(
    url="https://example.com",
    method="GET"
)
```

**Expected behavior**
What should happen in a secure implementation.

**Actual behavior**
What actually happens that creates the security vulnerability.

**Environment**
- LogicPwn version: [e.g. 1.0.0]
- Python version: [e.g. 3.11]
- OS: [e.g. Ubuntu 20.04]

**Impact assessment**
Describe the potential impact of this vulnerability:
- What could an attacker do?
- What systems could be affected?
- What data could be compromised?

**Suggested fix**
If you have ideas for how this could be fixed, please share them.

**Additional context**
Any other relevant information about the vulnerability.

**Responsible disclosure**
- [ ] I agree to responsible disclosure practices
- [ ] I will not publicly disclose this issue until it's fixed
- [ ] I understand this is for authorized security testing only

**Checklist**
- [ ] I have provided a clear description of the vulnerability
- [ ] I have included a proof of concept
- [ ] I have assessed the potential impact
- [ ] I have considered responsible disclosure
- [ ] I have not included real credentials or sensitive data 