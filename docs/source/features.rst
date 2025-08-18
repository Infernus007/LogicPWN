.. _features:

Comprehensive Feature Overview
==============================

LogicPwn is the most advanced open-source framework for business logic vulnerability testing and exploit chain automation. Built by security professionals for security professionals.

🔐 Advanced Authentication System
--------------------------------

**Multi-Protocol Authentication Support**

LogicPwn provides comprehensive authentication capabilities for modern web applications:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Authentication Type
     - LogicPwn Capabilities
   * - **Form-Based Login**
     - CSRF token extraction, session validation, multi-step workflows
   * - **OAuth 2.0/OpenID**
     - Authorization code flow, PKCE support, token refresh, Google/Microsoft/GitHub providers
   * - **SAML SSO**
     - Assertion processing, attribute mapping, Okta/Azure integration
   * - **Multi-Factor Auth**
     - TOTP, SMS, Email verification, backup codes
   * - **JWT Token Handling**
     - Token validation, signature verification, claim extraction

**Form-Based Authentication Examples**

.. code-block:: python

   # Basic form authentication with CSRF protection
   from logicpwn.core.auth import AuthConfig, CSRFConfig
   
   csrf_config = CSRFConfig(
       enabled=True,
       auto_include=True,
       refresh_on_failure=True
   )
   
   auth_config = AuthConfig(
       url="https://app.example.com/login",
       credentials={"username": "admin", "password": "secret"},
       csrf_config=csrf_config,
       session_validation_url="/dashboard",
       success_indicators=["Welcome", "Dashboard"],
       max_retries=3,
       timeout=15
   )

**OAuth 2.0 Integration**

.. code-block:: python

   # OAuth 2.0 with popular providers
   from logicpwn.core.auth import (
       create_google_oauth_config, 
       create_microsoft_oauth_config, 
       create_github_oauth_config
   )
   
   # Google OAuth configuration
   google_config = create_google_oauth_config(
       client_id="your-google-client-id",
       client_secret="your-google-secret",
       redirect_uri="http://localhost:8080/callback"
   )
   
   # Microsoft Azure AD OAuth
   microsoft_config = create_microsoft_oauth_config(
       client_id="your-azure-client-id",
       client_secret="your-azure-secret",
       tenant="your-tenant-id"
   )
   
   # GitHub OAuth
   github_config = create_github_oauth_config(
       client_id="your-github-client-id",
       client_secret="your-github-secret"
   )

**SAML SSO Configuration**

.. code-block:: python

   # SAML SSO with identity providers
   from logicpwn.core.auth import create_okta_saml_config, create_azure_saml_config
   
   # Okta SAML configuration
   okta_config = create_okta_saml_config(
       sp_entity_id="https://your-app.com",
       sp_acs_url="https://your-app.com/saml/acs",
       okta_domain="your-domain",
       app_id="your_okta_app_id"
   )
   
   # Azure AD SAML configuration
   azure_config = create_azure_saml_config(
       sp_entity_id="https://your-app.com",
       sp_acs_url="https://your-app.com/saml/acs",
       tenant_id="your-azure-tenant-id",
       app_id="your-azure-app-id"
   )

**Multi-Factor Authentication**

.. code-block:: python

   # MFA configuration and testing
   from logicpwn.core.auth import MFAConfig, MFAManager
   
   mfa_config = MFAConfig(
       totp_issuer="YourApp",
       totp_period=30,
       totp_digits=6,
       sms_provider="twilio",
       sms_config={
           "account_sid": "your_twilio_sid",
           "auth_token": "your_twilio_token",
           "from_number": "+1234567890"
       },
       email_provider="sendgrid",
       email_config={
           "api_key": "your_sendgrid_key",
           "from_email": "noreply@yourapp.com"
       },
       code_length=6,
       code_expiry=300,  # 5 minutes
       max_attempts=3
   )
   
   # Create MFA manager
   mfa_manager = MFAManager(mfa_config)
   
   # Create TOTP challenge
   totp_challenge = mfa_manager.create_challenge("totp", "user@example.com")
   
   # Create SMS challenge
   sms_challenge = mfa_manager.create_challenge("sms", "+1234567890")
   
   # Verify challenge
   is_valid = mfa_manager.verify_challenge(totp_challenge.challenge_id, "123456")

**Enhanced Multi-Protocol Authentication**

.. code-block:: python

   # Comprehensive authentication with multiple protocols
   from logicpwn.core.auth import EnhancedAuthenticator, EnhancedAuthConfig
   
   enhanced_config = EnhancedAuthConfig(
       base_config=auth_config,
       oauth_config=google_config,
       saml_config=okta_config,
       mfa_config=mfa_config,
       jwt_config=jwt_config,
       flow_timeout=300,  # 5 minutes for multi-step flows
       max_redirects=10
   )
   
   authenticator = EnhancedAuthenticator(enhanced_config)
   
   # Intelligent authentication detection
   session = authenticator.authenticate_intelligent("https://app.example.com/login")
   
   # Multi-step OAuth + MFA flow
   oauth_mfa_flow = authenticator.authenticate_multi_step(
       "oauth_mfa",
       provider_id="google",
       mfa_method="totp"
   )
   
   # JWT token validation
   jwt_claims = authenticator.validate_jwt_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

**JWT Token Management**

.. code-block:: python

   # JWT configuration and validation
   from logicpwn.core.auth import JWTConfig, JWTHandler
   
   jwt_config = JWTConfig(
       secret_key="your-secret-key",
       expected_issuer="https://your-app.com",
       expected_audience="api-users",
       verify_signature=True,
       verify_exp=True,
       verify_nbf=True,
       verify_iat=True,
       leeway=10  # 10 seconds clock skew tolerance
   )
   
   jwt_handler = JWTHandler(jwt_config)
   
   # Create JWT token
   claims = {
       'sub': 'user123',
       'role': 'admin',
       'exp': int(time.time()) + 3600  # 1 hour expiry
   }
   token = jwt_handler.create_token(claims)
   
   # Validate JWT token
   validated_claims = jwt_handler.validate_token(token)
   print(f"User ID: {validated_claims.sub}")
   print(f"Role: {validated_claims.custom_claims.get('role')}")

**Session Management & Validation**

.. code-block:: python

   # Advanced session management
   from logicpwn.core.auth import authenticate_session, validate_session
   
   # Authenticate with comprehensive session handling
   session = authenticate_session(auth_config)
   
   # Validate session state
   is_valid = validate_session(session, auth_config.session_validation_url)
   
   # DVWA validator for testing
   from logicpwn.core.integration_utils import create_dvwa_validator
   
   dvwa_validator = create_dvwa_validator("http://localhost/DVWA")
   if dvwa_validator.authenticate():
       # Test DVWA with authenticated session
       result = dvwa_validator.request_and_validate(
           "GET", "/vulnerabilities/sqli/?id=1' OR 1=1--&Submit=Submit",
           validation_preset="sql_injection"
       )

⚡ High-Performance Execution Engine
-----------------------------------

**Asynchronous Request Processing**

LogicPwn's async architecture delivers unmatched performance for large-scale security testing:

- **Concurrent Request Execution**: Test 100+ endpoints simultaneously
- **Connection Pool Management**: Efficient resource utilization
- **Adaptive Rate Limiting**: Respect target application limits
- **Circuit Breaker Pattern**: Automatic failure handling and recovery

.. code-block:: python

   # High-performance async testing
   async with AsyncSessionManager() as manager:
       await manager.authenticate(auth_config)
       
       # Execute 1000 requests concurrently  
       results = await manager.execute_exploit_chain([
           {"url": f"/api/users/{i}", "method": "GET"} 
           for i in range(1000)
       ])

**Performance Monitoring & Optimization**

.. code-block:: python

   @monitor_performance("vulnerability_scan")
   def comprehensive_security_test():
       # Automatic performance tracking
       # Memory usage, request timing, error rates
       pass
   
   # Get detailed metrics
   metrics = get_performance_summary()
   print(f"Requests per second: {metrics.requests_per_second}")
   print(f"Memory usage: {metrics.peak_memory_mb}MB")

🔍 Intelligent Vulnerability Detection
-------------------------------------

**Multi-Criteria Response Analysis**

LogicPwn goes beyond simple pattern matching with sophisticated validation:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Analysis Type
     - Capabilities
   * - **Pattern Matching**
     - Regex, keyword detection, response structure analysis
   * - **Status Code Analysis**
     - HTTP status patterns, redirect chains, error conditions
   * - **Response Time Analysis**
     - Timing attack detection, performance anomalies
   * - **Header Analysis**
     - Security headers, cookie attributes, caching directives
   * - **Content Analysis**
     - JSON path extraction, HTML parsing, binary analysis
   * - **Confidence Scoring**
     - Quantified vulnerability likelihood (0-100%)

**Pre-Built Vulnerability Detection Presets**

.. code-block:: python

   # 8 built-in validation presets
   available_presets = [
       "sql_injection",        # SQL injection detection
       "xss",                 # Cross-site scripting
       "directory_traversal", # Path traversal attacks  
       "auth_bypass",         # Authentication bypass
       "info_disclosure",     # Information leakage
       "api_success",         # API response validation
       "login_success",       # Authentication success
       "error_page"           # Error condition detection
   ]
   
   # Easy preset usage
   result = validator.request_and_validate(
       "GET", "/search?q=' OR 1=1--",
       validation_preset="sql_injection"
   )

**Custom Validation Rules**

.. code-block:: python

   # Create sophisticated custom validation
   custom_validation = ValidationConfig(
       success_criteria=[
           "admin panel", "privileged access", "dashboard"
       ],
       failure_criteria=[
           "access denied", "unauthorized", "login required"
       ],
       regex_patterns=[
           r"Session ID: ([A-Za-z0-9]+)",
           r"User role: (\w+)"
       ],
       status_codes=[200, 302],
       confidence_threshold=0.7,
       require_all_success=False
   )

🎯 Advanced Access Control Testing
---------------------------------

**Systematic IDOR Detection**

LogicPwn provides the most comprehensive IDOR testing capabilities available:

.. code-block:: python

   # Enterprise-grade IDOR testing
   config = AccessDetectorConfig(
       current_user_id="user123",
       authorized_ids=["user123", "user456"],  # Should have access
       unauthorized_ids=["admin", "user789"],  # Should not have access
       compare_unauthenticated=True,           # Test anonymous access
       rate_limit=0.5,                        # Requests per second
       request_timeout=30,                    # Per-request timeout
       max_concurrent=10                      # Concurrent requests
   )
   
   results = detect_idor_flaws(
       session,
       endpoint_template="https://api.example.com/users/{id}",
       test_ids=["user123", "user456", "admin", "user789"],
       success_indicators=["user_data", "profile"],
       failure_indicators=["access_denied", "unauthorized"],
       config=config
   )

**Multi-Context Access Testing**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Test Context
     - LogicPwn Capability
   * - **Horizontal Privilege Escalation**
     - User A accessing User B's resources
   * - **Vertical Privilege Escalation**  
     - User accessing admin-only functions
   * - **Anonymous Access Testing**
     - Unauthenticated access to protected resources
   * - **Cross-Tenant Testing**
     - Multi-tenant application isolation validation
   * - **Role-Based Access Control**
     - Systematic testing of role permissions

🔗 Automated Exploit Chain Orchestration  
-----------------------------------------

**Visual Workflow Definition**

Define complex multi-step attacks with intuitive configuration:

.. code-block:: python

   # Complex exploit chain automation
   privilege_escalation_chain = ExploitChain(
       name="Admin Panel Privilege Escalation",
       description="Multi-step attack to gain administrative access",
       steps=[
           ExploitStep(
               name="Initial Authentication",
               description="Login as regular user",
               request_config=RequestConfig(
                   url="https://target.com/login",
                   method="POST",
                   data={"username": "user", "password": "password"}
               ),
               success_indicators=["Welcome", "Dashboard"]
           ),
           ExploitStep(
               name="Session Token Extraction", 
               description="Extract session token for privilege escalation",
               request_config=RequestConfig(
                   url="https://target.com/api/user/profile",
                   method="GET"
               ),
               success_indicators=["session_token"],
               payload_injection_points=[
                   PayloadInjectionPoint(
                       location="header",
                       parameter="Authorization",
                       extraction_pattern=r"token\":\"([^\"]+)\""
                   )
               ]
           ),
           ExploitStep(
               name="Admin Panel Access",
               description="Attempt to access admin panel with escalated privileges",
               request_config=RequestConfig(
                   url="https://target.com/admin/panel",
                   method="GET"
               ),
               success_indicators=["admin_dashboard", "user_management"],
               critical=True  # Mark as critical step
           )
       ]
   )

**Dynamic Payload Generation**

.. code-block:: python

   # Intelligent payload injection
   payload_types = [
       PayloadType.STATIC,        # Fixed payloads
       PayloadType.RANDOM,        # Random generation  
       PayloadType.FUZZ,          # Fuzzing patterns
       PayloadType.TEMPLATE,      # Template-based
       PayloadType.CONTEXT_AWARE  # Context-sensitive
   ]
   
   # Context-aware payload injection
   injection_point = PayloadInjectionPoint(
       location="query_param",
       parameter="user_id",
       payload_type=PayloadType.CONTEXT_AWARE,
       context_source="previous_response",
       extraction_pattern=r"admin_user_id\":(\d+)"
   )

📊 Comprehensive Performance & Load Testing
------------------------------------------

**Stress Testing Capabilities**

.. code-block:: python

   # Advanced stress testing
   stress_config = StressTestConfig(
       max_concurrent=100,        # Concurrent connections
       duration=300,              # Test duration (seconds)
       ramp_up_time=30,          # Gradual load increase
       memory_monitoring=True,    # Track memory usage
       cpu_monitoring=True,       # Monitor CPU utilization
       request_timeout=10         # Request timeout
   )
   
   async with StressTester(stress_config) as tester:
       # Run comprehensive load testing
       metrics = await tester.run_stress_test(
           target_configs=[
               {"url": "https://api.example.com/users", "method": "GET"},
               {"url": "https://api.example.com/orders", "method": "GET"}
           ],
           auth_config=auth_config
       )
   
       print(f"Requests per second: {metrics.requests_per_second}")
       print(f"Error rate: {metrics.error_rate}%")
       print(f"Average response time: {metrics.avg_response_time}ms")

**Performance Optimization Features**

- **Response Caching**: Intelligent caching to avoid redundant requests
- **Connection Pooling**: Efficient HTTP connection management  
- **Memory Management**: Optimized memory usage for long-running tests
- **Resource Monitoring**: Real-time CPU, memory, and network monitoring

📄 Professional Reporting & Documentation
----------------------------------------

**Multi-Format Report Generation**

.. code-block:: python

   # Professional vulnerability reports
   reporter = ReportGenerator(
       config=ReportConfig(
           target_url="https://api.example.com",
           report_title="Security Assessment Report",
           include_cvss=True,
           include_remediation=True,
           template="professional"
       )
   )
   
   # Add vulnerability findings
   finding = VulnerabilityFinding(
       id="IDOR-001",
       title="Insecure Direct Object Reference in User API",
       severity="High",
       cvss_score=7.5,
       description="User profile endpoints allow unauthorized access...",
       affected_endpoints=["/api/users/{id}", "/api/profiles/{id}"],
       proof_of_concept="GET /api/users/admin HTTP/1.1...",
       impact="Unauthorized access to sensitive user data",
       remediation="Implement proper access control checks",
       references=["OWASP-A01", "CWE-639"],
       discovered_at=datetime.now()
   )
   reporter.add_finding(finding)
   
   # Generate multiple formats
   reporter.export_to_file("report.html", "html")
   reporter.export_to_file("report.md", "markdown")  
   reporter.export_to_file("report.json", "json")

**Report Templates & Customization**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Report Type
     - Features
   * - **Executive Summary**
     - High-level findings, business impact, risk assessment
   * - **Technical Report**
     - Detailed vulnerability analysis, proof-of-concepts, remediation
   * - **Compliance Report**
     - OWASP Top 10, NIST, ISO 27001 mapping
   * - **Developer Report**
     - Code-level recommendations, fix implementations

🛡️ Enterprise Security Features
-------------------------------

**Secure Logging & Data Protection**

.. code-block:: python

   # Automatic sensitive data redaction
   log_config = LoggingConfig(
       redact_credentials=True,
       redact_tokens=True,
       redact_patterns=[
           r"password[\"\':][\s]*[\"\'](.*?)[\"\'']",
           r"api[_-]?key[\"\':][\s]*[\"\'](.*?)[\"\'']",
           r"Authorization:\s*Bearer\s+(.+)"
       ],
       log_level="INFO",
       log_rotation=True,
       max_log_size="100MB"
   )

**Access Control & Audit Trail**

- **Request/Response Logging**: Complete audit trail of all security tests
- **Sensitive Data Redaction**: Automatic credential and token masking
- **Role-Based Access**: Control who can run specific test categories
- **Compliance Integration**: GDPR, HIPAA, SOX compliance features

🧩 Extensible Architecture
-------------------------

**Middleware System**

.. code-block:: python

   # Custom middleware for specialized testing
   class CustomSecurityMiddleware(BaseMiddleware):
       def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
           # Pre-request processing
           return context
       
       def process_response(self, context: MiddlewareContext, response: Any) -> Any:
           # Post-response analysis
           return response
   
   # Register custom middleware
   middleware_manager.register(CustomSecurityMiddleware())

**Plugin Architecture**

.. code-block:: python

   # Custom validation plugins
   class CustomValidationPlugin:
       def validate(self, response, config):
           # Custom vulnerability detection logic
           return ValidationResult(is_valid=True, confidence=0.8)
   
   # Custom payload generators
   class CustomPayloadGenerator:
       def generate_payloads(self, context):
           # Generate context-specific payloads
           return ["custom_payload_1", "custom_payload_2"]

⚙️ Configuration & Integration
------------------------------

**Flexible Configuration Management**

.. code-block:: python

   # Environment-specific configurations
   config_profiles = {
       "development": {
           "timeout": 30,
           "max_retries": 2,
           "log_level": "DEBUG"
       },
       "production": {
           "timeout": 10,
           "max_retries": 1,
           "log_level": "INFO"
       }
   }

**CI/CD Integration**

.. code-block:: yaml

   # GitHub Actions integration
   - name: LogicPwn Security Testing
     run: |
       python -m logicpwn.scripts.security_scan \
         --config security_config.yaml \
         --output security_report.json \
         --fail-on-high-severity

🚀 Getting Started
-----------------

**Quick Installation**

.. code-block:: bash

   # Install with all features
   pip install logicpwn[async,reporting,stress]
   
   # Or install core only
   pip install logicpwn

**5-Minute Quick Start**

.. code-block:: python

   from logicpwn.core.auth import AuthConfig
   from logicpwn.core.integration_utils import AuthenticatedValidator
   
   # Configure authentication
   auth_config = AuthConfig(
       url="https://demo.testfire.net/login.jsp",
       credentials={"uid": "admin", "passw": "admin"},
       success_indicators=["Hello Admin"]
   )
   
   # Create validator with performance monitoring
   validator = AuthenticatedValidator(
       auth_config, 
       "https://demo.testfire.net",
       enable_performance_monitoring=True
   )
   
   # Authenticate and test
   if validator.authenticate():
       # Test for SQL injection
       result = validator.request_and_validate(
           "GET", "/bank/queryxpath.aspx?name=' OR 1=1--",
           validation_preset="sql_injection"
       )
       
       print(f"Vulnerability detected: {result['validation'].is_valid}")
       print(f"Confidence: {result['validation'].confidence_score}")

.. seealso::

   * :doc:`getting_started` - Complete installation and setup guide
   * :doc:`comparison` - How LogicPwn compares to other tools
   * :doc:`api_reference` - Complete API documentation
