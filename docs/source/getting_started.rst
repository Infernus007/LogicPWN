Getting Started with LogicPwn
=============================

This comprehensive guide will help you get started with LogicPwn, from installation to your first exploit chain. Whether you're a security researcher, penetration tester, or developer, this guide covers everything you need to know.

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

Basic Authentication and Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start with a simple authentication and request example:

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

Build complex exploit chains with response validation and data extraction:

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
~~~~~~~~~~~~~~~~~~~~~~~~

Scale your testing with high-performance async execution:

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
----------------------

Monitor your testing performance and cache efficiency:

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
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

LogicPwn supports configuration via environment variables:

.. code-block:: bash

   export LOGICPWN_TIMEOUT=60
