"""
Enhanced protocol support for LogicPwn access testing.

This module extends the access testing capabilities beyond HTTP/HTTPS to support:
- GraphQL endpoints with introspection and mutation testing
- WebSocket connections for real-time access control testing
- Enhanced SSL verification and security checks
"""

import asyncio
import json
import ssl
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

import requests
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI

from logicpwn.core.logging import log_error, log_info, log_warning

from .models import AccessTestResult


class ProtocolType(Enum):
    """Supported protocol types for access testing."""

    HTTP = "http"
    HTTPS = "https"
    GRAPHQL = "graphql"
    WEBSOCKET = "ws"
    WEBSOCKET_SECURE = "wss"


@dataclass
class GraphQLQuery:
    """GraphQL query configuration for access testing."""

    query: str
    variables: Optional[dict[str, Any]] = None
    operation_name: Optional[str] = None


@dataclass
class WebSocketConfig:
    """WebSocket connection configuration."""

    url: str
    headers: Optional[dict[str, str]] = None
    subprotocols: Optional[list[str]] = None
    timeout: int = 30
    ssl_context: Optional[ssl.SSLContext] = None


class GraphQLTester:
    """GraphQL-specific access testing capabilities."""

    def __init__(self, endpoint: str, headers: Optional[dict[str, str]] = None):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
            }
        }

        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }

        fragment InputValue on __InputValue {
            name
            description
            type { ...TypeRef }
            defaultValue
        }

        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                    ofType {
                                        kind
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

    def test_introspection(self, session: requests.Session) -> AccessTestResult:
        """Test GraphQL introspection access."""
        log_info(f"Testing GraphQL introspection on {self.endpoint}")

        try:
            response = session.post(
                self.endpoint,
                json={"query": self.introspection_query},
                headers=self.headers,
            )

            # Check if introspection is enabled
            introspection_enabled = (
                response.status_code == 200
                and "data" in response.json()
                and "__schema" in response.json().get("data", {})
            )

            return AccessTestResult(
                id_tested="introspection",
                endpoint_url=self.endpoint,
                status_code=response.status_code,
                access_granted=introspection_enabled,
                vulnerability_detected=introspection_enabled,  # Introspection can be a security risk
                response_indicators=["__schema"] if introspection_enabled else [],
                response_body=response.text[:500],
                request_method="POST",
                request_data={"query": self.introspection_query},
            )

        except Exception as e:
            log_error(f"GraphQL introspection test failed: {e}")
            return AccessTestResult(
                id_tested="introspection",
                endpoint_url=self.endpoint,
                status_code=0,
                access_granted=False,
                vulnerability_detected=False,
                response_indicators=[],
                error_message=str(e),
                request_method="POST",
            )

    def test_query_access(
        self, session: requests.Session, query: GraphQLQuery, id_value: Union[str, int]
    ) -> AccessTestResult:
        """Test access to specific GraphQL queries with ID substitution."""
        log_info(f"Testing GraphQL query access for ID {id_value}")

        try:
            # Substitute ID in query and variables
            processed_query = query.query.replace("{ID}", str(id_value))
            processed_variables = {}

            if query.variables:
                for key, value in query.variables.items():
                    if isinstance(value, str):
                        processed_variables[key] = value.replace("{ID}", str(id_value))
                    else:
                        processed_variables[key] = value

            payload = {
                "query": processed_query,
                "variables": processed_variables if processed_variables else None,
                "operationName": query.operation_name,
            }

            response = session.post(self.endpoint, json=payload, headers=self.headers)

            response_data = response.json() if response.content else {}
            has_data = "data" in response_data and response_data["data"] is not None
            has_errors = "errors" in response_data

            # Access granted if we get data without authorization errors
            access_granted = (
                response.status_code == 200
                and has_data
                and not (
                    has_errors
                    and any(
                        "unauthorized" in str(error).lower()
                        or "forbidden" in str(error).lower()
                        for error in response_data["errors"]
                    )
                )
            )

            return AccessTestResult(
                id_tested=id_value,
                endpoint_url=self.endpoint,
                status_code=response.status_code,
                access_granted=access_granted,
                vulnerability_detected=access_granted,  # Depends on authorization logic
                response_indicators=["data"] if has_data else [],
                response_body=response.text[:500],
                request_method="POST",
                request_data=payload,
            )

        except Exception as e:
            log_error(f"GraphQL query test failed for ID {id_value}: {e}")
            return AccessTestResult(
                id_tested=id_value,
                endpoint_url=self.endpoint,
                status_code=0,
                access_granted=False,
                vulnerability_detected=False,
                response_indicators=[],
                error_message=str(e),
                request_method="POST",
            )


class WebSocketTester:
    """WebSocket-specific access testing capabilities."""

    def __init__(self, config: WebSocketConfig):
        self.config = config

    async def test_connection_access(
        self, id_value: Union[str, int]
    ) -> AccessTestResult:
        """Test WebSocket connection access with ID-based authentication."""
        log_info(f"Testing WebSocket connection access for ID {id_value}")

        try:
            # Add ID to connection URL or headers
            url = self.config.url.replace("{ID}", str(id_value))
            headers = self.config.headers.copy() if self.config.headers else {}

            # Try to establish WebSocket connection
            async with websockets.connect(
                url,
                extra_headers=headers,
                subprotocols=self.config.subprotocols,
                ssl=self.config.ssl_context,
                timeout=self.config.timeout,
            ) as websocket:

                # Connection successful
                log_info(f"WebSocket connection established for ID {id_value}")

                # Try to send a test message
                test_message = json.dumps({"type": "ping", "id": str(id_value)})
                await websocket.send(test_message)

                try:
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)

                    return AccessTestResult(
                        id_tested=id_value,
                        endpoint_url=url,
                        status_code=200,  # WebSocket doesn't have HTTP status codes
                        access_granted=True,
                        vulnerability_detected=True,  # Successful connection might indicate access control issue
                        response_indicators=["connection_established"],
                        response_body=response[:500] if response else "",
                        request_method="WEBSOCKET",
                        request_data={"message": test_message},
                    )

                except asyncio.TimeoutError:
                    # Connection established but no response
                    return AccessTestResult(
                        id_tested=id_value,
                        endpoint_url=url,
                        status_code=200,
                        access_granted=True,
                        vulnerability_detected=True,
                        response_indicators=["connection_established", "no_response"],
                        response_body="",
                        request_method="WEBSOCKET",
                        request_data={"message": test_message},
                    )

        except ConnectionClosed as e:
            log_warning(f"WebSocket connection closed for ID {id_value}: {e}")
            return AccessTestResult(
                id_tested=id_value,
                endpoint_url=url if "url" in locals() else self.config.url,
                status_code=e.code if hasattr(e, "code") else 0,
                access_granted=False,
                vulnerability_detected=False,
                response_indicators=["connection_closed"],
                error_message=str(e),
                request_method="WEBSOCKET",
            )

        except InvalidURI as e:
            log_error(f"Invalid WebSocket URI for ID {id_value}: {e}")
            return AccessTestResult(
                id_tested=id_value,
                endpoint_url=self.config.url,
                status_code=0,
                access_granted=False,
                vulnerability_detected=False,
                response_indicators=[],
                error_message=f"Invalid URI: {str(e)}",
                request_method="WEBSOCKET",
            )

        except Exception as e:
            log_error(f"WebSocket connection test failed for ID {id_value}: {e}")
            return AccessTestResult(
                id_tested=id_value,
                endpoint_url=self.config.url,
                status_code=0,
                access_granted=False,
                vulnerability_detected=False,
                response_indicators=[],
                error_message=str(e),
                request_method="WEBSOCKET",
            )

    async def test_message_access(
        self, id_value: Union[str, int], messages: list[dict[str, Any]]
    ) -> list[AccessTestResult]:
        """Test access to specific WebSocket messages/channels."""
        results = []

        try:
            url = self.config.url.replace("{ID}", str(id_value))
            headers = self.config.headers.copy() if self.config.headers else {}

            async with websockets.connect(
                url,
                extra_headers=headers,
                subprotocols=self.config.subprotocols,
                ssl=self.config.ssl_context,
                timeout=self.config.timeout,
            ) as websocket:

                for i, message in enumerate(messages):
                    try:
                        # Send test message
                        message_str = json.dumps(message)
                        await websocket.send(message_str)

                        # Wait for response
                        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)

                        results.append(
                            AccessTestResult(
                                id_tested=f"{id_value}_msg_{i}",
                                endpoint_url=url,
                                status_code=200,
                                access_granted=True,
                                vulnerability_detected=True,
                                response_indicators=["message_response"],
                                response_body=response[:500],
                                request_method="WEBSOCKET",
                                request_data=message,
                            )
                        )

                    except asyncio.TimeoutError:
                        results.append(
                            AccessTestResult(
                                id_tested=f"{id_value}_msg_{i}",
                                endpoint_url=url,
                                status_code=200,
                                access_granted=False,
                                vulnerability_detected=False,
                                response_indicators=["no_response"],
                                response_body="",
                                request_method="WEBSOCKET",
                                request_data=message,
                            )
                        )

        except Exception as e:
            log_error(f"WebSocket message testing failed for ID {id_value}: {e}")
            results.append(
                AccessTestResult(
                    id_tested=id_value,
                    endpoint_url=self.config.url,
                    status_code=0,
                    access_granted=False,
                    vulnerability_detected=False,
                    response_indicators=[],
                    error_message=str(e),
                    request_method="WEBSOCKET",
                )
            )

        return results


def create_ssl_context(
    verify_ssl: bool = True,
    cert_file: Optional[str] = None,
    key_file: Optional[str] = None,
) -> ssl.SSLContext:
    """Create SSL context with enhanced security settings."""
    if verify_ssl:
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        # Enhanced security settings
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers(
            "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
        )

    else:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    if cert_file and key_file:
        context.load_cert_chain(cert_file, key_file)

    return context


def detect_protocol_type(url: str) -> ProtocolType:
    """Detect protocol type from URL."""
    url_lower = url.lower()

    if url_lower.startswith("ws://"):
        return ProtocolType.WEBSOCKET
    elif url_lower.startswith("wss://"):
        return ProtocolType.WEBSOCKET_SECURE
    elif "/graphql" in url_lower or url_lower.endswith("/graphql"):
        return ProtocolType.GRAPHQL
    elif url_lower.startswith("https://"):
        return ProtocolType.HTTPS
    else:
        return ProtocolType.HTTP
