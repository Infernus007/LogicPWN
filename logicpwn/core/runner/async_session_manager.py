"""
Async session management for LogicPwn with enhanced security and lifecycle management.

Security Features:
- SSL/TLS certificate validation with warnings
- Secure session lifecycle management
- Enhanced error handling and recovery
- Connection pooling with security controls
"""

import asyncio
import ssl
import warnings
from typing import Any, Dict, List, Optional, Union

import aiohttp
from loguru import logger

from logicpwn.core.config.config_utils import get_timeout
from logicpwn.core.logging import log_error, log_info, log_warning
from logicpwn.exceptions import (
    NetworkError,
    RequestExecutionError,
    ResponseError,
    TimeoutError,
    ValidationError,
)
from logicpwn.models.request_result import RequestResult


class AsyncSessionManager:
    """Async session manager with enhanced security and lifecycle management."""

    def __init__(
        self,
        auth_config: Optional[dict[str, Any]] = None,
        max_concurrent: int = 10,
        timeout: Optional[int] = None,
        verify_ssl: bool = True,
        min_tls_version: str = "TLSv1.2",
        warn_on_ssl_disabled: bool = True,
    ):
        """
        Initialize async session manager with enhanced security.

        Args:
            auth_config: Authentication configuration
            max_concurrent: Maximum concurrent requests
            timeout: Default timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            min_tls_version: Minimum TLS version to use
            warn_on_ssl_disabled: Whether to warn when SSL is disabled
        """
        self.auth_config = auth_config
        self.max_concurrent = max_concurrent
        self.timeout = timeout or get_timeout()
        self.verify_ssl = verify_ssl
        self.min_tls_version = min_tls_version
        self.warn_on_ssl_disabled = warn_on_ssl_disabled
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookies: dict[str, str] = {}
        self.headers: dict[str, str] = {}
        self._session_closed = False

    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context with security warnings and proper configuration."""
        if not self.verify_ssl:
            if self.warn_on_ssl_disabled:
                warnings.warn(
                    "SSL verification is disabled. This allows man-in-the-middle attacks. "
                    "Only use this in controlled testing environments.",
                    UserWarning,
                    stacklevel=2,
                )
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

        # Create secure SSL context
        context = ssl.create_default_context()

        # Set minimum TLS version for security
        if self.min_tls_version == "TLSv1.2":
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        elif self.min_tls_version == "TLSv1.3":
            context.minimum_version = ssl.TLSVersion.TLSv1_3

        return context

    @property
    def session_closed(self) -> bool:
        """Check if the session was properly closed."""
        return self._session_closed

    async def __aenter__(self):
        """Initialize session with enhanced security configuration."""
        ssl_context = self._create_ssl_context()

        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=self.max_concurrent,
            ssl=ssl_context,
            verify_ssl=self.verify_ssl,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        timeout_config = aiohttp.ClientTimeout(total=self.timeout)

        # Set secure default headers
        default_headers = {
            "User-Agent": "LogicPwn-SessionManager/2.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        self.session = aiohttp.ClientSession(
            connector=connector, timeout=timeout_config, headers=default_headers
        )

        if self.auth_config:
            await self.authenticate()

        log_info(
            "Enhanced session manager initialized",
            {
                "ssl_verification": self.verify_ssl,
                "min_tls_version": self.min_tls_version,
                "max_concurrent": self.max_concurrent,
            },
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with enhanced cleanup."""
        if self.session:
            try:
                await self.session.close()
                # Wait for underlying connections to close properly
                await asyncio.sleep(0.1)
                self._session_closed = True
                log_info("Session manager closed successfully")
            except Exception as e:
                log_error(
                    e, {"component": "AsyncSessionManager", "action": "session_cleanup"}
                )
                self._session_closed = False
            finally:
                self.session = None
        else:
            self._session_closed = False

    async def authenticate(self) -> bool:
        """
        Authenticate using the provided configuration.

        Returns:
            True if authentication successful, False otherwise

        Raises:
            ValidationError: If no authentication configuration provided
        """
        if not self.auth_config:
            raise ValidationError("No authentication configuration provided")

        try:
            auth_url = self.auth_config["url"]
            method = self.auth_config.get("method", "POST")
            credentials = self.auth_config.get("credentials", {})
            headers = self.auth_config.get("headers", {})

            request_data = credentials.copy()

            async with self.session.request(
                method=method, url=auth_url, data=request_data, headers=headers
            ) as response:
                if response.status == 200:
                    # Update cookies and headers from successful auth
                    if hasattr(response.cookies, "items"):
                        # Handle dictionary-like cookie objects (for mocks)
                        for key, value in response.cookies.items():
                            self.cookies[key] = value
                    else:
                        # Handle real aiohttp cookie objects
                        for cookie in response.cookies:
                            try:
                                if hasattr(cookie, "key") and hasattr(cookie, "value"):
                                    # aiohttp cookie object
                                    self.cookies[cookie.key] = cookie.value
                                elif hasattr(cookie, "name") and hasattr(
                                    cookie, "value"
                                ):
                                    # requests-style cookie
                                    self.cookies[cookie.name] = cookie.value
                                else:
                                    # Handle as string (for mocks)
                                    cookie_str = str(cookie)
                                    if "=" in cookie_str:
                                        key, value = cookie_str.split("=", 1)
                                        self.cookies[key] = value
                            except (AttributeError, ValueError) as e:
                                log_warning(
                                    f"Failed to parse cookie: {cookie}, error: {e}"
                                )

                    self.headers.update(headers)
                    log_info(
                        "Authentication successful",
                        {"url": auth_url, "status": response.status},
                    )
                    return True
                else:
                    log_error(
                        NetworkError(f"Authentication failed: {response.status}"),
                        {"url": auth_url, "status": response.status},
                    )
                    return False

        except aiohttp.ClientError as e:
            log_error(
                NetworkError(f"Authentication network error: {str(e)}"),
                {"url": self.auth_config.get("url", "unknown")},
            )
            return False
        except Exception as e:
            log_error(
                RequestExecutionError(f"Authentication error: {str(e)}"),
                {"url": self.auth_config.get("url", "unknown")},
            )
            return False

    async def get(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request("DELETE", url, **kwargs)

    async def _send_authenticated_request(
        self, method: str, url: str, **kwargs
    ) -> RequestResult:
        headers = kwargs.get("headers", {}).copy()
        headers.update(self.headers)
        cookies = kwargs.get("cookies", {}).copy()
        cookies.update(self.cookies)
        import aiohttp

        request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers,
            "cookies": cookies,
            **{k: v for k, v in kwargs.items() if k not in ["headers", "cookies"]},
        }
        async with self.session.request(**request_kwargs) as response:
            self.cookies.update(response.cookies)
            content = await response.read()
            text = content.decode("utf-8", errors="ignore")
            try:
                if "application/json" in response.headers.get("content-type", ""):
                    body = await response.json()
                else:
                    body = text
            except Exception:
                body = text
            return RequestResult.from_response(
                url=url,
                method=method,
                response=type(
                    "MockResponse",
                    (),
                    {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "content": content,
                        "json": lambda: body if isinstance(body, dict) else None,
                    },
                )(),
                duration=0.0,
            )

    async def execute_exploit_chain(
        self, exploit_configs: list[dict[str, Any]]
    ) -> list[RequestResult]:
        results = []
        for config in exploit_configs:
            method = config.get("method", "GET")
            url = config["url"]
            data = config.get("data")
            headers = config.get("headers", {})
            if method.upper() == "GET":
                result = await self.get(url, headers=headers)
            elif method.upper() == "POST":
                result = await self.post(url, data=data, headers=headers)
            elif method.upper() == "PUT":
                result = await self.put(url, data=data, headers=headers)
            elif method.upper() == "DELETE":
                result = await self.delete(url, headers=headers)
            else:
                raise ValidationError(f"Unsupported HTTP method: {method}")
            results.append(result)
            if result.status_code >= 400:
                log_warning(
                    f"Exploit step failed: {url}",
                    {"status_code": result.status_code, "method": method},
                )
        return results
