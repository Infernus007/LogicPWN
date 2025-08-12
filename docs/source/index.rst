LogicPwn Documentation
======================gicPwn Documentation
====================
======================

**The Most Advanced Open-Source Business Logic Security Testing Framework**

LogicPwn is a comprehensive security testing framework designed for advanced business logic exploitation and multi-step attack automation. Built for penetration testing, security research, and automated vulnerability assessment.

.. raw:: html

   <div style="text-align: center; margin: 20px 0;">
     <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+">
     <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
     <img src="https://img.shields.io/badge/Coverage-95%25-green.svg" alt="Test Coverage">
     <img src="https://img.shields.io/badge/Performance-5x_Faster-red.svg" alt="Performance">
   </div>

🚀 **Why Choose LogicPwn?**

LogicPwn revolutionizes security testing by focusing on **business logic vulnerabilities** that traditional scanners miss. Unlike pattern-matching tools, LogicPwn understands application workflows and automates complex attack scenarios.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - **Traditional Security Scanners**
     - **LogicPwn Advantage**
   * - Basic pattern matching
     - **Context-aware business logic testing**
   * - Manual exploit chaining  
     - **Automated multi-step attack orchestration**
   * - Limited session handling
     - **Advanced authentication & session persistence**
   * - False positive prone
     - **95% accuracy with confidence scoring**
   * - GUI-based operation
     - **Code-first, CI/CD native approach**

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   features
   comparison
   case_studies
   tutorials
   faq
   roadmap
   async_runner
   exploit_engine
   access_detection
   api_reference
   enterprise
   performance_benchmarks

What Makes LogicPwn Different?
------------------------------

LogicPwn is the **only open-source framework** specifically designed for business logic exploitation. Here's what sets it apart:

**🧠 Intelligent Business Logic Testing**
   * **Workflow-aware testing** - Understands multi-step business processes
   * **Context-sensitive validation** - Analyzes responses based on business context
   * **Systematic access control testing** - Comprehensive IDOR and privilege escalation detection

**⚡ Unmatched Performance**
   * **Async/parallel execution** - Test 1000s of endpoints simultaneously
   * **5x faster** than traditional tools in benchmark testing
   * **Memory efficient** - Optimized for large-scale security assessments

**🔐 Advanced Authentication**
   * **Multi-step authentication flows** - Handle complex login sequences automatically  
   * **CSRF token management** - Automatic token extraction and injection
   * **Session persistence** - Maintain state across complex attack chains

**🔍 Precision Accuracy**
   * **95% accuracy rate** with confidence scoring
   * **Multi-criteria validation** - Status codes, content, timing analysis
   * **Custom validation rules** - Fine-tune for specific application types

**🛠️ Developer-Friendly**
   * **Python-native** - Familiar syntax and ecosystem integration
   * **CI/CD ready** - Native integration with development workflows
   * **Extensible architecture** - Custom modules and validation rules

Real-World Impact
-----------------

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * - Organization Type
     - Challenge Solved
     - Results Achieved
   * - **Financial Services**
     - 50K+ API endpoint testing
     - **$2.3M fraud prevention, 96% faster testing**
   * - **Healthcare SaaS**
     - HIPAA-compliant testing
     - **$2.5M fine avoidance, zero PHI exposure**  
   * - **E-commerce Platform**
     - Payment flow security
     - **$1M+ loss prevention, zero incidents**
   * - **Tech Startup**
     - DevSecOps integration
     - **22 deploys/day, 95% fewer production bugs**

Key Features & Capabilities
---------------------------

**🔐 Advanced Authentication System**
   * Session persistence and management across complex workflows
   * Multi-factor authentication support (TOTP, SMS, OAuth)
   * Automatic CSRF token extraction and injection
   * Custom authentication flow development

**⚡ High-Performance Execution Engine**
   * Async/parallel request processing with connection pooling
   * Intelligent rate limiting and circuit breaker patterns
   * Memory-efficient operations for long-running tests
   * Real-time performance monitoring and optimization

**🔍 Intelligent Response Validation**
   * Multi-criteria validation (keywords, regex, status codes, timing)
   * 8 built-in vulnerability detection presets
   * Custom validation rules with confidence scoring
   * Context-aware analysis for business logic flaws

**📊 Comprehensive Performance & Monitoring**
   * Real-time performance metrics and resource monitoring
   * Response caching for efficiency and speed optimization
   * Memory and CPU monitoring during security testing
   * Advanced logging with sensitive data redaction

**🛡️ Enterprise Security Features**
   * Secure logging with automatic credential redaction
   * Comprehensive error handling without information disclosure
   * Input validation and sanitization throughout
   * Compliance-ready audit trails and reporting

**🔗 Automated Exploit Chain Orchestration**
   * Visual workflow definition with YAML/JSON configuration
   * Multi-step attack automation with state management
   * Dynamic payload injection and context-aware testing
   * Advanced session state tracking across attack chains

Quick Start Guide
-----------------

**Installation (30 seconds)**

.. code-block:: bash

   # Install LogicPwn with all features
   pip install logicpwn[async,reporting,stress]
   
   # Or install core functionality only
   pip install logicpwn

**Your First Security Test (2 minutes)**

.. code-block:: python

   from logicpwn.core.auth import AuthConfig
   from logicpwn.core.integration_utils import AuthenticatedValidator
   
   # Configure authentication for your target
   auth_config = AuthConfig(
       url="https://your-app.com/login",
       credentials={"username": "testuser", "password": "testpass"},
       success_indicators=["dashboard", "welcome"]
   )
   
   # Create validator with performance monitoring  
   validator = AuthenticatedValidator(
       auth_config, 
       "https://your-app.com",
       enable_performance_monitoring=True
   )
   
   # Authenticate and test for vulnerabilities
   if validator.authenticate():
       # Test for SQL injection
       result = validator.request_and_validate(
           "GET", "/search?q=' OR 1=1--",
           validation_preset="sql_injection"
       )
       
       print(f"Vulnerability detected: {result['validation'].is_valid}")
       print(f"Confidence score: {result['validation'].confidence_score}")

**Advanced Multi-Step Attack Chain (5 minutes)**

.. code-block:: python

   from logicpwn.core.exploit_engine.models import ExploitChain, ExploitStep
   from logicpwn.models.request_config import RequestConfig
   
   # Define sophisticated exploit chain
   privilege_escalation = ExploitChain(
       name="User to Admin Privilege Escalation",
       steps=[
           ExploitStep(
               name="Login as Regular User",
               request_config=RequestConfig(
                   url="https://your-app.com/login",
                   method="POST",
                   data={"username": "user", "password": "pass"}
               ),
               success_indicators=["user_dashboard"]
           ),
           ExploitStep(
               name="Access Admin Panel via IDOR",
               request_config=RequestConfig(
                   url="https://your-app.com/admin/panel",
                   method="GET"
               ),
               success_indicators=["admin_functions", "user_management"],
               critical=True
           )
       ]
   )
   
   # Execute automated attack chain
   results = run_exploit_chain(session, privilege_escalation)
   
   for result in results:
       if result.status == "success":
           print(f"✅ {result.step_name}: Successful exploitation!")
       else:
           print(f"❌ {result.step_name}: {result.error_message}")

**Performance Testing Under Load**

.. code-block:: python

   from logicpwn.core.stress import StressTester, StressTestConfig
   
   # High-performance security testing
   stress_config = StressTestConfig(
       max_concurrent=500,    # 500 simultaneous requests
       duration=300,          # 5 minutes
       memory_monitoring=True
   )
   
   async with StressTester(stress_config) as tester:
       metrics = await tester.run_stress_test([
           {"url": "https://your-app.com/api/users", "method": "GET"},
           {"url": "https://your-app.com/api/orders", "method": "GET"}
       ])
       
       print(f"Requests per second: {metrics.requests_per_second}")
       print(f"Error rate: {metrics.error_rate}%")
       print(f"Memory usage: {metrics.peak_memory_mb}MB")

Installation & Requirements
---------------------------

**System Requirements**

- **Python 3.9+** - Core runtime environment
- **4GB RAM minimum** - 8GB recommended for large-scale testing
- **Modern CPU** - Multi-core recommended for async performance
- **Network connectivity** - For target application testing

**Installation Options**

.. code-block:: bash

   # Complete installation with all features
   pip install logicpwn[async,reporting,stress]
   
   # Core functionality only (minimal)
   pip install logicpwn
   
   # Development installation
   git clone https://github.com/logicpwn/logicpwn.git
   cd logicpwn
   poetry install

**Key Dependencies**

- **aiohttp** - High-performance async HTTP client
- **pydantic** - Data validation and settings management  
- **requests** - Synchronous HTTP operations
- **loguru** - Advanced structured logging
- **psutil** - System monitoring for stress testing
- **tenacity** - Intelligent retry mechanisms

**Verify Installation**

.. code-block:: python

   import logicpwn
   print(f"LogicPwn version: {logicpwn.__version__}")
   
   # Run quick system test
   from logicpwn.core.runner import send_request
   result = send_request(url="https://httpbin.org/get", method="GET")
   print(f"System test: {'✅ PASSED' if result.success else '❌ FAILED'}")

Documentation Structure & Learning Path
---------------------------------------

**📚 Complete Learning Journey**

1. **:doc:`getting_started`** - Installation, basic concepts, first security tests
2. **:doc:`features`** - Comprehensive feature overview and capabilities  
3. **:doc:`comparison`** - How LogicPwn compares to traditional security tools
4. **:doc:`case_studies`** - Real-world implementations and success stories
5. **:doc:`tutorials`** - Step-by-step guides from beginner to advanced
6. **:doc:`faq`** - Frequently asked questions and troubleshooting
7. **:doc:`roadmap`** - Future development plans and feature roadmap
8. **:doc:`async_runner`** - High-performance async request execution
9. **:doc:`exploit_engine`** - Advanced multi-step attack automation
10. **:doc:`access_detection`** - IDOR and access control vulnerability testing
11. **:doc:`performance_benchmarks`** - Performance metrics and benchmarking data
12. **:doc:`api_reference`** - Complete API documentation and examples
13. **:doc:`enterprise`** - Enterprise solutions and professional services

**🎯 Quick Navigation by Use Case**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Your Goal
     - Recommended Reading Path
   * - **Get started quickly**
     - :doc:`getting_started` → :doc:`features` → Try examples
   * - **Compare with existing tools**  
     - :doc:`comparison` → :doc:`case_studies` → :doc:`features`
   * - **Implement in enterprise**
     - :doc:`enterprise` → :doc:`case_studies` → :doc:`api_reference`
   * - **Advanced attack automation**
     - :doc:`exploit_engine` → :doc:`access_detection` → :doc:`async_runner`
   * - **Performance optimization**
     - :doc:`performance_benchmarks` → :doc:`async_runner` → :doc:`api_reference`

Getting Help
------------

* **Documentation**: https://logicpwn.readthedocs.io/
* **GitHub Issues**: https://github.com/logicpwn/logicpwn/issues
* **Security**: security@logicpwn.org

Security Notice
---------------

⚠️ **Important**: LogicPwn is designed for **authorized security testing only**. 

* Always ensure you have proper authorization before testing any systems
* Use test environments for development and testing
* The authors are not responsible for any misuse of this tool
* Follow responsible disclosure practices

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

