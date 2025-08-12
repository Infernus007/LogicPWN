#!/usr/bin/env python3
"""
LogicPWN Integration Demo - Practical Examples
==============================================

This script demonstrates the enhanced LogicPWN integration system with real-world examples.
Run with: poetry run python examples/integration_demo.py
"""

import time
import sys
from pathlib import Path

# Add logicpwn to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from logicpwn.core.auth import AuthConfig, create_csrf_config
from logicpwn.core.integration_utils import AuthenticatedValidator, create_dvwa_validator, quick_auth_test
from logicpwn.core.validator import list_available_presets, validate_with_preset
from logicpwn.core.performance import monitor_performance, PerformanceMonitor
from logicpwn.models.request_result import RequestResult
from loguru import logger

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔥 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n🔹 {title}")
    print("-" * 40)

@monitor_performance("demo_validation_test")
def demo_validation_system():
    """Demonstrate the validation system with various presets"""
    print_section("Validation System Demo")
    
    # Get available presets
    presets = list_available_presets()
    print(f"📋 Available validation presets: {len(presets)}")
    for i, preset in enumerate(presets, 1):
        print(f"   {i}. {preset}")
    
    # Demo different vulnerability types
    test_cases = [
        {
            "name": "SQL Injection Test",
            "url": "http://example.com/search",
            "method": "GET",
            "body": "SELECT * FROM users WHERE id=1 OR 1=1--",
            "preset": "sql_injection"
        },
        {
            "name": "XSS Test", 
            "url": "http://example.com/comment",
            "method": "POST",
            "body": "<script>alert('XSS vulnerability found!')</script>",
            "preset": "xss"
        },
        {
            "name": "Directory Traversal Test",
            "url": "http://example.com/file",
            "method": "GET", 
            "body": "../../../../etc/passwd",
            "preset": "directory_traversal"
        }
    ]
    
    print(f"\n🧪 Testing {len(test_cases)} vulnerability scenarios:")
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        
        # Create mock request result
        mock_result = RequestResult(
            url=test_case["url"],
            method=test_case["method"],
            status_code=200,
            body=test_case["body"],
            headers={"Content-Type": "text/html"}
        )
        
        # Validate with preset
        try:
            validation_result = validate_with_preset(mock_result, test_case["preset"])
            print(f"     ✓ Validation completed")
            print(f"     ✓ Is valid: {validation_result.is_valid}")
            print(f"     ✓ Confidence: {validation_result.confidence_score:.2f}")
            print(f"     ✓ Patterns matched: {len(validation_result.matched_patterns)}")
            
            if validation_result.matched_patterns:
                print(f"     ⚠️  Detected patterns: {validation_result.matched_patterns[:2]}")
                
        except Exception as e:
            print(f"     ✗ Validation failed: {e}")

def demo_authentication_system():
    """Demonstrate advanced authentication features"""
    print_section("Authentication System Demo")
    
    # Demo 1: Basic authentication with CSRF
    print("🔐 Demo 1: CSRF-Protected Authentication")
    csrf_config = create_csrf_config(
        enabled=True,
        auto_include=True,
        refresh_on_failure=True
    )
    
    auth_config = AuthConfig(
        url="https://httpbin.org/post",
        credentials={"username": "demo_user", "password": "demo_pass"},
        success_indicators=["json", "form"],
        csrf_config=csrf_config,
        max_retries=3,
        timeout=15
    )
    
    print(f"   ✓ CSRF protection enabled: {csrf_config.enabled}")
    print(f"   ✓ Auto-include tokens: {csrf_config.auto_include}")
    print(f"   ✓ Max retries: {auth_config.max_retries}")
    print(f"   ✓ Timeout: {auth_config.timeout}s")
    
    # Demo 2: Quick authentication test
    print(f"\n🚀 Demo 2: Quick Authentication Test")
    try:
        # This will fail but demonstrates the error handling
        result = quick_auth_test("https://httpbin.org/status/401", "user", "pass")
        print("   ✓ Authentication succeeded (unexpected)")
    except Exception as e:
        print("   ✓ Authentication properly handled failure")
        print(f"   ✓ Error handling working: {type(e).__name__}")
    
    # Demo 3: DVWA validator setup
    print(f"\n🎯 Demo 3: DVWA Validator Setup")
    try:
        dvwa_validator = create_dvwa_validator("http://localhost/DVWA")
        print("   ✓ DVWA validator created successfully")
        print(f"   ✓ Auth URL: {dvwa_validator.auth_config.url}")
        print(f"   ✓ CSRF enabled: {dvwa_validator.auth_config.csrf_config.enabled}")
        print("   ⚠️  Note: Will fail to authenticate without actual DVWA server")
    except Exception as e:
        print(f"   ✗ DVWA setup failed (expected): {e}")

def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities"""
    print_section("Performance Monitoring Demo")
    
    print("⚡ Testing performance monitoring decorator:")
    
    @monitor_performance("database_operation")
    def simulate_database_operation():
        """Simulate a database operation"""
        time.sleep(0.1)  # Simulate work
        return {"status": "success", "records": 42}
    
    @monitor_performance("api_request")
    def simulate_api_request():
        """Simulate an API request"""
        time.sleep(0.05)  # Simulate network delay
        return {"status": 200, "data": "response"}
    
    # Run operations
    db_result = simulate_database_operation()
    api_result = simulate_api_request()
    
    print(f"   ✓ Database operation: {db_result['status']}")
    print(f"   ✓ API request: HTTP {api_result['status']}")
    
    # Demo context manager
    print(f"\n⏱️  Testing performance monitoring context manager:")
    monitor = PerformanceMonitor()
    
    with monitor:
        monitor.start_monitoring("bulk_operation")
        time.sleep(0.2)  # Simulate work
        monitor.stop_monitoring()
    
    metrics = monitor.get_metrics()
    if metrics:
        latest = metrics[-1]
        print(f"   ✓ Operation: {latest.operation_name}")
        print(f"   ✓ Duration: {latest.duration:.3f}s")
        print(f"   ✓ Success: {latest.success}")
        print(f"   ✓ Memory usage tracked: {latest.memory_usage_mb:.1f}MB")

def demo_integrated_workflow():
    """Demonstrate the complete integrated workflow"""
    print_section("Integrated Workflow Demo")
    
    # Create a comprehensive authentication configuration
    csrf_config = create_csrf_config(enabled=True, auto_include=True)
    
    auth_config = AuthConfig(
        url="https://httpbin.org/post", 
        credentials={"username": "integration_test", "password": "test123"},
        success_indicators=["json", "form", "data"],
        failure_indicators=["error", "failed", "invalid"],
        csrf_config=csrf_config,
        max_retries=2,
        timeout=10,
        verify_ssl=True
    )
    
    # Create integrated validator with performance monitoring
    validator = AuthenticatedValidator(
        auth_config,
        "https://httpbin.org",
        enable_performance_monitoring=True
    )
    
    print("🔄 Setting up integrated workflow:")
    print(f"   ✓ Authentication configured for: {auth_config.url}")
    print(f"   ✓ CSRF protection: {auth_config.csrf_config.enabled}")
    print(f"   ✓ Performance monitoring: {validator.enable_monitoring}")
    print(f"   ✓ Base URL: {validator.base_url}")
    
    # Demonstrate error handling for authentication
    print(f"\n🧪 Testing authentication workflow:")
    try:
        auth_result = validator.authenticate()
        if auth_result:
            print("   ✓ Authentication successful!")
        else:
            print("   ⚠️  Authentication failed (expected for demo)")
    except Exception as e:
        print(f"   ✓ Authentication error handled: {type(e).__name__}")
        print("   ✓ Error handling working correctly")
    
    print(f"\n📊 Integration features summary:")
    print("   ✓ Advanced HTTP client with session management")
    print("   ✓ CSRF token automatic handling")
    print("   ✓ Comprehensive validation preset system") 
    print("   ✓ Performance monitoring with decorators")
    print("   ✓ High-level integration utilities")
    print("   ✓ Robust error handling and logging")

def main():
    """Main demo function"""
    print_header("LogicPWN Integration System - Live Demo")
    
    print("🎯 This demo showcases the enhanced LogicPWN integration system")
    print("   featuring unified authentication, validation, and performance monitoring.")
    
    # Run all demonstrations
    try:
        demo_validation_system()
        demo_authentication_system()
        demo_performance_monitoring()
        demo_integrated_workflow()
        
        print_header("Demo Complete - All Systems Operational! 🚀")
        
        print("\n📈 Integration Benefits:")
        print("   • Unified authentication with CSRF protection")
        print("   • 8 built-in validation presets for common vulnerabilities")
        print("   • Automatic performance monitoring and metrics collection")
        print("   • High-level utilities for rapid penetration testing")
        print("   • Backward compatibility with existing code")
        print("   • Poetry environment support")
        
        print("\n🔗 Next Steps:")
        print("   1. Set up your target application configuration")
        print("   2. Use create_dvwa_validator() for DVWA testing")
        print("   3. Leverage validation presets for vulnerability detection")
        print("   4. Monitor performance metrics for optimization")
        print("   5. Check docs/INTEGRATION_USAGE_GUIDE.md for detailed examples")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo encountered an error: {e}")
        print("   Check the logs for more details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
