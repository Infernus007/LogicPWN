.. _access-detection:

Access & IDOR Detection
=======================

LogicPwn provides comprehensive modules for detecting insecure direct object references (IDOR), access control flaws, tenant isolation issues, and privilege escalation vulnerabilities. The enhanced framework supports both basic and advanced testing scenarios with intelligent automation capabilities.

Overview
--------
- **Enhanced IDOR Detection**: Advanced ID generation, pattern recognition, and intelligent fuzzing
- **Tenant Isolation Testing**: Multi-tenant application security validation and cross-tenant access detection
- **Privilege Escalation Detection**: Role hierarchy mapping, admin function discovery, and privilege boundary testing
- **Intelligent ID Generation**: Automated pattern detection and smart ID enumeration strategies
- **High Performance**: Concurrent testing with optimized request handling
- **Integration Ready**: Seamless integration with session/auth modules and exploit chains

Core Functions
--------------

**Basic IDOR Detection**

.. autofunction:: logicpwn.core.access.detector.detect_idor_flaws
.. autofunction:: logicpwn.core.access.detector.detect_idor_flaws_async

**Enhanced Access Testing**

.. autofunction:: logicpwn.core.access.enhanced_detector.EnhancedAccessTester.comprehensive_test
.. autofunction:: logicpwn.core.access.enhanced_detector.EnhancedAccessTester.test_idor_with_smart_ids
.. autofunction:: logicpwn.core.access.enhanced_detector.EnhancedAccessTester.test_tenant_isolation
.. autofunction:: logicpwn.core.access.enhanced_detector.EnhancedAccessTester.test_privilege_escalation

**Intelligent ID Generation**

.. autofunction:: logicpwn.core.access.id_generation.EnhancedIDGenerator.generate_smart_id_list
.. autofunction:: logicpwn.core.access.id_generation.PatternDetector.detect_patterns

**Tenant Isolation Testing**

.. autofunction:: logicpwn.core.access.tenant_isolation.TenantIsolationTester.test_cross_tenant_access
.. autofunction:: logicpwn.core.access.tenant_isolation.TenantEnumerator.enumerate_tenants

**Privilege Escalation Detection**

.. autofunction:: logicpwn.core.access.privilege_escalation.PrivilegeEscalationTester.test_privilege_escalation
.. autofunction:: logicpwn.core.access.privilege_escalation.RoleHierarchyMapper.discover_admin_functions

Quick Start Example
-------------------

**Basic IDOR Testing**

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
       print(f"ID: {result.id_tested}, Access: {result.access_granted}, Vuln: {result.vulnerability_detected}")

**Enhanced Comprehensive Testing**

.. code-block:: python

   from logicpwn.core.access.enhanced_detector import EnhancedAccessTester
   import requests

   session = requests.Session()
   session.cookies.set('auth_token', 'user1_token')
   
   tester = EnhancedAccessTester(session)
   
   # Comprehensive testing with all capabilities
   results = tester.comprehensive_test(
       endpoint_template="https://target.com/api/users/{id}/profile",
       known_valid_ids=["user1", "user2"],
       current_user_context={"user_id": "user1", "role": "user"},
       tenant_context={"tenant_id": "tenant1", "org_id": "org1"}
   )
   
   print(f"IDOR vulnerabilities: {len(results['idor_results'])}")
   print(f"Tenant isolation issues: {len(results['tenant_results'])}")
   print(f"Privilege escalation paths: {len(results['privilege_results'])}")

**Intelligent ID Generation**

.. code-block:: python

   from logicpwn.core.access.id_generation import EnhancedIDGenerator
   
   generator = EnhancedIDGenerator()
   
   # Generate smart IDs based on pattern detection
   smart_ids = generator.generate_smart_id_list(
       known_ids=["user123", "user456", "user789"],
       target_count=100,
       include_edge_cases=True
   )
   
   print(f"Generated {len(smart_ids)} test IDs")
   
   # Use generated IDs for testing
   results = detect_idor_flaws(
       session, endpoint_template, smart_ids,
       success_indicators, failure_indicators, config
   )

**Tenant Isolation Testing**

.. code-block:: python

   from logicpwn.core.access.tenant_isolation import TenantIsolationTester
   
   tenant_tester = TenantIsolationTester(session)
   
   # Test cross-tenant access violations
   results = tenant_tester.test_cross_tenant_access(
       endpoint_template="https://target.com/api/tenants/{tenant_id}/data/{id}",
       current_tenant="tenant1",
       target_tenants=["tenant2", "tenant3"],
       test_ids=["data1", "data2", "data3"]
   )
   
   for result in results:
       if result.vulnerability_detected:
           print(f"Cross-tenant access vulnerability: {result.details}")

**Privilege Escalation Testing**

.. code-block:: python

   from logicpwn.core.access.privilege_escalation import PrivilegeEscalationTester
   
   priv_tester = PrivilegeEscalationTester(session)
   
   # Test for privilege escalation vulnerabilities
   results = priv_tester.test_privilege_escalation(
       base_url="https://target.com/api",
       current_user_context={"user_id": "user1", "role": "user"},
       target_roles=["admin", "manager", "superuser"]
   )
   
   for result in results:
       if result.vulnerability_detected:
           print(f"Privilege escalation found: {result.escalation_type} - {result.details}")
       Advanced Configuration
---------------------

**Custom Pattern Detection**

.. code-block:: python

   from logicpwn.core.access.id_generation import PatternDetector, EnhancedIDGenerator
   
   # Configure custom patterns for ID generation
   detector = PatternDetector()
   patterns = detector.detect_patterns([
       "UUID-abc123", "UUID-def456", "UUID-ghi789"  # Custom UUID format
   ])
   
   generator = EnhancedIDGenerator()
   custom_ids = generator.generate_ids_for_pattern(
       patterns[0], count=50, 
       privilege_level="admin",  # Generate admin-level IDs
       tenant_context="org_premium"
   )

**Multi-Context Testing**

.. code-block:: python

   from logicpwn.core.access.enhanced_detector import EnhancedAccessTester
   
   # Test with multiple user contexts and roles
   contexts = [
       {"user_id": "user1", "role": "user", "tenant": "tenant1"},
       {"user_id": "admin1", "role": "admin", "tenant": "tenant1"}, 
       {"user_id": "user2", "role": "user", "tenant": "tenant2"}
   ]
   
   tester = EnhancedAccessTester(session)
   
   for context in contexts:
       # Update session context
       session.headers.update({"X-User-Role": context["role"]})
       session.headers.update({"X-Tenant-ID": context["tenant"]})
       
       results = tester.test_idor_with_smart_ids(
           endpoint_template="https://target.com/api/data/{id}",
           known_valid_ids=["data1", "data2"],
           user_context=context
       )

**Performance Optimization**

.. code-block:: python

   from logicpwn.core.access.enhanced_detector import EnhancedAccessTester
   
   # Configure for high-performance testing
   tester = EnhancedAccessTester(
       session, 
       max_concurrent_requests=20,  # Increase concurrency
       request_delay=0.1,           # Reduce delay between requests
       timeout=5                    # Set shorter timeout
   )
   
   # Test large ID sets efficiently
   large_id_set = generator.generate_smart_id_list(
       known_ids=["id1", "id2"], 
       target_count=1000
   )
   
   results = tester.test_idor_with_smart_ids(
       endpoint_template, large_id_set,
       batch_size=50  # Process in batches
   )

Async Testing Examples
----------------------

**Basic Async IDOR Detection**

.. code-block:: python

   import asyncio
   from logicpwn.core.access.detector import detect_idor_flaws_async
   
   async def test_idor():
       results = await detect_idor_flaws_async(
           endpoint_template,
           test_ids,
           success_indicators,
           failure_indicators,
           config
       )
       for result in results:
           print(result)
   
   asyncio.run(test_idor())

**Async Enhanced Testing**

.. code-block:: python

   import asyncio
   from logicpwn.core.access.enhanced_detector import EnhancedAccessTester
   
   async def comprehensive_async_test():
       tester = EnhancedAccessTester(session)
       
       # Run multiple test types concurrently
       idor_task = asyncio.create_task(
           tester.test_idor_with_smart_ids_async(endpoint_template, test_ids)
       )
       
       tenant_task = asyncio.create_task(
           tester.test_tenant_isolation_async(endpoint_template, tenant_context)
       )
       
       priv_task = asyncio.create_task(
           tester.test_privilege_escalation_async(base_url, user_context)
       )
       
       # Wait for all tests to complete
       idor_results, tenant_results, priv_results = await asyncio.gather(
           idor_task, tenant_task, priv_task
       )
       
       return {
           'idor': idor_results,
           'tenant': tenant_results, 
           'privilege': priv_results
       }
   
   results = asyncio.run(comprehensive_async_test())

Integration Examples
--------------------

**Integration with Authentication Module**

.. code-block:: python

   from logicpwn.core.auth import SessionManager
   from logicpwn.core.access.enhanced_detector import EnhancedAccessTester
   
   # Authenticate and get session
   auth_manager = SessionManager()
   session = auth_manager.authenticate(
       login_url="https://target.com/login",
       credentials={"username": "testuser", "password": "testpass"}
   )
   
   # Use authenticated session for access testing
   tester = EnhancedAccessTester(session)
   results = tester.comprehensive_test(endpoint_template, known_ids)

**Integration with Exploit Chains**

.. code-block:: python

   from logicpwn.core.exploit_engine import ExploitChain
   from logicpwn.core.access.enhanced_detector import EnhancedAccessTester
   
   # Create exploit chain for discovered vulnerabilities
   chain = ExploitChain()
   tester = EnhancedAccessTester(session)
   
   # Test for access control flaws
   results = tester.comprehensive_test(endpoint_template, known_ids)
   
   # Add discovered vulnerabilities to exploit chain
   for result in results['idor_results']:
       if result.vulnerability_detected:
           chain.add_step(
               "idor_exploit",
               target_url=result.test_url,
               vulnerability_type="IDOR",
               payload=result.test_payload
           )
   
   # Execute exploit chain
   chain.execute()

Best Practices
--------------

**Rate Limiting and Stealth**

.. code-block:: python

   # Configure for stealthy testing
   tester = EnhancedAccessTester(
       session,
       max_concurrent_requests=3,  # Lower concurrency
       request_delay=1.0,          # Longer delays
       randomize_delays=True,      # Randomize request timing
       use_different_user_agents=True
   )

**Error Handling and Resilience**

.. code-block:: python

   try:
       results = tester.comprehensive_test(
           endpoint_template, known_ids,
           retry_failed_requests=True,
           max_retries=3,
           timeout=30
       )
   except Exception as e:
       print(f"Testing failed: {e}")
       # Fallback to basic testing
       results = detect_idor_flaws(session, endpoint_template, test_ids)

**Result Analysis and Reporting**

.. code-block:: python

   # Analyze results and generate reports
   summary = tester.generate_summary_report(results)
   
   print(f"Total vulnerabilities found: {summary['total_vulnerabilities']}")
   print(f"High severity issues: {summary['high_severity']}")
   print(f"Affected endpoints: {summary['affected_endpoints']}")
   
   # Export detailed results
   tester.export_results(results, format="json", filename="access_test_results.json")
   tester.export_results(results, format="csv", filename="access_test_results.csv")

Module Reference
----------------

**Core Modules**

- ``logicpwn.core.access.detector`` - Basic IDOR detection functionality
- ``logicpwn.core.access.enhanced_detector`` - Comprehensive enhanced testing framework
- ``logicpwn.core.access.id_generation`` - Intelligent ID generation and pattern detection
- ``logicpwn.core.access.tenant_isolation`` - Multi-tenant security testing
- ``logicpwn.core.access.privilege_escalation`` - Role hierarchy and privilege testing
- ``logicpwn.core.access.models`` - Data models and configuration classes

**Key Classes**

- ``EnhancedAccessTester`` - Main testing orchestrator
- ``EnhancedIDGenerator`` - Advanced ID generation with pattern recognition
- ``PatternDetector`` - Automatic ID pattern detection and analysis
- ``TenantIsolationTester`` - Cross-tenant access violation testing
- ``TenantEnumerator`` - Tenant discovery and enumeration
- ``PrivilegeEscalationTester`` - Privilege escalation vulnerability detection
- ``RoleHierarchyMapper`` - Application role discovery and mapping

Performance Notes
-----------------

**Scaling Considerations**

- **Concurrent Requests**: Default limit is 10, increase cautiously to avoid detection
- **Request Delays**: Minimum 0.1s recommended to prevent rate limiting
- **Batch Processing**: Large ID sets are automatically processed in batches
- **Memory Usage**: Smart ID generation caches patterns for efficiency
- **Network Optimization**: Connection pooling and keep-alive enabled by default

**Recommended Limits**

- **ID Generation**: Up to 10,000 IDs per pattern efficiently
- **Concurrent Testing**: 5-20 concurrent requests depending on target
- **Tenant Enumeration**: Limit DNS queries to avoid detection
- **Admin Function Discovery**: Use targeted paths to reduce noise

Troubleshooting
---------------

**Common Issues**

1. **Pattern Detection Failures**: Ensure minimum 3 sample IDs for reliable pattern detection
2. **Rate Limiting**: Reduce concurrency and increase delays if encountering 429 responses
3. **Authentication Issues**: Verify session state and token validity before testing
4. **False Positives**: Tune success/failure indicators based on application responses
5. **Network Timeouts**: Increase timeout values for slow target applications

**Debug Mode**

.. code-block:: python

   # Enable detailed logging for troubleshooting
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   tester = EnhancedAccessTester(session, debug=True)
   results = tester.comprehensive_test(endpoint_template, known_ids)

See Also
--------

- :doc:`authentication` - Session management and authentication bypass
- :doc:`exploit_engine` - Exploit chaining and automation  
- :doc:`business_logic` - Business logic flaw detection
- :ref:`api-reference` - Complete API documentation 