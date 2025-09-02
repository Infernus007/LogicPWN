"""
Reliability module for LogicPwn - Circuit Breakers, Rate Limiting, Security Metrics, and Fault Tolerance.
"""

from .adaptive_rate_limiter import (
    AdaptiveRateLimiter,
    RateLimitConfig,
    RequestMetrics,
    rate_limiter_registry,
)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerMetrics,
    CircuitBreakerOpenException,
    CircuitBreakerState,
    circuit_breaker_registry,
)
from .security_metrics import (
    SecurityEvent,
    SecurityEventType,
    SecurityMetricsCollector,
    SecuritySeverity,
    record_security_event,
    security_metrics,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitBreakerOpenException",
    "CircuitBreakerMetrics",
    "circuit_breaker_registry",
    "AdaptiveRateLimiter",
    "RateLimitConfig",
    "RequestMetrics",
    "rate_limiter_registry",
    "SecurityMetricsCollector",
    "SecurityEvent",
    "SecurityEventType",
    "SecuritySeverity",
    "security_metrics",
    "record_security_event",
]
