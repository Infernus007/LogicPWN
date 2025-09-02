"""
Performance metrics dataclass and helpers for LogicPwn performance monitoring.
"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""

    operation_name: str
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def memory_delta(self) -> float:
        """Memory usage change."""
        return self.memory_after - self.memory_before

    @property
    def memory_usage_mb(self) -> float:
        """Memory usage in MB."""
        return self.memory_after / 1024 / 1024
