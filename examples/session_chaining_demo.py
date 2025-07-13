"""
Session Chaining Demonstration for LogicPwn Framework.

This example shows how to chain authenticated sessions from different
authentication methods for advanced exploit workflows.
"""

import sys
from loguru import logger

# Add the project root to the path for imports
sys.path.insert(0, '.')

from logicpwn.core.auth import authenticate_session, validate_session
from logicpwn.exceptions import AuthenticationError


def create_basic_session():
    """Create a basic authenticated session.
    
    Returns:
        requests.Session: Authenticated session or None if failed
    """
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {
            "username": "user1",
            "password": "pass1"
        },
        "success_indicators": ["authenticated"],
        "timeout": 30
    }
    
    try:
        logger.info("Creating basic authenticated session...")
        session = authenticate_session(auth_config)
        logger.success("Basic session created successfully")
        return session
    except AuthenticationError as e:
        logger.error(f"Basic session creation failed: {e}")
        return None


def create_token_session():
    """Create a token-based authenticated session.
    
    Returns:
        requests.Session: Authenticated session or None if failed
    """
    auth_config = {
        "url": "https://httpbin.org/get",
        "method": "GET",
        "credentials": {
            "api_key": "token123",
            "client_id": "app123"
        },
        "headers": {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json"
        },
        "success_indicators": ["authenticated"],
        "timeout": 30
    }
    
    try:
        logger.info("Creating token-based authenticated session...")
        session = authenticate_session(auth_config)
        logger.success("Token session created successfully")
        return session
    except AuthenticationError as e:
        logger.error(f"Token session creation failed: {e}")
        return None


def exploit_with_session(session, session_name, target_url):
    """Use an authenticated session for exploit steps.
    
    Args:
        session: Authenticated session to use
        session_name: Name for logging purposes
        target_url: URL to exploit
    """
    if not session:
        logger.warning(f"{session_name}: No session available for exploitation")
        return False
    
    try:
        logger.info(f"{session_name}: Attempting exploit on {target_url}")
        response = session.get(target_url)
        
        if response.status_code == 200:
            logger.success(f"{session_name}: Exploit successful - {response.status_code}")
            return True
        else:
            logger.warning(f"{session_name}: Exploit failed - {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"{session_name}: Exploit error - {e}")
        return False


def demonstrate_session_chaining():
    """Demonstrate advanced session chaining for exploit workflows."""
    
    logger.info("=== Advanced Session Chaining Demonstration ===")
    
    # Create multiple sessions
    sessions = {
        "Basic Auth": create_basic_session(),
        "Token Auth": create_token_session()
    }
    
    # Define exploit targets
    exploit_targets = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers", 
        "https://httpbin.org/user-agent",
        "https://httpbin.org/status/200"
    ]
    
    # Execute exploit chains with different sessions
    for session_name, session in sessions.items():
        logger.info(f"\n--- {session_name} Exploit Chain ---")
        
        for i, target in enumerate(exploit_targets, 1):
            success = exploit_with_session(session, session_name, target)
            
            if success:
                logger.info(f"{session_name}: Step {i} completed successfully")
            else:
                logger.warning(f"{session_name}: Step {i} failed")
    
    # Demonstrate session validation
    logger.info("\n--- Session Validation ---")
    for session_name, session in sessions.items():
        if session:
            is_valid = validate_session(session, "https://httpbin.org/get")
            status = "VALID" if is_valid else "INVALID"
            logger.info(f"{session_name}: Session is {status}")
        else:
            logger.warning(f"{session_name}: No session to validate")
    
    logger.info("=== Session Chaining Demonstration Complete ===")


def demonstrate_session_reuse():
    """Demonstrate reusing sessions across different exploit scenarios."""
    
    logger.info("=== Session Reuse Demonstration ===")
    
    # Create a session
    session = create_basic_session()
    if not session:
        logger.error("Failed to create session for reuse demonstration")
        return
    
    # Reuse the same session for multiple scenarios
    scenarios = [
        ("Reconnaissance", "https://httpbin.org/get"),
        ("Information Gathering", "https://httpbin.org/headers"),
        ("Vulnerability Assessment", "https://httpbin.org/user-agent"),
        ("Exploitation", "https://httpbin.org/status/200"),
        ("Post-Exploitation", "https://httpbin.org/delay/1")
    ]
    
    for scenario_name, target_url in scenarios:
        logger.info(f"Executing {scenario_name} with persistent session...")
        success = exploit_with_session(session, "Reused Session", target_url)
        
        if success:
            logger.success(f"{scenario_name} completed successfully")
        else:
            logger.warning(f"{scenario_name} failed")
    
    logger.info("=== Session Reuse Demonstration Complete ===")


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    logger.info("=== LogicPwn Session Chaining Examples ===")
    logger.info("Note: Using httpbin.org for demonstration - always returns 200 OK")
    logger.info("In real scenarios, use applications with actual login validation")
    
    # Run demonstrations
    demonstrate_session_chaining()
    demonstrate_session_reuse()
    
    logger.info("=== Session Chaining Examples Completed ===") 