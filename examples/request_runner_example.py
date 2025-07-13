"""
Request Runner Examples for LogicPwn Framework.

This example demonstrates how to use the request runner module with
authenticated sessions for exploit chaining and multi-step security
testing workflows. Shows various request types and error handling
for advanced penetration testing scenarios.

Note: This example uses httpbin.org for demonstration purposes.
      httpbin.org always returns 200 OK regardless of credentials,
      making it perfect for testing the request framework
      without requiring actual login validation.
"""

import sys
from loguru import logger

# Add the project root to the path for imports
sys.path.insert(0, '.')

from logicpwn.core.auth import authenticate_session
from logicpwn.core.runner import send_request
from logicpwn.models.request_config import RequestConfig
from logicpwn.exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)


def demonstrate_get_request():
    """Demonstrate GET request with query parameters for exploit chaining.
    
    Returns:
        requests.Response: Response from the GET request
    """
    
    # First authenticate to get a session
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["authenticated"]
    }
    
    try:
        logger.info("Authenticating for GET request demonstration...")
        session = authenticate_session(auth_config)
        
        # Configure GET request with query parameters
        get_config = RequestConfig(
            url="https://httpbin.org/get",
            method="GET",
            params={"q": "logicpwn", "test": "value", "page": 1},
            headers={"User-Agent": "LogicPwn-Test"}
        )
        
        logger.info("Sending GET request with query parameters...")
        response = send_request(session, get_config)
        
        logger.success(f"GET request successful: {response.status_code}")
        logger.info(f"Response size: {len(response.content)} bytes")
        
        # Safe logging - show response preview
        response_preview = response.text[:200]
        logger.debug(f"Response preview: {response_preview}...")
        
        return response
        
    except (ValidationError, NetworkError, TimeoutError, ResponseError) as e:
        logger.error(f"GET request failed: {e}")
        return None


def demonstrate_post_request():
    """Demonstrate POST request with JSON body for exploit chaining.
    
    Returns:
        requests.Response: Response from the POST request
    """
    
    # First authenticate to get a session
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["authenticated"]
    }
    
    try:
        logger.info("Authenticating for POST request demonstration...")
        session = authenticate_session(auth_config)
        
        # Configure POST request with JSON body
        post_config = RequestConfig(
            url="https://httpbin.org/post",
            method="POST",
            json_data={
                "message": "Hello from LogicPwn",
                "test": True,
                "data": {"key": "value", "nested": {"item": "test"}}
            },
            headers={"Content-Type": "application/json"}
        )
        
        logger.info("Sending POST request with JSON body...")
        response = send_request(session, post_config)
        
        logger.success(f"POST request successful: {response.status_code}")
        
        # Parse and log response data
        try:
            response_data = response.json()
            logger.info(f"Response data keys: {list(response_data.keys())}")
        except Exception as e:
            logger.warning(f"Could not parse JSON response: {e}")
        
        return response
        
    except (ValidationError, NetworkError, TimeoutError, ResponseError) as e:
        logger.error(f"POST request failed: {e}")
        return None


def demonstrate_form_request():
    """Demonstrate POST request with form data for exploit chaining.
    
    Returns:
        requests.Response: Response from the form request
    """
    
    # First authenticate to get a session
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["authenticated"]
    }
    
    try:
        logger.info("Authenticating for form request demonstration...")
        session = authenticate_session(auth_config)
        
        # Configure POST request with form data
        form_config = RequestConfig(
            url="https://httpbin.org/post",
            method="POST",
            data={
                "username": "testuser",
                "password": "testpass",
                "action": "login",
                "remember": "true"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        logger.info("Sending POST request with form data...")
        response = send_request(session, form_config)
        
        logger.success(f"Form request successful: {response.status_code}")
        
        return response
        
    except (ValidationError, NetworkError, TimeoutError, ResponseError) as e:
        logger.error(f"Form request failed: {e}")
        return None


def demonstrate_raw_body_request():
    """Demonstrate POST request with raw body for exploit chaining.
    
    Returns:
        requests.Response: Response from the raw body request
    """
    
    # First authenticate to get a session
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["authenticated"]
    }
    
    try:
        logger.info("Authenticating for raw body request demonstration...")
        session = authenticate_session(auth_config)
        
        # Configure POST request with raw XML body
        xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<request>
    <action>test</action>
    <data>
        <key>value</key>
        <nested>
            <item>test</item>
        </nested>
    </data>
</request>"""
        
        raw_config = RequestConfig(
            url="https://httpbin.org/post",
            method="POST",
            raw_body=xml_body,
            headers={"Content-Type": "application/xml"}
        )
        
        logger.info("Sending POST request with raw XML body...")
        response = send_request(session, raw_config)
        
        logger.success(f"Raw body request successful: {response.status_code}")
        
        return response
        
    except (ValidationError, NetworkError, TimeoutError, ResponseError) as e:
        logger.error(f"Raw body request failed: {e}")
        return None


def demonstrate_all_http_methods():
    """Demonstrate all supported HTTP methods for exploit chaining.
    
    Returns:
        dict: Dictionary mapping HTTP methods to their responses
    """
    
    # First authenticate to get a session
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["authenticated"]
    }
    
    try:
        logger.info("Authenticating for HTTP methods demonstration...")
        session = authenticate_session(auth_config)
        
        # Test all supported HTTP methods
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]
        responses = {}
        
        for method in methods:
            logger.info(f"Testing {method} method...")
            
            # Add specific logging for HEAD requests
            if method == "HEAD":
                logger.info(f"{method} request - will return headers only, no body expected.")
            
            config = RequestConfig(
                url=f"https://httpbin.org/{method.lower()}",
                method=method,
                headers={"User-Agent": "LogicPwn-Test"}
            )
            
            # Add body for methods that support it
            if method in ["POST", "PUT", "PATCH"]:
                config.json_data = {"method": method, "test": True}
            
            try:
                response = send_request(session, config)
                responses[method] = response
                logger.success(f"{method} request successful: {response.status_code}")
                
                # Add specific logging for HEAD response
                if method == "HEAD":
                    logger.info(f"{method} response headers: {dict(response.headers)}")
                
            except Exception as e:
                logger.error(f"{method} request failed: {e}")
                responses[method] = None
        
        return responses
        
    except Exception as e:
        logger.error(f"HTTP methods demonstration failed: {e}")
        return {}


def demonstrate_error_handling():
    """Demonstrate comprehensive error handling for exploit chains.
    
    Returns:
        list: List of error messages caught for demonstration
    """
    
    error_messages = []
    
    # Test invalid URL
    try:
        invalid_config = {
            "url": "not-a-valid-url",
            "method": "GET"
        }
        session = authenticate_session({"url": "https://httpbin.org/post", "credentials": {"test": "test"}})
        response = send_request(session, invalid_config)
    except ValidationError as e:
        error_msg = f"Caught expected validation error: {e}"
        logger.info(error_msg)
        error_messages.append(error_msg)
    
    # Test invalid HTTP method
    try:
        invalid_method_config = {
            "url": "https://httpbin.org/get",
            "method": "INVALID_METHOD"
        }
        session = authenticate_session({"url": "https://httpbin.org/post", "credentials": {"test": "test"}})
        response = send_request(session, invalid_method_config)
    except ValidationError as e:
        error_msg = f"Caught expected validation error: {e}"
        logger.info(error_msg)
        error_messages.append(error_msg)
    
    # Test multiple body types
    try:
        multiple_body_config = {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "data": {"form": "data"},
            "json_data": {"json": "data"}
        }
        session = authenticate_session({"url": "https://httpbin.org/post", "credentials": {"test": "test"}})
        response = send_request(session, multiple_body_config)
    except ValidationError as e:
        error_msg = f"Caught expected validation error: {e}"
        logger.info(error_msg)
        error_messages.append(error_msg)
    
    return error_messages


def demonstrate_exploit_chain():
    """Demonstrate a complete exploit chain using authenticated requests.
    
    This shows how to chain multiple requests together for a complete
    security testing workflow.
    """
    
    logger.info("=== Starting Exploit Chain Demonstration ===")
    
    # Step 1: Authenticate
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "admin", "password": "admin123"},
        "success_indicators": ["authenticated"]
    }
    
    try:
        logger.info("Step 1: Authenticating...")
        session = authenticate_session(auth_config)
        logger.success("Authentication successful")
        
        # Step 2: Reconnaissance - GET request to gather information
        logger.info("Step 2: Performing reconnaissance...")
        recon_config = RequestConfig(
            url="https://httpbin.org/get",
            method="GET",
            params={"action": "recon", "target": "admin_panel"},
            headers={"User-Agent": "LogicPwn-Recon"}
        )
        recon_response = send_request(session, recon_config)
        logger.success(f"Reconnaissance completed: {recon_response.status_code}")
        
        # Step 3: Information gathering - POST request to test endpoints
        logger.info("Step 3: Gathering information...")
        info_config = RequestConfig(
            url="https://httpbin.org/post",
            method="POST",
            json_data={"action": "info_gather", "endpoints": ["users", "admin", "api"]},
            headers={"Content-Type": "application/json"}
        )
        info_response = send_request(session, info_config)
        logger.success(f"Information gathering completed: {info_response.status_code}")
        
        # Step 4: Exploitation - PUT request to test privilege escalation
        logger.info("Step 4: Testing exploitation...")
        exploit_config = RequestConfig(
            url="https://httpbin.org/put",
            method="PUT",
            json_data={"action": "exploit", "payload": "privilege_escalation"},
            headers={"Content-Type": "application/json"}
        )
        exploit_response = send_request(session, exploit_config)
        logger.success(f"Exploitation test completed: {exploit_response.status_code}")
        
        # Step 5: Post-exploitation - DELETE request to clean up
        logger.info("Step 5: Post-exploitation cleanup...")
        cleanup_config = RequestConfig(
            url="https://httpbin.org/delete",
            method="DELETE",
            headers={"Authorization": "Bearer cleanup_token"}
        )
        cleanup_response = send_request(session, cleanup_config)
        logger.success(f"Cleanup completed: {cleanup_response.status_code}")
        
        logger.success("=== Exploit Chain Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Exploit chain failed: {e}")


if __name__ == "__main__":
    # Configure logging for exploit chain demonstrations
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    logger.info("=== LogicPwn Request Runner Examples ===")
    logger.info("Note: Using httpbin.org for demonstration - always returns 200 OK")
    logger.info("In real scenarios, use applications with actual login validation")
    
    # Run request examples
    logger.info("\n1. GET Request with Query Parameters")
    demonstrate_get_request()
    
    logger.info("\n2. POST Request with JSON Body")
    demonstrate_post_request()
    
    logger.info("\n3. POST Request with Form Data")
    demonstrate_form_request()
    
    logger.info("\n4. POST Request with Raw Body")
    demonstrate_raw_body_request()
    
    logger.info("\n5. All HTTP Methods Demonstration")
    demonstrate_all_http_methods()
    
    logger.info("\n6. Error Handling Demonstration")
    demonstrate_error_handling()
    
    logger.info("\n7. Complete Exploit Chain Demonstration")
    demonstrate_exploit_chain()
    
    logger.info("\n=== Request Runner Examples Completed ===") 