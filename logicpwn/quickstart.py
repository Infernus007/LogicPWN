"""
LogicPWN Quick Start API

Simplified, high-level APIs for common security testing workflows.
Designed for ease of use without sacrificing power.

Examples:
    >>> # One-line IDOR test
    >>> from logicpwn import quick_idor_test
    >>> results = quick_idor_test(
    ...     "https://api.example.com",
    ...     "/api/users/{id}",
    ...     [1, 2, 3, "admin"]
    ... )

    >>> # Class-based testing
    >>> from logicpwn import SecurityTester
    >>> tester = SecurityTester("https://api.example.com")
    >>> tester.authenticate(username="user", password="pass")
    >>> results = tester.test_idor("/api/users/{id}", [1, 2, 3])
"""

from typing import Any, Optional, Union

import requests

from logicpwn.core.access import AccessDetectorConfig, detect_idor_flaws
from logicpwn.core.auth import AuthConfig, authenticate_session
from logicpwn.core.exploit_engine import load_exploit_chain_from_file, run_exploit_chain
from logicpwn.core.runner import HttpRunner


class SecurityTester:
    """
    High-level security testing interface with simplified API.

    This class provides an easy-to-use interface for common security tests
    without requiring deep knowledge of LogicPWN's internal architecture.

    Attributes:
        base_url: Target application base URL
        session: Authenticated requests session (set after authenticate())
        runner: HTTP request runner

    Examples:
        >>> # Basic usage
        >>> tester = SecurityTester("https://api.example.com")
        >>> tester.authenticate("admin", "password123")
        >>> results = tester.test_idor("/api/users/{id}", [1, 2, 3])

        >>> # With context manager (auto cleanup)
        >>> with SecurityTester("https://api.example.com") as tester:
        ...     tester.authenticate("admin", "password123")
        ...     results = tester.test_idor("/api/users/{id}", [1, 2, 3])
    """

    def __init__(self, base_url: str, verify_ssl: bool = True):
        """
        Initialize security tester.

        Args:
            base_url: Target application base URL (e.g., "https://api.example.com")
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.session: Optional[requests.Session] = None
        self.runner = HttpRunner()
        self._authenticated = False

    def authenticate(
        self,
        username: str,
        password: str,
        login_endpoint: str = "/login",
        method: str = "POST",
        username_field: str = "username",
        password_field: str = "password",
        success_indicators: Optional[list[str]] = None,
    ) -> bool:
        """
        Authenticate to the target application.

        Args:
            username: Username for authentication
            password: Password for authentication
            login_endpoint: Login endpoint path (default: "/login")
            method: HTTP method for login (default: "POST")
            username_field: Form field name for username (default: "username")
            password_field: Form field name for password (default: "password")
            success_indicators: List of text patterns indicating successful login
                              (default: ["dashboard", "welcome", "logged in"])

        Returns:
            True if authentication successful, False otherwise

        Examples:
            >>> tester.authenticate("admin", "pass123")
            >>> tester.authenticate("user", "secret", login_endpoint="/api/auth/login")
        """
        if success_indicators is None:
            success_indicators = ["dashboard", "welcome", "logged in", "success"]

        login_url = f"{self.base_url}{login_endpoint}"

        auth_config = AuthConfig(
            url=login_url,
            method=method,
            credentials={username_field: username, password_field: password},
            success_indicators=success_indicators,
            failure_indicators=["failed", "invalid", "incorrect"],
            verify_ssl=self.verify_ssl,
        )

        try:
            self.session = authenticate_session(auth_config)
            self._authenticated = True
            return True
        except Exception:
            self._authenticated = False
            return False

    def test_idor(
        self,
        endpoint_pattern: str,
        test_ids: list[Union[str, int]],
        success_indicators: Optional[list[str]] = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        """
        Test for Insecure Direct Object Reference (IDOR) vulnerabilities.

        Args:
            endpoint_pattern: Endpoint URL pattern with {id} placeholder
                            e.g., "/api/users/{id}" or "https://api.com/documents/{id}"
            test_ids: List of IDs to test for unauthorized access
            success_indicators: Text patterns indicating successful data access
                              (default: ["data", "user", "profile", "email"])
            method: HTTP method to use (default: "GET")

        Returns:
            Dictionary containing:
                - total_tested: Number of IDs tested
                - vulnerable_count: Number of IDOR vulnerabilities found
                - vulnerabilities: List of vulnerable endpoints
                - safe_endpoints: List of properly secured endpoints
                - summary: Human-readable summary

        Examples:
            >>> results = tester.test_idor("/api/users/{id}", [1, 2, 3, "admin"])
            >>> print(results['summary'])
            >>> for vuln in results['vulnerabilities']:
            ...     print(f"Vulnerable: {vuln.endpoint_url}")
        """
        if success_indicators is None:
            success_indicators = ["data", "user", "profile", "email", "details"]

        # Ensure we have a session
        if not self.session:
            self.session = requests.Session()

        # Build full URL if relative path provided
        if not endpoint_pattern.startswith("http"):
            endpoint_pattern = f"{self.base_url}{endpoint_pattern}"

        # Configure IDOR detector
        config = AccessDetectorConfig(
            method=method, request_timeout=30, max_concurrent_requests=10
        )

        # Run IDOR detection
        results = detect_idor_flaws(
            session=self.session,
            endpoint_template=endpoint_pattern,
            test_ids=[str(id_) for id_ in test_ids],
            success_indicators=success_indicators,
            failure_indicators=["denied", "unauthorized", "forbidden", "not found"],
            config=config,
        )

        # Analyze results
        vulnerabilities = [r for r in results if r.is_vulnerable]
        safe_endpoints = [r for r in results if not r.is_vulnerable]

        return {
            "total_tested": len(results),
            "vulnerable_count": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "safe_endpoints": safe_endpoints,
            "summary": f"Found {len(vulnerabilities)} IDOR vulnerabilities out of {len(results)} tests",
            "pass_rate": ((len(safe_endpoints) / len(results)) * 100) if results else 0,
        }

    def test_unauthorized_access(
        self, protected_endpoints: list[str], expected_status: int = 403
    ) -> dict[str, Any]:
        """
        Test if protected endpoints are properly secured.

        Tests whether endpoints that should be restricted (e.g., admin endpoints)
        are accessible without proper authorization.

        Args:
            protected_endpoints: List of endpoint paths that should be protected
            expected_status: Expected HTTP status for blocked access (default: 403)

        Returns:
            Dictionary containing:
                - accessible: List of improperly accessible endpoints
                - blocked: List of properly blocked endpoints
                - vulnerable: Boolean indicating if any endpoints are exposed
                - summary: Human-readable summary

        Examples:
            >>> results = tester.test_unauthorized_access([
            ...     "/api/admin/users",
            ...     "/api/admin/settings"
            ... ])
            >>> if results['vulnerable']:
            ...     print("Warning: Admin endpoints exposed!")
        """
        accessible = []
        blocked = []
        errors = []

        for endpoint in protected_endpoints:
            # Build full URL
            if not endpoint.startswith("http"):
                full_url = f"{self.base_url}{endpoint}"
            else:
                full_url = endpoint

            try:
                result = self.runner.get(full_url, verify_ssl=self.verify_ssl)

                if result.status_code == 200:
                    accessible.append(
                        {
                            "endpoint": endpoint,
                            "status": result.status_code,
                            "issue": "Endpoint accessible without proper authorization",
                        }
                    )
                elif result.status_code == expected_status:
                    blocked.append(endpoint)
                else:
                    # Unexpected status code
                    accessible.append(
                        {
                            "endpoint": endpoint,
                            "status": result.status_code,
                            "issue": f"Unexpected status {result.status_code} (expected {expected_status})",
                        }
                    )
            except Exception as e:
                errors.append({"endpoint": endpoint, "error": str(e)})

        return {
            "accessible": accessible,
            "blocked": blocked,
            "errors": errors,
            "vulnerable": len(accessible) > 0,
            "summary": f"{len(accessible)} endpoints improperly accessible, {len(blocked)} properly secured",
            "pass_rate": (
                ((len(blocked) / len(protected_endpoints)) * 100)
                if protected_endpoints
                else 0
            ),
        }

    def run_exploit_chain(self, yaml_file: str) -> list[Any]:
        """
        Execute a pre-defined exploit chain from YAML file.

        Args:
            yaml_file: Path to exploit chain YAML configuration file

        Returns:
            List of step execution results

        Examples:
            >>> results = tester.run_exploit_chain("tests/sql_injection_chain.yaml")
            >>> successful = sum(1 for r in results if r.status.value == "success")
            >>> print(f"Completed {successful}/{len(results)} steps")
        """
        chain = load_exploit_chain_from_file(yaml_file)
        return run_exploit_chain(chain, runner=self.runner)

    def __enter__(self):
        """Context manager entry - returns self for 'with' statements."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.close()

    def close(self):
        """Clean up resources (sessions, connections)."""
        if self.session:
            self.session.close()
        if hasattr(self.runner, "session") and self.runner.session:
            self.runner.session.close()


# Convenience functions for one-off tests


def quick_idor_test(
    target_url: str,
    endpoint_pattern: str,
    test_ids: list[Union[str, int]],
    username: Optional[str] = None,
    password: Optional[str] = None,
    success_indicators: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Quick one-function IDOR vulnerability test.

    Simplest way to test for IDOR vulnerabilities without setting up classes.

    Args:
        target_url: Base URL of target application
        endpoint_pattern: Endpoint with {id} placeholder (e.g., "/api/users/{id}")
        test_ids: List of IDs to test
        username: Optional username for authentication
        password: Optional password for authentication
        success_indicators: Optional list of success text patterns

    Returns:
        Dictionary with test results including vulnerabilities found

    Examples:
        >>> # Unauthenticated test
        >>> results = quick_idor_test(
        ...     "https://api.example.com",
        ...     "/api/users/{id}",
        ...     [1, 2, 3, "admin"]
        ... )

        >>> # Authenticated test
        >>> results = quick_idor_test(
        ...     "https://api.example.com",
        ...     "/api/documents/{id}",
        ...     [1, 2, 3],
        ...     username="testuser",
        ...     password="password123"
        ... )

        >>> print(results['summary'])
        >>> if results['vulnerable_count'] > 0:
        ...     print("Vulnerabilities found!")
    """
    tester = SecurityTester(target_url)

    # Authenticate if credentials provided
    if username and password:
        if not tester.authenticate(username, password):
            return {
                "error": "Authentication failed",
                "total_tested": 0,
                "vulnerable_count": 0,
                "vulnerabilities": [],
                "summary": "Authentication failed - could not run tests",
            }

    # Run IDOR test
    return tester.test_idor(endpoint_pattern, test_ids, success_indicators)


def quick_auth_test(
    login_url: str,
    username: str,
    password: str,
    success_indicators: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Quick authentication test.

    Test if authentication works and returns session information.

    Args:
        login_url: Full URL to login endpoint
        username: Username for authentication
        password: Password for authentication
        success_indicators: Optional list of success text patterns

    Returns:
        Dictionary with authentication results

    Examples:
        >>> result = quick_auth_test(
        ...     "https://app.com/login",
        ...     "admin",
        ...     "password123"
        ... )
        >>> if result['authenticated']:
        ...     print("Login successful!")
        ...     print(f"Session cookies: {result['cookies']}")
    """
    if success_indicators is None:
        success_indicators = ["dashboard", "welcome", "logged in", "success"]

    auth_config = AuthConfig(
        url=login_url,
        method="POST",
        credentials={"username": username, "password": password},
        success_indicators=success_indicators,
    )

    try:
        session = authenticate_session(auth_config)
        return {
            "authenticated": True,
            "success": True,
            "session": session,
            "cookies": dict(session.cookies),
            "message": "Authentication successful",
        }
    except Exception as e:
        return {
            "authenticated": False,
            "success": False,
            "error": str(e),
            "message": f"Authentication failed: {str(e)}",
        }


def quick_exploit_chain(
    yaml_file: str, runner: Optional[HttpRunner] = None
) -> list[Any]:
    """
    Quick exploit chain execution from YAML file.

    Load and execute an exploit chain in one function call.

    Args:
        yaml_file: Path to exploit chain YAML configuration
        runner: Optional custom HttpRunner instance

    Returns:
        List of step execution results

    Examples:
        >>> results = quick_exploit_chain("exploits/sql_injection.yaml")
        >>> successful = sum(1 for r in results if r.status.value == "success")
        >>> print(f"Completed {successful}/{len(results)} steps successfully")

        >>> # Check if all steps succeeded
        >>> if all(r.status.value == "success" for r in results):
        ...     print("All exploit steps successful - vulnerability confirmed!")
    """
    chain = load_exploit_chain_from_file(yaml_file)
    return run_exploit_chain(chain, runner=runner)


# Export public API
__all__ = [
    "SecurityTester",
    "quick_idor_test",
    "quick_auth_test",
    "quick_exploit_chain",
]
