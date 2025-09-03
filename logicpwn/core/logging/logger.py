"""
Logger class for LogicPwn with sensitive data redaction and error tracking.
"""

import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Optional

from logicpwn.core.config.config_utils import config, get_log_level

from .redactor import SensitiveDataRedactor


@dataclass
class ErrorPattern:
    """Represents a detected error pattern."""

    pattern_type: str
    error_type: str
    frequency: int
    recommendation: str
    first_occurrence: float
    last_occurrence: float


class ErrorTracker:
    """Track error frequency and patterns for better monitoring."""

    def __init__(self, window_size: int = 3600, pattern_threshold: int = 5):
        self.window_size = window_size
        self.pattern_threshold = pattern_threshold
        self.error_counts = defaultdict(deque)
        self.error_patterns = {}
        self.pattern_notifications = set()  # Prevent spam notifications

    def track_error(
        self, error_type: str, error_message: str, context: Optional[dict] = None
    ) -> Optional[ErrorPattern]:
        """Track error occurrence and detect patterns."""
        current_time = time.time()

        # Add error to tracking
        self.error_counts[error_type].append(
            {
                "timestamp": current_time,
                "message": error_message,
                "context": context or {},
            }
        )

        # Clean old entries
        self._cleanup_old_entries(error_type, current_time)

        # Check for patterns
        return self._detect_patterns(error_type, current_time)

    def _cleanup_old_entries(self, error_type: str, current_time: float):
        """Remove entries older than the window size."""
        cutoff_time = current_time - self.window_size
        while (
            self.error_counts[error_type]
            and self.error_counts[error_type][0]["timestamp"] < cutoff_time
        ):
            self.error_counts[error_type].popleft()

    def _detect_patterns(
        self, error_type: str, current_time: float
    ) -> Optional[ErrorPattern]:
        """Detect error patterns and return recommendations."""
        error_entries = list(self.error_counts[error_type])

        if len(error_entries) < self.pattern_threshold:
            return None

        # Calculate time intervals between errors
        timestamps = [entry["timestamp"] for entry in error_entries]
        intervals = [
            timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))
        ]

        if not intervals:
            return None

        avg_interval = sum(intervals) / len(intervals)
        pattern_key = f"{error_type}_{current_time // 60}"  # Group by minute

        # High frequency pattern (errors < 1 minute apart on average)
        if avg_interval < 60 and pattern_key not in self.pattern_notifications:
            self.pattern_notifications.add(pattern_key)
            return ErrorPattern(
                pattern_type="high_frequency",
                error_type=error_type,
                frequency=len(error_entries),
                recommendation="Consider implementing circuit breaker, rate limiting, or retry backoff",
                first_occurrence=timestamps[0],
                last_occurrence=timestamps[-1],
            )

        # Burst pattern (many errors in short time)
        recent_errors = [
            t for t in timestamps if current_time - t < 300
        ]  # Last 5 minutes
        if (
            len(recent_errors) > self.pattern_threshold
            and pattern_key not in self.pattern_notifications
        ):
            self.pattern_notifications.add(pattern_key)
            return ErrorPattern(
                pattern_type="burst",
                error_type=error_type,
                frequency=len(recent_errors),
                recommendation="Investigate recent changes or system load issues",
                first_occurrence=recent_errors[0],
                last_occurrence=recent_errors[-1],
            )

        return None

    def get_error_statistics(self) -> dict[str, Any]:
        """Get comprehensive error statistics."""
        current_time = time.time()
        stats = {}

        for error_type, entries in self.error_counts.items():
            entry_list = list(entries)
            if not entry_list:
                continue

            stats[error_type] = {
                "total_count": len(entry_list),
                "first_occurrence": entry_list[0]["timestamp"],
                "last_occurrence": entry_list[-1]["timestamp"],
                "avg_frequency": len(entry_list)
                / (self.window_size / 3600),  # Per hour
                "recent_count": len(
                    [e for e in entry_list if current_time - e["timestamp"] < 300]
                ),
            }

        return stats

    def clear_pattern_notifications(self):
        """Clear pattern notifications to allow re-detection."""
        self.pattern_notifications.clear()


class LogicPwnLogger:
    """Centralized logger for LogicPwn with sensitive data redaction and error tracking."""

    def __init__(self, name: str = "logicpwn"):
        self.logger = logging.getLogger(name)
        self.redactor = SensitiveDataRedactor()
        self.error_tracker = ErrorTracker()
        self.logging_enabled = True
        self._setup_logger()

    def _setup_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                config.logging_defaults.LOG_FORMAT,
                datefmt=config.logging_defaults.LOG_DATE_FORMAT,
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, get_log_level().upper()))

    def log_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[Any] = None,
        timeout: Optional[int] = None,
    ):
        if not self.logging_enabled:
            return
        if not config.logging_defaults.ENABLE_REQUEST_LOGGING:
            return
        redacted_url = self.redactor.redact_url_params(url)
        redacted_headers = self.redactor.redact_headers(headers or {})
        log_data = {
            "method": method,
            "url": redacted_url,
            "headers": redacted_headers,
            "timeout": timeout,
        }
        if params:
            log_data["params"] = self.redactor.redact_form_data(params)
        if body:
            if isinstance(body, dict):
                log_data["body"] = self.redactor.redact_form_data(body)
            elif isinstance(body, str):
                log_data["body"] = self.redactor._redact_string_body(body)
            else:
                log_data["body"] = str(body)[: self.redactor.max_body_size]
        self.logger.info(f"Request: {json.dumps(log_data, indent=2)}")

    def log_response(
        self,
        status_code: int,
        headers: Optional[dict] = None,
        body: Optional[Any] = None,
        response_time: Optional[float] = None,
    ):
        if not self.logging_enabled:
            return
        if not config.logging_defaults.ENABLE_RESPONSE_LOGGING:
            return
        redacted_headers = self.redactor.redact_headers(headers or {})
        log_data = {
            "status_code": status_code,
            "headers": redacted_headers,
            "response_time": response_time,
        }
        if body:
            if isinstance(body, (dict, list)):
                log_data["body"] = self.redactor.redact_json_body(body)
            elif isinstance(body, str):
                log_data["body"] = self.redactor._redact_string_body(body)
            else:
                log_data["body"] = str(body)[: self.redactor.max_body_size]
        self.logger.info(f"Response: {json.dumps(log_data, indent=2)}")

    def log_error(self, error: Exception, context: Optional[dict] = None):
        if not self.logging_enabled:
            return
        if not config.logging_defaults.ENABLE_ERROR_LOGGING:
            return
        log_data = {"error_type": type(error).__name__, "error_message": str(error)}
        if context:
            redacted_context = {}
            for key, value in context.items():
                if isinstance(value, dict):
                    redacted_context[key] = self.redactor.redact_form_data(value)
                elif (
                    isinstance(value, str)
                    and key.lower() in self.redactor.sensitive_params
                ):
                    redacted_context[key] = self.redactor.redaction_string
                else:
                    redacted_context[key] = value
            log_data["context"] = redacted_context
        self.logger.error(f"Error: {json.dumps(log_data, indent=2)}")

        # Track error for pattern detection
        error_type = type(error).__name__
        error_message = str(error)
        pattern = self.error_tracker.track_error(error_type, error_message, context)

        if pattern:
            self.logger.warning(
                f"Error pattern detected: {pattern.pattern_type}",
                extra={
                    "error_type": pattern.error_type,
                    "frequency": pattern.frequency,
                    "recommendation": pattern.recommendation,
                    "timespan": f"{pattern.last_occurrence - pattern.first_occurrence:.2f}s",
                },
            )

    def log_info(self, message: str, data: Optional[dict] = None):
        if not self.logging_enabled:
            return
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.info(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.info(message)

    def log_debug(self, message: str, data: Optional[dict] = None):
        if not self.logging_enabled:
            return
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.debug(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.debug(message)

    def log_warning(self, message: str, data: Optional[dict] = None):
        if not self.logging_enabled:
            return
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.warning(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.warning(message)

    def get_error_statistics(self) -> dict[str, Any]:
        """Get error statistics from tracker."""
        return self.error_tracker.get_error_statistics()

    def clear_error_pattern_notifications(self):
        """Clear error pattern notifications to allow re-detection."""
        self.error_tracker.clear_pattern_notifications()
