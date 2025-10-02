"""
Type definitions for LogicPwn runner module.

This module provides comprehensive type hints and type aliases
for better code clarity and IDE support.
"""

from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
    Union,
)

from logicpwn.models.request_config import RequestConfig
from logicpwn.models.request_result import RequestResult

# Type aliases for better readability
URL = str
Method = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
Headers = dict[str, str]
Params = dict[str, Any]
Data = Union[dict[str, Any], str, bytes, None]
JSONData = Optional[dict[str, Any]]
RawBody = Optional[str]
Timeout = Optional[float]
RequestConfigDict = dict[str, Any]

# Generic type for request configurations
T = TypeVar("T", bound=Union[RequestConfig, RequestConfigDict])


# Configuration type definitions
class RunnerConfigDict(TypedDict, total=False):
    """Type definition for runner configuration dictionary."""

    max_concurrent: int
    timeout: float
    verify_ssl: bool
    user_agent: str
    default_headers: Headers
    enable_caching: bool
    enable_http2: bool


class RetryConfigDict(TypedDict, total=False):
    """Type definition for retry configuration dictionary."""

    max_attempts: int
    base_delay: float
    max_delay: float
    exponential_base: float
    jitter: bool
    retryable_status_codes: list[int]
    respect_retry_after: bool


class RateLimitConfigDict(TypedDict, total=False):
    """Type definition for rate limit configuration dictionary."""

    algorithm: str
    requests_per_second: float
    burst_size: int
    window_size: int
    adaptive: bool


class SSLConfigDict(TypedDict, total=False):
    """Type definition for SSL configuration dictionary."""

    verification_level: str
    min_tls_version: str
    custom_ca_bundle: Optional[str]
    client_cert: Optional[str]
    client_key: Optional[str]


class SessionConfigDict(TypedDict, total=False):
    """Type definition for session configuration dictionary."""

    max_connections: int
    max_connections_per_host: int
    connection_timeout: float
    read_timeout: float
    total_timeout: float
    keepalive_timeout: float
    enable_cleanup_closed: bool
    force_close: bool
    auto_decompress: bool
    enable_http2: bool


# Logging types
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogContext = dict[str, Any]


class Logger(Protocol):
    """Protocol for logger objects."""

    def debug(self, message: str, context: Optional[LogContext] = None) -> None:
        """Log debug message."""
        ...

    def info(self, message: str, context: Optional[LogContext] = None) -> None:
        """Log info message."""
        ...

    def warning(self, message: str, context: Optional[LogContext] = None) -> None:
        """Log warning message."""
        ...

    def error(self, message: str, context: Optional[LogContext] = None) -> None:
        """Log error message."""
        ...

    def critical(self, message: str, context: Optional[LogContext] = None) -> None:
        """Log critical message."""
        ...


# Rate limiter types
class RateLimiter(Protocol):
    """Protocol for rate limiter objects."""

    async def acquire(self) -> bool:
        """Acquire permission for request."""
        ...


class SyncRateLimiter(Protocol):
    """Protocol for synchronous rate limiter objects."""

    def acquire(self) -> bool:
        """Acquire permission for request."""
        ...


# Session types
class SessionManager(Protocol):
    """Protocol for session manager objects."""

    async def __aenter__(self) -> "SessionManager":
        """Async context manager entry."""
        ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        ...

    async def get(self, url: URL, **kwargs: Any) -> RequestResult:
        """Send GET request."""
        ...

    async def post(self, url: URL, **kwargs: Any) -> RequestResult:
        """Send POST request."""
        ...

    async def put(self, url: URL, **kwargs: Any) -> RequestResult:
        """Send PUT request."""
        ...

    async def delete(self, url: URL, **kwargs: Any) -> RequestResult:
        """Send DELETE request."""
        ...


# Request builder types
class RequestBuilder(Protocol):
    """Protocol for request builder objects."""

    def method(self, method: Method) -> "RequestBuilder":
        """Set HTTP method."""
        ...

    def headers(self, headers: Headers) -> "RequestBuilder":
        """Set headers."""
        ...

    def params(self, params: Params) -> "RequestBuilder":
        """Set parameters."""
        ...

    def data(self, data: Data) -> "RequestBuilder":
        """Set data."""
        ...

    def json_data(self, json_data: JSONData) -> "RequestBuilder":
        """Set JSON data."""
        ...

    def timeout(self, timeout: Timeout) -> "RequestBuilder":
        """Set timeout."""
        ...

    def build(self) -> RequestConfig:
        """Build the request configuration."""
        ...


# Error types
class LogicPwnError(Exception):
    """Base exception for LogicPwn with enhanced error context."""

    def __init__(
        self,
        message: str,
        context: Optional[LogContext] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.context = context or {}
        self.suggestion = suggestion


class NetworkError(LogicPwnError):
    """Network-related errors."""


class TimeoutError(LogicPwnError):
    """Timeout errors."""


class RequestExecutionError(LogicPwnError):
    """Request execution errors."""


class ValidationError(LogicPwnError):
    """Validation errors."""


class ConfigurationError(LogicPwnError):
    """Configuration errors."""


# Utility types
RequestConfigList = list[Union[RequestConfig, RequestConfigDict]]
RequestResultList = list[RequestResult]

# Callback types
RequestCallback = Callable[[RequestResult], None]
ErrorCallback = Callable[[Exception], None]
RetryCallback = Callable[[int, Exception], bool]


# Context manager types
class AsyncContextManager(Protocol):
    """Protocol for async context managers."""

    async def __aenter__(self) -> Any:
        """Async context manager entry."""
        ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        ...


# Factory types
RunnerFactory = Callable[[Optional[RunnerConfigDict]], Any]
ConfigFactory = Callable[[], Any]

# Export all types
__all__ = [
    # Type aliases
    "URL",
    "Method",
    "Headers",
    "Params",
    "Data",
    "JSONData",
    "RawBody",
    "Timeout",
    "RequestConfigDict",
    "RequestConfigList",
    "RequestResultList",
    # Protocols
    "Logger",
    "RateLimiter",
    "SyncRateLimiter",
    "SessionManager",
    "RequestBuilder",
    "AsyncContextManager",
    # TypedDict classes
    "RunnerConfigDict",
    "RetryConfigDict",
    "RateLimitConfigDict",
    "SSLConfigDict",
    "SessionConfigDict",
    # Error classes
    "LogicPwnError",
    "NetworkError",
    "TimeoutError",
    "RequestExecutionError",
    "ValidationError",
    "ConfigurationError",
    # Callback types
    "RequestCallback",
    "ErrorCallback",
    "RetryCallback",
    # Factory types
    "RunnerFactory",
    "ConfigFactory",
    # Generic types
    "T",
]
