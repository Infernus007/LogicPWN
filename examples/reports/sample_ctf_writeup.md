# CTF Writeup - IDOR Challenge

**Target:** https://ctf.target.com
**Assessment Date:** 2025-07-14
**Total Findings:** 1
**Critical Issues:** 0

---

## Vulnerability Details

### High - Insecure Direct Object Reference in User Profile
**CVSS Score:** 7.5
**Affected Endpoints:** /api/users/{id}

**Description:**
The application exposes user profile data without proper authorization checks.

**Proof of Concept:**
```http
GET /api/users/123 HTTP/1.1
Host: ctf.target.com
...
```

**Impact:**
Allows access to other users' data, leading to flag exposure.

**Remediation:**
Add access control to user profile endpoints.

**References:** N/A
**Discovered At:** 2025-07-14T10:15:32Z

---

## Appendix
- **Scan Duration:** 0:30:00
- **LogicPwn Version:** 1.0.0
- **Authentication:** N/A 