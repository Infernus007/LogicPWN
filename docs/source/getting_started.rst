Getting Started
==============

This guide will help you get started with LogicPwn, from installation to your first exploit chain.

Installation
-----------

Prerequisites
------------

Basic Installation
-----------------

Install LogicPwn using pip:

.. code-block:: bash

   pip install logicpwn

For async functionality (recommended):

.. code-block:: bash

   pip install logicpwn[async]

Development Installation
----------------------

Clone the repository and install in development mode:

.. code-block:: bash

   git clone https://github.com/logicpwn/logicpwn.git
   cd logicpwn
   poetry install

Verify Installation
-----------------

Test that LogicPwn is installed correctly:

.. code-block:: python

   import logicpwn
   print(logicpwn.__version__)

Basic Usage
----------

Simple Request
-------------

Send a basic HTTP request:

.. code-block:: python

   from logicpwn.core import send_request
   from logicpwn.models import RequestResult
   
   # Send a GET request
   result = send_request(
       url="https://httpbin.org/get",
       method="GET",
       headers={"User-Agent": "LogicPwn/1.0"}
   )
   
   print(f"Status: {result.status_code}")
   print(f"Response: {result.body}")

POST Request with Data
--------------------

Send a POST request with form data:

.. code-block:: python

   result = send_request(
       url="https://httpbin.org/post",
       method="POST",
       data={"username": "admin", "password": "secret123"},
       headers={"Content-Type": "application/x-www-form-urlencoded"}
   )

JSON Request
-----------

Send a request with JSON data:

.. code-block:: python

   result = send_request(
       url="https://httpbin.org/post",
       method="POST",
       json_data={"action": "login", "credentials": {"user": "admin"}},
       headers={"Content-Type": "application/json"}
   )

Authentication
-------------

Basic Authentication
------------------

Authenticate with a target system:

.. code-block:: python

   from logicpwn.core import authenticate_session, AuthConfig
   
   # Configure authentication
   auth_config = AuthConfig(
       login_url="https://target.com/login",
       credentials={"username": "admin", "password": "secret123"},
       method="POST"
   )
   
   # Authenticate and get session
   session = authenticate_session(auth_config)
   
   # Use authenticated session
   response = session.get("https://target.com/admin/panel")
   print(f"Admin panel status: {response.status_code}")

Session Management
-----------------

Work with persistent sessions:

.. code-block:: python

   # Validate session is still active
   if validate_session(session):
       print("Session is valid")
   else:
       print("Session expired, re-authenticating")
       session = authenticate_session(auth_config)

Async Requests
-------------

Single Async Request
------------------

Send async requests for better performance:

.. code-block:: python

   import asyncio
   from logicpwn.core import send_request_async
   
   async def main():
       result = await send_request_async(
           url="https://httpbin.org/get",
           method="GET"
       )
       print(f"Async result: {result.status_code}")
   
   asyncio.run(main())

Batch Async Requests
-------------------

Send multiple requests concurrently:

.. code-block:: python

   import asyncio
   from logicpwn.core import send_requests_batch_async
   
   async def main():
       request_configs = [
           {"url": "https://httpbin.org/get", "method": "GET"},
           {"url": "https://httpbin.org/post", "method": "POST", "json_data": {"test": "data"}},
           {"url": "https://httpbin.org/put", "method": "PUT", "json_data": {"update": "value"}}
       ]
       
       results = await send_requests_batch_async(request_configs, max_concurrent=5)
       
       for i, result in enumerate(results):
           print(f"Request {i+1}: {result.status_code}")
   
   asyncio.run(main())

Async Session Management
----------------------

Use async sessions for high-performance exploit chaining:

.. code-block:: python

   import asyncio
   from logicpwn.core import AsyncSessionManager
   
   async def main():
       auth_config = {
           "url": "https://target.com/login",
           "method": "POST",
           "credentials": {"username": "admin", "password": "secret123"}
       }
       
       async with AsyncSessionManager(auth_config=auth_config) as session:
           # Authenticated requests
           result1 = await session.get("https://target.com/api/users")
           result2 = await session.post("https://target.com/api/admin", json_data={"action": "exploit"})
           
           print(f"Users API: {result1.status_code}")
           print(f"Admin API: {result2.status_code}")
   
   asyncio.run(main())

Configuration
------------

Environment Variables
-------------------

LogicPwn can be configured via environment variables:

.. code-block:: bash

   export LOGICPWN_TIMEOUT=30
   export LOGICPWN_MAX_RETRIES=3
   export LOGICPWN_LOG_LEVEL=INFO
   export LOGICPWN_ENABLE_SESSION_PERSISTENCE=true

Configuration File
-----------------

Create a configuration file for persistent settings:

.. code-block:: python

   from logicpwn.core.config import config
   
   # Set configuration values
   config.set_timeout(30)
   config.set_max_retries(5)
   config.set_log_level("DEBUG")
   
   # Save configuration
   config.save()

Logging
-------

Basic Logging
------------

LogicPwn provides comprehensive logging:

.. code-block:: python

   from logicpwn.core import log_info, log_error, log_debug
   
   log_info("Starting exploit chain", {"target": "https://target.com"})
   log_debug("Sending request", {"url": "https://target.com/api/data"})
   log_error("Request failed", {"status_code": 500})

Secure Logging
-------------

Sensitive data is automatically redacted:

.. code-block:: python

   # Password will be redacted in logs
   result = send_request(
       url="https://target.com/login",
       method="POST",
       data={"username": "admin", "password": "secret123"}
   )

Middleware
---------

Using Middleware
--------------

LogicPwn includes a middleware system for extensibility:

.. code-block:: python

   from logicpwn.core import add_middleware, AuthenticationMiddleware, RetryMiddleware
   
   # Add authentication middleware
   auth_middleware = AuthenticationMiddleware()
   add_middleware(auth_middleware)
   
   # Add retry middleware
   retry_middleware = RetryMiddleware(max_retries=3)
   add_middleware(retry_middleware)

Custom Middleware
----------------

Create custom middleware for specific needs:

.. code-block:: python

   from logicpwn.core import BaseMiddleware, MiddlewareContext
   
   class CustomMiddleware(BaseMiddleware):
       def __init__(self, name="CustomMiddleware"):
           super().__init__(name)
       
       def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
           # Add custom headers
           context.headers["X-Custom-Header"] = "LogicPwn"
           return context
       
       def process_response(self, context: MiddlewareContext, response: Any) -> Any:
           # Process response
           return response

Error Handling
-------------

Exception Handling
-----------------

Handle different types of errors:

.. code-block:: python

   from logicpwn.exceptions import NetworkError, ValidationError, TimeoutError
   
   try:
       result = send_request(url="https://target.com/api/data")
   except NetworkError as e:
       print(f"Network error: {e}")
   except ValidationError as e:
       print(f"Validation error: {e}")
   except TimeoutError as e:
       print(f"Timeout error: {e}")

Response Analysis
----------------

Analyze responses for security issues:

.. code-block:: python

   result = send_request(url="https://target.com/api/data")
   
   if result.has_vulnerabilities:
       print("Security vulnerabilities detected!")
       print(f"Sensitive data: {result.security_analysis.has_sensitive_data}")
       print(f"Error messages: {result.security_analysis.error_messages}")

Next Steps
----------

* Explore :doc:`async_runner` for high-performance async functionality
* Review the :doc:`api_reference` for complete API documentation

Troubleshooting
--------------

Common Issues
------------

**Import Error**: Make sure LogicPwn is installed correctly:

.. code-block:: bash

   pip install --upgrade logicpwn

**Async Import Error**: Install async dependencies:

.. code-block:: bash

   pip install aiohttp

**Configuration Error**: Check environment variables and configuration:

.. code-block:: python

   from logicpwn.core.config import config
   print(config.get_timeout())
   print(config.get_log_level())

Getting Help
-----------

* Check the :doc:`api_reference` for detailed API documentation
* Open an issue on GitHub for bugs or feature requests
* Join the community discussions for support 