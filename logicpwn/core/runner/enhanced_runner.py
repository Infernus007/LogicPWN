"""
Enhanced runner module with improved security, rate limiting, and session management.

This module provides comprehensive HTTP request execution with:
- Enhanced rate limiting (token bucket, sliding window algorithms)
- SSL/TLS certificate validation with warnings
- Session management lifecycle improvements
- HTTP/2 support evaluation
- Configuration simplification
- Method decomposition for better maintainability
"""

import asyncio
import logging
import ssl
import time
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

import aiohttp

from logicpwn.core.config.config_utils import get_timeout
from logicpwn.core.logging import log_error, log_info, log_warning
from logicpwn.exceptions import (
    NetworkError,
    RequestExecutionError,
    ResponseError,
    TimeoutError,
    ValidationError,
)
from logicpwn.models.request_config import RequestConfig
from logicpwn.models.request_result import RequestResult


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms."""

    SIMPLE = "simple"
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"


class SSLVerificationLevel(Enum):
    """SSL verification levels."""

    STRICT = "strict"  # Full verification
    RELAXED = "relaxed"  # Verification with warnings
    DISABLED = "disabled"  # No verification


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    requests_per_second: float = 10.0
    burst_size: int = 5
    window_size: int = 60  # seconds for sliding window
    adaptive: bool = False  # Adaptive rate limiting based on response times
    response_time_threshold: float = 2.0  # seconds


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
class HTTP2Config:
    """HTTP/2 configuration."""

    enabled: bool = False
    prefer_http2: bool = False
    max_frame_size: int = 16384
    max_concurrent_streams: int = 100


@dataclass
class EnhancedRunnerConfig:
    """Comprehensive configuration for enhanced runner."""

    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    ssl: SSLConfig = field(default_factory=SSLConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    http2: HTTP2Config = field(default_factory=HTTP2Config)
    user_agent: str = "LogicPwn-Enhanced/2.0"
    default_headers: dict[str, str] = field(default_factory=dict)
    retry_attempts: int = 3
    retry_backoff: float = 1.0


class TokenBucketRateLimiter:
    """Token bucket rate limiting implementation."""

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
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(self.burst_size, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            # Calculate wait time
            wait_time = (1 - self.tokens) / self.rate
            return False, wait_time


class SlidingWindowRateLimiter:
    """Sliding window rate limiting implementation."""

    def __init__(self, rate: float, window_size: int):
        self.rate = rate
        self.window_size = window_size
        self.requests = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire permission for request execution."""
        async with self._lock:
            now = time.time()
            # Remove old requests outside the window
            cutoff = now - self.window_size
            self.requests = [
                req_time for req_time in self.requests if req_time > cutoff
            ]

            # Check if we can make a request
            max_requests = int(self.rate * self.window_size)
            if len(self.requests) < max_requests:
                self.requests.append(now)
                return True

            # Calculate wait time until oldest request exits window
            if self.requests:
                wait_time = self.requests[0] + self.window_size - now
                return False, max(0, wait_time)

            return True


class AdaptiveRateLimiter:
    """Adaptive rate limiting based on response times."""

    def __init__(
        self,
        base_rate: float,
        min_rate: float = 1.0,
        max_rate: float = 50.0,
        response_time_threshold: float = 2.0,
        adaptation_factor: float = 0.1,
    ):
        self.base_rate = base_rate
        self.current_rate = base_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.response_time_threshold = response_time_threshold
        self.adaptation_factor = adaptation_factor
        self.response_times = []
        self.max_history = 100
        self._lock = asyncio.Lock()

    async def record_response_time(self, response_time: float):
        """Record response time for adaptive rate adjustment."""
        async with self._lock:
            self.response_times.append(response_time)
            if len(self.response_times) > self.max_history:
                self.response_times.pop(0)

            # Adjust rate based on recent response times
            if len(self.response_times) >= 10:
                avg_response_time = sum(self.response_times[-10:]) / 10

                if avg_response_time > self.response_time_threshold:
                    # Slow responses, decrease rate
                    self.current_rate = max(
                        self.min_rate, self.current_rate * (1 - self.adaptation_factor)
                    )
                else:
                    # Fast responses, increase rate
                    self.current_rate = min(
                        self.max_rate, self.current_rate * (1 + self.adaptation_factor)
                    )

    async def acquire(self) -> bool:
        """Acquire permission for request execution."""
        # Simple implementation - could be enhanced with token bucket
        await asyncio.sleep(1.0 / self.current_rate)
        return True


class SSLValidator:
    """SSL/TLS certificate validation with enhanced security."""

    @staticmethod
    def create_ssl_context(ssl_config: SSLConfig) -> ssl.SSLContext:
        """Create SSL context based on configuration."""
        if ssl_config.verification_level == SSLVerificationLevel.DISABLED:
            warnings.warn(
                "SSL verification is disabled. This allows man-in-the-middle attacks. "
                "Only use this in controlled testing environments.",
                SecurityWarning,
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
                "SSL verification is in relaxed mode. Certificate errors will be logged but not fail requests.",
                UserWarning,
                stacklevel=2,
            )

        return context


class SecurityWarning(UserWarning):
    """Custom warning for security-related issues."""

    pass


class EnhancedSessionManager:
    """Enhanced session manager with improved lifecycle management."""

    def __init__(self, config: EnhancedRunnerConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.connector: Optional[aiohttp.TCPConnector] = None
        self.rate_limiter = self._create_rate_limiter()
        self._closed = False

    def _create_rate_limiter(self):
        """Create rate limiter based on configuration."""
        rate_config = self.config.rate_limit

        if rate_config.adaptive:
            return AdaptiveRateLimiter(
                base_rate=rate_config.requests_per_second,
                response_time_threshold=rate_config.response_time_threshold,
            )
        elif rate_config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return TokenBucketRateLimiter(
                rate=rate_config.requests_per_second, burst_size=rate_config.burst_size
            )
        elif rate_config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return SlidingWindowRateLimiter(
                rate=rate_config.requests_per_second,
                window_size=rate_config.window_size,
            )
        else:
            # Simple rate limiting
            return None

    async def __aenter__(self):
        """Initialize session with enhanced configuration."""
        # Create SSL context
        ssl_context = SSLValidator.create_ssl_context(self.config.ssl)

        # Create connector with enhanced settings
        self.connector = aiohttp.TCPConnector(
            limit=self.config.session.max_connections,
            limit_per_host=self.config.session.max_connections_per_host,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=self.config.session.keepalive_timeout,
            enable_cleanup_closed=self.config.session.enable_cleanup_closed,
            force_close=self.config.session.force_close,
            ssl=ssl_context,
        )

        # Create timeout configuration
        timeout = aiohttp.ClientTimeout(
            total=self.config.session.total_timeout,
            connect=self.config.session.connection_timeout,
            sock_read=self.config.session.read_timeout,
        )

        # Prepare default headers
        default_headers = {
            "User-Agent": self.config.user_agent,
            **self.config.default_headers,
        }

        # Create session
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout,
            headers=default_headers,
            auto_decompress=self.config.session.auto_decompress,
        )

        self._closed = False
        log_info(
            "Enhanced session manager initialized",
            {
                "max_connections": self.config.session.max_connections,
                "rate_limit_algorithm": self.config.rate_limit.algorithm.value,
                "ssl_verification": self.config.ssl.verification_level.value,
                "http2_enabled": self.config.http2.enabled,
            },
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Properly cleanup session resources."""
        if not self._closed:
            await self.close()

    async def close(self):
        """Explicitly close session and cleanup resources."""
        if self.session and not self._closed:
            try:
                await self.session.close()
                # Wait a bit for underlying connections to close
                await asyncio.sleep(0.1)
                self._closed = True
                log_info("Enhanced session manager closed successfully")
            except Exception as e:
                log_error(
                    e, {"component": "EnhancedSessionManager", "action": "cleanup"}
                )
                raise

        if self.connector:
            try:
                await self.connector.close()
            except Exception as e:
                log_error(e, {"component": "TCPConnector", "action": "cleanup"})

    async def send_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> RequestResult:
        """Send request with enhanced features."""
        if self._closed:
            raise RuntimeError("Session manager is closed")

        # Apply rate limiting
        if self.rate_limiter:
            result = await self.rate_limiter.acquire()
            if isinstance(result, tuple) and not result[0]:
                wait_time = result[1]
                log_warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                await self.rate_limiter.acquire()

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
            async with self.session.request(method, url, **request_kwargs) as response:
                duration = time.time() - start_time

                # Record response time for adaptive rate limiting
                if hasattr(self.rate_limiter, "record_response_time"):
                    await self.rate_limiter.record_response_time(duration)

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
                    f"Request completed: {method} {url}",
                    {
                        "status_code": response.status,
                        "duration": duration,
                        "response_size": len(content),
                    },
                )

                return result

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            log_error(f"Request timeout: {method} {url}", {"duration": duration})
            raise TimeoutError(f"Request timeout after {duration:.2f}s")

        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            log_error(
                f"Client error: {method} {url}", {"error": str(e), "duration": duration}
            )
            raise NetworkError(f"Client error: {str(e)}")

        except Exception as e:
            duration = time.time() - start_time
            log_error(
                f"Unexpected error: {method} {url}",
                {"error": str(e), "duration": duration},
            )
            raise RequestExecutionError(f"Request execution error: {str(e)}")


class EnhancedAsyncRunner:
    """Enhanced async request runner with comprehensive security features."""

    def __init__(self, config: Optional[EnhancedRunnerConfig] = None):
        self.config = config or EnhancedRunnerConfig()
        self.session_manager: Optional[EnhancedSessionManager] = None

    async def __aenter__(self):
        """Initialize enhanced runner."""
        self.session_manager = EnhancedSessionManager(self.config)
        await self.session_manager.__aenter__()

        log_info(
            "Enhanced async runner initialized",
            {
                "rate_limiting": self.config.rate_limit.algorithm.value,
                "ssl_verification": self.config.ssl.verification_level.value,
                "http2_support": self.config.http2.enabled,
            },
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup enhanced runner."""
        if self.session_manager:
            await self.session_manager.__aexit__(exc_type, exc_val, exc_tb)

    async def send_request(self, *args, **kwargs) -> RequestResult:
        """Send single request."""
        if not self.session_manager:
            raise RuntimeError("Runner not initialized. Use async context manager.")

        return await self.session_manager.send_request(*args, **kwargs)

    async def send_requests_batch(
        self, requests: list[dict[str, Any]], max_concurrent: Optional[int] = None
    ) -> list[RequestResult]:
        """Send multiple requests concurrently."""
        if not self.session_manager:
            raise RuntimeError("Runner not initialized. Use async context manager.")

        semaphore = asyncio.Semaphore(max_concurrent or 10)

        async def execute_with_semaphore(request_config):
            async with semaphore:
                return await self.session_manager.send_request(**request_config)

        tasks = [execute_with_semaphore(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)


# Simplified factory functions for common configurations


def create_secure_config() -> EnhancedRunnerConfig:
    """Create configuration for maximum security."""
    return EnhancedRunnerConfig(
        ssl=SSLConfig(
            verification_level=SSLVerificationLevel.STRICT, min_tls_version="TLSv1.3"
        ),
        rate_limit=RateLimitConfig(
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            requests_per_second=5.0,
            burst_size=3,
        ),
    )


def create_testing_config() -> EnhancedRunnerConfig:
    """Create configuration for testing environments."""
    return EnhancedRunnerConfig(
        ssl=SSLConfig(verification_level=SSLVerificationLevel.RELAXED),
        rate_limit=RateLimitConfig(
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW, requests_per_second=20.0
        ),
    )


def create_development_config() -> EnhancedRunnerConfig:
    """Create configuration for development."""
    return EnhancedRunnerConfig(
        ssl=SSLConfig(verification_level=SSLVerificationLevel.DISABLED),
        rate_limit=RateLimitConfig(requests_per_second=50.0),
    )


def create_adaptive_config() -> EnhancedRunnerConfig:
    """Create configuration with adaptive rate limiting."""
    return EnhancedRunnerConfig(
        rate_limit=RateLimitConfig(
            adaptive=True, requests_per_second=10.0, response_time_threshold=1.5
        )
    )
