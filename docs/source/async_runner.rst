Async Request Execution
================================
======================

LogicPwn provides high-performance async request execution capabilities using aiohttp for concurrent request handling. This module is designed for large-scale security testing and exploit chaining scenarios.

Overview
--------

The async functionality includes:

* **AsyncRequestRunner**: High-performance async HTTP request execution
* **AsyncSessionManager**: Async session management with authentication
* **Batch Processing**: Concurrent request execution
* **Rate Limiting**: Configurable request rate limiting
* **Connection Pooling**: Efficient connection management
* **Error Handling**: Comprehensive async error handling

AsyncRequestRunner
-------------------
-----------------

The AsyncRequestRunner provides high-performance async HTTP request execution with connection pooling and rate limiting.

Basic Usage
----------

.. code-block:: python

   import asyncio
   from logicpwn.core import AsyncRequestRunner
   
   async def main():
       async with AsyncRequestRunner() as runner:
           result = await runner.send_request(
               url="https://httpbin.org/get",
               method="GET",
               headers={"User-Agent": "LogicPwn-Async/1.0"}
           )
           print(f"Status: {result.status_code}")
           print(f"Response: {result.body}")
   
   asyncio.run(main())

Configuration
------------

Configure the AsyncRequestRunner with custom settings:

.. code-block:: python

   async with AsyncRequestRunner(
       max_concurrent=10,      # Maximum concurrent requests
       rate_limit=5.0,         # Requests per second
       timeout=30,             # Request timeout
       verify_ssl=False        # SSL verification
   ) as runner:
       # Use runner...

Batch Requests
-------------

Send multiple requests concurrently:

.. code-block:: python

   async with AsyncRequestRunner(max_concurrent=5) as runner:
       request_configs = [
           {"url": "https://api1.example.com", "method": "GET"},
           {"url": "https://api2.example.com", "method": "POST", "json_data": {"test": "data"}},
           {"url": "https://api3.example.com", "method": "PUT", "json_data": {"update": "value"}}
       ]
       
       results = await runner.send_requests_batch(request_configs)
       
       for i, result in enumerate(results):
           print(f"Request {i+1}: {result.status_code}")

Request Types
------------

**GET Request**:

.. code-block:: python

   result = await runner.send_request(
       url="https://api.example.com/data",
       method="GET",
       params={"page": 1, "limit": 10}
   )

**POST with Form Data**:

.. code-block:: python

   result = await runner.send_request(
       url="https://api.example.com/login",
       method="POST",
       data={"username": "admin", "password": "secret123"}
   )

**POST with JSON**:

.. code-block:: python

   result = await runner.send_request(
       url="https://api.example.com/api/users",
       method="POST",
       json_data={"name": "John", "email": "john@example.com"}
   )

**PUT Request**:

.. code-block:: python

   result = await runner.send_request(
       url="https://api.example.com/api/users/123",
       method="PUT",
       json_data={"name": "John Updated", "email": "john.updated@example.com"}
   )

**DELETE Request**:

.. code-block:: python

   result = await runner.send_request(
       url="https://api.example.com/api/users/123",
       method="DELETE"
   )

Error Handling
-------------

Handle different types of async errors:

.. code-block:: python

   from logicpwn.exceptions import NetworkError, TimeoutError
   
   try:
       result = await runner.send_request(url="https://api.example.com/data")
   except asyncio.TimeoutError:
       print("Request timed out")
   except aiohttp.ClientError as e:
       print(f"Network error: {e}")

AsyncSessionManager
------------------

The AsyncSessionManager provides async session management with authentication and session persistence.

Basic Usage
----------

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
           # Session is automatically authenticated
           result = await session.get("https://target.com/api/data")
           print(f"Authenticated request: {result.status_code}")
   
   asyncio.run(main())

Authentication Configuration
-------------------------

Configure authentication with various options:

.. code-block:: python

   auth_config = {
       "url": "https://target.com/login",
       "method": "POST",
       "credentials": {
           "username": "admin",
           "password": "secret123"
       },
       "headers": {
           "Content-Type": "application/x-www-form-urlencoded",
           "User-Agent": "LogicPwn/1.0"
       }
   }
   
   async with AsyncSessionManager(auth_config=auth_config) as session:
       # Use authenticated session...

Session Methods
--------------

**GET Request**:

.. code-block:: python

   result = await session.get(
       "https://target.com/api/users",
       headers={"Accept": "application/json"}
   )

**POST Request**:

.. code-block:: python

   result = await session.post(
       "https://target.com/api/users",
       data={"name": "John", "email": "john@example.com"}
   )

**PUT Request**:

.. code-block:: python

   result = await session.put(
       "https://target.com/api/users/123",
       json_data={"name": "John Updated"}
   )

**DELETE Request**:

.. code-block:: python

   result = await session.delete("https://target.com/api/users/123")
   print(f"Delete status: {result.status_code}")

Exploit Chaining
---------------

Execute complex exploit chains with session persistence:

.. code-block:: python

   async def exploit_chain():
       auth_config = {
           "url": "https://target.com/login",
           "method": "POST",
           "credentials": {"username": "admin", "password": "secret123"}
       }
       
       async with AsyncSessionManager(auth_config=auth_config) as session:
           # Step 1: Authenticate and access admin panel
           admin_result = await session.get("https://target.com/admin/panel")
           
           # Step 2: Extract user data
           users_result = await session.get("https://target.com/api/users")
           
           # Step 3: Exploit user management
           exploit_result = await session.post(
               "https://target.com/api/admin/users",
               json_data={"action": "create", "user": {"role": "admin"}}
           )
           
           # Step 4: Verify exploit
           verify_result = await session.get("https://target.com/api/admin/users")
           
           return [admin_result, users_result, exploit_result, verify_result]
   
   results = await exploit_chain()
   for i, result in enumerate(results):
       print(f"Step {i+1}: {result.status_code}")

Convenience Functions
--------------------

Single Async Request
-------------------

Use the convenience function for simple async requests:

.. code-block:: python

   from logicpwn.core import send_request_async
   
   async def main():
       result = await send_request_async(
           url="https://httpbin.org/get",
           method="GET",
           headers={"User-Agent": "LogicPwn"}
       )
       print(f"Result: {result.status_code}")
   
   asyncio.run(main())

Batch Async Requests
-------------------

Send multiple requests concurrently using the convenience function:

.. code-block:: python

   from logicpwn.core import send_requests_batch_async
   
   async def main():
       request_configs = [
           {"url": "https://api1.example.com", "method": "GET"},
           {"url": "https://api2.example.com", "method": "POST", "json_data": {"test": "data"}},
           {"url": "https://api3.example.com", "method": "PUT", "json_data": {"update": "value"}}
       ]
       
       results = await send_requests_batch_async(request_configs, max_concurrent=5)
       
       for i, result in enumerate(results):
           print(f"Request {i+1}: {result.status_code}")
   
   asyncio.run(main())

Async Context Manager
--------------------

Use the async context manager for session management:

.. code-block:: python

   from logicpwn.core import async_session_manager
   
   async def main():
       auth_config = {
           "url": "https://target.com/login",
           "method": "POST",
           "credentials": {"username": "admin", "password": "secret123"}
       }
       
       async with async_session_manager(auth_config=auth_config, max_concurrent=10) as session:
           result = await session.get("https://target.com/api/data")
           print(f"Session result: {result.status_code}")
   
   asyncio.run(main())

Advanced Usage
-------------

Rate Limiting
------------

Implement custom rate limiting:

.. code-block:: python

   import asyncio
   import time
   
   class RateLimitedRunner:
       def __init__(self, requests_per_second=10):
           self.requests_per_second = requests_per_second
           self.last_request_time = 0
           self.min_interval = 1.0 / requests_per_second
       
       async def send_request_with_rate_limit(self, runner, **kwargs):
           current_time = time.time()
           time_since_last = current_time - self.last_request_time
           
           if time_since_last < self.min_interval:
               await asyncio.sleep(self.min_interval - time_since_last)
           
           self.last_request_time = time.time()
           return await runner.send_request(**kwargs)
   
   async def main():
       rate_limiter = RateLimitedRunner(requests_per_second=5)
       
       async with AsyncRequestRunner() as runner:
           for i in range(10):
               result = await rate_limiter.send_request_with_rate_limit(
                   runner,
                   url=f"https://httpbin.org/get?request={i}",
                   method="GET"
               )
               print(f"Request {i}: {result.status_code}")
   
   asyncio.run(main())

Connection Pooling
-----------------

Optimize connection pooling for high-performance scenarios:

.. code-block:: python

   async with AsyncRequestRunner(
       max_concurrent=20,
       verify_ssl=False
   ) as runner:
       # Large batch of requests
       request_configs = [
           {"url": f"https://api.example.com/endpoint/{i}", "method": "GET"}
           for i in range(100)
       ]
       
       results = await runner.send_requests_batch(request_configs)
       print(f"Completed {len(results)} requests")

Error Recovery
-------------

Implement robust error recovery:

.. code-block:: python

   async def robust_request(runner, url, max_retries=3):
       for attempt in range(max_retries):
           try:
               result = await runner.send_request(url=url, method="GET")
               return result
           except Exception as e:
               if attempt == max_retries - 1:
                   raise e
               await asyncio.sleep(2 ** attempt)  # Exponential backoff
   
   async def main():
       async with AsyncRequestRunner() as runner:
           try:
               result = await robust_request(runner, "https://api.example.com/data")
               print(f"Success: {result.status_code}")
           except Exception as e:
               print(f"Failed after retries: {e}")
   
   asyncio.run(main())

Performance Monitoring
--------------------

Monitor async request performance:

.. code-block:: python

   import time
   import statistics
   
   async def benchmark_requests():
       async with AsyncRequestRunner(max_concurrent=10) as runner:
           start_time = time.time()
           
           request_configs = [
               {"url": "https://httpbin.org/get", "method": "GET"}
               for _ in range(50)
           ]
           
           results = await runner.send_requests_batch(request_configs)
           
           end_time = time.time()
           total_time = end_time - start_time
           
           successful = sum(1 for r in results if r.status_code == 200)
           
           print(f"Total requests: {len(results)}")
           print(f"Successful: {successful}")
           print(f"Total time: {total_time:.2f}s")
           print(f"Requests per second: {len(results) / total_time:.2f}")
   
   asyncio.run(benchmark_requests())

Best Practices
-------------

1. **Use Context Managers**: Always use async context managers for proper resource cleanup
2. **Handle Exceptions**: Implement proper error handling for network issues
3. **Rate Limiting**: Use rate limiting to avoid overwhelming target systems
4. **Connection Pooling**: Configure appropriate connection pool sizes
5. **Session Persistence**: Use AsyncSessionManager for authenticated workflows
6. **Monitor Performance**: Track request performance and adjust concurrency accordingly
7. **Secure Logging**: Ensure sensitive data is properly redacted in logs

Performance Tips
--------------

* Use appropriate `max_concurrent` values based on target system capacity
* Implement rate limiting for production environments
* Monitor memory usage with large batch requests
* Use connection pooling for repeated requests to the same hosts
* Consider using `verify_ssl=False` for testing environments only

Security Considerations
---------------------

* Always use HTTPS in production environments
* Implement proper authentication and session management
* Monitor for sensitive data exposure in logs
* Use secure credential storage
* Implement proper access controls and authorization

Troubleshooting
--------------

Common Issues
------------

**Connection Errors**: Check network connectivity and target availability
**Timeout Errors**: Increase timeout values for slow targets
**Memory Issues**: Reduce `max_concurrent` for large batch requests
**SSL Errors**: Verify SSL certificates or use `verify_ssl=False` for testing

Debugging
---------

Enable debug logging for troubleshooting:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   async with AsyncRequestRunner() as runner:
       result = await runner.send_request(url="https://api.example.com/data") 