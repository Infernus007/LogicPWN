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
- Multiple rate limiting algorithms (simple, token bucket, sliding window, adaptive)
- Secure session lifecycle management
- Request/response middleware support
- Built-in caching and performance monitoring
- Configurable SSL verification with warnings
- Automatic retry with exponential backoff

Usage::

    # Synchronous requests
    from . import HttpRunner

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
import random
import re
import ssl
import threading
import time
import uuid
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Optional,
)

import aiohttp
import requests

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from logicpwn.core.cache import response_cache
from logicpwn.core.config.config_utils import get_timeout
from logicpwn.core.performance import monitor_performance
from logicpwn.exceptions import (
    NetworkError,
    RequestExecutionError,
    TimeoutError,
    ValidationError,
)
from logicpwn.models.request_config import RequestConfig
from logicpwn.models.request_result import RequestMetadata, RequestResult

# Import standardized logging and type definitions
from .standardized_logging import (
    LogAction,
    LogComponent,
    StandardizedLogger,
    get_logger,
    log_error,
    log_info,
    log_request,
    log_response,
)
from .type_definitions import (
    URL,
    Data,
    ErrorCallback,
    Headers,
    JSONData,
    Method,
    Params,
    RawBody,
    RequestCallback,
    RequestConfigList,
    RequestResultList,
    Timeout,
)


class RateLimitAlgorithm(Enum):
    """Available rate limiting algorithms."""

    SIMPLE = "simple"
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    ADAPTIVE = "adaptive"


class SSLVerificationLevel(Enum):
    """SSL verification levels."""

    STRICT = "strict"  # Full verification
    RELAXED = "relaxed"  # Verification with warnings
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
    # Adaptive rate limiting parameters
    adaptive_min_rate: float = 1.0
    adaptive_max_rate: float = 50.0
    adaptive_increase_factor: float = 1.2
    adaptive_decrease_factor: float = 0.8


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
    # HTTP/2 Support
    enable_http2: bool = True
    # HTTP/2 implementation: 'aiohttp' (limited), 'httpx' (full HTTP/2), or 'auto'
    http2_implementation: str = "auto"  # auto, aiohttp, httpx
    http2_connection_window_size: int = 65536
    http2_stream_window_size: int = 65536


@dataclass
class RetryConfig:
    """Comprehensive retry configuration for request resilience.

    Parameters
    ----------
    max_attempts: int
        Maximum attempts including the first try (default: 3).
    base_delay: float
        Initial backoff delay in seconds before applying `exponential_base`.
    max_delay: float
        Upper bound for any computed backoff delay.
    exponential_base: float
        Exponential growth base (e.g., 2.0 for doubling each attempt).
    jitter: bool
        If True, adds ±10% jitter to backoff to avoid thundering herd.
    retryable_status_codes: set[int]
        HTTP status codes that should be retried (defaults include 429, 5xx).
    retryable_exceptions: tuple[type[Exception], ...]
        Exception types that should trigger a retry.
    respect_retry_after: bool
        If True, honors Retry-After header when present.
    backoff_multiplier: float
        Multiplies the computed delay to stretch/shrink backoff windows.
    """

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_status_codes: set[int] = field(
        default_factory=lambda: {500, 502, 503, 504, 429}
    )
    retryable_exceptions: tuple = (NetworkError, TimeoutError, RequestExecutionError)
    respect_retry_after: bool = True
    backoff_multiplier: float = 1.0

    @classmethod
    def conservative(cls) -> "RetryConfig":
        """Return a conservative retry policy preset.

        - Fewer attempts, shorter window. Suitable for non-idempotent operations.
        """
        return cls(
            max_attempts=2,
            base_delay=0.5,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=True,
            retryable_status_codes={429, 503},
            respect_retry_after=True,
            backoff_multiplier=1.0,
        )

    @classmethod
    def balanced(cls) -> "RetryConfig":
        """Return a balanced retry policy preset suitable for most workloads."""
        return cls(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            jitter=True,
            retryable_status_codes={500, 502, 503, 504, 429},
            respect_retry_after=True,
            backoff_multiplier=1.0,
        )

    @classmethod
    def aggressive(cls) -> "RetryConfig":
        """Return an aggressive retry policy preset for resilient idempotent calls."""
        return cls(
            max_attempts=5,
            base_delay=0.5,
            max_delay=60.0,
            exponential_base=2.0,
            jitter=True,
            retryable_status_codes={500, 502, 503, 504, 429},
            respect_retry_after=True,
            backoff_multiplier=1.25,
        )


@dataclass
class RunnerConfig:
    """Comprehensive configuration for HTTP runner.

    Attributes
    ----------
    rate_limit: RateLimitConfig
        Rate limiting configuration (algorithm, RPS, burst/window/adaptive).
    ssl: SSLConfig
        SSL/TLS verification and client authentication settings.
    session: SessionConfig
        Connection/session tuning for async client.
    retry: RetryConfig
        Retry/backoff strategy.
    user_agent: str
        Default User-Agent for requests.
    default_headers: dict[str, str]
        Headers merged into every request by default.
    enable_response_cache: bool
        If True, cache 200-OK GET responses in the in-memory response cache.

    Backward compatibility
    ----------------------
    retry_attempts, retry_backoff are mapped to `retry` at runtime if provided.
    """

    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    ssl: SSLConfig = field(default_factory=SSLConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    user_agent: str = "LogicPwn-Runner/2.0"
    default_headers: dict[str, str] = field(default_factory=dict)
    enable_response_cache: bool = True

    # Backward compatibility
    retry_attempts: int = 3
    retry_backoff: float = 1.0


class SimpleRateLimiter:
    """
    Simple rate limiter for basic request throttling with thread safety.

    Provides basic rate limiting with a fixed requests-per-second limit.
    Thread-safe implementation using asyncio.Lock for synchronization.
    """

    def __init__(self, requests_per_second: float):
        """
        Initialize simple rate limiter.

        Args:
            requests_per_second: Maximum requests per second allowed
        """
        self.requests_per_second = requests_per_second
        self.last_request_time = 0.0
        self._lock = asyncio.Lock()
        self._thread_lock = threading.Lock()

    def acquire(self) -> None:
        """
        Acquire permission for request execution.

        Blocks until the minimum interval has passed since the last request.
        Thread-safe implementation.
        """
        with self._thread_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            min_interval = 1.0 / self.requests_per_second

            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                time.sleep(sleep_time)

            self.last_request_time = time.time()

    async def acquire_async(self) -> None:
        """
        Async version of acquire for simple rate limiting.

        Thread-safe async implementation that respects rate limits.
        """
        async with self._lock:
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
        """Async version of acquire for token bucket."""
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
            self.tokens = max(0, self.tokens - 1)
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
        # Truncate long lines for flake8 compliance
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
            if self.requests:
                wait_time = self.requests[0] + self.window_size - now
                await asyncio.sleep(max(0, wait_time))
                self.requests.append(time.time())
                return True
            return False


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on response times."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.current_rate = config.requests_per_second
        self.last_request_time = 0.0
        self.response_times = []
        self._lock = asyncio.Lock()

    def _adjust_rate(self, response_time: float) -> None:
        """Adjust rate based on response time."""
        if not self.config.adaptive:
            return

        self.response_times.append(response_time)
        if len(self.response_times) > 10:  # Keep last 10 response times
            self.response_times.pop(0)

        avg_response_time = sum(self.response_times) / len(self.response_times)

        if avg_response_time > self.config.response_time_threshold:
            # Slow down
            self.current_rate = max(
                self.config.adaptive_min_rate,
                self.current_rate * self.config.adaptive_decrease_factor,
            )
        else:
            # Speed up
            self.current_rate = min(
                self.config.adaptive_max_rate,
                self.current_rate * self.config.adaptive_increase_factor,
            )

    def acquire(self, response_time: Optional[float] = None) -> None:
        """Acquire permission for a request with adaptive adjustment."""
        if response_time is not None:
            self._adjust_rate(response_time)

        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.current_rate

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    async def acquire_async(self, response_time: Optional[float] = None) -> None:
        """Async version of acquire with adaptive adjustment."""
        async with self._lock:
            if response_time is not None:
                self._adjust_rate(response_time)

            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            min_interval = 1.0 / self.current_rate

            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                await asyncio.sleep(sleep_time)

            self.last_request_time = time.time()


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


class RetryManager:
    """
    Comprehensive retry mechanism with exponential backoff and jitter.

    Provides intelligent retry logic with configurable backoff strategies,
    status code filtering, and exception handling.
    """

    def __init__(self, config: RetryConfig):
        """
        Initialize retry manager with configuration.

        Args:
            config: Retry configuration settings
        """
        self.config = config

    def should_retry(
        self,
        attempt: int,
        exception: Optional[Exception] = None,
        status_code: Optional[int] = None,
    ) -> bool:
        """
        Determine if a request should be retried.

        Args:
            attempt: Current attempt number (0-based)
            exception: Exception that occurred (if any)
            status_code: HTTP status code (if any)

        Returns:
            True if request should be retried, False otherwise
        """
        if attempt >= self.config.max_attempts:
            return False

        # Check if exception is retryable
        if exception and isinstance(exception, self.config.retryable_exceptions):
            return True

        # Check if status code is retryable
        if status_code and status_code in self.config.retryable_status_codes:
            return True

        return False

    def calculate_delay(self, attempt: int, retry_after: Optional[str] = None) -> float:
        """
        Calculate delay for next retry attempt.

        Args:
            attempt: Current attempt number (0-based)
            retry_after: Retry-After header value (if any)

        Returns:
            Delay in seconds before next attempt
        """
        # Respect Retry-After header if present
        if self.config.respect_retry_after and retry_after:
            try:
                return float(retry_after)
            except (ValueError, TypeError):
                pass

        # Calculate exponential backoff
        delay = self.config.base_delay * (self.config.exponential_base**attempt)
        delay *= self.config.backoff_multiplier

        # Apply jitter to prevent thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)

        # Cap at maximum delay
        return min(delay, self.config.max_delay)

    async def wait_for_retry(
        self, attempt: int, retry_after: Optional[str] = None
    ) -> None:
        """
        Wait for the calculated delay before retry.

        Args:
            attempt: Current attempt number (0-based)
            retry_after: Retry-After header value (if any)
        """
        delay = self.calculate_delay(attempt, retry_after)
        if delay > 0:
            await asyncio.sleep(delay)

    def wait_for_retry_sync(
        self, attempt: int, retry_after: Optional[str] = None
    ) -> None:
        """
        Synchronous wait for the calculated delay before retry.

        Args:
            attempt: Current attempt number (0-based)
            retry_after: Retry-After header value (if any)
        """
        delay = self.calculate_delay(attempt, retry_after)
        if delay > 0:
            time.sleep(delay)


class HttpRunner:
    """
    Enhanced HTTP request runner with consolidated API.

    This runner provides a single, consistent interface for all HTTP operations:
    - Synchronous and asynchronous request execution
    - Session management with authentication support
    - Batch request processing
    - Advanced rate limiting and throttling
    - SSL/TLS certificate validation with security warnings
    - Comprehensive error handling and retry logic
    - Response analysis and vulnerability detection

    Usage:
        # Basic usage
        runner = HttpRunner()
        result = runner.get("https://example.com")

        # Async usage
        async with runner:
            result = await runner.get_async("https://example.com")

        # Batch requests
        results = await runner.batch([
            {"url": "https://example.com/1", "method": "GET"},
            {"url": "https://example.com/2", "method": "POST", "json_data": {"key": "value"}}
        ])
    """

    def __init__(self, config: Optional[RunnerConfig] = None) -> None:
        """
        Initialize HTTP runner with configuration.

        Args:
            config: Runner configuration. If None, uses default configuration.
        """
        self.config: RunnerConfig = config or RunnerConfig()
        self.session: Optional[requests.Session] = None
        self.async_session: Optional[aiohttp.ClientSession] = None
        self.connector: Optional[aiohttp.TCPConnector] = None
        self.rate_limiter = self._create_rate_limiter()
        self.retry_manager = RetryManager(self.config.retry)
        self._closed: bool = False

        # Initialize standardized logger
        self.logger: StandardizedLogger = get_logger(LogComponent.RUNNER)

        # Warn at construction time if SSL verification is disabled
        if self.config.ssl.verification_level == SSLVerificationLevel.DISABLED:
            self.logger.warning(
                "SSL verification is disabled. This allows man-in-the-middle attacks. "
                "Only use this in controlled testing environments.",
                LogAction.SSL_VERIFY,
                {"verification_level": self.config.ssl.verification_level.value},
            )

        # Backward compatibility: migrate old retry settings
        if hasattr(self.config, "retry_attempts") and self.config.retry_attempts != 3:
            self.config.retry.max_attempts = self.config.retry_attempts
        if hasattr(self.config, "retry_backoff") and self.config.retry_backoff != 1.0:
            self.config.retry.base_delay = self.config.retry_backoff

        self.logger.info(
            "HTTP runner initialized",
            LogAction.INIT,
            {
                "max_concurrent": self.config.session.max_connections,
                "ssl_verification": self.config.ssl.verification_level.value,
                "rate_limiting": self.config.rate_limit.algorithm.value,
                "retry_attempts": self.config.retry.max_attempts,
            },
        )

    # Convenient HTTP methods for better API consistency
    def get(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send GET request."""
        return self.send_request(
            url=url,
            method="GET",
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs,
        )

    def post(
        self,
        url: URL,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send POST request."""
        return self.send_request(
            url=url,
            method="POST",
            headers=headers,
            data=data,
            json_data=json_data,
            timeout=timeout,
            **kwargs,
        )

    def put(
        self,
        url: URL,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send PUT request."""
        return self.send_request(
            url=url,
            method="PUT",
            headers=headers,
            data=data,
            json_data=json_data,
            timeout=timeout,
            **kwargs,
        )

    def delete(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send DELETE request."""
        return self.send_request(
            url=url,
            method="DELETE",
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def patch(
        self,
        url: URL,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send PATCH request."""
        return self.send_request(
            url=url,
            method="PATCH",
            headers=headers,
            data=data,
            json_data=json_data,
            timeout=timeout,
            **kwargs,
        )

    def head(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send HEAD request."""
        return self.send_request(
            url=url,
            method="HEAD",
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs,
        )

    def options(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send OPTIONS request."""
        return self.send_request(
            url=url,
            method="OPTIONS",
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    # Async convenience methods
    async def get_async(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send async GET request."""
        return await self.send_request_async(
            url=url,
            method="GET",
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs,
        )

    async def post_async(
        self,
        url: URL,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send async POST request."""
        return await self.send_request_async(
            url=url,
            method="POST",
            headers=headers,
            data=data,
            json_data=json_data,
            timeout=timeout,
            **kwargs,
        )

    async def put_async(
        self,
        url: URL,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send async PUT request."""
        return await self.send_request_async(
            url=url,
            method="PUT",
            headers=headers,
            data=data,
            json_data=json_data,
            timeout=timeout,
            **kwargs,
        )

    async def delete_async(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send async DELETE request."""
        return await self.send_request_async(
            url=url,
            method="DELETE",
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def patch_async(
        self,
        url: URL,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send async PATCH request."""
        return await self.send_request_async(
            url=url,
            method="PATCH",
            headers=headers,
            data=data,
            json_data=json_data,
            timeout=timeout,
            **kwargs,
        )

    async def head_async(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send async HEAD request."""
        return await self.send_request_async(
            url=url,
            method="HEAD",
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs,
        )

    async def options_async(
        self,
        url: URL,
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """Send async OPTIONS request."""
        return await self.send_request_async(
            url=url,
            method="OPTIONS",
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    # Batch processing methods
    async def batch(
        self,
        requests: RequestConfigList,
        max_concurrent: Optional[int] = None,
        **kwargs: Any,
    ) -> RequestResultList:
        """
        Send multiple requests concurrently.

        Args:
            requests: List of request configurations
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional parameters

        Returns:
            List of RequestResult objects
        """
        return await self.send_requests_batch(
            request_configs=requests,
            max_concurrent=max_concurrent,
            **kwargs,
        )

    async def batch_get(
        self,
        urls: list[URL],
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        timeout: Optional[Timeout] = None,
        max_concurrent: Optional[int] = None,
        **kwargs: Any,
    ) -> RequestResultList:
        """Send multiple GET requests concurrently."""
        requests = [
            {
                "url": url,
                "method": "GET",
                "headers": headers,
                "params": params,
                "timeout": timeout,
                **kwargs,
            }
            for url in urls
        ]
        return await self.batch(requests, max_concurrent=max_concurrent)

    async def batch_post(
        self,
        url_data_pairs: list[tuple[URL, Optional[Data], Optional[JSONData]]],
        headers: Optional[Headers] = None,
        timeout: Optional[Timeout] = None,
        max_concurrent: Optional[int] = None,
        **kwargs: Any,
    ) -> RequestResultList:
        """Send multiple POST requests concurrently."""
        requests = [
            {
                "url": url,
                "method": "POST",
                "headers": headers,
                "data": data,
                "json_data": json_data,
                "timeout": timeout,
                **kwargs,
            }
            for url, data, json_data in url_data_pairs
        ]
        return await self.batch(requests, max_concurrent=max_concurrent)

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
        elif rate_config.algorithm == RateLimitAlgorithm.ADAPTIVE:
            return AdaptiveRateLimiter(config=rate_config)
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
        json_data: Optional[dict[str, Any]],
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
        url: URL,
        method: Method = "GET",
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        raw_body: Optional[RawBody] = None,
        timeout: Optional[Timeout] = None,
        verify_ssl: bool = True,
        session: Optional[requests.Session] = None,
        disable_cache: bool = False,
        retry_config: Optional[RetryConfig] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        on_success: Optional[RequestCallback] = None,
        on_error: Optional[ErrorCallback] = None,
    ) -> RequestResult:
        """Send a synchronous HTTP request with retry and rate limiting.

        Parameters
        ----------
        url: str
            Target URL.
        method: str
            HTTP method (e.g., "GET", "POST").
        headers: dict[str, str] | None
            Request headers to merge with defaults.
        params: dict[str, Any] | None
            Query parameters for the request.
        data: Any | None
            Form or raw data (mutually exclusive with `json_data` and `raw_body`).
        json_data: dict[str, Any] | None
            JSON body (mutually exclusive with `data` and `raw_body`).
        raw_body: str | None
            Raw body (mutually exclusive with `data` and `json_data`).
        timeout: int | None
            Per-request timeout; falls back to global default.
        verify_ssl: bool
            If False, disables SSL verification for this call (emits warning).
        session: requests.Session | None
            Optional session to use; otherwise a session is managed lazily.
        disable_cache: bool
            If True, bypass response cache even when globally enabled.
        retry_config: RetryConfig | None
            Override the runner's retry configuration for this request only.
        rate_limit_config: RateLimitConfig | None
            Override the runner's rate limiting configuration for this request only.

        Returns
        -------
        RequestResult
            Structured result containing status, headers, body, and metadata.

        Raises
        ------
        ValidationError
            If request configuration is invalid.
        NetworkError
            If network-related errors occur.
        TimeoutError
            If the request times out across all attempts.
        RequestExecutionError
            If the request ultimately fails after retries or hits retryable statuses.
        """
        # Validate request
        self._validate_body_types(data, json_data, raw_body)
        self._validate_ssl_configuration(verify_ssl)

        # Optionally override retry and rate limit settings per-request
        original_retry_manager = self.retry_manager
        original_rate_limiter = self.rate_limiter
        if retry_config is not None:
            self.retry_manager = RetryManager(retry_config)
        if rate_limit_config is not None:
            # Create transient limiter without mutating global config
            temp_runner_config = RunnerConfig(
                rate_limit=rate_limit_config,
                ssl=self.config.ssl,
                session=self.config.session,
                retry=self.config.retry,
                user_agent=self.config.user_agent,
                default_headers=self.config.default_headers,
                enable_response_cache=self.config.enable_response_cache,
            )
            self.rate_limiter = HttpRunner(temp_runner_config)._create_rate_limiter()

        # Execute with retry logic
        last_exception = None
        effective_attempts = self.retry_manager.config.max_attempts
        for attempt in range(effective_attempts):
            try:
                return self._execute_sync_request(
                    url=url,
                    method=method,
                    headers=headers,
                    params=params,
                    data=data,
                    json_data=json_data,
                    raw_body=raw_body,
                    timeout=timeout,
                    verify_ssl=verify_ssl,
                    session=session,
                    attempt=attempt,
                    disable_cache=disable_cache,
                )
            except Exception as e:
                last_exception = e

                # Check if we should retry
                if not self.retry_manager.should_retry(attempt, exception=e):
                    break

                # Wait before retry (except on last attempt)
                if attempt < effective_attempts - 1:
                    retry_after_header = None
                    if hasattr(e, "response") and getattr(e, "response", None):
                        retry_after_header = getattr(e.response, "headers", {}).get(
                            "Retry-After"
                        )
                    self.retry_manager.wait_for_retry_sync(
                        attempt, retry_after=retry_after_header
                    )

        # Restore original managers before raising
        self.retry_manager = original_retry_manager
        self.rate_limiter = original_rate_limiter

        # If we get here, all retries failed
        if isinstance(last_exception, requests.exceptions.Timeout):
            error_msg = (
                f"⏰ Request timed out after {self.config.retry.max_attempts} attempts"
            )
            suggestion = "💡 Try increasing the timeout value or check if the server is responding."
            raise TimeoutError(f"{error_msg}\n\n{suggestion}") from last_exception
        elif isinstance(last_exception, requests.exceptions.ConnectionError):
            error_msg = (
                f"🌐 Connection error after {self.config.retry.max_attempts} attempts"
            )
            suggestion = (
                "💡 Check your network connection and verify the URL is correct."
            )
            raise NetworkError(
                f"{error_msg}: {str(last_exception)}\n\n{suggestion}"
            ) from last_exception
        else:
            error_msg = f"❌ Request execution error after {self.config.retry.max_attempts} attempts"
            suggestion = "💡 Check your request parameters and try again."
            raise RequestExecutionError(
                f"{error_msg}: {str(last_exception)}\n\n{suggestion}"
            ) from last_exception

    def _execute_sync_request(
        self,
        url: str,
        method: str,
        headers: Optional[dict[str, str]],
        params: Optional[dict[str, Any]],
        data: Optional[Any],
        json_data: Optional[dict[str, Any]],
        raw_body: Optional[str],
        timeout: Optional[int],
        verify_ssl: bool,
        session: Optional[requests.Session],
        attempt: int,
        disable_cache: bool,
    ) -> RequestResult:
        """
        Execute a single synchronous request attempt.

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Form data or raw data
            json_data: JSON data
            raw_body: Raw request body
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            session: Optional requests session to use
            attempt: Current attempt number (0-based)

        Returns:
            RequestResult object with response data and metadata

        Raises:
            Various request exceptions that may be retryable
        """
        # Apply rate limiting
        if self.rate_limiter:
            self.rate_limiter.acquire()

        # Use provided session or create new one
        if session is None:
            if self.session is None:
                self.session = requests.Session()
                self.session.verify = verify_ssl
                self.session.headers.update(
                    {
                        "User-Agent": self.config.user_agent,
                        **self.config.default_headers,
                    }
                )
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

        # Prepare kwargs
        kwargs = {
            "method": request_config.method,
            "url": request_config.url,
            "headers": request_config.headers,
            "params": request_config.params,
            "data": request_config.data,
            "json": request_config.json_data,
            "timeout": request_config.timeout,
            "verify": request_config.verify_ssl,
        }

        # Optional response caching for GET
        if (
            method.upper() == "GET"
            and self.config.enable_response_cache
            and not disable_cache
        ):
            cached = response_cache.get_response(url, method, params, headers)
            if cached is not None:
                duration = time.time() - start_time
                result = RequestResult.from_response(url, method, cached, duration)
                result.metadata = result.metadata or RequestMetadata(
                    request_id=str(uuid.uuid4()), timestamp=time.time()
                )
                return result

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
            duration=duration,
            method=method,
            url=self._sanitize_url(url),
        )

        # Cache GET responses
        if (
            method.upper() == "GET"
            and response.status_code == 200
            and self.config.enable_response_cache
            and not disable_cache
        ):
            response_cache.set_response(url, method, response, params, headers)

        # Check if status code is retryable
        if self.retry_manager.should_retry(attempt, status_code=response.status_code):
            raise RequestExecutionError(
                f"Retryable status code: {response.status_code}"
            )

        return result

    async def __aenter__(self):
        """Initialize async session with HTTP/2 support."""
        ssl_context = SSLValidator.create_ssl_context(self.config.ssl)

        # Determine HTTP/2 implementation
        use_httpx = self.config.session.enable_http2 and (
            self.config.session.http2_implementation == "httpx"
            or (self.config.session.http2_implementation == "auto" and HTTPX_AVAILABLE)
        )

        if use_httpx:
            # Use httpx for true HTTP/2 support
            self._httpx_client = httpx.AsyncClient(
                http2=True,
                verify=(
                    ssl_context
                    if self.config.ssl.verification_level
                    != SSLVerificationLevel.DISABLED
                    else False
                ),
                timeout=httpx.Timeout(
                    connect=self.config.session.connection_timeout,
                    read=self.config.session.read_timeout,
                    write=10.0,
                    pool=5.0,
                ),
                limits=httpx.Limits(
                    max_connections=self.config.session.max_connections,
                    max_keepalive_connections=self.config.session.max_connections_per_host,
                ),
                headers={
                    "User-Agent": self.config.user_agent,
                    **self.config.default_headers,
                },
            )
            log_info("HTTP/2 enabled with httpx client")
        else:
            # Fallback to aiohttp (HTTP/1.1)
            self._httpx_client = None

        # Configure connector for aiohttp fallback
        connector_kwargs = {
            "limit": self.config.session.max_connections,
            "limit_per_host": self.config.session.max_connections_per_host,
            "ssl": ssl_context,
            "ttl_dns_cache": 300,
            "use_dns_cache": True,
            "keepalive_timeout": self.config.session.keepalive_timeout,
            "enable_cleanup_closed": self.config.session.enable_cleanup_closed,
            "force_close": self.config.session.force_close,
        }

        if self.config.session.enable_http2 and not HTTPX_AVAILABLE:
            log_info(
                "HTTP/2 requested but httpx not available, falling back to HTTP/1.1"
            )
        else:
            log_info("HTTP/1.1 mode enabled for async requests")

        self.connector = aiohttp.TCPConnector(**connector_kwargs)

        # Fixed timeout configuration with proper breakdown
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
        if self._httpx_client:
            try:
                await self._httpx_client.aclose()
                log_info("HTTP/2 httpx client closed successfully")
            except Exception as e:
                log_error(e, {"component": "HttpRunner", "action": "httpx_cleanup"})

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

    async def _process_async_response(
        self, response, url: str, method: str, start_time: float
    ) -> RequestResult:
        """Process async response and create RequestResult."""
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

    async def send_request_async(
        self,
        url: URL,
        method: Method = "GET",
        headers: Optional[Headers] = None,
        params: Optional[Params] = None,
        data: Optional[Data] = None,
        json_data: Optional[JSONData] = None,
        raw_body: Optional[RawBody] = None,
        timeout: Optional[Timeout] = None,
        disable_cache: bool = False,
        retry_config: Optional[RetryConfig] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        on_success: Optional[RequestCallback] = None,
        on_error: Optional[ErrorCallback] = None,
        **kwargs: Any,
    ) -> RequestResult:
        """
        Send asynchronous HTTP request with retry logic.

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
            raise RuntimeError(
                "Async session not initialized. Use async context manager."
            )

        # Optionally override retry and rate limit per-request
        original_retry_manager = self.retry_manager
        original_rate_limiter = self.rate_limiter

        try:
            if retry_config is not None:
                self.retry_manager = RetryManager(retry_config)
            if rate_limit_config is not None:
                temp_runner_config = RunnerConfig(
                    rate_limit=rate_limit_config,
                    ssl=self.config.ssl,
                    session=self.config.session,
                    retry=self.config.retry,
                    user_agent=self.config.user_agent,
                    default_headers=self.config.default_headers,
                    enable_response_cache=self.config.enable_response_cache,
                )
                self.rate_limiter = HttpRunner(
                    temp_runner_config
                )._create_rate_limiter()

            # Execute with retry logic
            last_exception = None
            effective_attempts = self.retry_manager.config.max_attempts

            for attempt in range(effective_attempts):
                try:
                    return await self._execute_async_request(
                        url=url,
                        method=method,
                        headers=headers,
                        params=params,
                        data=data,
                        json_data=json_data,
                        attempt=attempt,
                        disable_cache=disable_cache,
                        **kwargs,
                    )
                except Exception as e:
                    last_exception = e

                    # Check if we should retry
                    if not self.retry_manager.should_retry(attempt, exception=e):
                        break

                    # Wait before retry (except on last attempt)
                    if attempt < effective_attempts - 1:
                        await self.retry_manager.wait_for_retry(attempt)

            # If we get here, all retries failed
            # Handle the final exception
            if isinstance(last_exception, asyncio.TimeoutError):
                error_msg = (
                    f"⏰ Async request timed out after {effective_attempts} attempts"
                )
                suggestion = "💡 Try increasing the timeout value or check if the server is responding."
                raise TimeoutError(f"{error_msg}\n\n{suggestion}") from last_exception
            elif isinstance(last_exception, aiohttp.ClientError):
                error_msg = f"🌐 Network error after {effective_attempts} attempts"
                suggestion = (
                    "💡 Check your network connection and verify the URL is correct."
                )
                raise NetworkError(
                    f"{error_msg}: {str(last_exception)}\n\n{suggestion}"
                ) from last_exception
            else:
                error_msg = f"❌ Async request execution error after {effective_attempts} attempts"
                suggestion = "💡 Check your request parameters and try again."
                raise RequestExecutionError(
                    f"{error_msg}: {str(last_exception)}\n\n{suggestion}"
                ) from last_exception

        finally:
            # Always restore original managers
            self.retry_manager = original_retry_manager
            self.rate_limiter = original_rate_limiter

    async def _execute_async_request(
        self,
        url: str,
        method: str,
        headers: Optional[dict[str, str]],
        params: Optional[dict[str, Any]],
        data: Optional[Any],
        json_data: Optional[dict[str, Any]],
        attempt: int,
        disable_cache: bool,
        **kwargs,
    ) -> RequestResult:
        """
        Execute a single asynchronous request attempt.

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Request data
            json_data: JSON data
            attempt: Current attempt number (0-based)
            **kwargs: Additional request parameters

        Returns:
            RequestResult object with response data and metadata

        Raises:
            Various request exceptions that may be retryable
        """
        # Apply rate limiting
        if self.rate_limiter and hasattr(self.rate_limiter, "acquire_async"):
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

        # Cache GET responses (async) if enabled and not bypassed
        if (
            method.upper() == "GET"
            and self.config.enable_response_cache
            and not disable_cache
        ):
            cached = response_cache.get_response(url, method, params, headers)
            if cached is not None:
                duration = time.time() - start_time
                return RequestResult.from_response(url, method, cached, duration)

        # Use httpx for HTTP/2 or aiohttp for HTTP/1.1
        if self._httpx_client:
            # HTTP/2 with httpx
            async with self._httpx_client.stream(
                method, url, **request_kwargs
            ) as response:
                result = await self._process_httpx_response(
                    response, url, method, start_time
                )

                # Check if status code is retryable
                if self.retry_manager.should_retry(
                    attempt, status_code=response.status_code
                ):
                    retry_after = response.headers.get("Retry-After")
                    max_attempts = self.retry_manager.config.max_attempts
                    if attempt < max_attempts - 1:
                        await self.retry_manager.wait_for_retry(attempt, retry_after)
                    raise RequestExecutionError(
                        f"Retryable status code: {response.status_code}"
                    )

                # Cache successful GET responses
                if (
                    method.upper() == "GET"
                    and response.status_code == 200
                    and self.config.enable_response_cache
                    and not disable_cache
                ):
                    response_cache.set_response(url, method, result, params, headers)

                return result
        else:
            # HTTP/1.1 with aiohttp
            async with self.async_session.request(
                method, url, **request_kwargs
            ) as response:
                result = await self._process_async_response(
                    response, url, method, start_time
                )

                # Check if status code is retryable
                if self.retry_manager.should_retry(
                    attempt, status_code=response.status
                ):
                    retry_after = response.headers.get("Retry-After")
                    # Respect Retry-After in async path
                    max_attempts = self.retry_manager.config.max_attempts
                    if attempt < max_attempts - 1:
                        await self.retry_manager.wait_for_retry(attempt, retry_after)
                    raise RequestExecutionError(
                        f"Retryable status code: {response.status}"
                    )

                # Cache successful GET responses
                if (
                    method.upper() == "GET"
                    and response.status == 200
                    and self.config.enable_response_cache
                    and not disable_cache
                ):
                    response_cache.set_response(url, method, result, params, headers)

                return result

    async def _process_httpx_response(
        self, response, url: str, method: str, start_time: float
    ) -> RequestResult:
        """Process httpx response and create RequestResult."""
        duration = time.time() - start_time

        # Read response content
        content = b""
        async for chunk in response.aiter_bytes():
            content += chunk

        text = content.decode("utf-8", errors="ignore")

        # Parse JSON if applicable
        body = text
        try:
            if "application/json" in response.headers.get("content-type", ""):
                import json

                body = json.loads(text)
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
                    "status_code": response.status_code,
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
            f"HTTP/2 request completed: {method} {url}",
            {
                "status_code": response.status_code,
                "duration": duration,
                "response_size": len(content),
                "http_version": getattr(response, "http_version", "HTTP/2"),
            },
        )

        return result

    async def send_requests_batch(
        self,
        request_configs: RequestConfigList,
        max_concurrent: Optional[int] = None,
        on_success: Optional[RequestCallback] = None,
        on_error: Optional[ErrorCallback] = None,
    ) -> RequestResultList:
        """
        Send multiple requests concurrently.

        Args:
            requests: List of request configurations
            max_concurrent: Maximum concurrent requests

        Returns:
            List of RequestResult objects or exceptions

        Raises:
            RuntimeError: If async session not initialized
        """
        if self._closed or not self.async_session:
            raise RuntimeError(
                "Async session not initialized. Use async context manager."
            )

        semaphore = asyncio.Semaphore(max_concurrent or 10)

        async def execute_with_semaphore(request_config):
            async with semaphore:
                return await self.send_request_async(**request_config)

        tasks = [execute_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def send_request_streaming(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[dict[str, Any]] = None,
        chunk_size: int = 8192,
        **kwargs,
    ):
        """
        Send streaming HTTP request for large responses.

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Request data
            json_data: JSON data
            chunk_size: Size of chunks to read
            **kwargs: Additional request parameters

        Yields:
            bytes: Response content chunks

        Raises:
            RuntimeError: If async session not initialized
            ValidationError: If request configuration is invalid
            NetworkError: If network issues occur
            TimeoutError: If request times out
        """
        if self._closed or not self.async_session:
            raise RuntimeError(
                "Async session not initialized. Use async context manager."
            )

        # Apply rate limiting
        if self.rate_limiter and hasattr(self.rate_limiter, "acquire_async"):
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

        try:
            async with self.async_session.request(
                method, url, **request_kwargs
            ) as response:
                async for chunk in response.content.iter_chunked(chunk_size):
                    yield chunk

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            raise RequestExecutionError(f"Request execution error: {str(e)}") from e

    def validate_session_health(self) -> bool:
        """
        Validate session is still healthy and responsive.

        Returns:
            True if session is healthy, False otherwise
        """
        if not self.session:
            return False

        try:
            # Use a lightweight health check endpoint
            response = self.session.get(
                "https://httpbin.org/status/200",
                timeout=5,
                verify=self.config.ssl.verification_level
                != SSLVerificationLevel.DISABLED,
            )
            return response.status_code == 200
        except Exception:
            return False

    async def validate_session_health_async(self) -> bool:
        """
        Validate async session is still healthy and responsive.

        Returns:
            True if session is healthy, False otherwise
        """
        if not self.async_session:
            return False

        try:
            async with self.async_session.get(
                "https://httpbin.org/status/200", timeout=5
            ) as response:
                return response.status == 200
        except Exception:
            return False


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


def _parse_rate_limit_env(config):
    import os

    rate_algo = os.getenv("LOGICPWN_RATE_LIMIT_ALGORITHM")
    if rate_algo:
        try:
            config.rate_limit.algorithm = RateLimitAlgorithm(rate_algo)
        except ValueError:
            pass
    rate_rps = os.getenv("LOGICPWN_RATE_LIMIT_RPS")
    if rate_rps:
        try:
            config.rate_limit.requests_per_second = float(rate_rps)
        except ValueError:
            pass


def _parse_ssl_env(config):
    import os

    ssl_verification = os.getenv("LOGICPWN_SSL_VERIFICATION")
    if ssl_verification:
        try:
            config.ssl.verification_level = SSLVerificationLevel(ssl_verification)
        except ValueError:
            pass
    ssl_tls_version = os.getenv("LOGICPWN_SSL_MIN_TLS_VERSION")
    if ssl_tls_version:
        config.ssl.min_tls_version = ssl_tls_version


def _parse_session_env(config):
    import os

    http2_enabled = os.getenv("LOGICPWN_HTTP2_ENABLED")
    if http2_enabled:
        config.session.enable_http2 = http2_enabled.lower() in ("true", "1", "yes")
    max_connections = os.getenv("LOGICPWN_MAX_CONNECTIONS")
    if max_connections:
        try:
            config.session.max_connections = int(max_connections)
        except ValueError:
            pass


def load_config_from_env() -> RunnerConfig:
    """Load configuration from environment variables."""
    config = RunnerConfig()
    _parse_rate_limit_env(config)
    _parse_ssl_env(config)
    _parse_session_env(config)
    return config


# Legacy compatibility exports
def _execute_request(session, config):
    """Internal function to execute HTTP requests."""
    if hasattr(config, "url"):
        # RequestConfig object
        kwargs = {
            "method": config.method,
            "url": config.url,
            "headers": config.headers,
            "params": config.params,
            "data": config.data,
            "json": config.json_data,
            "timeout": config.timeout,
            "verify": config.verify_ssl,
        }
    elif isinstance(config, dict):
        # Dictionary config
        kwargs = {
            "method": config.get("method", "GET"),
            "url": config["url"],
            "headers": config.get("headers"),
            "params": config.get("params"),
            "data": config.get("data"),
            "json": config.get("json_data"),
            "timeout": config.get("timeout"),
            "verify": config.get("verify_ssl", True),
        }
    else:
        raise ValueError(
            f"Configuration must be dict or RequestConfig, got {type(config)}"
        )

    return session.request(**kwargs)
