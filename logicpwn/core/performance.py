"""
Performance monitoring and optimization for LogicPwn Business Logic Exploitation Framework.

This module provides comprehensive performance monitoring, profiling, and optimization
capabilities for high-performance security testing and exploit chaining workflows.

Key Features:
- Request performance monitoring
- Memory usage tracking
- Response time analysis
- Performance bottlenecks detection
- Optimization recommendations
- Real-time performance metrics
- Performance benchmarking

Usage::

    # Monitor request performance
    with PerformanceMonitor() as monitor:
                                            result = send_request(url, method)
                                            metrics = monitor.get_metrics()
    
    # Benchmark performance
    benchmark = PerformanceBenchmark()
    results = benchmark.run_benchmark(request_configs)
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections import defaultdict
import statistics
from loguru import logger


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
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def memory_delta(self) -> float:
                                            """Memory usage change."""
                                            return self.memory_after - self.memory_before

    @property
    def memory_usage_mb(self) -> float:
                                            """Memory usage in MB."""
                                            return self.memory_after / 1024 / 1024


class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self):
                                            """Initialize performance monitor."""
                                            self.metrics: List[PerformanceMetrics] = []
                                            self.current_operation: Optional[str] = None
                                            self.start_time: Optional[float] = None
                                            self.start_memory: Optional[float] = None
                                            self.peak_memory: float = 0
                                            self._lock = threading.Lock()
    
    def __enter__(self):
                                            """Context manager entry."""
                                            self.start_monitoring()
                                            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
                                            """Context manager exit."""
                                            self.stop_monitoring()
    
    def start_monitoring(self, operation_name: str = "default"):
                                            """Start monitoring an operation."""
                                            with self._lock:
                                                self.current_operation = operation_name
                                                self.start_time = time.time()
                                                self.start_memory = psutil.Process().memory_info().rss
                                                self.peak_memory = self.start_memory
    
    def stop_monitoring(self) -> Optional[PerformanceMetrics]:
                                            """Stop monitoring and return metrics."""
                                            if not self.start_time:
                                                return None
                                            
                                            with self._lock:
                                                end_time = time.time()
                                                end_memory = psutil.Process().memory_info().rss
                                                duration = end_time - self.start_time
                                                
                                                # Get CPU usage
                                                cpu_percent = psutil.cpu_percent(interval=0.1)
                                                
                                                metrics = PerformanceMetrics(
                                                    operation_name=self.current_operation,
                                                    duration=duration,
                                                    memory_before=self.start_memory,
                                                    memory_after=end_memory,
                                                    memory_peak=self.peak_memory,
                                                    cpu_percent=cpu_percent
                                                )
                                                
                                                self.metrics.append(metrics)
                                                
                                                # Reset monitoring
                                                self.current_operation = None
                                                self.start_time = None
                                                self.start_memory = None
                                                self.peak_memory = 0
                                                
                                                return metrics
    
    def monitor_operation(self, operation_name: str):
                                            """Decorator for monitoring operations."""
                                            def decorator(func: Callable) -> Callable:
                                                def wrapper(*args, **kwargs):
                                                    self.start_monitoring(operation_name)
                                                    try:
                                                        result = func(*args, **kwargs)
                                                        return result
                                                    finally:
                                                        self.stop_monitoring()
                                                return wrapper
                                            return decorator
    
    def get_metrics(self) -> List[PerformanceMetrics]:
                                            """Get all collected metrics."""
                                            with self._lock:
                                                return self.metrics.copy()
    
    def get_summary(self) -> Dict[str, Any]:
                                            """Get performance summary."""
                                            if not self.metrics:
                                                return {}
                                            
                                            durations = [m.duration for m in self.metrics]
                                            memory_deltas = [m.memory_delta for m in self.metrics]
                                            cpu_percents = [m.cpu_percent for m in self.metrics]
                                            
                                            return {
                                                'total_operations': len(self.metrics),
                                                'total_duration': sum(durations),
                                                'average_duration': statistics.mean(durations),
                                                'min_duration': min(durations),
                                                'max_duration': max(durations),
                                                'total_memory_delta': sum(memory_deltas),
                                                'average_memory_delta': statistics.mean(memory_deltas),
                                                'peak_memory_usage': max(m.memory_peak for m in self.metrics),
                                                'average_cpu_percent': statistics.mean(cpu_percents),
                                                'operations': [m.operation_name for m in self.metrics]
                                            }


class PerformanceBenchmark:
    """Performance benchmarking for LogicPwn operations."""
    
    def __init__(self, iterations: int = 10):
                                            """
                                            Initialize performance benchmark.
                                            
                                            Args:
                                                iterations: Number of iterations per test
                                            """
                                            self.iterations = iterations
                                            self.results: Dict[str, List[float]] = defaultdict(list)
    
    def benchmark_request(self, url: str, method: str = "GET", 
                                                            headers: Optional[Dict] = None) -> Dict[str, Any]:
                                            """
                                            Benchmark a single request.
                                            
                                            Args:
                                                url: Request URL
                                                method: HTTP method
                                                headers: Request headers
                                                
                                            Returns:
                                                Benchmark results
                                            """
                                            from .runner import send_request_advanced
                                            
                                            durations = []
                                            memory_usage = []
                                            
                                            for i in range(self.iterations):
                                                with PerformanceMonitor() as monitor:
                                                    try:
                                                        result = send_request_advanced(url=url, method=method, headers=headers)
                                                        metrics = monitor.get_metrics()
                                                        if metrics:
                                                            durations.append(metrics[0].duration)
                                                            memory_usage.append(metrics[0].memory_usage_mb)
                                                    except Exception as e:
                                                        logger.warning(f"Request failed in iteration {i}: {e}")
                                            
                                            if durations:
                                                return {
                                                    'url': url,
                                                    'method': method,
                                                    'iterations': len(durations),
                                                    'average_duration': statistics.mean(durations),
                                                    'min_duration': min(durations),
                                                    'max_duration': max(durations),
                                                    'std_duration': statistics.stdev(durations) if len(durations) > 1 else 0,
                                                    'average_memory_mb': statistics.mean(memory_usage),
                                                    'max_memory_mb': max(memory_usage),
                                                    'success_rate': len(durations) / self.iterations * 100
                                                }
                                            else:
                                                return {
                                                    'url': url,
                                                    'method': method,
                                                    'error': 'All iterations failed'
                                                }
    
    def benchmark_batch_requests(self, request_configs: List[Dict[str, Any]], 
                                                                   max_concurrent: int = 10) -> Dict[str, Any]:
                                            """
                                            Benchmark batch request processing.
                                            
                                            Args:
                                                request_configs: List of request configurations
                                                max_concurrent: Maximum concurrent requests
                                                
                                            Returns:
                                                Benchmark results
                                            """
                                            from .async_runner import send_requests_batch_async
                                            import asyncio
                                            
                                            durations = []
                                            memory_usage = []
                                            
                                            for i in range(self.iterations):
                                                with PerformanceMonitor() as monitor:
                                                    try:
                                                        loop = asyncio.new_event_loop()
                                                        asyncio.set_event_loop(loop)
                                                        results = loop.run_until_complete(
                                                            send_requests_batch_async(request_configs, max_concurrent)
                                                        )
                                                        loop.close()
                                                        
                                                        metrics = monitor.get_metrics()
                                                        if metrics:
                                                            durations.append(metrics[0].duration)
                                                            memory_usage.append(metrics[0].memory_usage_mb)
                                                    except Exception as e:
                                                        logger.warning(f"Batch request failed in iteration {i}: {e}")
                                            
                                            if durations:
                                                return {
                                                    'request_count': len(request_configs),
                                                    'max_concurrent': max_concurrent,
                                                    'iterations': len(durations),
                                                    'average_duration': statistics.mean(durations),
                                                    'min_duration': min(durations),
                                                    'max_duration': max(durations),
                                                    'std_duration': statistics.stdev(durations) if len(durations) > 1 else 0,
                                                    'average_memory_mb': statistics.mean(memory_usage),
                                                    'max_memory_mb': max(memory_usage),
                                                    'success_rate': len(durations) / self.iterations * 100,
                                                    'requests_per_second': len(request_configs) / statistics.mean(durations)
                                                }
                                            else:
                                                return {
                                                    'request_count': len(request_configs),
                                                    'max_concurrent': max_concurrent,
                                                    'error': 'All iterations failed'
                                                }
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
                                            """
                                            Run comprehensive performance benchmark.
                                            
                                            Returns:
                                                Comprehensive benchmark results
                                            """
                                            results = {}
                                            
                                                # Single request benchmarks
                                            single_requests = [
                                                {"url": "https://httpbin.org/get", "method": "GET"},
                                                {"url": "https://httpbin.org/post", "method": "POST"},
                                                {"url": "https://httpbin.org/put", "method": "PUT"},
                                                {"url": "https://httpbin.org/delete", "method": "DELETE"}
                                            ]
                                            
                                            for req in single_requests:
                                                key = f"{req['method']}_{req['url'].split('/')[-1]}"
                                                results[key] = self.benchmark_request(req['url'], req['method'])
                                            
                                                # Batch request benchmarks
                                            batch_configs = [
                                                {"url": f"https://httpbin.org/get?i={i}", "method": "GET"}
                                                for i in range(10)
                                            ]
                                            
                                            results['batch_10_requests'] = self.benchmark_batch_requests(batch_configs, 5)
                                            
                                                # Large batch benchmark
                                            large_batch_configs = [
                                                {"url": f"https://httpbin.org/get?i={i}", "method": "GET"}
                                                for i in range(50)
                                            ]
                                            
                                            results['batch_50_requests'] = self.benchmark_batch_requests(large_batch_configs, 10)
                                            
                                            return results


class MemoryProfiler:
    """Memory usage profiling and optimization."""
    
    def __init__(self):
                                            """Initialize memory profiler."""
                                            self.process = psutil.Process()
                                            self.snapshots: List[Dict[str, Any]] = []
    
    def take_snapshot(self, label: str = "snapshot") -> Dict[str, Any]:
                                            """
                                            Take memory usage snapshot.
                                            
                                            Args:
                                                label: Snapshot label
                                                
                                            Returns:
                                                Memory snapshot data
                                            """
                                            memory_info = self.process.memory_info()
                                            snapshot = {
                                                'label': label,
                                                'timestamp': time.time(),
                                                'rss_mb': memory_info.rss / 1024 / 1024,
                                                'vms_mb': memory_info.vms / 1024 / 1024,
                                                'percent': self.process.memory_percent(),
                                                'cpu_percent': self.process.cpu_percent()
                                            }
                                            self.snapshots.append(snapshot)
                                            return snapshot
    
    def get_memory_growth(self) -> List[Dict[str, Any]]:
                                            """Get memory growth analysis."""
                                            if len(self.snapshots) < 2:
                                                return []
                                            
                                            growth = []
                                            for i in range(1, len(self.snapshots)):
                                                prev = self.snapshots[i-1]
                                                curr = self.snapshots[i]
                                                
                                                growth.append({
                                                    'from_label': prev['label'],
                                                    'to_label': curr['label'],
                                                    'rss_growth_mb': curr['rss_mb'] - prev['rss_mb'],
                                                    'vms_growth_mb': curr['vms_mb'] - prev['vms_mb'],
                                                    'time_delta': curr['timestamp'] - prev['timestamp']
                                                })
                                            
                                            return growth
    
    def get_optimization_recommendations(self) -> List[str]:
                                            """Get memory optimization recommendations."""
                                            recommendations = []
                                            
                                            if not self.snapshots:
                                                return recommendations
                                            
                                            current_memory = self.snapshots[-1]['rss_mb']
                                            
                                            if current_memory > 500:  # 500MB
                                                recommendations.append("High memory usage detected. Consider implementing response streaming.")
                                            
                                            if len(self.snapshots) > 1:
                                                growth = self.get_memory_growth()
                                                total_growth = sum(g['rss_growth_mb'] for g in growth)
                                                
                                                if total_growth > 100:  # 100MB growth
                                                    recommendations.append("Significant memory growth detected. Check for memory leaks.")
                                            
                                            return recommendations


# Global performance monitoring instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str):
    """Decorator for monitoring function performance."""
    return performance_monitor.monitor_operation(operation_name)


@contextmanager
def performance_context(operation_name: str):
    """Context manager for performance monitoring."""
    performance_monitor.start_monitoring(operation_name)
    try:
                                            yield performance_monitor
    finally:
                                            performance_monitor.stop_monitoring()


def get_performance_summary() -> Dict[str, Any]:
    """Get current performance summary."""
    return performance_monitor.get_summary()


def run_performance_benchmark() -> Dict[str, Any]:
    """Run comprehensive performance benchmark."""
    benchmark = PerformanceBenchmark()
    return benchmark.run_comprehensive_benchmark() 