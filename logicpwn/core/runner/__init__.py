"""
LogicPwn runner module with unified API and consolidated interfaces.

This module provides HTTP request functionality with:
- Unified API that consolidates all similar interfaces
- Fixed async timeout handling
- User-friendly error messages with actionable suggestions
- Simplified configuration options
- Consistent sync/async support

The unified API reduces confusion by providing a single interface
for all HTTP request operations instead of multiple similar classes.
"""

from logicpwn.models.request_config import RequestConfig as _RequestConfig
from logicpwn.models.request_result import RequestResult as _RequestResult

# Import core modules
from .async_request_helpers import (
    async_session_manager,
    send_request_async,
    send_requests_batch_async,
)
from .async_runner_core import AsyncRequestContext, AsyncRequestRunner
from .async_session_manager import AsyncSessionManager
from .request_builder import (
    CommonRequests,
    RequestBuilder,
    build_request,
)
from .runner import (
    HttpRunner,
    RateLimitAlgorithm,
    RateLimitConfig,
    RetryConfig,
    RetryManager,
    RunnerConfig,
    SessionConfig,
    SSLConfig,
    SSLVerificationLevel,
    create_development_config,
    create_secure_config,
    create_testing_config,
)

# Import standardized components
from .standardized_logging import (
    LogAction,
    LogComponent,
    StandardizedLogger,
    get_logger,
    log_error,
    log_info,
    log_request,
    log_response,
    log_warning,
)
from .type_definitions import (
    URL,
    ConfigurationError,
    Data,
    ErrorCallback,
    Headers,
    JSONData,
    LogicPwnError,
    Method,
    NetworkError,
    Params,
    RawBody,
    RequestCallback,
    RequestConfigDict,
    RequestConfigList,
    RequestExecutionError,
    RequestResultList,
    RetryCallback,
    Timeout,
    TimeoutError,
    ValidationError,
)

# Enhanced HttpRunner now provides consolidated API


# Re-export key classes for backward compatibility
RequestConfig = _RequestConfig
RequestResult = _RequestResult

# Export main classes and functions
__all__ = [
    # Enhanced core classes (recommended)
    "HttpRunner",
    "AsyncRequestRunner",
    "AsyncSessionManager",
    "RequestConfig",
    "RequestResult",
    # Configuration
    "RunnerConfig",
    "RateLimitConfig",
    "RetryConfig",
    "SessionConfig",
    "SSLConfig",
    "SSLVerificationLevel",
    "RateLimitAlgorithm",
    # Preset configurations
    "create_development_config",
    "create_secure_config",
    "create_testing_config",
    # Convenience functions
    "send_request_async",
    "send_requests_batch_async",
    "async_session_manager",
    # Request building
    "CommonRequests",
    "RequestBuilder",
    "build_request",
    # Async context
    "AsyncRequestContext",
    # Retry management
    "RetryManager",
    # Standardized logging
    "StandardizedLogger",
    "LogComponent",
    "LogAction",
    "get_logger",
    "log_info",
    "log_error",
    "log_request",
    "log_response",
    "log_warning",
    # Type definitions
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
    "RequestCallback",
    "ErrorCallback",
    "RetryCallback",
    # Error types
    "LogicPwnError",
    "NetworkError",
    "TimeoutError",
    "RequestExecutionError",
    "ValidationError",
    "ConfigurationError",
]
