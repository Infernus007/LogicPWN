"""
LogicPwn Core Module

This module provides the core functionality for business logic exploitation
and multi-step attack automation. It includes authentication, request execution,
response validation, and advanced async capabilities.

Key Components:
- Authentication and session management
- Request execution with advanced features
- Response validation and analysis
- Async/parallel execution
- Performance monitoring and caching
- Stress testing and load testing
"""

from .auth import (
    authenticate_session,
    validate_session,
    logout_session,
    AuthConfig
)

from .runner import (
    send_request,
    send_request_advanced,
    RequestConfig
)

from .validator import (
    validate_response,
    extract_from_response,
    validate_json_response,
    validate_html_response,
    chain_validations,
    ValidationResult,
    ValidationConfig,
    ValidationType,
    VulnerabilityPatterns,
    validate_validation_config,
    MAX_RESPONSE_TEXT_LENGTH,
    DEFAULT_CONFIDENCE_THRESHOLD
)

from .async_runner_core import AsyncRequestRunner, AsyncRequestContext
from .async_session_manager import AsyncSessionManager
from .async_request_helpers import send_request_async, send_requests_batch_async, async_session_manager

from .performance import (
    PerformanceMonitor,
    PerformanceBenchmark,
    MemoryProfiler,
    monitor_performance,
    performance_context,
    get_performance_summary
)

from .cache import (
    response_cache,
    session_cache,
    config_cache,
    get_cache_stats,
    clear_all_caches
)

from .stress_tester import (
    StressTester,
    StressTestConfig,
    StressTestMetrics,
    run_quick_stress_test,
    run_exploit_chain_stress_test
)

from .utils import (
    check_indicators,
    prepare_request_kwargs,
    validate_config
)

from .config import (
    config,
    get_timeout,
    get_max_retries
)

from .logging_utils import (
    log_info,
    log_warning,
    log_error,
    log_debug,
    log_request,
    log_response
)

__all__ = [
    # Authentication
    "authenticate_session",
    "validate_session", 
    "logout_session",
    "AuthConfig",
    
    # Request Execution
    "send_request",
    "send_request_advanced",
    "RequestConfig",
    
    # Response Validation
    "validate_response",
    "extract_from_response",
    "validate_json_response",
    "validate_html_response",
    "chain_validations",
    "ValidationResult",
    "ValidationConfig",
    "ValidationType",
    "VulnerabilityPatterns",
    "validate_validation_config",
    "MAX_RESPONSE_TEXT_LENGTH",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    
    # Async Execution
    "AsyncRequestRunner",
    "AsyncSessionManager",
    "send_request_async",
    "send_requests_batch_async",
    "async_session_manager",
    
    # Performance & Caching
    "PerformanceMonitor",
    "PerformanceBenchmark",
    "MemoryProfiler",
    "monitor_performance",
    "performance_context",
    "get_performance_summary",
    "response_cache",
    "session_cache",
    "config_cache",
    "get_cache_stats",
    "clear_all_caches",
    
    # Stress Testing
    "StressTester",
    "StressTestConfig",
    "StressTestMetrics",
    "run_quick_stress_test",
    "run_exploit_chain_stress_test",
    
    # Utilities
    "check_indicators",
    "prepare_request_kwargs",
    "validate_config",
    "config",
    "get_timeout",
    "get_max_retries",
    "log_info",
    "log_warning",
    "log_error",
    "log_debug",
    "log_request",
    "log_response"
] 