"""
LogicPwn Response Validator Example
Demonstrates various validation scenarios for VAPT and CTF scenarios.

This example shows how to use the response validator module for:
- Basic success/failure validation
- Regex pattern matching and data extraction
- Vulnerability detection using pre-defined patterns
- JSON and HTML response validation
- Validation chaining for complex workflows
- Integration with auth and runner modules

Note: This example uses httpbin.org for demonstration purposes.
      httpbin.org always returns 200 OK regardless of input,
      making it perfect for testing the validation framework
      without requiring actual vulnerable applications.
"""

import sys
import requests
from loguru import logger

# Add the project root to the path for imports
sys.path.insert(0, '.')

from logicpwn.core.validator import (
    validate_response,
    extract_from_response,
    validate_json_response,
    validate_html_response,
    chain_validations,
    ValidationResult,
    ValidationConfig,
    ValidationType,
    VulnerabilityPatterns
)
from logicpwn.core.auth import authenticate_session, AuthConfig
from logicpwn.core.runner import send_request_advanced
from logicpwn.exceptions import (
    ValidationError,
    ResponseError,
    AuthenticationError,
    RequestExecutionError
)


def basic_validation_example():
    """Basic validation example for exploit chaining workflows.
    
    This example demonstrates simple success/failure criteria validation
    that can be used in exploit chains to determine next steps.
    """
    logger.info("🧩 Basic Response Validation Example")
    logger.info("=" * 50)
    
    try:
        # Make a request to get a response for validation
        response = requests.get("https://httpbin.org/json")
        
        # Example 1: Basic Success/Failure Validation
        logger.info("\n1. Basic Success/Failure Validation")
        
        # Check for success indicators
        success = validate_response(
            response=response,
            success_criteria=["slideshow", "json"],
            failure_criteria=["error", "denied"],
            status_codes=[200, 201]
        )
        logger.success(f"   Validation Result: {success}")
        
        # Example 2: Structured Result
        logger.info("\n2. Structured Validation Result")
        result = validate_response(
            response=response,
            success_criteria=["slideshow"],
            regex_patterns=[r'"title":\s*"([^"]*)"'],
            return_structured=True
        )
        
        if isinstance(result, ValidationResult):
            logger.success(f"   Valid: {result.is_valid}")
            logger.info(f"   Matched Patterns: {result.matched_patterns}")
            logger.info(f"   Confidence Score: {result.confidence_score:.2f}")
            logger.info(f"   Extracted Data: {result.extracted_data}")
        
        return True
        
    except Exception as e:
        logger.error(f"Basic validation example failed: {e}")
        return False


def regex_pattern_matching_example():
    """Regex pattern matching and data extraction example.
    
    This example shows how to extract specific data from responses
    using regex patterns, which is useful for exploit chaining.
    """
    logger.info("\n🔍 Regex Pattern Matching Example")
    logger.info("=" * 50)
    
    try:
        # Get a JSON response with structured data
        response = requests.get("https://httpbin.org/json")
        
        # Example 1: Basic Data Extraction
        logger.info("\n1. Basic Data Extraction")
        extracted_data = extract_from_response(
            response=response,
            regex=r'"title":\s*"([^"]*)"'
        )
        logger.success(f"   Extracted Title: {extracted_data}")
        
        # Example 2: Named Group Extraction
        logger.info("\n2. Named Group Extraction")
        structured_data = extract_from_response(
            response=response,
            regex=r'"slideshow":\s*{[^}]*"title":\s*"(?P<title>[^"]*)"[^}]*"author":\s*"(?P<author>[^"]*)"',
            group_names=["title", "author"]
        )
        logger.success(f"   Structured Data: {structured_data}")
        
        # Example 3: Multiple Matches
        logger.info("\n3. Multiple Matches Extraction")
        # Create a response with multiple user IDs
        multi_response = requests.get("https://httpbin.org/stream/3")
        user_ids = extract_from_response(
            response=multi_response,
            regex=r'"id":\s*(\d+)',
            extract_all=True
        )
        logger.success(f"   All User IDs: {user_ids}")
        
        return True
        
    except Exception as e:
        logger.error(f"Regex pattern matching example failed: {e}")
        return False


def vulnerability_detection_example():
    """Vulnerability detection using pre-defined patterns.
    
    This example demonstrates how to detect common vulnerabilities
    in responses using the built-in vulnerability patterns.
    """
    logger.info("\n🚨 Vulnerability Detection Example")
    logger.info("=" * 50)
    
    try:
        # Example 1: SQL Injection Detection
        logger.info("\n1. SQL Injection Detection")
        
        # Simulate SQL injection response (in real scenarios, this would come from actual testing)
        sql_injection_response = requests.Response()
        sql_injection_response.status_code = 500
        sql_injection_response._content = b'Warning: mysql_fetch_array(): supplied argument is not a valid MySQL result'
        sql_injection_response.headers = {'content-type': 'text/html'}
        
        sql_detected = validate_response(
            response=sql_injection_response,
            regex_patterns=VulnerabilityPatterns.SQL_INJECTION,
            return_structured=True
        )
        
        if isinstance(sql_detected, ValidationResult):
            logger.warning(f"   SQL Injection Detected: {sql_detected.is_valid}")
            if sql_detected.is_valid:
                logger.warning(f"   Matched Patterns: {sql_detected.matched_patterns}")
        
        # Example 2: XSS Detection
        logger.info("\n2. XSS Detection")
        
        # Simulate XSS response
        xss_response = requests.Response()
        xss_response.status_code = 200
        xss_response._content = b'<script>alert("XSS")</script>'
        xss_response.headers = {'content-type': 'text/html'}
        
        xss_detected = validate_response(
            response=xss_response,
            regex_patterns=VulnerabilityPatterns.XSS_INDICATORS,
            return_structured=True
        )
        
        if isinstance(xss_detected, ValidationResult):
            logger.warning(f"   XSS Detected: {xss_detected.is_valid}")
            if xss_detected.is_valid:
                logger.warning(f"   Matched Patterns: {xss_detected.matched_patterns}")
        
        # Example 3: Information Disclosure Detection
        logger.info("\n3. Information Disclosure Detection")
        
        # Simulate information disclosure response
        info_disclosure_response = requests.Response()
        info_disclosure_response.status_code = 500
        info_disclosure_response._content = b'Stack trace: /var/www/html/index.php:15'
        info_disclosure_response.headers = {'content-type': 'text/html'}
        
        info_detected = validate_response(
            response=info_disclosure_response,
            regex_patterns=VulnerabilityPatterns.INFO_DISCLOSURE,
            return_structured=True
        )
        
        if isinstance(info_detected, ValidationResult):
            logger.warning(f"   Information Disclosure Detected: {info_detected.is_valid}")
            if info_detected.is_valid:
                logger.warning(f"   Matched Patterns: {info_detected.matched_patterns}")
        
        return True
        
    except Exception as e:
        logger.error(f"Vulnerability detection example failed: {e}")
        return False


def json_validation_example():
    """JSON response validation example.
    
    This example shows how to validate JSON responses for
    structure, required keys, and forbidden keys.
    """
    logger.info("\n📄 JSON Response Validation Example")
    logger.info("=" * 50)
    
    try:
        # Get a JSON response
        response = requests.get("https://httpbin.org/json")
        
        # Example 1: Basic JSON Validation
        logger.info("\n1. Basic JSON Validation")
        json_result = validate_json_response(response)
        logger.success(f"   JSON Valid: {json_result.is_valid}")
        logger.info(f"   Confidence: {json_result.confidence_score:.2f}")
        
        # Example 2: Required Keys Validation
        logger.info("\n2. Required Keys Validation")
        required_result = validate_json_response(
            response=response,
            required_keys=["slideshow", "title"]
        )
        logger.success(f"   Required Keys Valid: {required_result.is_valid}")
        if not required_result.is_valid:
            logger.warning(f"   Missing Keys: {required_result.metadata.get('missing_keys', [])}")
        
        # Example 3: Forbidden Keys Validation
        logger.info("\n3. Forbidden Keys Validation")
        forbidden_result = validate_json_response(
            response=response,
            forbidden_keys=["password", "secret", "token"]
        )
        logger.success(f"   No Forbidden Keys: {forbidden_result.is_valid}")
        if not forbidden_result.is_valid:
            logger.warning(f"   Found Forbidden Keys: {forbidden_result.metadata.get('forbidden_keys_found', [])}")
        
        return True
        
    except Exception as e:
        logger.error(f"JSON validation example failed: {e}")
        return False


def html_validation_example():
    """HTML response validation example.
    
    This example shows how to validate HTML responses for
    specific content patterns and structure.
    """
    logger.info("\n🌐 HTML Response Validation Example")
    logger.info("=" * 50)
    
    try:
        # Get an HTML response
        response = requests.get("https://httpbin.org/html")
        
        # Example 1: Basic HTML Validation
        logger.info("\n1. Basic HTML Validation")
        html_result = validate_html_response(response)
        logger.success(f"   HTML Valid: {html_result.is_valid}")
        logger.info(f"   Confidence: {html_result.confidence_score:.2f}")
        
        # Example 2: Title Pattern Validation
        logger.info("\n2. Title Pattern Validation")
        title_result = validate_html_response(
            response=response,
            title_patterns=["html", "httpbin"]
        )
        logger.success(f"   Title Patterns Valid: {title_result.is_valid}")
        if title_result.is_valid:
            logger.info(f"   Extracted Title: {title_result.extracted_data.get('title', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"HTML validation example failed: {e}")
        return False


def validation_chaining_example():
    """Validation chaining example for complex workflows.
    
    This example demonstrates how to chain multiple validations
    together for complex exploit scenarios.
    """
    logger.info("\n⛓️ Validation Chaining Example")
    logger.info("=" * 50)
    
    try:
        # Get a response for chaining
        response = requests.get("https://httpbin.org/json")
        
        # Define a validation chain
        validation_chain = [
            {
                "success_criteria": ["slideshow", "json"],
                "return_structured": True
            },
            {
                "regex_patterns": [r'"title":\s*"([^"]*)"'],
                "return_structured": True
            },
            {
                "status_codes": [200, 201],
                "return_structured": True
            },
            {
                "headers_criteria": {"content-type": "application/json"},
                "return_structured": True
            }
        ]
        
        logger.info("\n1. Executing Validation Chain")
        results = chain_validations(response, validation_chain)
        
        # Analyze results
        logger.info(f"   Chain Length: {len(results)}")
        successful_steps = sum(1 for result in results if result.is_valid)
        logger.success(f"   Successful Steps: {successful_steps}/{len(results)}")
        
        # Show detailed results
        for i, result in enumerate(results, 1):
            status = "✅ PASS" if result.is_valid else "❌ FAIL"
            logger.info(f"   Step {i}: {status} (confidence: {result.confidence_score:.2f})")
            
            if result.extracted_data:
                logger.info(f"      Extracted: {result.extracted_data}")
        
        # Example 2: Conditional Logic Based on Chain Results
        logger.info("\n2. Conditional Logic Based on Chain Results")
        
        if all(result.is_valid for result in results):
            logger.success("   All validations passed - proceeding with exploit")
            # Extract data from successful regex step
            regex_result = results[1]  # Second step was regex
            if regex_result.extracted_data:
                title = regex_result.extracted_data.get("group_1")
                logger.info(f"   Extracted title: {title}")
        else:
            logger.warning("   Some validations failed - adjusting strategy")
            failed_steps = [i for i, result in enumerate(results, 1) if not result.is_valid]
            logger.warning(f"   Failed steps: {failed_steps}")
        
        return True
        
    except Exception as e:
        logger.error(f"Validation chaining example failed: {e}")
        return False


def integration_with_auth_example():
    """Integration example with authentication module.
    
    This example shows how to combine authentication with
    response validation for complete exploit workflows.
    """
    logger.info("\n🔐 Integration with Authentication Example")
    logger.info("=" * 50)
    
    try:
        # Example 1: Authenticate and Validate Response
        logger.info("\n1. Authentication + Response Validation")
        
        # Create auth config (using httpbin for demo)
        auth_config = {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "credentials": {
                "username": "admin",
                "password": "admin123"
            },
            "success_indicators": ["authenticated", "welcome"],
            "failure_indicators": ["denied", "unauthorized"],
            "timeout": 30
        }
        
        # Authenticate (this would normally work with a real app)
        logger.info("   Authenticating...")
        session = authenticate_session(auth_config)
        logger.success("   Authentication successful")
        
        # Make authenticated request
        logger.info("   Making authenticated request...")
        auth_response = session.get("https://httpbin.org/json")
        
        # Validate the authenticated response
        auth_validation = validate_response(
            response=auth_response,
            success_criteria=["slideshow", "json"],
            status_codes=[200, 201],
            return_structured=True
        )
        
        if isinstance(auth_validation, ValidationResult):
            logger.success(f"   Authenticated Response Valid: {auth_validation.is_valid}")
            logger.info(f"   Confidence: {auth_validation.confidence_score:.2f}")
        
        # Example 2: Extract Data from Authenticated Response
        logger.info("\n2. Data Extraction from Authenticated Response")
        
        extracted_data = extract_from_response(
            response=auth_response,
            regex=r'"title":\s*"([^"]*)"'
        )
        
        if extracted_data:
            logger.success(f"   Extracted from authenticated response: {extracted_data}")
        
        return True
        
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Integration example failed: {e}")
        return False


def integration_with_runner_example():
    """Integration example with request runner module.
    
    This example shows how to combine request execution with
    response validation for automated testing workflows.
    """
    logger.info("\n🚀 Integration with Request Runner Example")
    logger.info("=" * 50)
    
    try:
        # Example 1: Advanced Request + Validation
        logger.info("\n1. Advanced Request with Validation")
        
        # Make advanced request
        result = send_request_advanced(
            url="https://httpbin.org/json",
            method="GET",
            headers={"User-Agent": "LogicPwn/1.0"},
            timeout=30
        )
        
        logger.success(f"   Request Status: {result.status_code}")
        logger.info(f"   Response Size: {result.metadata.response_size} bytes")
        
        # Validate the response
        validation = validate_response(
            response=result,  # RequestResult can be used as response
            success_criteria=["slideshow"],
            regex_patterns=[r'"title":\s*"([^"]*)"'],
            return_structured=True
        )
        
        if isinstance(validation, ValidationResult):
            logger.success(f"   Response Validation: {validation.is_valid}")
            logger.info(f"   Confidence: {validation.confidence_score:.2f}")
            
            if validation.extracted_data:
                title = validation.extracted_data.get("group_1")
                logger.info(f"   Extracted Title: {title}")
        
        # Example 2: Security Analysis Integration
        logger.info("\n2. Security Analysis Integration")
        
        if result.security_analysis:
            logger.info("   Security Analysis Results:")
            logger.info(f"      Sensitive Data: {result.security_analysis.has_sensitive_data}")
            logger.info(f"      Error Messages: {result.security_analysis.has_error_messages}")
            logger.info(f"      SQL Errors: {result.security_analysis.has_sql_errors}")
            logger.info(f"      XSS Vectors: {result.security_analysis.has_xss_vectors}")
            
            if result.has_vulnerabilities():
                logger.warning("   ⚠️  Vulnerabilities detected in response!")
                summary = result.get_vulnerability_summary()
                for vuln_type, detected in summary.items():
                    if detected:
                        logger.warning(f"      - {vuln_type}")
        
        return True
        
    except RequestExecutionError as e:
        logger.error(f"Request execution failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Integration example failed: {e}")
        return False


def advanced_validation_config_example():
    """Advanced validation configuration example.
    
    This example shows how to use ValidationConfig objects
    for complex validation scenarios.
    """
    logger.info("\n⚙️ Advanced Validation Configuration Example")
    logger.info("=" * 50)
    
    try:
        # Create advanced validation configuration
        validation_config = ValidationConfig(
            success_criteria=["slideshow", "json", "title"],
            failure_criteria=["error", "denied", "unauthorized"],
            regex_patterns=[
                r'"title":\s*"([^"]*)"',
                r'"author":\s*"([^"]*)"',
                r'"slideshow":\s*{[^}]*}'
            ],
            status_codes=[200, 201, 202],
            headers_criteria={
                "content-type": "application/json",
                "server": "gunicorn"
            },
            return_structured=True,
            confidence_threshold=0.6
        )
        
        logger.info("\n1. Using ValidationConfig Object")
        logger.info(f"   Success Criteria: {validation_config.success_criteria}")
        logger.info(f"   Regex Patterns: {len(validation_config.regex_patterns)} patterns")
        logger.info(f"   Status Codes: {validation_config.status_codes}")
        logger.info(f"   Confidence Threshold: {validation_config.confidence_threshold}")
        
        # Get response for validation
        response = requests.get("https://httpbin.org/json")
        
        # Use the configuration
        result = validate_response(
            response=response,
            success_criteria=validation_config.success_criteria,
            failure_criteria=validation_config.failure_criteria,
            regex_patterns=validation_config.regex_patterns,
            status_codes=validation_config.status_codes,
            headers_criteria=validation_config.headers_criteria,
            return_structured=validation_config.return_structured,
            confidence_threshold=validation_config.confidence_threshold
        )
        
        if isinstance(result, ValidationResult):
            logger.success(f"   Validation Result: {result.is_valid}")
            logger.info(f"   Confidence: {result.confidence_score:.2f}")
            logger.info(f"   Matched Patterns: {len(result.matched_patterns)}")
            logger.info(f"   Extracted Data Keys: {list(result.extracted_data.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Advanced validation config example failed: {e}")
        return False


def main():
    """Main function to run all validation examples."""
    logger.info("🧩 LogicPwn Response Validator Examples")
    logger.info("=" * 60)
    
    examples = [
        ("Basic Validation", basic_validation_example),
        ("Regex Pattern Matching", regex_pattern_matching_example),
        ("Vulnerability Detection", vulnerability_detection_example),
        ("JSON Validation", json_validation_example),
        ("HTML Validation", html_validation_example),
        ("Validation Chaining", validation_chaining_example),
        ("Auth Integration", integration_with_auth_example),
        ("Runner Integration", integration_with_runner_example),
        ("Advanced Config", advanced_validation_config_example)
    ]
    
    results = {}
    
    for name, example_func in examples:
        logger.info(f"\n{'='*20} {name} {'='*20}")
        try:
            success = example_func()
            results[name] = success
            if success:
                logger.success(f"✅ {name} completed successfully")
            else:
                logger.error(f"❌ {name} failed")
        except Exception as e:
            logger.error(f"❌ {name} failed with exception: {e}")
            results[name] = False
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 VALIDATION EXAMPLES SUMMARY")
    logger.info("="*60)
    
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"   {name}: {status}")
    
    logger.info(f"\n   Overall: {successful}/{total} examples passed")
    
    if successful == total:
        logger.success("🎉 All validation examples completed successfully!")
    else:
        logger.warning(f"⚠️  {total - successful} examples failed")
    
    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 