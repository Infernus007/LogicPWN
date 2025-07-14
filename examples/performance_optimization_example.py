#!/usr/bin/env python3
"""
Performance Optimization Example for LogicPwn.

This example demonstrates the integrated performance monitoring and caching
features of LogicPwn, showing how they improve real-world security testing
workflows.

Features Demonstrated:
- Automatic performance monitoring of requests and authentication
- Response caching for improved performance
- Session caching for authentication
- Configuration caching for faster access
- Performance metrics and statistics
- Cache statistics and management
"""

import asyncio
import time
from typing import Dict, Any

from logicpwn.core import (
    authenticate_session,
    send_request,
    send_request_advanced,
    validate_response,
    get_cache_stats,
    clear_all_caches,
    get_performance_summary
)
from logicpwn.core.performance import (
    PerformanceMonitor,
    PerformanceBenchmark,
    monitor_performance,
    performance_context
)
from logicpwn.core.cache import (
    response_cache,
    session_cache,
    config_cache,
    cached
)
from logicpwn.core.config.config_utils import get_timeout, get_max_retries


def demonstrate_integrated_performance_monitoring():
    """Demonstrate integrated performance monitoring across all modules."""
    print("🔍 Integrated Performance Monitoring Demo")
    print("=" * 50)
    
    # Example authentication config
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["authenticated", "success"],
        "headers": {"User-Agent": "LogicPwn/1.0"}
    }
    
    # Example request configs
    request_configs = [
        {
            "url": "https://httpbin.org/get",
            "method": "GET",
            "headers": {"User-Agent": "LogicPwn/1.0"}
        },
        {
            "url": "https://httpbin.org/json",
            "method": "GET",
            "headers": {"Accept": "application/json"}
        },
        {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "json_data": {"test": "data"},
            "headers": {"Content-Type": "application/json"}
        }
    ]
    
    print("\n1. Authentication with Performance Monitoring")
    print("-" * 40)
    
    # Monitor authentication performance
    with PerformanceMonitor() as monitor:
        try:
            session = authenticate_session(auth_config)
            print("✅ Authentication successful")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
        
        auth_metrics = monitor.get_metrics()
        if auth_metrics:
            metric = auth_metrics[0]
            print(f"   Duration: {metric.duration:.3f}s")
            print(f"   Memory Usage: {metric.memory_usage_mb:.2f} MB")
            print(f"   CPU Usage: {metric.cpu_percent:.1f}%")
    
    print("\n2. Request Execution with Caching")
    print("-" * 40)
    
    # First request (cache miss)
    with PerformanceMonitor() as monitor:
        try:
            response = send_request(session, request_configs[0])
            print(f"✅ First request: {response.status_code}")
        except Exception as e:
            print(f"❌ First request failed: {e}")
        
        first_metrics = monitor.get_metrics()
        if first_metrics:
            metric = first_metrics[0]
            print(f"   Duration: {metric.duration:.3f}s")
    
    # Second request (cache hit)
    with PerformanceMonitor() as monitor:
        try:
            response = send_request(session, request_configs[0])
            print(f"✅ Second request: {response.status_code}")
        except Exception as e:
            print(f"❌ Second request failed: {e}")
        
        second_metrics = monitor.get_metrics()
        if second_metrics:
            metric = second_metrics[0]
            print(f"   Duration: {metric.duration:.3f}s")
    
    print("\n3. Advanced Request with Validation")
    print("-" * 40)
    
    # Advanced request with validation
    with PerformanceMonitor() as monitor:
        try:
            result = send_request_advanced(
                url="https://httpbin.org/json",
                method="GET",
                headers={"Accept": "application/json"}
            )
            print(f"✅ Advanced request: {result.status_code}")
            
            # Validate response
            validation_result = validate_response(
                result.response,
                success_criteria=["slideshow"],
                regex_patterns=[r'"title":\s*"([^"]*)"'],
                return_structured=True
            )
            print(f"✅ Validation: {validation_result.is_valid}")
            
        except Exception as e:
            print(f"❌ Advanced request failed: {e}")
        
        advanced_metrics = monitor.get_metrics()
        if advanced_metrics:
            metric = advanced_metrics[0]
            print(f"   Duration: {metric.duration:.3f}s")
    
    print("\n4. Performance Summary")
    print("-" * 40)
    
    # Get overall performance summary
    summary = get_performance_summary()
    if summary:
        print(f"Total Operations: {summary.get('total_operations', 0)}")
        print(f"Total Duration: {summary.get('total_duration', 0):.3f}s")
        print(f"Average Duration: {summary.get('average_duration', 0):.3f}s")
        print(f"Peak Memory: {summary.get('peak_memory_usage', 0):.2f} MB")


def demonstrate_caching_features():
    """Demonstrate caching features and statistics."""
    print("\n🔧 Caching Features Demo")
    print("=" * 50)
    
    # Clear caches to start fresh
    clear_all_caches()
    print("✅ Caches cleared")
    
    # Demonstrate response caching
    print("\n1. Response Caching")
    print("-" * 20)
    
    # First request (cache miss)
    try:
        response = send_request_advanced(
            url="https://httpbin.org/get",
            method="GET"
        )
        print("✅ First request completed (cache miss)")
    except Exception as e:
        print(f"❌ First request failed: {e}")
    
    # Second request (cache hit)
    try:
        response = send_request_advanced(
            url="https://httpbin.org/get",
            method="GET"
        )
        print("✅ Second request completed (cache hit)")
    except Exception as e:
        print(f"❌ Second request failed: {e}")
    
    # Demonstrate session caching
    print("\n2. Session Caching")
    print("-" * 20)
    
    auth_config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["authenticated"]
    }
    
    # First authentication (cache miss)
    try:
        session1 = authenticate_session(auth_config)
        print("✅ First authentication completed (cache miss)")
    except Exception as e:
        print(f"❌ First authentication failed: {e}")
    
    # Second authentication (cache hit)
    try:
        session2 = authenticate_session(auth_config)
        print("✅ Second authentication completed (cache hit)")
    except Exception as e:
        print(f"❌ Second authentication failed: {e}")
    
    # Demonstrate configuration caching
    print("\n3. Configuration Caching")
    print("-" * 20)
    
    # First access (cache miss)
    timeout1 = get_timeout()
    retries1 = get_max_retries()
    print(f"✅ First config access: timeout={timeout1}, retries={retries1}")
    
    # Second access (cache hit)
    timeout2 = get_timeout()
    retries2 = get_max_retries()
    print(f"✅ Second config access: timeout={timeout2}, retries={retries2}")
    
    # Show cache statistics
    print("\n4. Cache Statistics")
    print("-" * 20)
    
    stats = get_cache_stats()
    
    print("Response Cache:")
    response_stats = stats.get('response_cache', {})
    print(f"  Hits: {response_stats.get('hits', 0)}")
    print(f"  Misses: {response_stats.get('misses', 0)}")
    print(f"  Hit Rate: {response_stats.get('hit_rate', 0):.1f}%")
    print(f"  Size: {response_stats.get('size', 0)}")
    
    print("\nSession Cache:")
    session_stats = stats.get('session_cache', {})
    print(f"  Hits: {session_stats.get('hits', 0)}")
    print(f"  Misses: {session_stats.get('misses', 0)}")
    print(f"  Hit Rate: {session_stats.get('hit_rate', 0):.1f}%")
    print(f"  Size: {session_stats.get('size', 0)}")
    
    print("\nConfig Cache:")
    config_stats = stats.get('config_cache', {})
    print(f"  Hits: {config_stats.get('hits', 0)}")
    print(f"  Misses: {config_stats.get('misses', 0)}")
    print(f"  Hit Rate: {config_stats.get('hit_rate', 0):.1f}%")
    print(f"  Size: {config_stats.get('size', 0)}")


@cached(ttl=300)
def expensive_validation_function(data: Dict[str, Any]) -> bool:
    """Example of function-level caching."""
    # Simulate expensive validation
    time.sleep(0.1)
    return len(data) > 0


def demonstrate_function_caching():
    """Demonstrate function-level caching."""
    print("\n⚡ Function-Level Caching Demo")
    print("=" * 50)
    
    test_data = {"key": "value", "test": "data"}
    
    # First call (cache miss)
    start_time = time.time()
    result1 = expensive_validation_function(test_data)
    duration1 = time.time() - start_time
    print(f"✅ First call: {result1} (took {duration1:.3f}s)")
    
    # Second call (cache hit)
    start_time = time.time()
    result2 = expensive_validation_function(test_data)
    duration2 = time.time() - start_time
    print(f"✅ Second call: {result2} (took {duration2:.3f}s)")
    
    print(f"Performance improvement: {duration1/duration2:.1f}x faster")


def demonstrate_benchmarking():
    """Demonstrate performance benchmarking."""
    print("\n📊 Performance Benchmarking Demo")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark(iterations=3)
    
    # Benchmark different request types
    print("\n1. Benchmarking Request Types")
    print("-" * 30)
    
    try:
        results = benchmark.benchmark_request(
            url="https://httpbin.org/get",
            method="GET"
        )
        print(f"GET Request: {results.get('average_duration', 0):.3f}s avg")
    except Exception as e:
        print(f"❌ GET benchmark failed: {e}")
    
    try:
        results = benchmark.benchmark_request(
            url="https://httpbin.org/post",
            method="POST",
            headers={"Content-Type": "application/json"},
            data={"test": "data"}
        )
        print(f"POST Request: {results.get('average_duration', 0):.3f}s avg")
    except Exception as e:
        print(f"❌ POST benchmark failed: {e}")
    
    print("\n2. Memory Profiling")
    print("-" * 20)
    
    from logicpwn.core.performance import MemoryProfiler
    
    profiler = MemoryProfiler()
    
    # Take snapshots during operations
    profiler.take_snapshot("before_operations")
    
    try:
        # Perform some operations
        session = authenticate_session({
            "url": "https://httpbin.org/post",
            "method": "POST",
            "credentials": {"username": "test", "password": "test"},
            "success_indicators": ["authenticated"]
        })
        
        response = send_request(session, {
            "url": "https://httpbin.org/get",
            "method": "GET"
        })
        
        profiler.take_snapshot("after_operations")
        
        growth = profiler.get_memory_growth()
        if growth:
            print(f"Memory growth: {growth[-1].get('memory_mb', 0):.2f} MB")
        
        recommendations = profiler.get_optimization_recommendations()
        if recommendations:
            print("Optimization recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"  - {rec}")
    
    except Exception as e:
        print(f"❌ Memory profiling failed: {e}")


def main():
    """Run all performance optimization demonstrations."""
    print("🚀 LogicPwn Performance Optimization Demo")
    print("=" * 60)
    
    try:
        # Demonstrate integrated performance monitoring
        demonstrate_integrated_performance_monitoring()
        
        # Demonstrate caching features
        demonstrate_caching_features()
        
        # Demonstrate function-level caching
        demonstrate_function_caching()
        
        # Demonstrate benchmarking
        demonstrate_benchmarking()
        
        print("\n✅ All demonstrations completed successfully!")
        print("\nKey Benefits:")
        print("• Automatic performance monitoring of all operations")
        print("• Intelligent caching for improved response times")
        print("• Session persistence for multi-step workflows")
        print("• Configuration caching for faster access")
        print("• Comprehensive performance metrics and statistics")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 