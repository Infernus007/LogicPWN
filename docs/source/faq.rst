.. _faq:

Frequently Asked Questions
==========================

Get answers to the most common questions about LogicPwn, from basic setup to advanced enterprise deployment scenarios.

🚀 Getting Started
-----------------

**Q: What makes LogicPwn different from other security testing tools?**

A: LogicPwn is specifically designed for **business logic vulnerability testing**, which traditional scanners miss. Key differences:

- **Business Process Understanding**: LogicPwn comprehends multi-step workflows, not just individual requests
- **Advanced Session Management**: Handles complex authentication flows, CSRF tokens, and session persistence automatically
- **Async Architecture**: Concurrent testing capabilities for improved performance
- **Python-Native**: Code-first approach enables unlimited customization and CI/CD integration
- **Multi-Protocol Auth**: Native support for OAuth 2.0, SAML, JWT, and MFA

**Q: Do I need programming experience to use LogicPwn?**

A: Basic Python knowledge is recommended but not required to get started:

- **Beginners**: Use pre-built validation presets and example configurations
- **Intermediate**: Customize authentication flows and validation rules  
- **Advanced**: Build custom exploit chains and integrate with enterprise systems

**Q: How long does it take to set up LogicPwn for a new application?**

A: Setup time depends on application complexity:

- **Simple web apps**: 15-30 minutes using built-in presets
- **Complex authentication**: 1-2 hours to configure multi-step flows
- **Enterprise integration**: 1-2 days for full CI/CD integration

**Q: Can LogicPwn test both web applications and APIs?**

A: Yes, LogicPwn excels at both:

.. code-block:: python

   # Web application testing
   web_auth = AuthConfig(
       url="https://app.example.com/login",
       credentials={"username": "user", "password": "pass"},
       success_indicators=["Welcome", "Dashboard"]
   )
   
   # API testing  
   api_auth = AuthConfig(
       url="https://api.example.com/auth/login",
       credentials={"email": "user@example.com", "password": "pass"},
       success_indicators=["access_token", "expires_in"],
       auth_type="bearer_token"
   )

🔧 Technical Questions
---------------------

**Q: What programming languages and frameworks does LogicPwn support for testing?**

A: LogicPwn is **language-agnostic** - it tests applications via HTTP/HTTPS regardless of backend technology:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Technology
     - LogicPwn Support
   * - **Web Frameworks**
     - Django, Flask, Rails, Spring Boot, Express.js, ASP.NET, Laravel
   * - **API Types**
     - REST, GraphQL, SOAP, gRPC (via HTTP gateway)
   * - **Authentication**
     - Form-based, OAuth, SAML, JWT, API keys, custom protocols
   * - **Frontend**
     - React, Angular, Vue.js, traditional server-side rendered apps

**Q: How does LogicPwn handle rate limiting and avoid getting blocked?**

A: LogicPwn includes sophisticated anti-blocking mechanisms:

.. code-block:: python

   # Built-in rate limiting and retry logic
   stress_config = StressTestConfig(
       max_concurrent=50,           # Limit simultaneous connections
       requests_per_second=10,      # Respect rate limits
       retry_backoff=2.0,           # Exponential backoff
       user_agent_rotation=True,    # Rotate user agents
       proxy_rotation=True,         # Use proxy rotation
       request_spacing=0.5          # Minimum time between requests
   )

**Q: Can LogicPwn test applications behind VPNs or firewalls?**

A: Yes, LogicPwn supports various network configurations:

- **VPN Access**: Run LogicPwn from within VPN-connected environments
- **Proxy Support**: HTTP/HTTPS/SOCKS proxy configuration
- **Custom Headers**: Add authentication headers, API keys, or custom routing
- **Certificate Handling**: Support for self-signed certificates and custom CAs

**Q: How accurate is LogicPwn's vulnerability detection?**

A: LogicPwn uses multi-criteria validation to improve detection accuracy:

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * - Validation Method
     - Description
     - Best For
   * - **Pattern Matching**
     - Response content analysis
     - Known vulnerability patterns
   * - **Multi-Criteria Analysis**
     - Combined validation techniques
     - Business logic flaws
   * - **Context-Aware Validation**
     - Application context consideration
     - Complex workflows
   * - **Machine Learning** (Enterprise)
     - Adaptive pattern recognition
     - Advanced threat detection

🛡️ Security & Compliance
------------------------

**Q: Is LogicPwn safe to use on production systems?**

A: LogicPwn includes multiple safety features, but use with caution on production:

**Safety Features**:
- Non-destructive testing by default
- Rate limiting to prevent DoS
- Automatic sensitive data redaction
- Comprehensive logging for audit trails

**Production Testing Guidelines**:
- Always get explicit permission before testing production
- Use dedicated test accounts with limited privileges
- Configure conservative rate limits
- Monitor application performance during testing
- Have rollback procedures ready

**Q: How does LogicPwn protect sensitive data during testing?**

A: LogicPwn implements comprehensive data protection:

.. code-block:: python

   # Automatic sensitive data redaction
   logging_config = LoggingConfig(
       redact_credentials=True,
       redact_patterns=[
           r"password[\"\':][\s]*[\"\'](.*?)[\"\'']",
           r"api[_-]?key[\"\':][\s]*[\"\'](.*?)[\"\'']", 
           r"token[\"\':][\s]*[\"\'](.*?)[\"\'']",
           r"\b\d{16}\b",  # Credit card numbers
           r"\b\d{3}-\d{2}-\d{4}\b"  # Social Security Numbers
       ],
       audit_trail=True,
       encryption_at_rest=True  # Enterprise feature
   )

**Q: What compliance frameworks does LogicPwn support?**

A: LogicPwn supports major compliance requirements:

.. list-table::
   :widths: 25 35 40
   :header-rows: 1

   * - Framework
     - LogicPwn Features
     - Use Cases
   * - **OWASP Top 10**
     - Built-in validation presets
     - Web application security testing
   * - **PCI DSS**
     - Payment flow testing, data protection
     - E-commerce, financial applications
   * - **HIPAA**
     - PHI detection, access control testing
     - Healthcare applications
   * - **SOC 2**
     - Security control testing, audit trails
     - SaaS platforms, cloud services
   * - **GDPR**
     - Data exposure detection, consent flows
     - EU data processing applications

⚡ Performance & Scalability
---------------------------

**Q: How many requests per second can LogicPwn handle?**

A: Performance depends on configuration and target application:

.. list-table::
   :widths: 30 25 25 20
   :header-rows: 1

   * - Scenario
     - Requests/Second
     - Concurrent Connections
     - Memory Usage
   * - **Single-threaded**
     - 50-100
     - 1
     - 50MB
   * - **Multi-threaded**
     - 200-500
     - 10-50
     - 200MB
   * - **Async (Standard)**
     - 1,000-2,000
     - 100-500
     - 400MB
   * - **Enterprise Cluster**
     - 10,000+
     - 1,000+
     - 2GB+

**Q: Can LogicPwn scale to test large applications with thousands of endpoints?**

A: Yes, LogicPwn is designed for enterprise-scale testing:

.. code-block:: python

   # Large-scale testing example
   async def enterprise_scale_testing():
       # Test 10,000 endpoints across 100 user contexts
       endpoints = generate_endpoint_list(10000)
       user_contexts = generate_user_contexts(100)
       
       # Distributed testing across multiple workers
       results = await distribute_testing(
           endpoints=endpoints,
           user_contexts=user_contexts,
           workers=10,
           max_concurrent_per_worker=100
       )
       
       return analyze_results(results)

**Q: How does LogicPwn compare to commercial tools?**

A: LogicPwn offers unique advantages for business logic testing:

.. list-table::
   :widths: 25 35 40
   :header-rows: 1

   * - Tool Category
     - Primary Strengths
     - LogicPwn's Unique Value
   * - **Commercial DAST**
     - Broad vulnerability coverage
     - **Business logic & access control focus**
   * - **Open Source Scanners**
     - Cost-effective, customizable
     - **Specialized exploit chain automation**
   * - **Manual Testing Tools**
     - Comprehensive analysis
     - **Automated complex workflow testing**

LogicPwn is designed to complement existing tools by addressing business logic vulnerabilities that traditional scanners often miss.

🏢 Enterprise & Professional
---------------------------

**Q: What's included in LogicPwn Enterprise Edition?**

A: Enterprise Edition provides advanced features for large organizations:

**Performance Enhancements**:
- 10,000+ concurrent connections
- Distributed testing across multiple nodes
- Advanced caching and optimization
- Priority support and SLA

**Security Features**:
- Role-based access control (RBAC)
- SSO integration (SAML, OAuth, LDAP)
- Advanced audit trails and compliance reporting
- Hardware security module (HSM) integration

**Integration Capabilities**:
- SIEM integration (Splunk, QRadar, Sentinel)
- Vulnerability management (Qualys, Rapid7, Tenable)
- Ticketing systems (Jira, ServiceNow)
- CI/CD platforms (Jenkins, GitLab, Azure DevOps)

**Q: Do you offer professional services and training?**

A: Yes, we provide comprehensive professional services:

**Training Programs**:
- 2-day LogicPwn Fundamentals workshop
- Advanced business logic testing certification
- Custom training for enterprise teams
- Online self-paced learning modules

**Consulting Services**:
- Security assessment methodology development
- Custom vulnerability research
- Application-specific testing workflow design
- CI/CD integration consulting

**Professional Services**:
- Penetration Testing as a Service (PTaaS)
- Managed security testing programs
- Custom integration development
- 24/7 security operations support

**Q: What support options are available?**

A: Multiple support tiers to meet different needs:

.. list-table::
   :widths: 20 25 25 30
   :header-rows: 1

   * - Support Level
     - Response Time
     - Channels
     - Included Services
   * - **Community**
     - Best effort
     - GitHub, Forums
     - **Community support, documentation**
   * - **Professional** 
     - 8 hours
     - Email, Phone
     - **Dedicated support rep, training credits**
   * - **Enterprise**
     - 2 hours
     - All channels
     - **Dedicated team, on-site support**
   * - **Mission Critical**
     - 30 minutes
     - War room
     - **24/7 dedicated engineer, SLA guarantee**

🔧 Troubleshooting
-----------------

**Q: LogicPwn authentication keeps failing. How do I debug this?**

A: Authentication issues are common with new setups. Try these debugging steps:

.. code-block:: python

   # Enable debug logging
   import logging
   from loguru import logger
   
   # Set up comprehensive logging
   logger.add("debug.log", level="DEBUG", rotation="10 MB")
   logging.getLogger("logicpwn").setLevel(logging.DEBUG)
   
   # Test authentication step by step
   auth_config = AuthConfig(
       url="https://your-app.com/login",
       credentials={"username": "test", "password": "test"},
       success_indicators=["welcome", "dashboard"],
       failure_indicators=["invalid", "error"],
       debug=True  # Enable debug mode
   )
   
   # Manual authentication testing
   validator = AuthenticatedValidator(auth_config, "https://your-app.com")
   
   # Check each step
   print("1. Testing connectivity...")
   response = validator.session.get("https://your-app.com/login")
   print(f"   Status: {response.status_code}")
   
   print("2. Testing authentication...")
   auth_result = validator.authenticate()
   print(f"   Success: {auth_result}")
   
   if not auth_result:
       print("3. Checking authentication response...")
       # Manual login attempt with detailed logging
       login_response = validator.session.post(
           "https://your-app.com/login",
           data={"username": "test", "password": "test"}
       )
       print(f"   Response: {login_response.text[:200]}")

**Q: My tests are running very slowly. How can I optimize performance?**

A: Several optimization strategies can dramatically improve performance:

.. code-block:: python

   # Performance optimization techniques
   
   # 1. Use async execution for multiple requests
   async def optimized_testing():
       async with AsyncSessionManager() as manager:
           # Parallel execution instead of sequential
           tasks = [
               manager.send_request("GET", f"/api/endpoint/{i}")
               for i in range(100)
           ]
           results = await asyncio.gather(*tasks)
   
   # 2. Enable response caching
   from logicpwn.core.cache import response_cache
   
   @response_cache.cache(expire=300)  # Cache for 5 minutes
   def cached_request(url):
       return send_request(url=url, method="GET")
   
   # 3. Optimize concurrent connections
   stress_config = StressTestConfig(
       max_concurrent=50,        # Start with 50, increase gradually
       connection_pool_size=20,  # Reuse connections
       keep_alive=True,         # HTTP keep-alive
       compress=True            # Enable compression
   )

**Q: How do I handle applications with complex CSRF protection?**

A: LogicPwn includes advanced CSRF handling capabilities:

.. code-block:: python

   # Advanced CSRF configuration
   csrf_config = CSRFConfig(
       enabled=True,
       token_name="csrf_token",
       auto_include=True,
       refresh_on_failure=True,
       
       # Multiple extraction patterns for different applications
       extraction_patterns=[
           r'name="csrf_token" value="([^"]+)"',           # Form fields
           r'<meta name="csrf-token" content="([^"]+)"',   # Meta tags
           r'"csrf_token":"([^"]+)"',                      # JSON responses
           r'window\.csrf_token = "([^"]+)"'               # JavaScript variables
       ],
       
       # Custom injection locations
       injection_locations=["form_data", "headers", "query_params"],
       
       # Handle token expiration
       expiry_detection_patterns=[
           "token expired", "csrf mismatch", "invalid token"
       ]
   )

💰 Pricing & Licensing
---------------------

**Q: Is LogicPwn really free and open source?**

A: Yes, LogicPwn Community Edition is completely free under MIT license:

- **No usage limits** for security testing
- **Full source code** available on GitHub
- **Commercial use permitted** without restrictions
- **No phone-home or telemetry** in community edition

**Q: When should I consider upgrading to Enterprise Edition?**

A: Consider Enterprise when you need:

.. list-table::
   :widths: 40 30 30
   :header-rows: 1

   * - Requirement
     - Community Edition
     - Enterprise Edition
   * - **Team Size**
     - 1-5 users
     - **5+ users**
   * - **Performance**
     - Up to 100 concurrent
     - **Up to 10,000 concurrent**
   * - **Support**
     - Community forums
     - **Professional support with SLA**
   * - **Compliance**
     - Basic reporting
     - **Advanced compliance & audit**
   * - **Integration**
     - Limited
     - **Enterprise SIEM, ticketing, SSO**

**Q: What's the ROI of using LogicPwn vs. traditional tools?**

A: Organizations typically see positive ROI through:

**Cost Savings**:
- **Open source advantage**: No licensing fees compared to commercial DAST tools
- **Time efficiency**: Automated testing reduces manual security assessment effort
- **Reduced false positives**: Context-aware validation minimizes manual verification time

**Risk Reduction**:
- **Business logic coverage**: Find vulnerabilities traditional tools miss
- **Faster time to detection**: Identify issues in development vs. production
- **Compliance efficiency**: Automated compliance reporting saves audit costs

📞 Getting Help
--------------

**Q: Where can I get help if I'm stuck?**

A: Multiple resources are available:

**Community Resources** (Free):
- **Documentation**: Comprehensive guides and examples
- **GitHub Issues**: Bug reports and feature requests  
- **Community Forum**: Peer-to-peer support and discussions
- **Stack Overflow**: Tagged questions with logicpwn tag

**Professional Support** (Paid):
- **Email Support**: Direct access to LogicPwn engineers
- **Phone Support**: Real-time troubleshooting assistance
- **Screen Sharing**: Live debugging sessions
- **Custom Development**: Tailored solutions for specific needs

**Q: How do I report a bug or request a feature?**

A: We welcome community contributions:

**Bug Reports**:
1. Search existing GitHub issues first
2. Provide minimal reproduction example
3. Include LogicPwn version and Python version
4. Describe expected vs. actual behavior

**Feature Requests**:
1. Check the roadmap for planned features
2. Describe the use case and business value
3. Provide examples of how the feature would be used
4. Consider contributing the implementation

**Security Issues**:
- Report privately to security@logicpwn.org
- Include detailed reproduction steps
- Do not disclose publicly until fixed

.. seealso::

   * :doc:`getting_started` - Start your LogicPwn journey
   * :doc:`tutorials` - Step-by-step learning guides  
   * :doc:`enterprise` - Enterprise solutions and support
