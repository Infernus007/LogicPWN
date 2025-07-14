.. _access-detection:

Access & IDOR Detection
=======================

LogicPwn provides advanced modules for detecting insecure direct object references (IDOR) and access control flaws, both synchronously and asynchronously.

Overview
--------
- Test REST APIs for unauthorized access to user resources
- Support for custom HTTP methods, per-ID data, and multiple baselines
- High concurrency for large-scale testing
- Integrates with session/auth modules and exploit chains

Key Functions
-------------

.. autofunction:: logicpwn.core.access.detector.detect_idor_flaws
.. autofunction:: logicpwn.core.access.detector.detect_idor_flaws_async

Advanced Usage Example
----------------------

.. code-block:: python

   from logicpwn.core.access.detector import detect_idor_flaws
   from logicpwn.core.access.models import AccessDetectorConfig
   import requests

   session = requests.Session()
   session.cookies.set('auth_token', 'user1_token')

   endpoint_template = "https://target.com/api/users/{id}/profile"
   test_ids = ["user1", "user2", "user3"]
   success_indicators = ["profile data", "email", "username"]
   failure_indicators = ["access denied", "unauthorized", "forbidden"]

   config = AccessDetectorConfig(
       current_user_id="user1",
       authorized_ids=["user1"],
       unauthorized_ids=["user2", "user3"],
       compare_unauthenticated=True,
       method="GET",
       max_concurrent_requests=5
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
       print(f"Tested ID: {result.id_tested}, Access granted: {result.access_granted}, Vulnerability: {result.vulnerability_detected}")

Async Example
-------------

.. code-block:: python

   import asyncio
   from logicpwn.core.access.detector import detect_idor_flaws_async
   # ... (same config as above)

   async def main():
       results = await detect_idor_flaws_async(
           endpoint_template,
           test_ids,
           success_indicators,
           failure_indicators,
           config
       )
       for result in results:
           print(result)

   asyncio.run(main())

See Also
--------
- :doc:`exploit_engine` for exploit chaining and automation
- :ref:`api-reference` for full API details 