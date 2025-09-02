"""
Performance utility functions for LogicPwn performance monitoring.
"""

from typing import Any

from logicpwn.core.performance.performance_monitor import PerformanceMonitor


def get_performance_summary() -> dict[str, Any]:
    """Get a summary of all performance metrics collected so far."""
    monitor = PerformanceMonitor()
    return monitor.get_summary()
