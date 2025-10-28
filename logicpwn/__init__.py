"""
LogicPWN - Business Logic Vulnerability Testing Framework

A powerful, easy-to-use framework for testing business logic vulnerabilities in web applications.

Quick Start:
    >>> from logicpwn import SecurityTester, quick_idor_test
    >>>
    >>> # One-line IDOR test
    >>> results = quick_idor_test(
    ...     "https://api.example.com",
    ...     "/api/users/{id}",
    ...     [1, 2, 3, "admin"]
    ... )
    >>> print(results['summary'])
    >>>
    >>> # Class-based testing with authentication
    >>> with SecurityTester("https://api.example.com") as tester:
    ...     tester.authenticate("admin", "password123")
    ...     results = tester.test_idor("/api/users/{id}", [1, 2, 3])
    ...     print(results['summary'])

Documentation: https://logicpwn.github.io
Repository: https://github.com/Infernus007/LogicPWN
"""

__version__ = "0.4.0"
__author__ = "LogicPwn Team"

# === Access Control Testing ===
from logicpwn.core.access import (
    EnhancedAccessTester,
    detect_idor_flaws,
    detect_idor_flaws_async,
)

# === Core Authentication ===
from logicpwn.core.auth import (
    AuthConfig,
    CSRFConfig,
    JWTHandler,
    authenticate_session,
    logout_session,
    validate_session,
)

# === Caching ===
from logicpwn.core.cache import (
    clear_all_caches,
    config_cache,
    get_cache_stats,
    response_cache,
    session_cache,
)

# === Configuration ===
from logicpwn.core.config.config_utils import (
    get_max_retries,
    get_timeout,
)

# === Exploit Engine ===
from logicpwn.core.exploit_engine import (
    ExploitChain,
    ExploitStep,
    async_run_exploit_chain,
    load_exploit_chain_from_file,
    run_exploit_chain,
)

# === Logging ===
from logicpwn.core.logging import (
    log_debug,
    log_error,
    log_info,
    log_request,
    log_response,
    log_warning,
)

# === Performance & Monitoring ===
from logicpwn.core.performance import (
    MemoryProfiler,
    PerformanceBenchmark,
    PerformanceMonitor,
    get_performance_summary,
    monitor_performance,
    performance_context,
)

# === HTTP Runner ===
from logicpwn.core.runner import (
    AsyncRequestRunner,
    AsyncSessionManager,
    HttpRunner,
    RunnerConfig,
    async_session_manager,
    send_request_async,
    send_requests_batch_async,
)

# === Stress Testing ===
from logicpwn.core.stress import (
    StressTestConfig,
    StressTester,
    StressTestMetrics,
    run_exploit_chain_stress_test,
    run_quick_stress_test,
)

# === Utilities ===
from logicpwn.core.utils import (
    check_indicators,
    prepare_request_kwargs,
    validate_config,
)

# === Response Validation ===
from logicpwn.core.validator import (
    ValidationConfig,
    ValidationResult,
    validate_response,
    validate_with_preset,
)

# === Legacy Exceptions (for backwards compatibility) ===
from logicpwn.exceptions import (
    LoginFailedException,
    NetworkError,
    TimeoutError,
    ValidationError,
)

# === Enhanced Exceptions ===
from logicpwn.exceptions.enhanced_exceptions import (
    AuthenticationError,
    ConfigurationError,
    ExploitChainError,
    IDORTestError,
    LogicPwnError,
    SessionError,
)

# === Models ===
from logicpwn.models import (
    RequestConfig,
    RequestMetadata,
    RequestResult,
    SecurityAnalysis,
)

# === High-Level Convenience APIs (RECOMMENDED STARTING POINT) ===
from logicpwn.quickstart import (
    SecurityTester,
    quick_auth_test,
    quick_exploit_chain,
    quick_idor_test,
)

# === Result Objects ===
from logicpwn.results import (
    ExploitChainResult,
    SecurityTestResult,
)

# === Public API ===
__all__ = [
    # === Quick Start APIs (RECOMMENDED) ===
    "SecurityTester",
    "quick_idor_test",
    "quick_auth_test",
    "quick_exploit_chain",
    # === Authentication ===
    "authenticate_session",
    "validate_session",
    "logout_session",
    "AuthConfig",
    "CSRFConfig",
    "JWTHandler",
    # === Testing Functions ===
    "detect_idor_flaws",
    "detect_idor_flaws_async",
    "run_exploit_chain",
    "async_run_exploit_chain",
    "load_exploit_chain_from_file",
    # === Core Classes ===
    "HttpRunner",
    "RunnerConfig",
    "AsyncRequestRunner",
    "AsyncSessionManager",
    "EnhancedAccessTester",
    "ExploitChain",
    "ExploitStep",
    # === Async Functions ===
    "send_request_async",
    "send_requests_batch_async",
    "async_session_manager",
    # === Validation ===
    "validate_response",
    "validate_with_preset",
    "ValidationConfig",
    "ValidationResult",
    # === Result Objects ===
    "SecurityTestResult",
    "ExploitChainResult",
    # === Models ===
    "RequestConfig",
    "RequestResult",
    "RequestMetadata",
    "SecurityAnalysis",
    # === Enhanced Exceptions ===
    "LogicPwnError",
    "AuthenticationError",
    "IDORTestError",
    "ExploitChainError",
    "ConfigurationError",
    "SessionError",
    # === Legacy Exceptions ===
    "LoginFailedException",
    "NetworkError",
    "TimeoutError",
    "ValidationError",
    # === Performance & Monitoring ===
    "PerformanceMonitor",
    "PerformanceBenchmark",
    "MemoryProfiler",
    "monitor_performance",
    "performance_context",
    "get_performance_summary",
    # === Caching ===
    "response_cache",
    "session_cache",
    "config_cache",
    "get_cache_stats",
    "clear_all_caches",
    # === Stress Testing ===
    "StressTester",
    "StressTestConfig",
    "StressTestMetrics",
    "run_quick_stress_test",
    "run_exploit_chain_stress_test",
    # === Configuration ===
    "get_timeout",
    "get_max_retries",
    # === Logging ===
    "log_info",
    "log_warning",
    "log_error",
    "log_debug",
    "log_request",
    "log_response",
    # === Utilities ===
    "check_indicators",
    "prepare_request_kwargs",
    "validate_config",
    # === Version ===
    "__version__",
    "__author__",
]
