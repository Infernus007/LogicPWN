"""
Memory profiling utilities for LogicPwn performance monitoring.
"""

import time
from typing import Any

import psutil


class MemoryProfiler:
    def __init__(self):
        self.snapshots: list[dict[str, Any]] = []

    def take_snapshot(self, label: str = "snapshot") -> dict[str, Any]:
        snapshot = {
            "label": label,
            "timestamp": time.time(),
            "memory": psutil.Process().memory_info().rss,
        }
        self.snapshots.append(snapshot)
        return snapshot

    def get_memory_growth(self) -> list[dict[str, Any]]:
        growth = []
        for i in range(1, len(self.snapshots)):
            prev = self.snapshots[i - 1]
            curr = self.snapshots[i]
            growth.append(
                {
                    "from": prev["label"],
                    "to": curr["label"],
                    "delta": curr["memory"] - prev["memory"],
                }
            )
        return growth

    def get_optimization_recommendations(self) -> list[str]:
        # Placeholder for optimization logic
        return ["Consider reducing memory usage in high-growth areas."]
