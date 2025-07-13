Getting Started with LogicPwn
============================

This guide will help you get started with LogicPwn, from installation to your first exploit chain.

Installation
-----------

LogicPwn requires Python 3.9+ and can be installed via pip:

.. code-block:: bash

   pip install logicpwn[async]

For development installation:

.. code-block:: bash

   git clone https://github.com/logicpwn/logicpwn.git
   cd logicpwn
   poetry install

Quick Start
----------

Basic Authentication and Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logicpwn.core import authenticate_session, send_request
   
   # Configure authentication
   auth_config = {
       "url": "https://target.com/login",
       "credentials": {"username": "admin", "password": "secret"},
       "success_indicators": ["dashboard", "welcome"]
   }
   
   # Authenticate and get session
   session = authenticate_session(auth_config)
   
   # Send authenticated request
   response = send_request(session, {
       "url": "https://target.com/admin/panel",
       "method": "GET"
   })
   
   print(f"Status: {response.status_code}")
   print(f"Content: {response.text[:200]}...")

Advanced Exploit Chaining
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logicpwn.core import (
       authenticate_session, 
       send_request, 
       validate_response,
       extract_from_response
   )
   
   # Step 1: Authenticate
   session = authenticate_session(auth_config)
   
   # Step 2: Access admin panel
   admin_response = send_request(session, {
       "url": "https://target.com/admin/panel",
       "method": "GET"
   })
   
   # Step 3: Validate response
   is_admin = validate_response(
       admin_response,
       success_criteria=["admin", "privileged"],
       regex_patterns=[r"user_id:\s*(\d+)"]
   )
   
   if is_admin:
       # Step 4: Extract user ID for next exploit
       user_ids = extract_from_response(
           admin_response, 
           r"user_id:\s*(\d+)"
       )
       
       # Step 5: Exploit user ID
       for user_id in user_ids:
           exploit_response = send_request(session, {
               "url": f"https://target.com/api/users/{user_id}/delete",
               "method": "POST"
           })
           print(f"Exploited user {user_id}")

Async/Parallel Execution
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from logicpwn.core import AsyncSessionManager
   
   async def exploit_chain():
       async with AsyncSessionManager() as manager:
           # Authenticate
           await manager.authenticate(auth_config)
           
           # Send multiple requests in parallel
           request_configs = [
               {"url": "https://target.com/api/users", "method": "GET"},
               {"url": "https://target.com/api/admin", "method": "GET"},
               {"url": "https://target.com/api/settings", "method": "GET"}
           ]
           
           results = await manager.send_requests_batch(request_configs)
           
           for i, result in enumerate(results):
               print(f"Request {i+1}: {result.status_code}")
   
   # Run the exploit chain
   asyncio.run(exploit_chain())

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logicpwn.core import (
       authenticate_session, 
       send_request,
       get_performance_summary,
       get_cache_stats
   )
   
   # Your exploit chain here...
   session = authenticate_session(auth_config)
   response = send_request(session, {"url": "https://target.com/api/data"})
   
   # Get performance metrics
   performance = get_performance_summary()
   cache_stats = get_cache_stats()
   
   print(f"Total operations: {performance.get('total_operations', 0)}")
   print(f"Average duration: {performance.get('average_duration', 0):.3f}s")
   print(f"Cache hit rate: {cache_stats['response_cache']['hit_rate']:.1f}%")

Configuration
------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

LogicPwn supports configuration via environment variables:

.. code-block:: bash

   export LOGICPWN_TIMEOUT=60
   export LOGICPWN_MAX_RETRIES=5
   export LOGICPWN_LOG_LEVEL=DEBUG
   export LOGICPWN_ENABLE_REQUEST_LOGGING=true

Configuration File
~~~~~~~~~~~~~~~~~

Create a configuration file for your project:

.. code-block:: python

   # config.py
   from logicpwn.core.config import config
   
   # Update default settings
   config.update_config(
       TIMEOUT=60,
       MAX_RETRIES=5,
       VERIFY_SSL=False  # For testing environments
   )

Best Practices
-------------

Security Considerations
~~~~~~~~~~~~~~~~~~~~~

1. **Always get authorization** before testing any systems
2. **Use test environments** for development and testing
3. **Secure credential storage** - never hardcode credentials
4. **Monitor rate limits** to avoid being blocked
5. **Log responsibly** - avoid logging sensitive data

Performance Tips
~~~~~~~~~~~~~~~

1. **Use caching** for repeated requests
2. **Implement rate limiting** for large-scale testing
3. **Use async execution** for parallel operations
4. **Monitor memory usage** for long-running chains
5. **Clean up sessions** after use

Error Handling
~~~~~~~~~~~~~

.. code-block:: python

   from logicpwn.exceptions import (
       AuthenticationError,
       NetworkError,
       ValidationError
   )
   
   try:
       session = authenticate_session(auth_config)
       response = send_request(session, request_config)
   except AuthenticationError as e:
       print(f"Authentication failed: {e}")
   except NetworkError as e:
       print(f"Network error: {e}")
   except ValidationError as e:
       print(f"Configuration error: {e}")

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Authentication Fails**
- Check credentials and success indicators
- Verify URL format and accessibility
- Check for rate limiting or IP blocking

**Network Errors**
- Verify target is accessible
- Check SSL certificate issues
- Ensure proper proxy configuration

**Performance Issues**
- Enable caching for repeated requests
- Use async execution for parallel operations
- Monitor memory usage

**Validation Errors**
- Check configuration format
- Verify required fields are present
- Ensure proper data types

Getting Help
-----------

* **Documentation**: https://logicpwn.readthedocs.io/
* **GitHub Issues**: https://github.com/logicpwn/logicpwn/issues
* **Security**: security@logicpwn.org

Next Steps
----------

* Read the :doc:`async_runner` guide for high-performance execution
* Check the :doc:`api_reference` for complete API documentation
* Explore the examples directory for more use cases 