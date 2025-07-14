# Bug Bounty Submission - IDOR Vulnerability

**Target:** https://target.com
**Assessment Date:** 2025-07-14
**Total Findings:** 1
**Critical Issues:** 0

---

## Vulnerability Details

### High - Insecure Direct Object Reference in User Profile
**CVSS Score:** 7.5
**Affected Endpoints:** /api/users/{id}

**Description:**
Application allows unauthorized access to user profiles...

**Proof of Concept:**
```http
GET /api/users/123 HTTP/1.1
Host: target.com
...
```

**Impact:**
Attackers can access sensitive user information...

**Remediation:**
Implement proper authorization checks...

**References:** N/A
**Discovered At:** 2025-07-14T10:15:32Z

---

## Appendix
- **Scan Duration:** 0:30:00
- **LogicPwn Version:** 1.0.0
- **Authentication:** test@example.com 