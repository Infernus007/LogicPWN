# LogicPWN Examples

This directory contains practical examples demonstrating LogicPWN's core functionality for security testing and business logic vulnerability assessment.

## 🚀 Quick Start

1. **Install LogicPWN**: `poetry install`
2. **Start DVWA**: `docker run -d -p 8080:80 vulnerables/web-dvwa:latest`
3. **Run examples**: `poetry run python examples/01_basic_example.py`

## 📁 Available Examples

### Core Examples

| Example | Description | Prerequisites |
|---------|-------------|---------------|
| `01_basic_example.py` | Basic HTTP requests and security analysis | Internet connection |
| `02_dvwa_complete.py` | Complete DVWA workflow (check → setup → login → explore) | DVWA on localhost:8080 |
| `03_simple_exploits.py` | Basic exploit chains (SQL injection, XSS testing) | DVWA logged in |
| `08_dvwa_working_flow.py` | **COMPLETE WORKING DVWA WORKFLOW** | DVWA container |
| `04_dvwa_xss_complete.py` | Comprehensive XSS testing (Reflected, Stored, DOM) | DVWA setup |
| `05_xss_quick_demo.py` | Quick XSS demo with exploit URL generation | DVWA accessible |

### DVWA Testing Examples

| Example | Description | Purpose |
|---------|-------------|---------|
| `dvwa_real_test.py` | DVWA connectivity and form detection | Test setup and connectivity |
| `dvwa_auth_example.py` | DVWA authentication with admin/admin | Authentication flow demo |

## 🎯 DVWA Setup Guide

DVWA (Damn Vulnerable Web Application) is used for realistic testing:

```bash
# 1. Start DVWA container
docker run -d -p 8080:80 vulnerables/web-dvwa:latest

# 2. Setup database (visit in browser)
open http://localhost:8080/setup.php
# Click "Create / Reset Database"

# 3. Login credentials
Username: admin
Password: admin

# 4. Run examples
poetry run python examples/02_dvwa_complete.py
```

## 🔧 Running Examples

### Method 1: Poetry (Recommended)
```bash
poetry run python examples/01_basic_example.py
poetry run python examples/02_dvwa_complete.py
poetry run python examples/03_simple_exploits.py
```

### Method 2: Direct Python
```bash
cd /path/to/logicPWN
python -m examples.01_basic_example
python -m examples.02_dvwa_complete
python -m examples.03_simple_exploits
```

## 📊 Example Features Demonstrated

| Feature | Example Files | Description |
|---------|---------------|-------------|
| **Basic Requests** | `01_basic_example.py` | GET, POST, headers, data handling |
| **Security Analysis** | All examples | Automatic security pattern detection |
| **Authentication** | `02_dvwa_complete.py`, `dvwa_auth_example.py` | Form-based login, CSRF handling |
| **Session Management** | `02_dvwa_complete.py`, `03_simple_exploits.py` | Cookie handling, session persistence |
| **XSS Testing** | `03_simple_exploits.py`, `04_dvwa_xss_complete.py`, `05_xss_quick_demo.py` | Reflected, Stored, DOM XSS detection |
| **Exploit URL Generation** | `04_dvwa_xss_complete.py`, `05_xss_quick_demo.py` | Automated exploit URL creation |
| **SQL Injection** | `03_simple_exploits.py` | Basic SQL injection testing |
| **Response Analysis** | All examples | Content analysis, error detection |

## 🛡️ Security Testing Workflow

The examples demonstrate a complete security testing workflow:

```
1. Reconnaissance → 01_basic_example.py
2. Authentication → 02_dvwa_complete.py
3. Vulnerability Testing → 03_simple_exploits.py
4. Analysis & Reporting → Built into all examples
```

## 🔍 Troubleshooting

### Common Issues

**"Cannot connect to DVWA"**
```bash
# Check if DVWA is running
docker ps | grep dvwa
# If not running, start it
docker run -d -p 8080:80 vulnerables/web-dvwa:latest
```

**"Database needs setup"**
- Visit: http://localhost:8080/setup.php
- Click "Create / Reset Database"

**"Login failed"**
- Ensure database is setup
- Use credentials: admin/admin
- Check DVWA is accessible

**"Import errors"**
```bash
# Reinstall dependencies
poetry install
# Or check Python path
poetry run python -c "import logicpwn; print('OK')"
```

## 📚 Next Steps

After running these examples:

1. **Explore DVWA vulnerabilities**: SQL injection, XSS, CSRF, etc.
2. **Modify security levels**: Change DVWA security level and retest
3. **Build custom chains**: Combine multiple vulnerability tests
4. **Try other targets**: Test against your own applications
5. **Read the docs**: Check `/docs` for advanced features

## 🎯 Learning Path

**Beginner**: Start with `01_basic_example.py`
**Intermediate**: Progress to `02_dvwa_complete.py`
**Advanced**: Study `03_simple_exploits.py` and build custom chains

Each example includes detailed comments and error handling to help understand LogicPWN's capabilities.
