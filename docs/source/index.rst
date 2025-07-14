LogicPwn Documentation
======================

LogicPwn is a comprehensive security testing framework designed for advanced business logic exploitation and multi-step attack automation. Built for penetration testing, security research, and automated vulnerability assessment.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   async_runner
   api_reference
   # Add a reference to the new IDOR & Access Control Detection section
   (see getting_started for usage example)

What is LogicPwn?
-----------------

LogicPwn is a powerful Python framework for **business logic exploitation** and **exploit chaining automation**. It's designed for security professionals who need to:

* **Automate complex attack chains** with persistent sessions
* **Test business logic vulnerabilities** systematically  
* **Scale security testing** with async/parallel execution
* **Validate responses** with advanced pattern matching
* **Monitor performance** and cache results for efficiency

Key Features
------------

**🔐 Advanced Authentication**
   * Session persistence and management
   * Multi-step authentication workflows
   * Secure credential handling with redaction

**⚡ High-Performance Execution**
   * Async/parallel request processing
   * Connection pooling and rate limiting
   * Batch request execution

**🔍 Intelligent Response Validation**
   * Multi-criteria validation (keywords, regex, status codes)
   * Vulnerability pattern detection
   * Data extraction with regex patterns
   * Confidence scoring for validation results

**📊 Performance & Monitoring**
   * Real-time performance metrics
   * Response caching for efficiency
   * Memory and CPU monitoring
   * Comprehensive logging with security

**🛡️ Security-First Design**
   * Secure logging with data redaction
   * Comprehensive error handling
   * Input validation and sanitization
   * Rate limiting and throttling

Quick Start
-----------

Install LogicPwn:

.. code-block:: bash

   pip install logicpwn[async]

Basic usage:

.. code-block:: python

   from logicpwn.core import authenticate_session, send_request
   
   # Configure authentication
   auth_config = {
       "url": "https://target.com/login",
       "credentials": {"username": "admin", "password": "secret"},
       "success_indicators": ["dashboard", "welcome"]
   }
   
   # Authenticate and chain exploits
   session = authenticate_session(auth_config)
   response = session.get("https://target.com/admin/panel")
   print(f"Status: {response.status_code}")

Advanced async execution:

.. code-block:: python

   import asyncio
   from logicpwn.core import AsyncSessionManager
   
   async def exploit_chain():
       async with AsyncSessionManager() as manager:
           await manager.authenticate(auth_config)
           results = await manager.send_requests_batch(request_configs)
           for result in results:
               print(f"Request: {result.status_code}")
   
   asyncio.run(exploit_chain())

Installation
------------

LogicPwn requires Python 3.9+ and can be installed via pip:

.. code-block:: bash

   pip install logicpwn[async]

For development installation:

.. code-block:: bash

   git clone https://github.com/logicpwn/logicpwn.git
   cd logicpwn
   poetry install

Requirements
------------

* **Python 3.9+** - Core runtime
* **aiohttp** - Async HTTP client (for async functionality)
* **pydantic** - Data validation and settings management
* **requests** - Synchronous HTTP client
* **loguru** - Advanced logging
* **psutil** - System monitoring (for stress testing)

Documentation Structure
-----------------------

* :doc:`getting_started` - Complete installation and usage guide
* :doc:`async_runner` - High-performance async request execution
* :doc:`api_reference` - Complete API documentation and examples

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

