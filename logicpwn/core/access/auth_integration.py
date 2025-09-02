"""
Authentication integration for access testing module.

This module provides seamless integration between the access testing capabilities
and the authentication module, enabling automatic session management and
authenticated testing workflows.
"""

from dataclasses import dataclass
from typing import Optional, Union

import requests

from logicpwn.core.auth import (
    AuthConfig,
    LogicPwnHTTPClient,
    authenticate_session,
    create_authenticated_client,
    validate_session,
)
from logicpwn.core.logging import log_error, log_info, log_warning

from .core_logic import _test_single_id
from .models import AccessDetectorConfig, AccessTestResult
from .protocol_support import (
    GraphQLQuery,
    GraphQLTester,
    WebSocketConfig,
    WebSocketTester,
)


@dataclass
class AuthenticatedAccessConfig:
    """Configuration for authenticated access testing."""

    auth_config: AuthConfig
    access_config: AccessDetectorConfig
    auto_reauth: bool = True
    session_validation_interval: int = 10  # Validate session every N requests
    max_reauth_attempts: int = 3


class AuthenticatedAccessTester:
    """Access tester with integrated authentication management."""

    def __init__(self, config: AuthenticatedAccessConfig):
        self.config = config
        self.session: Optional[requests.Session] = None
        self.authenticated_client: Optional[LogicPwnHTTPClient] = None
        self.request_count = 0
        self.reauth_attempts = 0

    def _ensure_authenticated_session(self) -> requests.Session:
        """Ensure we have a valid authenticated session."""
        if self.session is None or self._should_revalidate_session():
            self._authenticate()
        return self.session

    def _should_revalidate_session(self) -> bool:
        """Check if session should be revalidated."""
        return (
            self.config.auto_reauth
            and self.request_count > 0
            and self.request_count % self.config.session_validation_interval == 0
        )

    def _authenticate(self) -> None:
        """Perform authentication and create session."""
        try:
            log_info("Authenticating session for access testing")

            # Use the auth module to create authenticated session
            self.session = authenticate_session(self.config.auth_config)
            self.authenticated_client = create_authenticated_client(
                self.config.auth_config, session=self.session
            )

            # Validate the session was created successfully
            if not validate_session(self.session, self.config.auth_config):
                raise Exception("Session validation failed after authentication")

            log_info("Authentication successful")
            self.reauth_attempts = 0

        except Exception as e:
            self.reauth_attempts += 1
            log_error(f"Authentication failed (attempt {self.reauth_attempts}): {e}")

            if self.reauth_attempts >= self.config.max_reauth_attempts:
                raise Exception(
                    f"Max authentication attempts ({self.config.max_reauth_attempts}) exceeded"
                )

            # Retry authentication
            self._authenticate()

    def test_single_id_authenticated(
        self,
        endpoint_url: str,
        id_value: Union[str, int],
        success_indicators: list[str],
        failure_indicators: list[str],
        request_timeout: int = 30,
    ) -> AccessTestResult:
        """Test single ID with authenticated session."""
        session = self._ensure_authenticated_session()
        self.request_count += 1

        try:
            result = _test_single_id(
                session=session,
                endpoint_url=endpoint_url,
                id_value=id_value,
                success_indicators=success_indicators,
                failure_indicators=failure_indicators,
                request_timeout=request_timeout,
                config=self.config.access_config,
            )

            # Check if we got an authentication error
            if self._is_auth_error(result):
                log_warning(
                    f"Authentication error detected for ID {id_value}, re-authenticating"
                )
                self._authenticate()

                # Retry with new session
                session = self._ensure_authenticated_session()
                result = _test_single_id(
                    session=session,
                    endpoint_url=endpoint_url,
                    id_value=id_value,
                    success_indicators=success_indicators,
                    failure_indicators=failure_indicators,
                    request_timeout=request_timeout,
                    config=self.config.access_config,
                )

            return result

        except Exception as e:
            log_error(f"Authenticated access test failed for ID {id_value}: {e}")
            return AccessTestResult(
                id_tested=id_value,
                endpoint_url=endpoint_url,
                status_code=0,
                access_granted=False,
                vulnerability_detected=False,
                response_indicators=[],
                error_message=str(e),
            )

    def test_multiple_ids_authenticated(
        self,
        endpoint_template: str,
        id_values: list[Union[str, int]],
        success_indicators: list[str],
        failure_indicators: list[str],
        request_timeout: int = 30,
    ) -> list[AccessTestResult]:
        """Test multiple IDs with authenticated session."""
        results = []

        for id_value in id_values:
            endpoint_url = endpoint_template.replace("{ID}", str(id_value))
            result = self.test_single_id_authenticated(
                endpoint_url=endpoint_url,
                id_value=id_value,
                success_indicators=success_indicators,
                failure_indicators=failure_indicators,
                request_timeout=request_timeout,
            )
            results.append(result)

        return results

    def test_graphql_authenticated(
        self,
        endpoint: str,
        query: GraphQLQuery,
        id_values: list[Union[str, int]],
        headers: Optional[dict[str, str]] = None,
    ) -> list[AccessTestResult]:
        """Test GraphQL queries with authenticated session."""
        session = self._ensure_authenticated_session()

        # Merge auth headers with provided headers
        merged_headers = {}
        if hasattr(self.authenticated_client, "session") and hasattr(
            self.authenticated_client.session, "headers"
        ):
            merged_headers.update(dict(self.authenticated_client.session.headers))
        if headers:
            merged_headers.update(headers)

        graphql_tester = GraphQLTester(endpoint, merged_headers)
        results = []

        for id_value in id_values:
            self.request_count += 1
            result = graphql_tester.test_query_access(session, query, id_value)

            # Check for auth errors and retry if needed
            if self._is_auth_error(result):
                log_warning(
                    f"GraphQL authentication error for ID {id_value}, re-authenticating"
                )
                self._authenticate()
                session = self._ensure_authenticated_session()
                result = graphql_tester.test_query_access(session, query, id_value)

            results.append(result)

        return results

    async def test_websocket_authenticated(
        self, ws_config: WebSocketConfig, id_values: list[Union[str, int]]
    ) -> list[AccessTestResult]:
        """Test WebSocket connections with authenticated headers."""
        # Add authentication headers to WebSocket config
        auth_headers = {}
        if hasattr(self.authenticated_client, "session") and hasattr(
            self.authenticated_client.session, "headers"
        ):
            auth_headers.update(dict(self.authenticated_client.session.headers))

        if ws_config.headers:
            auth_headers.update(ws_config.headers)

        authenticated_ws_config = WebSocketConfig(
            url=ws_config.url,
            headers=auth_headers,
            subprotocols=ws_config.subprotocols,
            timeout=ws_config.timeout,
            ssl_context=ws_config.ssl_context,
        )

        ws_tester = WebSocketTester(authenticated_ws_config)
        results = []

        for id_value in id_values:
            result = await ws_tester.test_connection_access(id_value)
            results.append(result)

        return results

    def _is_auth_error(self, result: AccessTestResult) -> bool:
        """Check if result indicates an authentication error."""
        auth_error_indicators = [
            "unauthorized",
            "unauthenticated",
            "login required",
            "access denied",
            "forbidden",
            "session expired",
        ]

        # Check status code
        if result.status_code in [401, 403]:
            return True

        # Check response body and indicators
        response_text = (result.response_body or "").lower()
        for indicator in auth_error_indicators:
            if indicator in response_text:
                return True

        # Check response indicators
        for indicator in result.response_indicators:
            if any(auth_ind in indicator.lower() for auth_ind in auth_error_indicators):
                return True

        return False

    def close(self) -> None:
        """Clean up resources."""
        if self.session:
            self.session.close()
        if self.authenticated_client:
            self.authenticated_client.close()


def create_authenticated_access_tester(
    auth_url: str,
    auth_method: str,
    credentials: dict[str, str],
    access_config: AccessDetectorConfig,
    success_indicators: list[str],
    failure_indicators: list[str],
    **kwargs,
) -> AuthenticatedAccessTester:
    """Create an authenticated access tester with simplified configuration."""

    auth_config = AuthConfig(
        url=auth_url,
        method=auth_method,
        credentials=credentials,
        success_indicators=success_indicators,
        failure_indicators=failure_indicators,
        **kwargs,
    )

    authenticated_config = AuthenticatedAccessConfig(
        auth_config=auth_config, access_config=access_config
    )

    return AuthenticatedAccessTester(authenticated_config)


async def run_authenticated_access_test_suite(
    tester: AuthenticatedAccessTester, test_suite: dict[str, any]
) -> dict[str, list[AccessTestResult]]:
    """Run a comprehensive authenticated access test suite."""
    results = {}

    # HTTP/HTTPS tests
    if "http_tests" in test_suite:
        http_tests = test_suite["http_tests"]
        results["http"] = tester.test_multiple_ids_authenticated(
            endpoint_template=http_tests["endpoint_template"],
            id_values=http_tests["id_values"],
            success_indicators=http_tests["success_indicators"],
            failure_indicators=http_tests["failure_indicators"],
            request_timeout=http_tests.get("timeout", 30),
        )

    # GraphQL tests
    if "graphql_tests" in test_suite:
        graphql_tests = test_suite["graphql_tests"]
        query = GraphQLQuery(
            query=graphql_tests["query"],
            variables=graphql_tests.get("variables"),
            operation_name=graphql_tests.get("operation_name"),
        )
        results["graphql"] = tester.test_graphql_authenticated(
            endpoint=graphql_tests["endpoint"],
            query=query,
            id_values=graphql_tests["id_values"],
            headers=graphql_tests.get("headers"),
        )

    # WebSocket tests
    if "websocket_tests" in test_suite:
        ws_tests = test_suite["websocket_tests"]
        ws_config = WebSocketConfig(
            url=ws_tests["url"],
            headers=ws_tests.get("headers"),
            subprotocols=ws_tests.get("subprotocols"),
            timeout=ws_tests.get("timeout", 30),
        )
        results["websocket"] = await tester.test_websocket_authenticated(
            ws_config=ws_config, id_values=ws_tests["id_values"]
        )

    return results
