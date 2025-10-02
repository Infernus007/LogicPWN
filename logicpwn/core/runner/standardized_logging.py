"""
Standardized logging for LogicPwn runner module.

This module provides consistent logging format and structured logging
across all runner components.
"""

import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Optional

from loguru import logger

from .type_definitions import LogContext, LogLevel


class LogComponent(Enum):
    """Logging components for structured logging."""

    RUNNER = "runner"
    ASYNC_RUNNER = "async_runner"
    SESSION_MANAGER = "session_manager"
    RATE_LIMITER = "rate_limiter"
    RETRY_MANAGER = "retry_manager"
    CACHE = "cache"
    SSL = "ssl"
    TIMEOUT = "timeout"
    NETWORK = "network"
    AUTH = "auth"


class LogAction(Enum):
    """Logging actions for structured logging."""

    INIT = "init"
    CLEANUP = "cleanup"
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    RETRY = "retry"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    SSL_VERIFY = "ssl_verify"
    AUTH = "auth"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"


@dataclass
class LogEntry:
    """Structured log entry."""

    timestamp: float
    level: LogLevel
    component: LogComponent
    action: LogAction
    message: str
    context: LogContext
    duration: Optional[float] = None
    status_code: Optional[int] = None
    url: Optional[str] = None
    method: Optional[str] = None
    error_type: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert log entry to dictionary."""
        return asdict(self)


class StandardizedLogger:
    """Standardized logger for LogicPwn runner module."""

    def __init__(self, component: LogComponent):
        """
        Initialize standardized logger.

        Args:
            component: The logging component
        """
        self.component = component
        self._start_times: dict[str, float] = {}

    def _create_context(
        self, action: LogAction, context: Optional[LogContext] = None, **kwargs: Any
    ) -> LogContext:
        """Create standardized log context."""
        base_context = {
            "component": self.component.value,
            "action": action.value,
            "timestamp": time.time(),
        }

        if context:
            base_context.update(context)

        # Add any additional kwargs
        base_context.update(kwargs)

        return base_context

    def _log(
        self,
        level: LogLevel,
        action: LogAction,
        message: str,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """Internal logging method."""
        log_context = self._create_context(action, context, **kwargs)

        # Format message with context
        formatted_message = f"[{self.component.value}] {message}"

        # Add context to log message
        if log_context:
            context_str = " | ".join(
                [
                    f"{k}={v}"
                    for k, v in log_context.items()
                    if k not in ["component", "action", "timestamp"]
                ]
            )
            if context_str:
                formatted_message += f" | {context_str}"

        # Log with appropriate level
        if level == "DEBUG":
            logger.debug(formatted_message)
        elif level == "INFO":
            logger.info(formatted_message)
        elif level == "WARNING":
            logger.warning(formatted_message)
        elif level == "ERROR":
            logger.error(formatted_message)
        elif level == "CRITICAL":
            logger.critical(formatted_message)

    def debug(
        self, message: str, context: Optional[LogContext] = None, **kwargs: Any
    ) -> None:
        """Log debug message."""
        self._log("DEBUG", LogAction.INIT, message, context, **kwargs)

    def info(
        self,
        message: str,
        action: LogAction = LogAction.INIT,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """Log info message."""
        self._log("INFO", action, message, context, **kwargs)

    def warning(
        self,
        message: str,
        action: LogAction = LogAction.ERROR,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """Log warning message."""
        self._log("WARNING", action, message, context, **kwargs)

    def error(
        self,
        message: str,
        action: LogAction = LogAction.ERROR,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """Log error message."""
        self._log("ERROR", action, message, context, **kwargs)

    def critical(
        self,
        message: str,
        action: LogAction = LogAction.ERROR,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """Log critical message."""
        self._log("CRITICAL", action, message, context, **kwargs)

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self._start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation not in self._start_times:
            return 0.0

        duration = time.time() - self._start_times[operation]
        del self._start_times[operation]
        return duration

    def log_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, str]] = None,
        data: Optional[Any] = None,
        context: Optional[LogContext] = None,
    ) -> None:
        """Log HTTP request."""
        request_context = {
            "method": method,
            "url": url,
            "headers": headers or {},
            "has_data": data is not None,
        }
        if context:
            request_context.update(context)

        self.info(f"🚀 {method} {url}", LogAction.REQUEST, request_context)

    def log_response(
        self,
        status_code: int,
        headers: dict[str, str],
        body: Any,
        duration: float,
        method: str,
        url: str,
        context: Optional[LogContext] = None,
    ) -> None:
        """Log HTTP response."""
        response_context = {
            "status_code": status_code,
            "method": method,
            "url": url,
            "duration": duration,
            "headers_count": len(headers),
            "body_size": len(str(body)) if body else 0,
        }
        if context:
            response_context.update(context)

        # Choose emoji based on status code
        if 200 <= status_code < 300:
            emoji = "✅"
        elif 300 <= status_code < 400:
            emoji = "🔄"
        elif 400 <= status_code < 500:
            emoji = "⚠️"
        else:
            emoji = "❌"

        self.info(
            f"{emoji} {status_code} {method} {url} ({duration:.3f}s)",
            LogAction.RESPONSE,
            response_context,
        )

    def log_error(
        self,
        error: Exception,
        action: LogAction = LogAction.ERROR,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """Log error with context."""
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        if context:
            error_context.update(context)

        # Add any additional kwargs
        error_context.update(kwargs)

        self.error(f"❌ {type(error).__name__}: {str(error)}", action, error_context)

    def log_timeout(
        self,
        url: str,
        method: str,
        timeout_value: float,
        context: Optional[LogContext] = None,
    ) -> None:
        """Log timeout error."""
        timeout_context = {
            "url": url,
            "method": method,
            "timeout": timeout_value,
        }
        if context:
            timeout_context.update(context)

        self.warning(
            f"⏰ Timeout after {timeout_value}s: {method} {url}",
            LogAction.TIMEOUT,
            timeout_context,
        )

    def log_retry(
        self,
        attempt: int,
        max_attempts: int,
        error: Exception,
        url: str,
        method: str,
        context: Optional[LogContext] = None,
    ) -> None:
        """Log retry attempt."""
        retry_context = {
            "attempt": attempt,
            "max_attempts": max_attempts,
            "url": url,
            "method": method,
            "error_type": type(error).__name__,
        }
        if context:
            retry_context.update(context)

        self.warning(
            f"🔄 Retry {attempt}/{max_attempts}: {method} {url}",
            LogAction.RETRY,
            retry_context,
        )

    def log_rate_limit(
        self, rate: float, algorithm: str, context: Optional[LogContext] = None
    ) -> None:
        """Log rate limiting."""
        rate_context = {
            "rate": rate,
            "algorithm": algorithm,
        }
        if context:
            rate_context.update(context)

        self.info(
            f"🚦 Rate limiting: {rate} req/s ({algorithm})",
            LogAction.RATE_LIMIT,
            rate_context,
        )

    def log_ssl(
        self, action: str, verify: bool, context: Optional[LogContext] = None
    ) -> None:
        """Log SSL operations."""
        ssl_context = {
            "action": action,
            "verify": verify,
        }
        if context:
            ssl_context.update(context)

        emoji = "🔒" if verify else "⚠️"
        self.info(
            f"{emoji} SSL {action}: verify={verify}", LogAction.SSL_VERIFY, ssl_context
        )


# Create component-specific loggers
def get_logger(component: LogComponent) -> StandardizedLogger:
    """Get a standardized logger for a component."""
    return StandardizedLogger(component)


# Convenience functions for backward compatibility
def log_info(message: str, context: Optional[LogContext] = None, **kwargs: Any) -> None:
    """Log info message with standardized format."""
    logger = get_logger(LogComponent.RUNNER)
    logger.info(message, context=context, **kwargs)


def log_error(
    error: Exception, context: Optional[LogContext] = None, **kwargs: Any
) -> None:
    """Log error with standardized format."""
    logger = get_logger(LogComponent.RUNNER)
    logger.log_error(error, context=context, **kwargs)


def log_request(
    method: str,
    url: str,
    headers: Optional[dict[str, str]] = None,
    data: Optional[Any] = None,
    **kwargs: Any,
) -> None:
    """Log request with standardized format."""
    logger = get_logger(LogComponent.RUNNER)
    # Only pass supported parameters to the logger
    logger.log_request(method, url, headers, data)


def log_response(
    status_code: int, headers: dict[str, str], body: Any, duration: float, **kwargs: Any
) -> None:
    """Log response with standardized format."""
    logger = get_logger(LogComponent.RUNNER)
    logger.log_response(status_code, headers, body, duration, **kwargs)


def log_warning(
    message: str, context: Optional[LogContext] = None, **kwargs: Any
) -> None:
    """Log warning with standardized format."""
    logger = get_logger(LogComponent.RUNNER)
    logger.warning(message, context=context, **kwargs)
