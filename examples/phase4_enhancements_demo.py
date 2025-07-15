#!/usr/bin/env python3
"""
Phase 4 Enhancements Demo - Logging, Middleware, and Config Improvements

This script demonstrates the enhancements implemented in Phase 4 of the LogicPwn audit:
- Enhanced error tracking and pattern detection
- Circuit breaker middleware for resilience
- Configuration validation and security checks

Usage:
    python examples/phase4_enhancements_demo.py

Features Demonstrated:
- Error frequency tracking and pattern detection
- Circuit breaker automatic failure handling
- Comprehensive configuration validation
- Enhanced logging with correlation tracking
- Middleware integration and management
"""

import time
import asyncio
from typing import Dict, Any

# Import core LogicPwn functionality
from logicpwn.core.config import config
from logicpwn.core.middleware import middleware_manager, add_middleware
from logicpwn.core.runner import send_request_advanced
from logicpwn.core.logging import log_info, log_warning, log_error

# Import new enhancements
from logicpwn.core.logging.enhanced_logger import EnhancedLogicPwnLogger, ErrorTracker
from logicpwn.core.middleware.circuit_breaker import CircuitBreakerMiddleware, CircuitBreakerError
from logicpwn.core.config.config_validator import ConfigValidator, validate_config_with_report


def demonstrate_enhanced_error_tracking():
    """Demonstrate enhanced error tracking and pattern detection."""
    print("\n🔍 Enhanced Error Tracking Demo")
    print("=" * 50)
    
    # Create enhanced logger
    enhanced_logger = EnhancedLogicPwnLogger()
    
    # Simulate various error patterns
    print("\n1. Simulating High-Frequency Error Pattern")
    print("-" * 40)
    
    # Simulate rapid errors
    for i in range(6):
        try:
            raise ValueError(f"Simulated error {i+1}")
        except Exception as e:
            enhanced_logger.log_error(e, {"iteration": i+1, "test": "high_frequency"})
        time.sleep(0.5)  # Short interval to trigger pattern detection
    
    print("\n2. Error Statistics")
    print("-" * 20)
    stats = enhanced_logger.get_error_statistics()
    for error_type, data in stats.items():
        print(f"Error Type: {error_type}")
        print(f"  Total Count: {data['total_count']}")
        print(f"  Recent Count: {data['recent_count']}")
        print(f"  Avg Frequency: {data['avg_frequency']:.2f}/hour")
    
    print("\n3. Simulating Burst Error Pattern")
    print("-" * 40)
    
    # Clear notifications for new pattern detection
    enhanced_logger.error_tracker.clear_pattern_notifications()
    
    # Simulate burst of different errors
    for i in range(8):
        try:
            if i % 2 == 0:
                raise ConnectionError(f"Network error {i+1}")
            else:
                raise TimeoutError(f"Timeout error {i+1}")
        except Exception as e:
            enhanced_logger.log_error(e, {"burst_test": True, "iteration": i+1})
        time.sleep(0.1)  # Very short interval for burst pattern


def demonstrate_circuit_breaker_middleware():
    """Demonstrate circuit breaker middleware functionality."""
    print("\n⚡ Circuit Breaker Middleware Demo")
    print("=" * 50)
    
    # Create and add circuit breaker middleware
    circuit_breaker = CircuitBreakerMiddleware(
        failure_threshold=3,  # Low threshold for demo
        recovery_timeout=5,   # Short timeout for demo
        error_threshold=0.6   # 60% error rate to trigger
    )
    
    add_middleware(circuit_breaker)
    print("✅ Circuit breaker middleware added")
    
    print(f"Initial state: {circuit_breaker.get_statistics()}")
    
    print("\n1. Testing Normal Requests")
    print("-" * 30)
    
    # Test successful requests
    for i in range(3):
        try:
            result = send_request_advanced(
                url="https://httpbin.org/status/200",  # Should succeed
                method="GET"
            )
            print(f"✅ Request {i+1}: Status {result.status_code}")
        except Exception as e:
            print(f"❌ Request {i+1} failed: {e}")
    
    print(f"After successful requests: {circuit_breaker.get_statistics()}")
    
    print("\n2. Testing Failure Scenarios")
    print("-" * 30)
    
    # Test requests that will fail (trigger circuit breaker)
    for i in range(5):
        try:
            result = send_request_advanced(
                url="https://httpbin.org/status/500",  # Will fail
                method="GET"
            )
            print(f"Request {i+1}: Status {result.status_code}")
        except CircuitBreakerError as e:
            print(f"🔴 Circuit breaker blocked request {i+1}: {e}")
        except Exception as e:
            print(f"❌ Request {i+1} failed: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print(f"After failure scenario: {circuit_breaker.get_statistics()}")
    
    print("\n3. Testing Recovery")
    print("-" * 20)
    
    print("Waiting for recovery timeout...")
    time.sleep(6)  # Wait for recovery timeout
    
    try:
        result = send_request_advanced(
            url="https://httpbin.org/status/200",  # Should succeed
            method="GET"
        )
        print(f"✅ Recovery request successful: Status {result.status_code}")
    except Exception as e:
        print(f"❌ Recovery request failed: {e}")
    
    print(f"Final state: {circuit_breaker.get_statistics()}")


def demonstrate_configuration_validation():
    """Demonstrate comprehensive configuration validation."""
    print("\n⚙️ Configuration Validation Demo")
    print("=" * 50)
    
    print("\n1. Current Configuration Validation")
    print("-" * 40)
    
    # Validate current configuration
    validation_report = validate_config_with_report(config)
    
    print(f"Configuration Valid: {'✅ YES' if validation_report['valid'] else '❌ NO'}")
    print(f"Summary: {validation_report['summary']}")
    
    if validation_report['issues']:
        print("\nDetected Issues:")
        for issue in validation_report['issues']:
            level_emoji = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}
            print(f"{level_emoji.get(issue['level'], '•')} {issue['level'].upper()}: {issue['message']}")
            if issue['suggestion']:
                print(f"   💡 Suggestion: {issue['suggestion']}")
            print(f"   📍 Field: {issue['field']}")
            print()
    
    print("\n2. Testing Configuration with Issues")
    print("-" * 40)
    
    # Create a configuration with known issues
    from logicpwn.core.config.config_models import Config, RequestDefaults, SecurityDefaults, LoggingDefaults
    
    test_config = Config()
    
    # Introduce some issues for demonstration
    test_config.request_defaults.TIMEOUT = 0  # Invalid timeout
    test_config.request_defaults.MAX_RETRIES = -1  # Invalid retries
    test_config.security_defaults.SENSITIVE_HEADERS = set()  # Empty sensitive headers
    test_config.logging_defaults.LOG_LEVEL = "INVALID"  # Invalid log level
    test_config.auth_defaults.SESSION_TIMEOUT = 30  # Too short
    
    test_validation = validate_config_with_report(test_config)
    
    print(f"Test Configuration Valid: {'✅ YES' if test_validation['valid'] else '❌ NO'}")
    print(f"Issues Found: {sum(test_validation['summary'].values())}")
    
    # Group issues by level
    for level in ["error", "warning", "info"]:
        level_issues = [issue for issue in test_validation['issues'] if issue['level'] == level]
        if level_issues:
            level_emoji = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}
            print(f"\n{level_emoji[level]} {level.upper()} Issues ({len(level_issues)}):")
            for issue in level_issues:
                print(f"  • {issue['message']}")
                if issue['suggestion']:
                    print(f"    💡 {issue['suggestion']}")
    
    print("\n3. Security Recommendations")
    print("-" * 30)
    
    if test_validation['recommendations']:
        for i, rec in enumerate(test_validation['recommendations'], 1):
            print(f"{i}. {rec}")
    else:
        print("No specific recommendations generated.")


def demonstrate_integrated_enhancements():
    """Demonstrate all enhancements working together."""
    print("\n🚀 Integrated Enhancements Demo")
    print("=" * 50)
    
    print("\n1. Setting up Enhanced Environment")
    print("-" * 40)
    
    # Setup enhanced logger
    enhanced_logger = EnhancedLogicPwnLogger()
    
    # Setup circuit breaker with custom settings
    circuit_breaker = CircuitBreakerMiddleware(
        failure_threshold=2,
        recovery_timeout=3,
        error_threshold=0.5
    )
    
    # Clear existing middleware and add our enhanced ones
    middleware_manager.middleware.clear()
    middleware_manager.enabled_middleware.clear()
    add_middleware(circuit_breaker)
    
    print("✅ Enhanced logging and circuit breaker configured")
    
    print("\n2. Running Mixed Request Scenario")
    print("-" * 40)
    
    urls_and_expected = [
        ("https://httpbin.org/status/200", "success"),
        ("https://httpbin.org/status/500", "failure"),
        ("https://httpbin.org/status/503", "failure"),
        ("https://httpbin.org/status/200", "success"),
        ("https://httpbin.org/status/500", "failure"),  # Should trigger circuit breaker
        ("https://httpbin.org/status/200", "blocked"),  # Should be blocked
    ]
    
    for i, (url, expected) in enumerate(urls_and_expected, 1):
        try:
            print(f"\nRequest {i} ({expected}): {url}")
            result = send_request_advanced(url=url, method="GET")
            print(f"  ✅ Status: {result.status_code}")
            
            # Simulate occasional errors for error tracking
            if result.status_code >= 500:
                enhanced_logger.log_error(
                    Exception(f"Server error {result.status_code}"),
                    {"url": url, "status": result.status_code}
                )
            
        except CircuitBreakerError as e:
            print(f"  🔴 Circuit breaker: {e}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            enhanced_logger.log_error(e, {"url": url, "request_num": i})
        
        time.sleep(0.5)  # Brief delay between requests
    
    print("\n3. Final System State")
    print("-" * 25)
    
    # Circuit breaker statistics
    cb_stats = circuit_breaker.get_statistics()
    print(f"Circuit Breaker State: {cb_stats['state']}")
    print(f"Total Requests: {cb_stats['total_requests']}")
    print(f"Error Rate: {cb_stats['error_rate']:.2%}")
    
    # Error tracking statistics
    error_stats = enhanced_logger.get_error_statistics()
    if error_stats:
        print(f"\nError Statistics:")
        for error_type, stats in error_stats.items():
            print(f"  {error_type}: {stats['total_count']} occurrences")


def main():
    """Run all Phase 4 enhancement demonstrations."""
    print("🛡️ LogicPwn Phase 4 Enhancements Demo")
    print("=" * 60)
    print("Demonstrating improved logging, middleware, and configuration validation")
    
    try:
        # Run individual demonstrations
        demonstrate_enhanced_error_tracking()
        demonstrate_circuit_breaker_middleware()
        demonstrate_configuration_validation()
        demonstrate_integrated_enhancements()
        
        print("\n" + "=" * 60)
        print("✅ All Phase 4 enhancements demonstrated successfully!")
        print("\nKey Improvements:")
        print("• 🔍 Enhanced error tracking with pattern detection")
        print("• ⚡ Circuit breaker middleware for resilience")
        print("• ⚙️ Comprehensive configuration validation")
        print("• 🔗 Integrated enhancement ecosystem")
        print("• 📊 Detailed statistics and monitoring")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
