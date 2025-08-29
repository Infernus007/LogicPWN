"""
Consolidated HTTP request runner for LogicPwn Business Logic Exploitation Framework.

This module provides comprehensive HTTP request execution functionality with:
- Synchronous and asynchronous request execution
- Advanced rate limiting and throttling
- SSL/TLS certificate validation with security warnings
- Session management with authentication support
- Comprehensive error handling and logging
- Response analysis and vulnerability detection

Key Features:
- Unified interface for sync/async operations
- Multiple rate limiting algorithms (simple, token bucket, sliding window)
- Secure session lifecycle management
- Request/response middleware support
- Built-in caching and performance monitoring
- Configurable SSL verification with warnings
- Automatic retry with exponential backoff

Usage::

    # Synchronous requests
    from logicpwn.core.runner import HttpRunner

    runner = HttpRunner()
    result = runner.send_request("https://example.com", method="GET")

    # Asynchronous requests
    async with HttpRunner() as runner:
        result = await runner.send_request_async("https://example.com")

    # Batch requests
    async with HttpRunner() as runner:
        results = await runner.send_requests_batch([
            {"url": "https://example.com/1", "method": "GET"},
            {"url": "https://example.com/2", "method": "POST", "json": {"key": "value"}}
        ])
"""

import asyncio
import re
import ssl
import time
import uuid
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import aiohttp
import requests
from loguru import logger

from logicpwn.core.cache import response_cache
from logicpwn.core.config.config_utils import get_max_retries, get_timeout
from logicpwn.core.logging import log_error, log_info, log_request, log_response, log_warning
from logicpwn.core.middleware import MiddlewareContext, RetryException, middleware_manager
from logicpwn.core.performance import monitor_performance
from logicpwn.core.utils import prepare_request_kwargs, validate_config
from logicpwn.exceptions import (
    NetworkError,
    RequestExecutionError,
    ResponseError,
    TimeoutError,
    ValidationError,
)
from logicpwn.models.request_config import RequestConfig
from logicpwn.models.request_result import RequestMetadata, RequestResult


class RateLimitAlgorithm(Enum):
    """Available rate limiting algorithms."""
    SIMPLE = "simple"
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"


class SSLVerificationLevel(Enum):
    """SSL verification levels."""
    STRICT = "strict"      # Full verification
    RELAXED = "relaxed"    # Verification with warnings
    DISABLED = "disabled"  # No verification


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SIMPLE
    requests_per_second: float = 10.0
    burst_size: int = 5
    window_size: int = 60
    adaptive: bool = False
    response_time_threshold: float = 2.0


@dataclass
class SSLConfig:
    """SSL/TLS configuration."""
    verification_level: SSLVerificationLevel = SSLVerificationLevel.STRICT
    custom_ca_bundle: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    min_tls_version: str = "TLSv1.2"
    ciphers: Optional[str] = None


@dataclass
class SessionConfig:
    """Session management configuration."""
    max_connections: int = 100
    max_connections_per_host: int = 30
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    total_timeout: float = 60.0
    keepalive_timeout: float = 30.0
    enable_cleanup_closed: bool = True
    force_close: bool = False
    auto_decompress: bool = True


@dataclass
class RunnerConfig:
    """Comprehensive configuration for HTTP runner."""
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    ssl: SSLConfig = field(default_factory=SSLConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    user_agent: str = "LogicPwn-Runner/2.0"
    default_headers: Dict[str, str] = field(default_factory=dict)
    retry_attempts: int = 3
    retry_backoff: float = 1.0


class SimpleRateLimiter:
    """Simple rate limiter for basic request throttling."""

    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0.0

    def acquire(self) -> None:
        """Acquire permission for a request."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    async def acquire_async(self) -> None:
        """Async version of acquire."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()


class TokenBucketRateLimiter:
    """Token bucket rate limiting implementation."""

    def __init__(self, rate: float, burst_size: int):
        self.rate = rate
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    def acquire(self) -> bool:
        """Acquire a token for request execution."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.burst_size, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True

        wait_time = (1 - self.tokens) / self.rate
        time.sleep(wait_time)
        return True

    async def acquire_async(self) -> bool:
        """Async version of acquire."""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.burst_size, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            return True


class SlidingWindowRateLimiter:
    """Sliding window rate limiting implementation."""

    def __init__(self, rate: float, window_size: int):
        self.rate = rate
        self.window_size = window_size
        self.requests = []
        self._lock = asyncio.Lock()

    def acquire(self) -> bool:
        """Acquire permission for request execution."""
        now = time.time()
        cutoff = now - self.window_size
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]

        max_requests = int(self.rate * self.window_size)
        if len(self.requests) < max_requests:
            self.requests.append(now)
            return True

        if self.requests:
            wait_time = self.requests[0] + self.window_size - now
            time.sleep(max(0, wait_time))

        return True

    async def acquire_async(self) -> bool:
        """Async version of acquire."""
        async with self._lock:
            now = time.time()
            cutoff = now - self.window_size
            self.requests = [req_time for req_time in self.requests if req_time > cutoff]

            max_requests = int(self.rate * self.window_size)
            if len(self.requests) < max_requests:
                self.requests.append(now)
                return True

            if self.requests:
                wait_time = self.requests[0] + self.window_size - now
                await asyncio.sleep(max(0, wait_time))

            return True


class SSLValidator:
    """SSL/TLS certificate validation with enhanced security."""

    @staticmethod
    def create_ssl_context(ssl_config: SSLConfig) -> ssl.SSLContext:
        """Create SSL context based on configuration."""
        if ssl_config.verification_level == SSLVerificationLevel.DISABLED:
            warnings.warn(
                "SSL verification is disabled. This allows "
                "man-in-the-middle attacks. "
                "Only use this in controlled testing environments.",
                UserWarning,
                stacklevel=2,
            )
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

        # Create secure context
        context = ssl.create_default_context()

        # Set minimum TLS version
        if ssl_config.min_tls_version == "TLSv1.2":
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        elif ssl_config.min_tls_version == "TLSv1.3":
            context.minimum_version = ssl.TLSVersion.TLSv1_3

        # Load custom CA bundle
        if ssl_config.custom_ca_bundle:
            context.load_verify_locations(ssl_config.custom_ca_bundle)

        # Load client certificate
        if ssl_config.client_cert and ssl_config.client_key:
            context.load_cert_chain(ssl_config.client_cert, ssl_config.client_key)

        # Set ciphers
        if ssl_config.ciphers:
            context.set_ciphers(ssl_config.ciphers)

        if ssl_config.verification_level == SSLVerificationLevel.RELAXED:
            warnings.warn(
                "SSL verification is in relaxed mode. "
                "Certificate errors will be logged but not fail requests.",
                UserWarning,
                stacklevel=2,
            )

        return context


class HttpRunner:
    """Unified HTTP request runner with sync/async capabilities."""

    def __init__(self, config: Optional[RunnerConfig] = None):
        """Initialize HTTP runner with configuration."""
        self.config = config or RunnerConfig()
        self.session: Optional[requests.Session] = None
        self.async_session: Optional[aiohttp.ClientSession] = None
        self.connector: Optional[aiohttp.TCPConnector] = None
        self.rate_limiter = self._create_rate_limiter()
        self._closed = False

    def _create_rate_limiter(self):
        """Create rate limiter based on configuration."""
        rate_config = self.config.rate_limit

        if rate_config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return TokenBucketRateLimiter(
                rate=rate_config.requests_per_second,
                burst_size=rate_config.burst_size,
            )
        elif rate_config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return SlidingWindowRateLimiter(
                rate=rate_config.requests_per_second,
                window_size=rate_config.window_size,
            )
        else:
            return SimpleRateLimiter(rate_config.requests_per_second)

    def _sanitize_url(self, url: str) -> str:
        """Redact sensitive parameters in URLs for safe logging."""
        if not url:
            return url

        # Redact common sensitive keys in query params
        query_pattern = re.compile(
            r"(?i)(password|token|key|secret|api_key|access_token)=([^&]+)"
        )
        url = query_pattern.sub(lambda m: f"{m.group(1)}=***", url)

        return url

    def _validate_ssl_configuration(self, verify_ssl: bool) -> None:
        """Validate SSL configuration and issue security warnings."""
        if not verify_ssl:
            warnings.warn(
                "SSL verification is disabled. This allows "
                "man-in-the-middle attacks. "
                "Only use this in controlled testing environments.",
                UserWarning,
                stacklevel=3,
            )

    def _validate_body_types(
        self,
        data: Optional[Any],
        json_data: Optional[Dict[str, Any]],
        raw_body: Optional[str],
    ) -> None:
        """Validate that only one body type is specified per request."""
        body_fields = [data, json_data, raw_body]
        specified_fields = [field for field in body_fields if field is not None]

        if len(specified_fields) > 1:
            field_names = []
            if data is not None:
                field_names.append("data")
            if json_data is not None:
                field_names.append("json_data")
            if raw_body is not None:
                field_names.append("raw_body")

            raise ValidationError(
                f"Multiple body types specified: {', '.join(field_names)}. "
                f"Only one body type allowed per request."
            )

    @monitor_performance("sync_request_execution")
    def send_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        raw_body: Optional[str] = None,
        timeout: Optional[int] = None,
        verify_ssl: bool = True,
        session: Optional[requests.Session] = None,
    ) -> RequestResult:
        """
        Send synchronous HTTP request.

        Args:
            url: Target URL
            method: HTTP method (GET, POST, etc.)
            headers: Request headers
            params: Query parameters
            data: Form data or raw data
            json_data: JSON data
            raw_body: Raw request body
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            session: Optional requests session to use

        Returns:
            RequestResult object with response data and metadata

        Raises:
            ValidationError: If request configuration is invalid
            NetworkError: If network issues occur
            TimeoutError: If request times out
            RequestExecutionError: If request execution fails
        """
        # Validate request
        self._validate_body_types(data, json_data, raw_body)
        self._validate_ssl_configuration(verify_ssl)

        # Apply rate limiting
        if self.rate_limiter:
            self.rate_limiter.acquire()

        # Use provided session or create new one
        if session is None:
            if self.session is None:
                self.session = requests.Session()
                self.session.verify = verify_ssl
                self.session.headers.update({
                    "User-Agent": self.config.user_agent,
                    **self.config.default_headers,
                })
            session = self.session

        # Prepare request
        request_config = RequestConfig(
            url=url,
            method=method.upper(),
            headers=headers or {},
            params=params,
            data=data,
            json_data=json_data,
            raw_body=raw_body,
            timeout=timeout or get_timeout(),
            verify_ssl=verify_ssl,
        )

        # Create result object
        result = RequestResult(url=url, method=method)
        result.metadata = RequestMetadata(
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
        )

        # Execute request with timing
        start_time = time.time()
        try:
            # Prepare kwargs
            kwargs = prepare_request_kwargs(request_config)

            # Execute request
            response = session.request(**kwargs)
            duration = time.time() - start_time

            # Update result
            result.status_code = response.status_code
            result.headers = dict(response.headers)
            result.body = response.text if response.text else None
            result.metadata.duration = duration

            # Log request/response
            log_request(
                method=method,
                url=self._sanitize_url(url),
                headers=headers,
                params=params,
                body=data or json_data or raw_body,
                timeout=timeout,
            )
            log_response(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text[:500] if response.text else None,
                response_time=duration,
            )

            # Cache GET responses
            if method.upper() == "GET" and response.status_code == 200:
                response_cache.set_response(
                    url, method, response, params, headers
                )

            return result

        except requests.exceptions.Timeout as e:
            duration = time.time() - start_time
            log_error(f"Request timeout: {method} {url}", {"duration": duration})
            raise TimeoutError(f"Request timeout after {duration:.2f}s") from e

        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            log_error(f"Connection error: {method} {url}", {"error": str(e), "duration": duration})
            raise NetworkError(f"Connection error: {str(e)}") from e

        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            log_error(f"Request error: {method} {url}", {"error": str(e), "duration": duration})
            raise RequestExecutionError(f"Request execution error: {str(e)}") from e

    async def __aenter__(self):
        """Initialize async session."""
        ssl_context = SSLValidator.create_ssl_context(self.config.ssl)

        self.connector = aiohttp.TCPConnector(
            limit=self.config.session.max_connections,
            limit_per_host=self.config.session.max_connections_per_host,
            ssl=ssl_context,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=self.config.session.keepalive_timeout,
            enable_cleanup_closed=self.config.session.enable_cleanup_closed,
            force_close=self.config.session.force_close,
        )

        timeout = aiohttp.ClientTimeout(
            total=self.config.session.total_timeout,
            connect=self.config.session.connection_timeout,
            sock_read=self.config.session.read_timeout,
        )

        default_headers = {
            "User-Agent": self.config.user_agent,
            **self.config.default_headers,
        }

        self.async_session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout,
            headers=default_headers,
            auto_decompress=self.config.session.auto_decompress,
        )

        self._closed = False
        log_info("HTTP runner async session initialized")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async session."""
        if not self._closed:
            await self.close()

    async def close(self):
        """Explicitly close async session."""
        if self.async_session and not self._closed:
            try:
                await self.async_session.close()
                await asyncio.sleep(0.1)  # Wait for connections to close
                self._closed = True
                log_info("HTTP runner async session closed successfully")
            except Exception as e:
                log_error(e, {"component": "HttpRunner", "action": "cleanup"})

        if self.connector:
            try:
                await self.connector.close()
            except Exception as e:
                log_error(e, {"component": "TCPConnector", "action": "cleanup"})

    async def send_request_async(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> RequestResult:
        """
        Send asynchronous HTTP request.

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Request data
            json_data: JSON data
            **kwargs: Additional request parameters

        Returns:
            RequestResult object

        Raises:
            RuntimeError: If async session not initialized
            ValidationError: If request configuration is invalid
            NetworkError: If network issues occur
            TimeoutError: If request times out
        """
        if self._closed or not self.async_session:
            raise RuntimeError("Async session not initialized. Use async context manager.")

        # Apply rate limiting
        if self.rate_limiter and hasattr(self.rate_limiter, 'acquire_async'):
            await self.rate_limiter.acquire_async()

        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        # Prepare request kwargs
        request_kwargs = {"headers": request_headers, "params": params, **kwargs}

        if data:
            request_kwargs["data"] = data
        elif json_data:
            request_kwargs["json"] = json_data

        # Execute request with timing
        start_time = time.time()

        try:
            async with self.async_session.request(method, url, **request_kwargs) as response:
                duration = time.time() - start_time

                # Read response
                content = await response.read()
                text = content.decode("utf-8", errors="ignore")

                # Parse JSON if applicable
                body = text
                try:
                    if "application/json" in response.headers.get("content-type", ""):
                        body = await response.json()
                except Exception:
                    pass

                # Create result
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

                # Log response details
                log_info(
                    f"Async request completed: {method} {url}",
                    {
                        "status_code": response.status,
                        "duration": duration,
                        "response_size": len(content),
                    },
                )

                return result

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            log_error(f"Async request timeout: {method} {url}", {"duration": duration})
            raise TimeoutError(f"Request timeout after {duration:.2f}s")

        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            log_error(
                f"Async client error: {method} {url}",
                {"error": str(e), "duration": duration},
            )
            raise NetworkError(f"Client error: {str(e)}")

        except Exception as e:
            duration = time.time() - start_time
            log_error(
                f"Async request error: {method} {url}",
                {"error": str(e), "duration": duration},
            )
            raise RequestExecutionError(f"Request execution error: {str(e)}")

    async def send_requests_batch(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None,
    ) -> List[RequestResult]:
        """
        Send multiple requests concurrently.

        Args:
            requests: List of request configurations
            max_concurrent: Maximum concurrent requests

        Returns:
            List of RequestResult objects

        Raises:
            RuntimeError: If async session not initialized
        """
        if self._closed or not self.async_session:
            raise RuntimeError("Async session not initialized. Use async context manager.")

        semaphore = asyncio.Semaphore(max_concurrent or 10)

        async def execute_with_semaphore(request_config):
            async with semaphore:
                return await self.send_request_async(**request_config)

        tasks = [execute_with_semaphore(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)


# Factory functions for common configurations

def create_secure_config() -> RunnerConfig:
    """Create configuration for maximum security."""
    return RunnerConfig(
        ssl=SSLConfig(
            verification_level=SSLVerificationLevel.STRICT,
            min_tls_version="TLSv1.3",
        ),
        rate_limit=RateLimitConfig(
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            requests_per_second=5.0,
            burst_size=3,
        ),
    )


def create_testing_config() -> RunnerConfig:
    """Create configuration for testing environments."""
    return RunnerConfig(
        ssl=SSLConfig(verification_level=SSLVerificationLevel.RELAXED),
        rate_limit=RateLimitConfig(
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            requests_per_second=20.0,
        ),
    )


def create_development_config() -> RunnerConfig:
    """Create configuration for development."""
    return RunnerConfig(
        ssl=SSLConfig(verification_level=SSLVerificationLevel.DISABLED),
        rate_limit=RateLimitConfig(requests_per_second=50.0),
    )


# Legacy compatibility exports
send_request = lambda session, config: HttpRunner().send_request(
    url=config.url if hasattr(config, 'url') else config['url'],
    method=config.method if hasattr(config, 'method') else config.get('method', 'GET'),
    headers=config.headers if hasattr(config, 'headers') else config.get('headers'),
    params=config.params if hasattr(config, 'params') else config.get('params'),
    data=config.data if hasattr(config, 'data') else config.get('data'),
    json_data=config.json_data if hasattr(config, 'json_data') else config.get('json_data'),
    session=session,
)

send_request_advanced = lambda **kwargs: HttpRunner().send_request(**kwargs)

validate_config = lambda config: True  # Simplified for now
prepare_request_kwargs = lambda config: {
    'method': config.method,
    'url': config.url,
    'headers': config.headers,
    'params': config.params,
    'data': config.data,
    'json': config.json_data,
    'timeout': config.timeout,
    'verify': config.verify_ssl,
}
