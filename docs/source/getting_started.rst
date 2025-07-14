Getting Started with LogicPwn
=============================

This comprehensive guide will help you get started with LogicPwn, from installation to your first exploit chain. Whether you're a security researcher, penetration tester, or developer, this guide covers everything you need to know.

Installation
------------

LogicPwn requires Python 3.9+ and can be installed via pip:

.. code-block:: bash

   pip install logicpwn

For development installation:

.. code-block:: bash

   git clone https://github.com/logicpwn/logicpwn.git
   cd logicpwn
   poetry install

Verify Installation
~~~~~~~~~~~~~~~~~~~

Test that LogicPwn is installed correctly:

.. code-block:: python

   import logicpwn
   print(logicpwn.__version__)

   # Test basic functionality
   from logicpwn.core import authenticate_session, send_request
   print("✅ LogicPwn installed successfully!")

Quick Start
-----------

Basic Authentication and Request (httpbin.org)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start with a simple authentication and request example using httpbin.org (no real authentication required):

.. code-block:: python

   from logicpwn.core import authenticate_session, send_request

   # For httpbin, credentials are not required, but the schema expects a dict
   auth_config = {
       "url": "https://httpbin.org/get",
       "method": "GET",
       "credentials": {},
       "success_indicators": ["url"]
   }

   session = authenticate_session(auth_config)
   response = send_request(session, {
       "url": "https://httpbin.org/get",
       "method": "GET"
   })

   print(f"Status: {response.status_code}")
   print(f"Content: {response.text[:200]}...")

POST Request Example (reqres.in)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Demonstrate a POST request with JSON data using reqres.in:

.. code-block:: python

   from logicpwn.core import authenticate_session, send_request

   auth_config = {
       "url": "https://reqres.in/api/login",
       "method": "POST",
       "credentials": {"email": "eve.holt@reqres.in", "password": "cityslicka"},
       "success_indicators": ["token"]
   }

   session = authenticate_session(auth_config)
   response = send_request(session, {
       "url": "https://reqres.in/api/users",
       "method": "POST",
       "json_data": {"name": "morpheus", "job": "leader"}
   })

   print(f"Status: {response.status_code}")
   print(f"Content: {response.text[:200]}...")

Advanced Exploit Chaining
~~~~~~~~~~~~~~~~~~~~~~~~~

Build complex exploit chains with response validation and data extraction (using httpbin.org):

.. code-block:: python

   from logicpwn.core import authenticate_session, send_request

   # Step 1: Authenticate (no real auth needed for httpbin)
   auth_config = {
       "url": "https://httpbin.org/get",
       "method": "GET",
       "credentials": {},
       "success_indicators": ["url"]
   }
   session = authenticate_session(auth_config)

   # Step 2: Access another endpoint
   response = send_request(session, {
       "url": "https://httpbin.org/uuid",
       "method": "GET"
   })

   if response.status_code == 200:
       print("Chained request successful!")
       print(f"UUID: {response.json().get('uuid')}")

Async/Parallel Execution (httpbin.org)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Async support is included by default. You do not need to install any extras.

Scale your testing with high-performance async execution:

.. code-block:: python

   import asyncio
   from logicpwn.core import AsyncSessionManager

   auth_config = {
       "url": "https://httpbin.org/get",
       "method": "GET",
       "credentials": {},
       "success_indicators": ["url"]
   }

   async def main():
       async with AsyncSessionManager(auth_config=auth_config) as manager:
           await manager.authenticate()
           request_configs = [
               {"url": "https://httpbin.org/get", "method": "GET"},
               {"url": "https://httpbin.org/uuid", "method": "GET"},
               {"url": "https://httpbin.org/ip", "method": "GET"}
           ]
           results = await manager.send_requests_batch(request_configs)
           for i, result in enumerate(results):
               print(f"Request {i+1}: {result.status_code} - {result.text[:100]}")

   asyncio.run(main())

Performance Monitoring
----------------------

Monitor your testing performance and cache efficiency:

.. code-block:: python

   from logicpwn.core import (
       authenticate_session, 
       send_request,
       get_performance_summary,
       get_cache_stats
   )

   auth_config = {
       "url": "https://httpbin.org/get",
       "method": "GET",
       "credentials": {},
       "success_indicators": ["url"]
   }
   session = authenticate_session(auth_config)
   response = send_request(session, {"url": "https://httpbin.org/get", "method": "GET"})

   # Get performance metrics
   performance = get_performance_summary()
   cache_stats = get_cache_stats()

   print(f"Total operations: {performance.get('total_operations', 0)}")
   print(f"Average duration: {performance.get('average_duration', 0):.3f}s")
   print(f"Cache hit rate: {cache_stats['response_cache']['hit_rate']:.1f}%")

IDOR & Access Control Detection
------------------------------

Detect insecure direct object references (IDOR) and access control flaws with LogicPwn's access detector module. (For demonstration, use httpbin.org endpoints, but note that real IDOR testing requires a real application with user-specific resources.)

.. code-block:: python

   from logicpwn.core.access.detector import detect_idor_flaws
   from logicpwn.core.access.models import AccessDetectorConfig
   import requests

   # Simulate an authenticated session (no real auth needed for httpbin)
   session = requests.Session()

   # The endpoint template with an {id} placeholder (httpbin doesn't use IDs, so this is illustrative)
   endpoint_template = "https://httpbin.org/anything/{id}"

   # IDs to test
   test_ids = ["1", "2", "3"]

   # Indicators for access granted/denied (httpbin always grants, so this is for demo)
   success_indicators = ["url"]
   failure_indicators = ["error"]

   config = AccessDetectorConfig(
       current_user_id="1",
       authorized_ids=["1"],
       unauthorized_ids=["2", "3"],
       compare_unauthenticated=True
   )

   results = detect_idor_flaws(
       session,
       endpoint_template,
       test_ids,
       success_indicators,
       failure_indicators,
       config
   )

   for result in results:
       print(f"Tested ID: {result.id_tested}")
       print(f"  Access granted: {result.access_granted}")
       print(f"  Vulnerability detected: {result.vulnerability_detected}")
       print(f"  Status code: {result.status_code}")
       print(f"  Error: {result.error_message}")
       print()

# Output will show which IDs are vulnerable to unauthorized access (for httpbin, all will be accessible).

See Also
--------

For advanced exploit automation, multi-step chain orchestration, and config-driven attack chaining, see :doc:`exploit_engine`.

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

LogicPwn supports configuration via environment variables. These are loaded automatically at startup and override defaults if set.

.. code-block:: bash

   export LOGICPWN_TIMEOUT=60
   export LOGICPWN_LOG_LEVEL=DEBUG

# Supported variables include LOGICPWN_TIMEOUT, LOGICPWN_MAX_RETRIES, LOGICPWN_VERIFY_SSL, LOGICPWN_SESSION_TIMEOUT, and more.
