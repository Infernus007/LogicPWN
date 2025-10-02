"""
Core async request runner logic for LogicPwn with fixed timeout handling.

This module provides:
- Fixed async timeout handling with proper aiohttp timeout configuration
- User-friendly error messages with actionable suggestions
- Simplified configuration with preset modes
- Proper session lifecycle management
- Enhanced security features
"""

import asyncio
import ssl
import time
import warnings
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp
from loguru import logger

from logicpwn.core.config.config_utils import get_timeout
from logicpwn.exceptions import (
    NetworkError,
    RequestExecutionError,
    TimeoutError,
    ValidationError,
)
from logicpwn.models.request_result import RequestResult

# Import standardized logging and type definitions
from .standardized_logging import (
    log_error,
    log_info,
    log_request,
    log_response,
)
from .type_definitions import (
    URL,
    Data,
    Headers,
    JSONData,
    Method,
    Params,
    RawBody,
    RequestConfigList,
    RequestResultList,
    Timeout,
)


def _validate_body_types(
    data: Optional[dict[str, Any]],
    json_data: Optional[dict[str, Any]],
    raw_body: Optional[str],
) -> None:
    """
    Validate that only one body type is specified per request.

    Args:
        data: Form data
        json_data: JSON data
        raw_body: Raw body content

    Raises:
        ValidationError: If multiple body types are specified
    """
    body_fields = [data, json_data, raw_body]
    specified_fields = [field for field in body_fields if field is not None]

    if len(specified_fields) > 1:
        field_names = []
        if data is not None:
            field_names.append("data (form data)")
        if json_data is not None:
            field_names.append("json_data (JSON data)")
        if raw_body is not None:
            field_names.append("raw_body (raw body content)")

        raise ValidationError(
            f"Multiple body types specified: {', '.join(field_names)}. "
            f"Only one body type allowed per request. Use either form data, "
            f"JSON data, or raw body content, but not multiple types."
        )


@dataclass
class SecurityConfig:
    """Security configuration for async runner."""

    verify_ssl: bool = True
    min_tls_version: str = "TLSv1.2"
    warn_on_ssl_disabled: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    enabled: bool = True
    requests_per_second: float = 10.0
    algorithm: str = "token_bucket"  # "token_bucket", "sliding_window", "simple"
    burst_size: int = 5
    window_size: int = 60


@dataclass
class AsyncRequestContext:
    """Context for async request execution."""

    request_id: str
    url: str
    method: str
    headers: dict[str, str]
    params: Optional[dict[str, Any]] = None
    body: Optional[Any] = None
    timeout: Optional[int] = None
    session_data: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None


class SimpleRateLimiter:
    """Simple rate limiter implementation."""

    def __init__(self, rate: float):
        self.rate = rate
        self.last_request = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire permission for request."""
        async with self._lock:
            now = time.time()
            time_since_last = now - self.last_request
            min_interval = 1.0 / self.rate

            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                await asyncio.sleep(wait_time)

            self.last_request = time.time()
            return True


class TokenBucketRateLimiter:
    """Token bucket rate limiter for better burst handling."""

    def __init__(self, rate: float, burst_size: int):
        self.rate = rate
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire a token for request execution."""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.burst_size, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            # Wait for next token
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            return True


class SlidingWindowRateLimiter:
    """Sliding window rate limiter for precise rate control."""

    def __init__(self, rate: float, window_size: int):
        self.rate = rate
        self.window_size = window_size
        self.requests = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire permission for request execution."""
        async with self._lock:
            now = time.time()
            cutoff = now - self.window_size
            self.requests = [
                req_time for req_time in self.requests if req_time > cutoff
            ]

            max_requests = int(self.rate * self.window_size)
            if len(self.requests) < max_requests:
                self.requests.append(now)
                return True

            # Wait until window allows next request
            if self.requests:
                wait_time = self.requests[0] + self.window_size - now
                await asyncio.sleep(max(0, wait_time))
                return await self.acquire()

            return True


class AsyncRequestRunner:
    """High-performance async request runner with enhanced security and rate limiting."""

    def __init__(
        self,
        max_concurrent: int = 10,
        rate_limit_config: Optional[RateLimitConfig] = None,
        security_config: Optional[SecurityConfig] = None,
        timeout: Optional[int] = None,
        # Backward compatibility parameters
        rate_limit: Optional[float] = None,
        verify_ssl: bool = True,
    ):
        """
        Initialize async request runner with enhanced features.

        Args:
            max_concurrent: Maximum concurrent requests
            rate_limit_config: Rate limiting configuration (new)
            security_config: Security configuration (new)
            timeout: Default timeout in seconds
            rate_limit: Requests per second (backward compatibility)
            verify_ssl: Whether to verify SSL (backward compatibility)
        """
        self.max_concurrent = max_concurrent

        # Handle backward compatibility for rate limiting
        if rate_limit_config is None and rate_limit is not None:
            rate_limit_config = RateLimitConfig(
                enabled=True, requests_per_second=rate_limit, algorithm="simple"
            )
        self.rate_limit_config = rate_limit_config or RateLimitConfig()

        # Handle backward compatibility for SSL
        if security_config is None:
            security_config = SecurityConfig(verify_ssl=verify_ssl)
        self.security_config = security_config

        self.timeout = timeout or get_timeout()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = self._create_rate_limiter()

    # Backward compatibility properties
    @property
    def rate_limit(self) -> Optional[float]:
        """Backward compatibility property for rate_limit."""
        return (
            self.rate_limit_config.requests_per_second
            if self.rate_limit_config.enabled
            else None
        )

    @property
    def verify_ssl(self) -> bool:
        """Backward compatibility property for verify_ssl."""
        return self.security_config.verify_ssl

    def _create_rate_limiter(self):
        """Create rate limiter based on configuration."""
        if not self.rate_limit_config.enabled:
            return None

        if self.rate_limit_config.algorithm == "token_bucket":
            return TokenBucketRateLimiter(
                rate=self.rate_limit_config.requests_per_second,
                burst_size=self.rate_limit_config.burst_size,
            )
        elif self.rate_limit_config.algorithm == "sliding_window":
            return SlidingWindowRateLimiter(
                rate=self.rate_limit_config.requests_per_second,
                window_size=self.rate_limit_config.window_size,
            )
        else:
            return SimpleRateLimiter(rate=self.rate_limit_config.requests_per_second)

    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context with security warnings."""
        if not self.security_config.verify_ssl:
            if self.security_config.warn_on_ssl_disabled:
                warnings.warn(
                    "SSL verification is disabled. This allows "
                    "man-in-the-middle attacks. "
                    "Only use this in controlled testing environments.",
                    UserWarning,
                    stacklevel=2,
                )
            return ssl.create_default_context()

        context = ssl.create_default_context()

        # Set minimum TLS version for security
        if self.security_config.min_tls_version == "TLSv1.2":
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        elif self.security_config.min_tls_version == "TLSv1.3":
            context.minimum_version = ssl.TLSVersion.TLSv1_3

        return context

    async def __aenter__(self):
        """Async context manager entry with enhanced session setup."""
        ssl_context = self._create_ssl_context()

        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=self.max_concurrent,
            ssl=ssl_context,
            verify_ssl=self.security_config.verify_ssl,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        # Get timeout configuration with proper breakdown
        total, connect, read = self.timeout, self.timeout * 0.3, self.timeout * 0.7
        timeout_config = aiohttp.ClientTimeout(
            total=total, connect=connect, sock_read=read
        )

        # HTTP/2 support evaluation (aiohttp supports HTTP/2 with h2 library)
        headers = {
            "User-Agent": "LogicPwn-AsyncRunner/2.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
        }

        self.session = aiohttp.ClientSession(
            connector=connector, timeout=timeout_config, headers=headers
        )

        log_info(
            "Enhanced async runner initialized",
            {
                "max_concurrent": self.max_concurrent,
                "rate_limiting": self.rate_limit_config.enabled,
                "ssl_verification": self.security_config.verify_ssl,
                "min_tls_version": self.security_config.min_tls_version,
            },
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper session cleanup."""
        if self.session:
            try:
                await self.session.close()
                # Wait for underlying connections to close
                await asyncio.sleep(0.1)
                log_info("Async runner session closed successfully")
            except Exception as e:
                log_error(e, {"component": "AsyncRequestRunner", "action": "cleanup"})

    async def send_request(
        self,
        url: URL,
        method: Method = "GET",
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        raw_body: Optional[RawBody] = None,
        timeout: Optional[Timeout] = None,
    ) -> RequestResult:
        """
        Send a single async HTTP request with rate limiting and security features.

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Form data
            json_data: JSON body
            raw_body: Raw body content
            timeout: Request timeout

        Returns:
            RequestResult with response analysis
        """
        # Validate body types - only one should be specified
        _validate_body_types(data, json_data, raw_body)

        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire()

        async with self.semaphore:
            return await self._execute_request(
                url=url,
                method=method,
                headers=headers or {},
                params=params or {},
                data=data,
                json_data=json_data,
                raw_body=raw_body,
                timeout=timeout or self.timeout,
            )

    async def send_requests_batch(
        self,
        request_configs: RequestConfigList,
        max_concurrent: Optional[int] = None,
    ) -> RequestResultList:
        """
        Send multiple requests concurrently.
        Args:
            request_configs: List of request configurations
            max_concurrent: Override max concurrent requests
        Returns:
            List of RequestResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent or self.max_concurrent)

        async def execute_with_semaphore(config):
            async with semaphore:
                if isinstance(config, dict):
                    return await self.send_request(**config)
                else:
                    return await self.send_request(
                        url=config.url,
                        method=config.method,
                        headers=config.headers,
                        params=config.params,
                        data=config.data,
                        json_data=config.json_data,
                        raw_body=config.raw_body,
                        timeout=config.timeout,
                    )

        tasks = [execute_with_semaphore(config) for config in request_configs]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_request(
        self,
        url: str,
        method: str,
        headers: dict[str, str],
        params: dict[str, Any],
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        raw_body: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> RequestResult:
        """Execute a single async request with comprehensive error handling."""
        import time

        start_time = time.time()
        try:
            # Prepare request data with proper timeout configuration
            request_timeout = timeout or self.timeout
            if request_timeout != self.timeout:
                # Use request-specific timeout with proper breakdown
                total, connect, read = (
                    request_timeout,
                    request_timeout * 0.3,
                    request_timeout * 0.7,
                )
                timeout_config = aiohttp.ClientTimeout(
                    total=total, connect=connect, sock_read=read
                )
            else:
                # Use session timeout (already configured)
                timeout_config = None

            request_kwargs = {
                "headers": headers,
                "params": params,
            }
            if timeout_config:
                request_kwargs["timeout"] = timeout_config
            if data:
                request_kwargs["data"] = data
            elif json_data:
                request_kwargs["json"] = json_data
            elif raw_body:
                request_kwargs["data"] = raw_body
            # Log request
            log_request(method, url, headers, data or json_data or raw_body)
            # Add specific logging for HEAD requests
            if method.upper() == "HEAD":
                log_info(
                    f"HEAD request to {url} - "
                    f"will return headers only, no body expected"
                )
            # Execute request
            async with self.session.request(method, url, **request_kwargs) as response:
                duration = time.time() - start_time

                # Read response content safely
                try:
                    content = await response.read()
                    text = content.decode("utf-8", errors="ignore")
                except UnicodeDecodeError:
                    # Fallback for problematic encodings
                    text = content.decode("latin-1", errors="ignore")
                except Exception as e:
                    logger.warning(f"Failed to read response content: {e}")
                    content = b""
                    text = ""

                # Parse response body
                body = text
                try:
                    content_type = response.headers.get("content-type", "").lower()
                    if "application/json" in content_type:
                        body = await response.json()
                except (aiohttp.ContentTypeError, ValueError, TypeError) as e:
                    # JSON parsing failed, keep as text
                    logger.debug(f"JSON parsing failed, keeping as text: {e}")
                    body = text
                except Exception as e:
                    logger.warning(f"Unexpected error parsing response body: {e}")
                    body = text
                # Create RequestResult
                result = RequestResult.from_response(
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
                    duration=duration,
                )
                # Log response
                log_response(response.status, dict(response.headers), body, duration)
                # Add specific logging for HEAD response
                if method.upper() == "HEAD":
                    log_info(f"HEAD response headers: {dict(response.headers)}")
                return result
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            timeout_value = timeout or self.timeout
            error_msg = f"⏰ Request to {url} timed out after {timeout_value} seconds"
            suggestion = f"💡 Try increasing the timeout value (current: {timeout_value}s) or check if the server is responding."

            log_error(
                TimeoutError(f"Request timeout after {timeout_value}s"),
                {
                    "url": url,
                    "method": method,
                    "duration": duration,
                    "timeout": timeout_value,
                },
            )
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=TimeoutError(f"{error_msg}\n\n{suggestion}"),
                duration=duration,
            )
        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            error_type = type(e).__name__

            if isinstance(e, aiohttp.ClientConnectorError):
                error_msg = f"🌐 Cannot connect to {url}"
                suggestion = "💡 Check if the URL is correct and the server is running. Verify network connectivity."
            elif isinstance(e, aiohttp.ClientTimeout):
                error_msg = f"⏰ Request to {url} timed out"
                suggestion = "💡 The server took too long to respond. Try increasing the timeout value."
            elif isinstance(e, aiohttp.ClientResponseError):
                error_msg = f"🚫 Server returned error for {url}"
                suggestion = (
                    "💡 Check the server status and verify the request parameters."
                )
            else:
                error_msg = f"🌐 Network error occurred: {str(e)}"
                suggestion = "💡 Check your network connection and try again."

            log_error(
                NetworkError(f"Network error: {str(e)}"),
                {
                    "url": url,
                    "method": method,
                    "duration": duration,
                    "error_type": error_type,
                },
            )
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=NetworkError(f"{error_msg}\n\n{suggestion}"),
                duration=duration,
            )
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__

            if "SSL" in str(e):
                error_msg = f"🔒 SSL certificate issue for {url}"
                suggestion = "💡 SSL certificate problem. Check certificate or disable SSL verification for testing."
            elif "JSON" in str(e):
                error_msg = f"📄 JSON parsing error for {url}"
                suggestion = "💡 Invalid JSON data. Check your request body format."
            elif "encoding" in str(e).lower():
                error_msg = f"🔤 Character encoding issue for {url}"
                suggestion = (
                    "💡 Character encoding problem. Check your request data encoding."
                )
            else:
                error_msg = f"❌ Request execution failed for {url}: {str(e)}"
                suggestion = "💡 Check your request parameters and try again."

            log_error(
                RequestExecutionError(f"Request execution error: {str(e)}"),
                {
                    "url": url,
                    "method": method,
                    "duration": duration,
                    "error_type": error_type,
                },
            )
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=RequestExecutionError(f"{error_msg}\n\n{suggestion}"),
                duration=duration,
            )
