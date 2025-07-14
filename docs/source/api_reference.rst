API Reference
=============

This section provides comprehensive API documentation for all LogicPwn modules, classes, and functions.

.. contents:: Table of Contents
   :depth: 2
   :local:

Core Modules
------------

Authentication Module
~~~~~~~~~~~~~~~~~~~~~

The authentication module provides session management and authentication capabilities.

.. automodule:: logicpwn.core.auth
   :members:
   :undoc-members:
   :show-inheritance:

**Key Functions:**

* ``authenticate_session()`` - Authenticate and return a session
* ``validate_session()`` - Validate if a session is still active
* ``logout_session()`` - Properly logout and clean up session

**Configuration:**

* ``AuthConfig`` - Configuration model for authentication

Request Runner Module
~~~~~~~~~~~~~~~~~~~~~

The request runner module handles HTTP request execution with advanced features.

.. automodule:: logicpwn.core.runner
   :members:
   :undoc-members:
   :show-inheritance:

**Key Functions:**

* ``send_request()`` - Send authenticated requests
* ``send_request_advanced()`` - Advanced request with full configuration

**Configuration:**

* ``RequestConfig`` - Configuration model for requests

Response Validator Module
~~~~~~~~~~~~~~~~~~~~~~~~~

The validator module provides comprehensive response validation and analysis.

.. automodule:: logicpwn.core.validator
   :members:
   :undoc-members:
   :show-inheritance:

**Key Functions:**

* ``validate_response()`` - Validate responses with multiple criteria
* ``extract_from_response()`` - Extract data using regex patterns
* ``chain_validations()`` - Execute validation chains
* ``validate_json_response()`` - Validate JSON responses
* ``validate_html_response()`` - Validate HTML responses

**Classes:**

* ``ValidationResult`` - Structured validation results
* ``ValidationConfig`` - Validation configuration
* ``VulnerabilityPatterns`` - Pre-defined vulnerability patterns

Async Runner Module
~~~~~~~~~~~~~~~~~~~

The async runner provides high-performance async request execution.

.. automodule:: logicpwn.core.async_runner
   :members:
   :undoc-members:
   :show-inheritance:

**Key Classes:**

* ``AsyncRequestRunner`` - High-performance async request execution
* ``AsyncSessionManager`` - Async session management with authentication

**Key Functions:**

* ``send_request_async()`` - Single async request
* ``send_requests_batch_async()`` - Batch async requests
* ``async_session_manager()`` - Async context manager

Performance Module
~~~~~~~~~~~~~~~~~~

The performance module provides monitoring and benchmarking capabilities.

.. automodule:: logicpwn.core.performance
   :members:
   :undoc-members:
   :show-inheritance:

**Key Classes:**

* ``PerformanceMonitor`` - Real-time performance monitoring
* ``PerformanceBenchmark`` - Performance benchmarking
* ``MemoryProfiler`` - Memory usage profiling

**Key Functions:**

* ``monitor_performance()`` - Performance monitoring decorator
* ``performance_context()`` - Performance context manager
* ``get_performance_summary()`` - Get performance metrics

Cache Module
~~~~~~~~~~~~

The cache module provides efficient caching for requests and sessions.

.. automodule:: logicpwn.core.cache
   :members:
   :undoc-members:
   :show-inheritance:

**Key Classes:**

* ``CacheManager`` - Generic cache management
* ``ResponseCache`` - HTTP response caching
* ``SessionCache`` - Session caching

**Key Functions:**

* ``get_cache_stats()`` - Get cache statistics
* ``clear_all_caches()`` - Clear all caches

Configuration Module
~~~~~~~~~~~~~~~~~~~~

The configuration module manages settings and defaults.

.. automodule:: logicpwn.core.config
   :members:
   :undoc-members:
   :show-inheritance:

**Key Functions:**

* ``get_timeout()`` - Get request timeout
* ``get_max_retries()`` - Get maximum retries

Utilities Module
~~~~~~~~~~~~~~~~

The utilities module provides shared functionality.

.. automodule:: logicpwn.core.utils
   :members:
   :undoc-members:
   :show-inheritance:

**Key Functions:**

* ``check_indicators()`` - Check response indicators
* ``prepare_request_kwargs()`` - Prepare request parameters
* ``validate_config()`` - Validate configuration

Logging Module
~~~~~~~~~~~~~~

The logging module provides secure logging capabilities.

.. automodule:: logicpwn.core.logging_utils
   :members:
   :undoc-members:
   :show-inheritance:

**Key Functions:**

* ``log_request()`` - Log request information
* ``log_response()`` - Log response information
* ``log_info()``, ``log_warning()``, ``log_error()`` - Log levels

Stress Testing Module
~~~~~~~~~~~~~~~~~~~~~

The stress testing module provides load testing capabilities.
