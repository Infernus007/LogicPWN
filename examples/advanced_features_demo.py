#!/usr/bin/env python3
"""
Advanced Features Demo for LogicPwn

This script demonstrates the advanced features of LogicPwn including:
- Centralized configuration management
- Sensitive data redaction and secure logging
- Middleware system for extensibility
- Advanced response analysis and security detection
- RequestResult with comprehensive metadata
- Exploit chaining with session persistence

Usage:
    python examples/advanced_features_demo.py

Note: This script uses httpbin.org for demonstration purposes.
In real penetration testing scenarios, replace with actual target URLs.
"""

import time
from typing import Dict, Any

from logicpwn.core.config import config, get_timeout, get_max_retries, get_sensitive_headers, get_redaction_string
from logicpwn.core.logging import logger, log_info, log_debug, log_warning
from logicpwn.core.middleware.middleware import (
    middleware_manager,
    add_middleware,
    enable_middleware,
    disable_middleware,
    list_middleware,
    LoggingMiddleware,
    SecurityMiddleware,
    RetryMiddleware
)
from logicpwn.core.runner import send_request_advanced
from logicpwn.models import RequestResult
from logicpwn.exceptions import RequestExecutionError


def demonstrate_configuration():
    """Demonstrate centralized configuration management."""
    print("\n" + "="*60)
    print("CONFIGURATION MANAGEMENT DEMO")
    print("="*60)
    
    # Show current configuration
    print(f"Default timeout: {get_timeout()} seconds")
    print(f"Max retries: {get_max_retries()}")
    print(f"Redaction string: {get_redaction_string()}")
    print(f"Sensitive headers: {get_sensitive_headers()}")
    
    # Update configuration
    print("\nUpdating configuration...")
    config.update_config(TIMEOUT=15, MAX_RETRIES=5)
    print(f"New timeout: {get_timeout()} seconds")
    print(f"New max retries: {get_max_retries()}")


def demonstrate_logging():
    """Demonstrate secure logging with sensitive data redaction."""
    print("\n" + "="*60)
    print("SECURE LOGGING DEMO")
    print("="*60)
    
    # Log with sensitive data (will be redacted)
    sensitive_data = {
        "username": "admin",
        "password": "secret123",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "api_key": "sk-1234567890abcdef",
        "session_id": "sess_9876543210fedcba"
    }
    
    print("Logging sensitive data (will be redacted):")
    log_info("Authentication attempt", sensitive_data)
    
    # Log regular data
    regular_data = {
        "url": "https://api.example.com/users",
        "method": "POST",
        "status_code": 200,
        "response_time": 0.245
    }
    
    print("\nLogging regular data:")
    log_info("API request completed", regular_data)


def demonstrate_middleware():
    """Demonstrate middleware system for extensibility."""
    print("\n" + "="*60)
    print("MIDDLEWARE SYSTEM DEMO")
    print("="*60)
    
    # Show current middleware
    print("Current middleware:")
    for mw in list_middleware():
        print(f"  - {mw['name']} ({mw['type']}): {'ENABLED' if mw['enabled'] else 'DISABLED'}")
    
    # Add custom middleware
    print("\nAdding custom middleware...")
    add_middleware(LoggingMiddleware())
    add_middleware(SecurityMiddleware())
    add_middleware(RetryMiddleware(max_retries=3))
    
    # Show updated middleware list
    print("\nUpdated middleware:")
    for mw in list_middleware():
        print(f"  - {mw['name']} ({mw['type']}): {'ENABLED' if mw['enabled'] else 'DISABLED'}")
    
    # Demonstrate middleware control
    print("\nDisabling security middleware...")
    disable_middleware("Security")
    
    print("Enabling retry middleware...")
    enable_middleware("Retry")
    
    print("\nFinal middleware status:")
    for mw in list_middleware():
        print(f"  - {mw['name']}: {'ENABLED' if mw['enabled'] else 'DISABLED'}")


def demonstrate_request_analysis():
    """Demonstrate advanced request analysis and security detection."""
    print("\n" + "="*60)
    print("ADVANCED REQUEST ANALYSIS DEMO")
    print("="*60)
    
    # Test 1: Normal request
    print("\n1. Testing normal request...")
    try:
        result = send_request_advanced(
            url="https://httpbin.org/json",
            method="GET",
            headers={"User-Agent": "LogicPwn/1.0"}
        )
        
        print(f"Status: {result.status_code}")
        print(f"Success: {result.is_success()}")
        print(f"Has vulnerabilities: {result.has_vulnerabilities()}")
        print(f"Response time: {result.metadata.total_time:.3f}s")
        
    except RequestExecutionError as e:
        print(f"Request failed: {e}")
    
    # Test 2: Request with error response (simulated)
    print("\n2. Testing request with error response...")
    try:
        result = send_request_advanced(
            url="https://httpbin.org/status/500",
            method="GET"
        )
        
        print(f"Status: {result.status_code}")
        print(f"Success: {result.is_success()}")
        print(f"Server error: {result.is_server_error()}")
        
    except RequestExecutionError as e:
        print(f"Request failed: {e}")
    
    # Test 3: Request with redirect
    print("\n3. Testing request with redirect...")
    try:
        result = send_request_advanced(
            url="https://httpbin.org/redirect/2",
            method="GET"
        )
        
        print(f"Status: {result.status_code}")
        print(f"Success: {result.is_success()}")
        print(f"Redirect: {result.is_redirect()}")
        print(f"Location header: {result.metadata.location}")
        
    except RequestExecutionError as e:
        print(f"Request failed: {e}")


def demonstrate_security_analysis():
    """Demonstrate security analysis features."""
    print("\n" + "="*60)
    print("SECURITY ANALYSIS DEMO")
    print("="*60)
    
    # Create a mock response with security issues
    print("Creating mock response with security issues...")
    
    # Simulate a response with debug information
    mock_response_html = """
    <html>
    <head><title>Debug Page</title></head>
    <body>
        <h1>Debug Information</h1>
        <p>PHP Version: 7.4.3</p>
        <p>Server: Apache/2.4.41</p>
        <p>Document Root: /var/www/html</p>
        <p>Error: SQL syntax error near 'SELECT * FROM users'</p>
        <script>console.log('Debug info');</script>
        <p>Development mode: ON</p>
        <p>Internal path: /home/admin/config.php</p>
    </body>
    </html>
    """
    
    # Create RequestResult manually to simulate security analysis
    result = RequestResult(url="https://example.com/debug", method="GET")
    result.set_response(
        status_code=200,
        headers={
            "content-type": "text/html",
            "server": "Apache/2.4.41",
            "x-debug-token": "abc123",
            "set-cookie": "session=xyz789"
        },
        body=mock_response_html
    )
    
    # Analyze security issues
    print(f"Has vulnerabilities: {result.has_vulnerabilities()}")
    print(f"Has error messages: {result.security_analysis.has_error_messages}")
    print(f"Has debug info: {result.security_analysis.has_debug_info}")
    print(f"Has version info: {result.security_analysis.has_version_info}")
    print(f"Has internal paths: {result.security_analysis.has_internal_paths}")
    print(f"Has SQL errors: {result.security_analysis.has_sql_errors}")
    print(f"Has XSS vectors: {result.security_analysis.has_xss_vectors}")
    print(f"Has session tokens: {result.security_analysis.has_session_tokens}")
    
    print(f"\nError messages found: {result.security_analysis.error_messages}")
    print(f"Debug info found: {result.security_analysis.debug_info}")
    print(f"Version info found: {result.security_analysis.version_info}")
    print(f"Internal paths found: {result.security_analysis.internal_paths}")


def demonstrate_session_chaining():
    """Demonstrate session chaining for exploit workflows."""
    print("\n" + "="*60)
    print("SESSION CHAINING DEMO")
    print("="*60)
    
    # Simulate a multi-step exploit chain
    print("Simulating multi-step exploit chain...")
    
    # Step 1: Initial reconnaissance
    print("\nStep 1: Initial reconnaissance")
    try:
        result1 = send_request_advanced(
            url="https://httpbin.org/headers",
            method="GET",
            headers={"User-Agent": "LogicPwn/1.0"}
        )
        
        print(f"Status: {result1.status_code}")
        print(f"Cookies received: {result1.get_cookies()}")
        
        # Extract session data for next step
        session_data = result1.get_session_data()
        print(f"Session data: {session_data}")
        
    except RequestExecutionError as e:
        print(f"Step 1 failed: {e}")
        return
    
    # Step 2: Authentication attempt
    print("\nStep 2: Authentication attempt")
    try:
        result2 = send_request_advanced(
            url="https://httpbin.org/post",
            method="POST",
            json_data={
                "username": "admin",
                "password": "password123",
                "action": "login"
            },
            headers={
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            session_data=session_data  # Use session from previous step
        )
        
        print(f"Status: {result2.status_code}")
        print(f"New cookies: {result2.get_cookies()}")
        
        # Update session data
        session_data.update(result2.get_session_data())
        
    except RequestExecutionError as e:
        print(f"Step 2 failed: {e}")
        return
    
    # Step 3: Privileged action
    print("\nStep 3: Privileged action")
    try:
        result3 = send_request_advanced(
            url="https://httpbin.org/put",
            method="PUT",
            json_data={
                "action": "update_user",
                "user_id": "123",
                "role": "admin"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token123"
            },
            session_data=session_data  # Use updated session
        )
        
        print(f"Status: {result3.status_code}")
        print(f"Final cookies: {result3.get_cookies()}")
        
        # Check for vulnerabilities in the chain
        if result3.has_vulnerabilities():
            print("WARNING: Security issues detected in exploit chain!")
            print(f"Vulnerabilities: {result3.security_analysis.to_dict()}")
        
    except RequestExecutionError as e:
        print(f"Step 3 failed: {e}")


def demonstrate_error_handling():
    """Demonstrate comprehensive error handling."""
    print("\n" + "="*60)
    print("ERROR HANDLING DEMO")
    print("="*60)
    
    # Test various error scenarios
    error_scenarios = [
        {
            "name": "Network timeout",
            "url": "https://httpbin.org/delay/10",
            "timeout": 1
        },
        {
            "name": "Invalid URL",
            "url": "https://invalid-domain-that-does-not-exist-12345.com",
            "timeout": 5
        },
        {
            "name": "Server error",
            "url": "https://httpbin.org/status/500",
            "timeout": 10
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\nTesting: {scenario['name']}")
        try:
            result = send_request_advanced(
                url=scenario['url'],
                method="GET",
                timeout=scenario['timeout']
            )
            print(f"Unexpected success: {result.status_code}")
            
        except RequestExecutionError as e:
            print(f"Expected error: {e}")
            print(f"Error type: {type(e).__name__}")


def main():
    """Main demonstration function."""
    print("LogicPwn Advanced Features Demonstration")
    print("="*60)
    print("This script demonstrates the advanced features of LogicPwn")
    print("including configuration management, secure logging, middleware,")
    print("security analysis, and session chaining for exploit workflows.")
    print("\nNote: Using httpbin.org for demonstration purposes.")
    print("In real penetration testing, replace with actual target URLs.")
    
    try:
        # Run demonstrations
        demonstrate_configuration()
        demonstrate_logging()
        demonstrate_middleware()
        demonstrate_request_analysis()
        demonstrate_security_analysis()
        demonstrate_session_chaining()
        demonstrate_error_handling()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print("All advanced features have been demonstrated successfully!")
        print("\nKey features demonstrated:")
        print("- Centralized configuration management")
        print("- Sensitive data redaction and secure logging")
        print("- Middleware system for extensibility")
        print("- Advanced response analysis and security detection")
        print("- RequestResult with comprehensive metadata")
        print("- Session chaining for exploit workflows")
        print("- Comprehensive error handling")
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error during demonstration: {e}")
        # Assuming log_error is available from logicpwn.core.logger or similar
        # For now, just print the error
        print(f"Error logging: {e}")


if __name__ == "__main__":
    main() 