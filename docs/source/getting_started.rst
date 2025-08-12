.. note::
   Always import from the relevant submodule, e.g. ``from logicpwn.core.runner import send_request``. Do not import directly from ``logicpwn.core``.

Getting Started with LogicPwn
============================
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

Synchronous Request (No Authentication)
---------------------------------------

.. code-block:: python

   import requests
   from logicpwn.core.runner import send_request

   session = requests.Session()
   request_config = {
       "url": "https://httpbin.org/get",
       "method": "GET"
   }
   response = send_request(session, request_config)
   print("Status:", response.status_code)
   print("Content:", response.text[:200])

Synchronous Authenticated Request
---------------------------------

.. code-block:: python

   from logicpwn.core.auth import authenticate_session
   from logicpwn.core.runner import send_request

   auth_config = {
       "url": "https://httpbin.org/basic-auth/user/passwd",
       "method": "GET",
       "credentials": {"username": "user", "password": "passwd"},
       "success_indicators": ["authenticated"]
   }
   session = authenticate_session(auth_config)
   request_config = {
       "url": "https://httpbin.org/basic-auth/user/passwd",
       "method": "GET"
   }
   response = send_request(session, request_config)
   print("Status:", response.status_code)
   print("Content:", response.text[:200])

Async Example (No Authentication)
---------------------------------

.. code-block:: python

   import asyncio
   from logicpwn.core.runner import AsyncSessionManager

   async def main():
       async with AsyncSessionManager() as manager:
           results = await manager.execute_exploit_chain([
               {"url": "https://httpbin.org/get", "method": "GET"},
               {"url": "https://httpbin.org/uuid", "method": "GET"}
           ])
           for i, result in enumerate(results):
               print(f"Request {i+1}: {result.status_code} - {result.text[:100]}")

   asyncio.run(main())

IDOR Detection Example
---------------------

.. code-block:: python

   import requests
   from logicpwn.core.access import detect_idor_flaws, AccessDetectorConfig

   session = requests.Session()
   endpoint_template = "https://httpbin.org/anything/{id}"
   test_ids = ["1", "2", "3"]
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

Reporting Example
-----------------

.. code-block:: python

   from logicpwn.core.reporter.orchestrator import (
       ReportGenerator, ReportConfig, VulnerabilityFinding, ReportMetadata
   )
   from datetime import datetime

   # Configure the report
   config = ReportConfig(
       target_url="https://httpbin.org/get",
       report_title="Security Assessment Report"
   )
   reporter = ReportGenerator(config)

   # Add a finding
   finding = VulnerabilityFinding(
       id="IDOR-001",
       title="IDOR in User Profile",
       severity="High",
       description="User profile accessible without auth...",
       affected_endpoints=["/anything/{id}"],
       proof_of_concept="GET /anything/123",
       impact="Sensitive data exposure",
       remediation="Add access control",
       discovered_at=datetime.now()
   )
   reporter.add_finding(finding)

   # Set metadata
   reporter.metadata = ReportMetadata(
       report_id="RPT-001",
       title="Security Assessment Report",
       target_url="https://httpbin.org/get",
       scan_start_time=datetime.now(),
       scan_end_time=datetime.now(),
       logicpwn_version="1.0.0",
       total_requests=100,
       findings_count={"High": 1}
   )

   # Generate and export
   reporter.export_to_file("report.md", "markdown")
   reporter.export_to_file("report.html", "html")

Exploit Engine Example
----------------------

.. code-block:: python

   import requests
   from logicpwn.core.exploit_engine.models import ExploitChain, ExploitStep
   from logicpwn.core.exploit_engine.exploit_engine import run_exploit_chain
   from logicpwn.models.request_config import RequestConfig

   # Define a simple exploit step
   step = ExploitStep(
       name="Get UUID",
       description="Fetch a UUID from httpbin",
       request_config=RequestConfig(
           url="https://httpbin.org/uuid",
           method="GET"
       ),
       success_indicators=["uuid"]
   )

   # Create an exploit chain
   chain = ExploitChain(
       name="Simple Chain",
       description="A single-step chain for demonstration",
       steps=[step]
   )

   # Use a plain session for public endpoints
   session = requests.Session()

   # Run the exploit chain
   results = run_exploit_chain(session, chain)

   for result in results:
       print(f"Step: {result.step_name}, Status: {result.status}, Error: {result.error_message}")
       if result.response is not None:
           print("Response:", result.response.text[:200])

Configuration
------------
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

LogicPwn supports configuration via environment variables. These are loaded automatically at startup and override defaults if set.

.. code-block:: bash

   export LOGICPWN_TIMEOUT=60
   export LOGICPWN_LOG_LEVEL=DEBUG

# Supported variables include LOGICPWN_TIMEOUT, LOGICPWN_MAX_RETRIES, LOGICPWN_VERIFY_SSL, LOGICPWN_SESSION_TIMEOUT, and more.
