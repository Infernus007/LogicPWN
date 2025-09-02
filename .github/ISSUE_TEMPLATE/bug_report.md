---
name: Bug report
about: Create a report to help us improve LogicPwn
title: '[BUG] '
labels: ['bug']
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Install LogicPwn with '...'
2. Run the following code '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Actual behavior**
A clear and concise description of what actually happened.

**Environment:**
 - OS: [e.g. Ubuntu 20.04, macOS 12.0, Windows 11]
 - Python version: [e.g. 3.9, 3.10, 3.11]
 - LogicPwn version: [e.g. 1.0.0]
 - Installation method: [e.g. pip, poetry, development]

**Code example**
```python
# Please provide a minimal code example that reproduces the issue
from logicpwn.core import send_request

result = send_request(
    url="https://example.com",
    method="GET"
)
```

**Error message**
```
# Please paste the full error message here
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
...
```

**Additional context**
Add any other context about the problem here, such as:
- Target system information
- Network configuration
- Security considerations

**Checklist**
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have provided a minimal code example
- [ ] I have included the full error message
- [ ] I have specified my environment details
