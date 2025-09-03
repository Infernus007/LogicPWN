"""
Demonstration of LogicPWN validator security enhancements.
Shows regex performance optimization and response size handling features.
"""

import time
from unittest.mock import Mock

import requests

from logicpwn.core.validator import (
    RegexSecurityValidator,
    ResponseSizeConfig,
    ValidationConfig,
    create_response_processor,
    safe_regex_search,
    validate_regex_pattern,
    validate_response,
)


def demo_regex_security():
    """Demonstrate regex security features."""
    print("=== Regex Security Demo ===")

    # 1. Pattern safety validation
    print("\n1. Pattern Safety Validation:")

    safe_pattern = r"admin.*panel"
    dangerous_pattern = r"(a+)+b"  # ReDoS pattern

    is_safe, warning = validate_regex_pattern(safe_pattern)
    print(f"Safe pattern '{safe_pattern}': {is_safe}")

    is_safe, warning = validate_regex_pattern(dangerous_pattern)
    print(f"Dangerous pattern '{dangerous_pattern}': {is_safe}")
    if warning:
        print(f"  Warning: {warning}")

    # 2. Complexity analysis
    print("\n2. Pattern Complexity Analysis:")
    validator = RegexSecurityValidator()

    patterns = [r"test", r"admin.*access", r"(user.*)+admin", r"(a*)*b", r".*.*.*"]

    for pattern in patterns:
        complexity = validator.analyze_pattern_complexity(pattern)
        print(f"Pattern '{pattern}': complexity = {complexity:.2f}")

    # 3. Safe regex execution
    print("\n3. Safe Regex Execution:")
    text = "Welcome to the admin panel access page"

    # This will work fine
    match = safe_regex_search(r"admin.*access", text, timeout=1.0)
    print(f"Safe search result: {match.group(0) if match else 'No match'}")

    # This would be blocked or timeout
    try:
        match = safe_regex_search(r"(a+)+b", "a" * 100, timeout=0.1)
        print(f"Dangerous search result: {match}")
    except Exception as e:
        print(f"Dangerous pattern blocked: {type(e).__name__}")


def demo_response_size_handling():
    """Demonstrate response size handling features."""
    print("\n=== Response Size Handling Demo ===")

    # 1. Create test responses
    small_response = Mock(spec=requests.Response)
    small_response.status_code = 200
    small_response.headers = {"content-type": "text/html"}
    small_response.text = "Small response with admin panel"
    small_response.content = small_response.text.encode()

    large_response = Mock(spec=requests.Response)
    large_response.status_code = 200
    large_response.headers = {"content-type": "text/html"}
    # Create large response with evidence
    large_content = "x" * 5000 + "SQL injection vulnerability detected" + "y" * 5000
    large_response.text = large_content
    large_response.content = large_content.encode()

    # 2. Configure response processor
    config = ResponseSizeConfig(
        max_response_size=20000,
        truncation_size=1000,
        preserve_evidence=True,
        evidence_window_size=100,
        sanitize_sensitive_data=True,
    )

    processor = create_response_processor(
        max_size=config.max_response_size,
        preserve_evidence=config.preserve_evidence,
        sanitize_data=config.sanitize_sensitive_data,
    )

    # 3. Process small response
    print("\n1. Small Response Processing:")
    patterns = [r"admin.*panel"]
    result = processor.process_response(small_response, patterns)

    print(f"Status: {result['status_code']}")
    print(f"Size category: {result['size_info']['size_category']}")
    print(f"Truncated: {result['truncated']}")
    print(f"Content: {result['content']['raw_content']}")

    # 4. Process large response
    print("\n2. Large Response Processing:")
    patterns = [r"SQL.*vulnerability"]
    result = processor.process_response(large_response, patterns)

    print(f"Status: {result['status_code']}")
    print(f"Size category: {result['size_info']['size_category']}")
    print(f"Truncated: {result['truncated']}")
    print(f"Evidence chunks: {len(result['evidence_chunks'])}")

    if result["evidence_chunks"]:
        chunk = result["evidence_chunks"][0]
        print(f"Evidence found: {chunk['match_text']}")
        print(f"Context: {chunk['context'][:100]}...")


def demo_integrated_validation():
    """Demonstrate integrated validation with security features."""
    print("\n=== Integrated Validation Demo ===")

    # Create test response
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.headers = {"content-type": "text/html"}
    response.text = (
        "Admin panel detected with potential SQL injection: password='secret123'"
    )
    response.content = response.text.encode()

    # 1. Basic validation with security
    print("\n1. Basic Validation with Security:")
    result = validate_response(
        response=response,
        regex_patterns=[r"Admin.*panel", r"SQL.*injection"],
        return_structured=True,
    )

    print(f"Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Matched patterns: {result.matched_patterns}")

    if "security_warnings" in result.metadata:
        print(f"Security warnings: {result.metadata['security_warnings']}")

    # 2. Advanced configuration
    print("\n2. Advanced Security Configuration:")

    config = ValidationConfig(
        regex_patterns=[r"Admin.*panel", r"SQL.*injection"],
        regex_timeout=1.0,
        max_regex_complexity=5.0,
        enable_regex_security=True,
        max_response_size=1024,
        preserve_evidence=True,
        sanitize_response_data=True,
        confidence_threshold=0.3,
    )

    result = validate_response(
        response=response, regex_patterns=config.regex_patterns, return_structured=True
    )

    print(f"Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Vulnerability type: {result.vulnerability_type}")

    # Check for response size info
    if "content_length" in result.metadata:
        print(f"Response size: {result.metadata['content_length']} bytes")


def demo_performance_comparison():
    """Demonstrate performance improvements."""
    print("\n=== Performance Comparison Demo ===")

    # Test pattern that could be problematic
    pattern = r"admin.*panel.*access"
    text = "Welcome to the admin panel access control system"

    # 1. Safe execution with timeout
    print("\n1. Safe Regex Execution:")
    start_time = time.time()

    try:
        match = safe_regex_search(pattern, text, timeout=1.0)
        elapsed = time.time() - start_time
        print(f"Safe search completed in {elapsed:.4f}s")
        print(f"Result: {match.group(0) if match else 'No match'}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"Safe search failed in {elapsed:.4f}s: {type(e).__name__}")

    # 2. Response processing performance
    print("\n2. Response Processing Performance:")

    # Create large response
    large_response = Mock(spec=requests.Response)
    large_response.status_code = 200
    large_response.headers = {"content-type": "text/html"}
    large_response.text = "data " * 10000 + "EVIDENCE" + " data" * 10000
    large_response.content = large_response.text.encode()

    start_time = time.time()
    processor = create_response_processor(preserve_evidence=True)
    result = processor.process_response(large_response, [r"EVIDENCE"])
    elapsed = time.time() - start_time

    print(f"Processed {len(large_response.text)} chars in {elapsed:.4f}s")
    print(f"Evidence chunks preserved: {len(result['evidence_chunks'])}")


def main():
    """Run all security enhancement demos."""
    print("LogicPWN Validator Security Enhancements Demo")
    print("=" * 50)

    try:
        demo_regex_security()
        demo_response_size_handling()
        demo_integrated_validation()
        demo_performance_comparison()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Security Features Demonstrated:")
        print("✓ Regex pattern safety validation")
        print("✓ Pattern complexity analysis")
        print("✓ Timeout protection for regex execution")
        print("✓ Response size handling with evidence preservation")
        print("✓ Sensitive data sanitization")
        print("✓ Integrated security warnings")
        print("✓ Performance optimizations")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
