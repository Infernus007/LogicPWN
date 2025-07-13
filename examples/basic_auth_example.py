"""
Business Logic Exploitation Authentication Examples for LogicPwn Framework.

This example demonstrates how to use the authentication module for
exploit chaining and multi-step security testing workflows. Shows
form-based login, token-based authentication, and session persistence
for advanced penetration testing scenarios.

Note: This example uses httpbin.org for demonstration purposes.
      httpbin.org always returns 200 OK regardless of credentials,
      making it perfect for testing the authentication framework
      without requiring actual login validation.
"""

import sys
from loguru import logger

# Add the project root to the path for imports
sys.path.insert(0, '.')

from logicpwn.core.auth import authenticate_session, validate_session, logout_session, AuthConfig
from logicpwn.exceptions import (
    AuthenticationError,
    LoginFailedException,
    NetworkError,
    ValidationError,
    TimeoutError
)


def basic_authentication_example():
    """Basic authentication example for exploit chaining workflows.
    
    Returns:
        requests.Session: Authenticated session for downstream chaining
    """
    
    # Configure authentication for target application
    # Note: httpbin.org/post always returns 200 for demo purposes.
    # In real tests, use an app with actual login validation.
    auth_config = {
        "url": "https://httpbin.org/post",  # Using httpbin for demo
        "method": "POST",
        "credentials": {
            "username": "testuser",
            "password": "testpass123"
        },
        "success_indicators": ["authenticated", "welcome"],
        "failure_indicators": ["invalid", "failed", "error"],
        "headers": {
            "User-Agent": "LogicPwn/1.0",
            "Accept": "application/json"
        },
        "timeout": 30,
        "verify_ssl": True
    }
    
    try:
        logger.info("Starting authentication process for exploit chaining...")
        
        # Authenticate and get persistent session
        session = authenticate_session(auth_config)
        logger.success("Authentication successful! Session ready for exploit chaining.")
        
        # Use the authenticated session for subsequent exploit steps
        logger.info("Making authenticated request to protected resource...")
        response = session.get("https://httpbin.org/get")
        
        if response.status_code == 200:
            logger.success("Successfully accessed protected resource")
            # Safe logging - only show first 200 chars and ensure no sensitive data
            response_preview = response.text[:200].replace("testuser", "***").replace("testpass123", "***")
            logger.debug(f"Response preview: {response_preview}...")
        else:
            logger.warning(f"Protected resource returned status code: {response.status_code}")
        
        # Validate session before proceeding with exploit chain
        logger.info("Validating session for exploit chaining...")
        is_valid = validate_session(session, "https://httpbin.org/get")
        if is_valid:
            logger.success("Session is still valid for exploit chaining")
        else:
            logger.warning("Session validation failed - may need re-authentication")
        
        # Clean up after exploit chain
        logger.info("Logging out after exploit chain...")
        logout_success = logout_session(session, "https://httpbin.org/get")
        if logout_success:
            logger.success("Logout successful - session cleaned up")
        else:
            logger.warning("Logout failed - session may still be active")
        
        return session  # Return session for downstream chaining
            
    except ValidationError as e:
        logger.error(f"Configuration error: {e}")
        logger.error(f"Field: {e.field}, Value: {e.value}")
        return None
        
    except LoginFailedException as e:
        logger.error(f"Login failed: {e}")
        logger.error(f"Response code: {e.response_code}")
        # Safe logging - sanitize response text
        safe_response = e.response_text.replace("testuser", "***").replace("testpass123", "***") if e.response_text else "No response text"
        logger.error(f"Response text: {safe_response}")
        return None
        
    except TimeoutError as e:
        logger.error(f"Authentication timed out: {e}")
        logger.error(f"Timeout setting: {e.timeout_seconds} seconds")
        return None
        
    except NetworkError as e:
        logger.error(f"Network error during authentication: {e}")
        if e.original_exception:
            logger.error(f"Original exception: {e.original_exception}")
        return None
            
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        return None


def get_method_authentication_example():
    """Example using GET method for authentication in exploit chains.
    
    Returns:
        requests.Session: Authenticated session for downstream chaining
    """
    
    # Note: httpbin.org/get always returns 200 for demo purposes.
    # In real tests, use an app with actual login validation.
    auth_config = {
        "url": "https://httpbin.org/get",
        "method": "GET",
        "credentials": {
            "username": "testuser",
            "password": "testpass123"
        },
        "success_indicators": ["authenticated"],
        "timeout": 30
    }
    
    try:
        logger.info("Starting GET-based authentication for exploit chaining...")
        session = authenticate_session(auth_config)
        logger.success("GET authentication successful! Ready for exploit chain.")
        
        # Use session for subsequent exploit steps
        response = session.get("https://httpbin.org/get")
        logger.info(f"Subsequent exploit request status: {response.status_code}")
        
        return session  # Return session for downstream chaining
        
    except AuthenticationError as e:
        logger.error(f"GET authentication failed: {e}")
        return None


def auth_config_object_example():
    """Example using AuthConfig object for advanced exploit chaining scenarios.
    
    Returns:
        requests.Session: Authenticated session for downstream chaining
    """
    
    try:
        # Create AuthConfig object for complex authentication scenarios
        # Note: httpbin.org/post always returns 200 for demo purposes.
        config = AuthConfig(
            url="https://httpbin.org/post",
            method="POST",
            credentials={
                "username": "admin",
                "password": "admin123"
            },
            success_indicators=["authenticated", "welcome"],
            failure_indicators=["invalid", "failed"],
            headers={
                "User-Agent": "LogicPwn/1.0",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=60,
            verify_ssl=False
        )
        
        logger.info("Using AuthConfig object for advanced authentication...")
        session = authenticate_session(config)
        logger.success("Authentication with AuthConfig successful! Ready for exploit chain.")
        
        return session  # Return session for downstream chaining
        
    except ValidationError as e:
        logger.error(f"AuthConfig validation error: {e}")
        return None
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        return None


def error_handling_example():
    """Example demonstrating comprehensive error handling for exploit chains.
    
    Returns:
        list: List of error messages caught for demonstration
    """
    
    error_messages = []
    
    # Test invalid URL configuration
    try:
        invalid_config = {
            "url": "invalid-url",
            "credentials": {"username": "test", "password": "test"}
        }
        session = authenticate_session(invalid_config)
    except ValidationError as e:
        error_msg = f"Caught expected validation error: {e}"
        logger.info(error_msg)
        error_messages.append(error_msg)
    
    # Test empty credentials
    try:
        empty_creds_config = {
            "url": "https://httpbin.org/post",
            "credentials": {}
        }
        session = authenticate_session(empty_creds_config)
    except ValidationError as e:
        error_msg = f"Caught expected validation error: {e}"
        logger.info(error_msg)
        error_messages.append(error_msg)
    
    # Test invalid HTTP method
    try:
        invalid_method_config = {
            "url": "https://httpbin.org/post",
            "method": "PUT",
            "credentials": {"username": "test", "password": "test"}
        }
        session = authenticate_session(invalid_method_config)
    except ValidationError as e:
        error_msg = f"Caught expected validation error: {e}"
        logger.info(error_msg)
        error_messages.append(error_msg)
    
    return error_messages


def session_persistence_example():
    """Example demonstrating session persistence for multi-step exploit chains.
    
    Returns:
        requests.Session: Authenticated session for downstream chaining
    """
    
    # Note: httpbin.org/post always returns 200 for demo purposes.
    # In real tests, use an app with actual login validation.
    auth_config = {
        "url": "https://httpbin.org/post",
        "credentials": {
            "username": "testuser",
            "password": "testpass"
        },
        "success_indicators": ["authenticated"]
    }
    
    try:
        logger.info("Creating authenticated session for multi-step exploit chain...")
        session = authenticate_session(auth_config)
        
        # Simulate multi-step exploit chain with persistent session
        exploit_steps = [
            "https://httpbin.org/get",      # Step 1: Reconnaissance
            "https://httpbin.org/headers",  # Step 2: Information gathering
            "https://httpbin.org/user-agent" # Step 3: Exploitation
        ]
        
        for i, url in enumerate(exploit_steps, 1):
            logger.info(f"Executing exploit step {i}: {url}")
            response = session.get(url)
            logger.info(f"Step {i} status: {response.status_code}")
            
        logger.success("Multi-step exploit chain completed successfully with persistent session")
        
        return session  # Return session for downstream chaining
        
    except AuthenticationError as e:
        logger.error(f"Session persistence example failed: {e}")
        return None


def demonstrate_session_chaining():
    """Demonstrate how to chain sessions from different authentication methods.
    
    This shows how you can use authenticated sessions from one example
    in subsequent exploit chains or other authentication scenarios.
    """
    
    logger.info("=== Demonstrating Session Chaining ===")
    
    # Get session from basic authentication
    session1 = basic_authentication_example()
    if session1:
        logger.info("Session 1 obtained successfully")
        
        # Use session1 for additional requests
        try:
            response = session1.get("https://httpbin.org/status/200")
            logger.info(f"Additional request with session1: {response.status_code}")
        except Exception as e:
            logger.error(f"Error with session1: {e}")
    else:
        logger.warning("Session 1 failed to authenticate")
    
    # Get session from GET authentication
    session2 = get_method_authentication_example()
    if session2:
        logger.info("Session 2 obtained successfully")
        
        # Use session2 for additional requests
        try:
            response = session2.get("https://httpbin.org/status/200")
            logger.info(f"Additional request with session2: {response.status_code}")
        except Exception as e:
            logger.error(f"Error with session2: {e}")
    else:
        logger.warning("Session 2 failed to authenticate")
    
    logger.info("=== Session Chaining Demonstration Complete ===")


if __name__ == "__main__":
    # Configure logging for exploit chain demonstrations
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    logger.info("=== LogicPwn Business Logic Exploitation Examples ===")
    logger.info("Note: Using httpbin.org for demonstration - always returns 200 OK")
    logger.info("In real scenarios, use applications with actual login validation")
    
    # Run exploit chain examples
    logger.info("\n1. Basic Authentication for Exploit Chaining")
    basic_authentication_example()
    
    logger.info("\n2. GET Method Authentication for Exploit Chains")
    get_method_authentication_example()
    
    logger.info("\n3. Advanced AuthConfig Object Example")
    auth_config_object_example()
    
    logger.info("\n4. Comprehensive Error Handling for Exploit Chains")
    error_handling_example()
    
    logger.info("\n5. Session Persistence for Multi-step Exploit Chains")
    session_persistence_example()
    
    logger.info("\n6. Session Chaining Demonstration")
    demonstrate_session_chaining()
    
    logger.info("\n=== Exploit Chain Examples Completed ===") 