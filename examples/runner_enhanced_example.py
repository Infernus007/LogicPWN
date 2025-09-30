#!/usr/bin/env python3
"""
Enhanced Runner Module Example

This example demonstrates the new features added to the LogicPWN runner module:
- Comprehensive retry mechanism with exponential backoff
- Streaming support for large responses
- Enhanced rate limiting with thread safety
- Session health validation
- Improved error handling and recovery
"""

import asyncio
import time

from logicpwn.core.runner import (
    CommonRequests,
    HttpRunner,
    RateLimitAlgorithm,
    RateLimitConfig,
    RequestBuilder,
    RetryConfig,
    RunnerConfig,
    SSLConfig,
    SSLVerificationLevel,
)


def demonstrate_retry_mechanism():
    """Demonstrate the new retry mechanism with exponential backoff."""
    print("=== Retry Mechanism Demo ===")

    # Configure retry with aggressive settings for demo
    retry_config = RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=True,
        retryable_status_codes={500, 502, 503, 504, 429},
        respect_retry_after=True,
    )

    # Create runner with retry configuration
    config = RunnerConfig(retry=retry_config)
    runner = HttpRunner(config)

    print(
        f"Retry configuration: {retry_config.max_attempts} attempts, "
        f"base delay: {retry_config.base_delay}s, "
        f"exponential base: {retry_config.exponential_base}"
    )

    # This will demonstrate retry behavior (will fail but show retry logic)
    try:
        result = runner.send_request("https://httpbin.org/status/500")
        print(f"Request succeeded: {result.status_code}")
    except Exception as e:
        print(f"Request failed after retries: {e}")


def demonstrate_streaming():
    """Demonstrate streaming support for large responses."""
    print("\n=== Streaming Support Demo ===")

    async def stream_large_response():
        config = RunnerConfig()
        async with HttpRunner(config) as runner:
            print("Streaming large response...")
            total_bytes = 0
            chunk_count = 0

            async for chunk in runner.send_request_streaming(
                "https://httpbin.org/bytes/10000", chunk_size=1024  # 10KB response
            ):
                total_bytes += len(chunk)
                chunk_count += 1
                print(f"Received chunk {chunk_count}: {len(chunk)} bytes")

                # Simulate processing
                await asyncio.sleep(0.01)

            print(f"Streaming complete: {total_bytes} bytes in {chunk_count} chunks")

    asyncio.run(stream_large_response())


def demonstrate_enhanced_rate_limiting():
    """Demonstrate enhanced rate limiting with thread safety."""
    print("\n=== Enhanced Rate Limiting Demo ===")

    # Configure aggressive rate limiting for demo
    rate_config = RateLimitConfig(
        requests_per_second=2.0,  # 2 requests per second
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        burst_size=3,
    )

    config = RunnerConfig(rate_limit=rate_config)
    runner = HttpRunner(config)

    print(
        f"Rate limiting: {rate_config.requests_per_second} req/s, "
        f"algorithm: {rate_config.algorithm}, burst: {rate_config.burst_size}"
    )

    # Make multiple requests to demonstrate rate limiting
    start_time = time.time()
    for i in range(5):
        try:
            result = runner.send_request("https://httpbin.org/get")
            elapsed = time.time() - start_time
            print(f"Request {i+1}: {result.status_code} (elapsed: {elapsed:.2f}s)")
        except Exception as e:
            print(f"Request {i+1} failed: {e}")


def demonstrate_session_health_validation():
    """Demonstrate session health validation."""
    print("\n=== Session Health Validation Demo ===")

    config = RunnerConfig()
    runner = HttpRunner(config)

    # Initial health check (may be False before any request initializes the session)
    is_healthy = runner.validate_session_health()
    print(f"Session health (pre-init): {'Healthy' if is_healthy else 'Unhealthy'}")

    # Make a request to initialize session and test
    try:
        result = runner.send_request("https://example.com")
        print(f"Test request: {result.status_code}")

        # Check health again
        is_healthy = runner.validate_session_health()
        print(
            f"Session health (post-request): {'Healthy' if is_healthy else 'Unhealthy'}"
        )
    except Exception as e:
        print(f"Test request failed: {e}")


def demonstrate_request_builder():
    """Demonstrate the enhanced request builder."""
    print("\n=== Request Builder Demo ===")

    # Using fluent API
    config = (
        RequestBuilder("https://httpbin.org/post")
        .post()
        .json_data({"message": "Hello from LogicPWN", "timestamp": time.time()})
        .header("X-Custom-Header", "LogicPWN-Demo")
        .timeout(30)
        .verify_ssl(True)
        .build()
    )

    print(f"Built request: {config.method} {config.url}")
    print(f"Headers: {config.headers}")
    print(f"JSON data: {config.json_data}")

    # Using common request patterns
    auth_request = CommonRequests.authenticated_get(
        "https://httpbin.org/get", token="demo-token-123", auth_type="Bearer"
    )

    print(f"Authenticated request: {auth_request.method} {auth_request.url}")
    print(f"Auth header: {auth_request.headers.get('Authorization')}")


async def demonstrate_async_features():
    """Demonstrate async features with retry and streaming."""
    print("\n=== Async Features Demo ===")

    # Configure retry for async requests
    retry_config = RetryConfig(max_attempts=2, base_delay=0.5, jitter=True)

    config = RunnerConfig(retry=retry_config)

    async with HttpRunner(config) as runner:
        print("Making async request with retry logic...")

        try:
            result = await runner.send_request_async("https://httpbin.org/get")
            print(f"Async request result: {result.status_code}")
        except Exception as e:
            print(f"Async request failed: {e}")

        # Test session health validation
        is_healthy = await runner.validate_session_health_async()
        print(f"Async session health: {'Healthy' if is_healthy else 'Unhealthy'}")


def demonstrate_ssl_security():
    """Demonstrate SSL security features."""
    print("\n=== SSL Security Demo ===")

    # Create secure SSL configuration
    ssl_config = SSLConfig(
        verification_level=SSLVerificationLevel.STRICT, min_tls_version="TLSv1.3"
    )

    config = RunnerConfig(ssl=ssl_config)
    runner = HttpRunner(config)

    print(f"SSL verification: {ssl_config.verification_level}")
    print(f"Minimum TLS version: {ssl_config.min_tls_version}")

    try:
        result = runner.send_request("https://httpbin.org/get")
        print(f"Secure request successful: {result.status_code}")
    except Exception as e:
        print(f"Secure request failed: {e}")


def main():
    """Run all demonstrations."""
    print("LogicPWN Enhanced Runner Module Demo")
    print("=" * 50)

    # Run synchronous demos
    demonstrate_retry_mechanism()
    demonstrate_enhanced_rate_limiting()
    demonstrate_session_health_validation()
    demonstrate_request_builder()
    demonstrate_ssl_security()

    # Run async demos
    demonstrate_streaming()
    asyncio.run(demonstrate_async_features())

    print("\n" + "=" * 50)
    print("Demo completed! All new features demonstrated.")


if __name__ == "__main__":
    main()
