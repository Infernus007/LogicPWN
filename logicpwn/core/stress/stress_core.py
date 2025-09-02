"""
Core stress testing logic for LogicPwn.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class StressTestConfig:
    max_concurrent: int = 50
    duration: int = 300
    rate_limit: Optional[float] = None
    timeout: int = 30
    verify_ssl: bool = True
    memory_monitoring: bool = True
    cpu_monitoring: bool = True
    error_threshold: float = 0.1
    warmup_duration: int = 30


@dataclass
class StressTestMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    requests_per_second: float = 0.0
    average_response_time: float = 0.0
    median_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    peak_memory_mb: float = 0.0
    peak_cpu_percent: float = 0.0
    status_code_distribution: dict[int, int] = field(default_factory=dict)
    error_distribution: dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_duration": self.total_duration,
            "requests_per_second": self.requests_per_second,
            "average_response_time": self.average_response_time,
            "median_response_time": self.median_response_time,
            "p95_response_time": self.p95_response_time,
            "p99_response_time": self.p99_response_time,
            "error_rate": self.error_rate,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "peak_memory_mb": self.peak_memory_mb,
            "peak_cpu_percent": self.peak_cpu_percent,
            "status_code_distribution": self.status_code_distribution,
            "error_distribution": self.error_distribution,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        return (
            f"StressTestMetrics("
            f"requests={self.total_requests}, "
            f"rps={self.requests_per_second:.2f}, "
            f"error_rate={self.error_rate:.2f}%, "
            f"avg_time={self.average_response_time:.3f}s)"
        )


class StressTester:
    def __init__(self, config: Optional[StressTestConfig] = None):
        self.config = config or StressTestConfig()
        self.metrics = StressTestMetrics()
        self.response_times: list[float] = []
        self.memory_samples: list[float] = []
        self.cpu_samples: list[float] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self._monitoring_task: Optional[asyncio.Task] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

    # ... (move all main orchestration and request methods here, except scenario helpers)
