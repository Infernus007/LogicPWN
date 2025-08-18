Async Request Execution
=======================
LogicPwn provides high-performance async request execution capabilities using aiohttp for concurrent request handling. This module is designed for large-scale security testing and exploit chaining scenarios.

Overview
The async functionality includes:

* **AsyncRequestRunner**: High-performance async HTTP request execution
* **AsyncSessionManager**: Async session management with authentication
* **Batch Processing**: Concurrent request execution
* **Rate Limiting**: Configurable request rate limiting
* **Connection Pooling**: Efficient connection management
* **Error Handling**: Comprehensive async error handling

Why Use Async?
~~~~~~~~~~~~~~

* **Performance**: Execute multiple requests concurrently
* **Scalability**: Handle hundreds of requests efficiently
* **Resource Efficiency**: Better memory and CPU utilization
* **Real-time Processing**: Process responses as they arrive
* **Rate Limiting**: Control request rates to avoid detection

AsyncRequestRunner
------------------

The AsyncRequestRunner provides high-performance async HTTP request execution with connection pooling and rate limiting.

Basic Usage
-----------
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
-------------
Configure the AsyncRequestRunner with custom settings:

.. code-block:: python

   async with AsyncRequestRunner(
       max_concurrent=10,      # Maximum concurrent requests
       rate_limit=5.0,         # Requests per second
       timeout=30,             # Request timeout
       verify_ssl=False        # SSL verification
   ) as runner:
       # Use runner...

**Configuration Options:**

* ``max_concurrent``: Maximum number of concurrent requests (default: 10)
* ``rate_limit``: Requests per second (default: None, no limit)
* ``timeout``: Request timeout in seconds (default: 30)
* ``verify_ssl``: SSL certificate verification (default: True)
* ``headers``: Default headers for all requests
* ``cookies``: Default cookies for all requests


Batch Requests
--------------

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
-------------

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
--------------

Handle different types of async errors:

.. code-block:: python

   from logicpwn.exceptions import NetworkError, TimeoutError
   
   try:
       result = await runner.send_request(url="https://api.example.com/data")
   except asyncio.TimeoutError:
       print("Request timed out")
   except aiohttp.ClientError as e:
       print(f"Network error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

AsyncSessionManager
-------------------

The AsyncSessionManager provides async session management with authentication and session persistence.

Basic Usage
-----------

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
----------------------------

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
       },
       "success_indicators": ["dashboard", "welcome"],
       "failure_indicators": ["error", "invalid"]
   }
   
   async with AsyncSessionManager(auth_config=auth_config) as session:
       # Use authenticated session...

Session Methods
---------------

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
----------------

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
---------------------
Single Async Request
--------------------

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
--------------------

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
---------------------
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
--------------

Rate Limiting
-------------

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
------------------

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

Performance Monitoring
----------------------

Monitor async performance:

.. code-block:: python

   import time
   from logicpwn.core import get_performance_summary
   
   async def monitored_requests():
       start_time = time.time()
       
       async with AsyncRequestRunner(max_concurrent=10) as runner:
           request_configs = [
               {"url": f"https://httpbin.org/get?i={i}", "method": "GET"}
               for i in range(50)
           ]
           
           results = await runner.send_requests_batch(request_configs)
           
           end_time = time.time()
           duration = end_time - start_time
           
           print(f"Completed {len(results)} requests in {duration:.2f}s")
           print(f"Average: {duration/len(results):.3f}s per request")
           
           # Get performance metrics
           performance = get_performance_summary()
           print(f"Performance summary: {performance}")
   
   asyncio.run(monitored_requests())

Error Recovery
--------------

Implement error recovery for robust async operations:

.. code-block:: python

   async def robust_request(runner, url, max_retries=3):
       for attempt in range(max_retries):
           try:
               result = await runner.send_request(url=url, method="GET")
               return result
           except asyncio.TimeoutError:
               print(f"Timeout on attempt {attempt + 1}")
               if attempt == max_retries - 1:
                   raise
               await asyncio.sleep(2 ** attempt)  # Exponential backoff
           except Exception as e:
               print(f"Error on attempt {attempt + 1}: {e}")
               if attempt == max_retries - 1:
                   raise
   
   async def main():
       async with AsyncRequestRunner() as runner:
           try:
               result = await robust_request(runner, "https://api.example.com/data")
               print(f"Success: {result.status_code}")
           except Exception as e:
               print(f"Failed after retries: {e}")
   
   asyncio.run(main())

Best Practices
--------------

**Performance Optimization:**

1. **Use appropriate concurrency limits** - Don't overwhelm servers
2. **Implement rate limiting** - Respect server limits
3. **Use connection pooling** - Reuse connections efficiently
4. **Monitor memory usage** - Clean up resources properly
5. **Handle errors gracefully** - Implement retry logic

**Security Considerations:**

1. **Validate URLs** - Ensure target URLs are authorized
2. **Secure credential handling** - Use environment variables
3. **Monitor request patterns** - Avoid detection
4. **Log responsibly** - Don't log sensitive data
5. **Use HTTPS** - Encrypt communications

**Error Handling:**

1. **Timeout handling** - Set appropriate timeouts
2. **Retry logic** - Implement exponential backoff
3. **Circuit breaker** - Stop requests on repeated failures
4. **Graceful degradation** - Handle partial failures
5. **Comprehensive logging** - Track all operations

Troubleshooting
---------------

**Common Issues:**

* **Connection errors**: Check network connectivity and SSL certificates
* **Timeout errors**: Increase timeout values or reduce concurrency
* **Memory issues**: Reduce max_concurrent or implement cleanup
* **Rate limiting**: Implement proper rate limiting
* **Authentication failures**: Verify credentials and success indicators

**Debugging Tips:**

* Enable debug logging for detailed information
* Use performance monitoring to identify bottlenecks
* Test with smaller batches first
