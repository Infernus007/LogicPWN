"""
Stress Testing Example for LogicPwn

This example demonstrates the comprehensive stress testing capabilities
of LogicPwn, including load testing, performance metrics, and concurrent
exploit chain execution.

Features Demonstrated:
- Basic stress testing with concurrent requests
- Load testing with exploit chains
- Burst testing for rapid request sequences
- Performance monitoring and metrics
- System resource monitoring
- Comprehensive reporting
- Error rate analysis
"""

import asyncio
import time
from typing import List, Dict, Any

from logicpwn.core.stress import (
    StressTester,
    StressTestConfig,
    StressTestMetrics,
    run_quick_stress_test,
    run_exploit_chain_stress_test
)


async def basic_stress_test_example():
    """Demonstrate basic stress testing with concurrent requests."""
    print("=== Basic Stress Testing Example ===")
    
    # Define target configurations
    target_configs = [
        {"url": "https://httpbin.org/get", "method": "GET"},
        {"url": "https://httpbin.org/post", "method": "POST", "json_data": {"test": "data"}},
        {"url": "https://httpbin.org/put", "method": "PUT", "json_data": {"update": "value"}},
        {"url": "https://httpbin.org/delete", "method": "DELETE"},
        {"url": "https://httpbin.org/status/200", "method": "GET"},
        {"url": "https://httpbin.org/status/404", "method": "GET"},
        {"url": "https://httpbin.org/delay/1", "method": "GET"},
        {"url": "https://httpbin.org/delay/2", "method": "GET"}
    ]
    
    # Configure stress test
    config = StressTestConfig(
        max_concurrent=20,
        duration=60,  # 1 minute
        warmup_duration=10,
        memory_monitoring=True,
        cpu_monitoring=True
    )
    
    # Run stress test
    async with StressTester(config) as tester:
        metrics = await tester.run_stress_test(target_configs)
        
        # Print results
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Error Rate: {metrics.error_rate:.2f}%")
        print(f"Requests/Second: {metrics.requests_per_second:.2f}")
        print(f"Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"Peak Memory Usage: {metrics.peak_memory_mb:.2f} MB")
        print(f"Peak CPU Usage: {metrics.peak_cpu_percent:.1f}%")
        
        # Generate detailed report
        report = tester.generate_report("text")
        print("\nDetailed Report:")
        print(report)


async def exploit_chain_stress_test_example():
    """Demonstrate stress testing with exploit chains."""
    print("\n=== Exploit Chain Stress Testing Example ===")
    
    # Define target URLs
    target_urls = [
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com",
        "https://reqres.in"
    ]
    
    # Define exploit chains
    exploit_chains = [
        # Chain 1: Basic reconnaissance
        [
            {"url": "https://target.com/api/status", "method": "GET"},
            {"url": "https://target.com/api/users", "method": "GET"},
            {"url": "https://target.com/api/admin", "method": "GET"}
        ],
        # Chain 2: Authentication bypass attempt
        [
            {"url": "https://target.com/login", "method": "POST", "json_data": {"user": "admin", "pass": "test"}},
            {"url": "https://target.com/admin/panel", "method": "GET"},
            {"url": "https://target.com/api/sensitive", "method": "GET"}
        ],
        # Chain 3: Data extraction
        [
            {"url": "https://target.com/api/data", "method": "GET"},
            {"url": "https://target.com/api/users/1", "method": "GET"},
            {"url": "https://target.com/api/config", "method": "GET"}
        ]
    ]
    
    # Authentication configuration (simulated)
    auth_config = {
        "url": "https://target.com/login",
        "credentials": {"username": "test", "password": "test"},
        "success_indicators": ["dashboard", "welcome"]
    }
    
    # Configure load test
    config = StressTestConfig(
        max_concurrent=5,  # Lower for exploit chains
        duration=120,  # 2 minutes
        warmup_duration=20,
        memory_monitoring=True,
        cpu_monitoring=True
    )
    
    # Run load test
    async with StressTester(config) as tester:
        metrics = await tester.run_load_test(target_urls, exploit_chains, auth_config)
        
        # Print results
        print(f"Exploit Chains Executed: {len(exploit_chains)}")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Error Rate: {metrics.error_rate:.2f}%")
        print(f"Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"P95 Response Time: {metrics.p95_response_time:.3f}s")
        print(f"P99 Response Time: {metrics.p99_response_time:.3f}s")


async def burst_testing_example():
    """Demonstrate burst testing with rapid request sequences."""
    print("\n=== Burst Testing Example ===")
    
    # Define target configuration
    target_config = {
        "url": "https://httpbin.org/get",
        "method": "GET",
        "headers": {"User-Agent": "LogicPwn-StressTest/1.0"}
    }
    
    # Configure burst test
    config = StressTestConfig(
        max_concurrent=50,
        duration=30,
        warmup_duration=5,
        memory_monitoring=True,
        cpu_monitoring=True
    )
    
    # Run burst test
    async with StressTester(config) as tester:
        metrics = await tester.run_burst_test(
            target_config=target_config,
            burst_size=50,
            burst_count=3
        )
        
        # Print results
        print(f"Burst Size: 50 requests")
        print(f"Burst Count: 3")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Error Rate: {metrics.error_rate:.2f}%")
        print(f"Requests/Second: {metrics.requests_per_second:.2f}")
        print(f"Peak Memory Usage: {metrics.peak_memory_mb:.2f} MB")
        print(f"Peak CPU Usage: {metrics.peak_cpu_percent:.1f}%")


async def quick_stress_test_example():
    """Demonstrate quick stress testing with convenience function."""
    print("\n=== Quick Stress Test Example ===")
    
    # Define target URLs
    target_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/post",
        "https://httpbin.org/put",
        "https://httpbin.org/delete",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/users/1",
        "https://reqres.in/api/users/1",
        "https://reqres.in/api/users/2"
    ]
    
    # Run quick stress test
    metrics = await run_quick_stress_test(
        target_urls=target_urls,
        duration=30,  # 30 seconds
        max_concurrent=15
    )
    
    # Print results
    print(f"Quick Test Results:")
    print(f"Total Requests: {metrics.total_requests}")
    print(f"Successful: {metrics.successful_requests}")
    print(f"Failed: {metrics.failed_requests}")
    print(f"Error Rate: {metrics.error_rate:.2f}%")
    print(f"Requests/Second: {metrics.requests_per_second:.2f}")
    print(f"Average Response Time: {metrics.average_response_time:.3f}s")


async def performance_comparison_example():
    """Compare performance between different configurations."""
    print("\n=== Performance Comparison Example ===")
    
    target_configs = [
        {"url": "https://httpbin.org/get", "method": "GET"},
        {"url": "https://httpbin.org/post", "method": "POST", "json_data": {"test": "data"}},
        {"url": "https://httpbin.org/put", "method": "PUT", "json_data": {"update": "value"}},
        {"url": "https://httpbin.org/delete", "method": "DELETE"}
    ]
    
    # Test different concurrency levels
    concurrency_levels = [5, 10, 20, 30]
    results = {}
    
    for concurrency in concurrency_levels:
        print(f"\nTesting with {concurrency} concurrent requests...")
        
        config = StressTestConfig(
            max_concurrent=concurrency,
            duration=30,
            warmup_duration=5
        )
        
        async with StressTester(config) as tester:
            metrics = await tester.run_stress_test(target_configs)
            results[concurrency] = metrics
            
            print(f"  Requests/Second: {metrics.requests_per_second:.2f}")
            print(f"  Error Rate: {metrics.error_rate:.2f}%")
            print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
    
    # Find optimal configuration
    best_config = max(results.keys(), key=lambda x: results[x].requests_per_second)
    print(f"\nOptimal Configuration: {best_config} concurrent requests")
    print(f"Best Performance: {results[best_config].requests_per_second:.2f} req/s")


async def error_analysis_example():
    """Demonstrate error analysis and reporting."""
    print("\n=== Error Analysis Example ===")
    
    # Mix of working and failing URLs
    target_configs = [
        {"url": "https://httpbin.org/get", "method": "GET"},
        {"url": "https://httpbin.org/status/404", "method": "GET"},
        {"url": "https://httpbin.org/status/500", "method": "GET"},
        {"url": "https://httpbin.org/delay/5", "method": "GET"},  # Timeout
        {"url": "https://invalid-domain-that-does-not-exist.com", "method": "GET"},  # DNS failure
        {"url": "https://httpbin.org/post", "method": "POST", "json_data": {"test": "data"}}
    ]
    
    config = StressTestConfig(
        max_concurrent=10,
        duration=45,
        warmup_duration=5,
        error_threshold=0.3  # 30% error rate threshold
    )
    
    async with StressTester(config) as tester:
        metrics = await tester.run_stress_test(target_configs)
        
        # Print error analysis
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Error Rate: {metrics.error_rate:.2f}%")
        
        print("\nStatus Code Distribution:")
        for status_code, count in sorted(metrics.status_code_distribution.items()):
            percentage = (count / metrics.total_requests) * 100
            print(f"  {status_code}: {count} requests ({percentage:.1f}%)")
        
        if metrics.error_distribution:
            print("\nError Distribution:")
            for error_type, count in metrics.error_distribution.items():
                percentage = (count / metrics.total_requests) * 100
                print(f"  {error_type}: {count} errors ({percentage:.1f}%)")
        
        # Check if error rate exceeds threshold
        if metrics.error_rate > config.error_threshold * 100:
            print(f"\n⚠️  Warning: Error rate ({metrics.error_rate:.2f}%) exceeds threshold ({config.error_threshold * 100:.1f}%)")
        else:
            print(f"\n✅ Error rate ({metrics.error_rate:.2f}%) is within acceptable limits")


async def main():
    """Run all stress testing examples."""
    print("LogicPwn Stress Testing Examples")
    print("=" * 50)
    
    try:
        # Run examples
        await basic_stress_test_example()
        await exploit_chain_stress_test_example()
        await burst_testing_example()
        await quick_stress_test_example()
        await performance_comparison_example()
        await error_analysis_example()
        
        print("\n" + "=" * 50)
        print("All stress testing examples completed successfully!")
        
    except Exception as e:
        print(f"Error during stress testing: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 