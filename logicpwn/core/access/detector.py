import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional, Union

import requests

from logicpwn.core.performance.performance_monitor import monitor_performance
from logicpwn.core.reliability import (
    AdaptiveRateLimiter,
    RateLimitConfig,
    SecurityEventType,
    SecuritySeverity,
    rate_limiter_registry,
    record_security_event,
)
from logicpwn.core.runner.async_runner_core import AsyncRequestRunner

from .core_logic import (
    _test_single_id_with_baselines,
    _test_single_id_with_baselines_async,
)
from .models import (
    AccessDetectorConfig,
    AccessTestResult,
    EnhancedAccessTestConfig,
    EnhancedAccessTestResults,
)
from .validation import _sanitize_test_id, _validate_inputs


def _get_request_config_for_id(
    config: AccessDetectorConfig, test_id: Union[str, int]
) -> dict:
    """Helper to get method and request data for a given test ID."""
    method = config.method or "GET"
    data = None
    if config.request_data_map and test_id in config.request_data_map:
        data = config.request_data_map[test_id]
    return {"method": method, "data": data}


def _create_thread_safe_session(base_session: requests.Session) -> requests.Session:
    """
    Create a thread-safe copy of a session for concurrent use.

    Each thread gets its own session instance to prevent race conditions
    while preserving authentication state and configuration.
    """
    # Create a new session instance
    thread_session = requests.Session()

    # Copy authentication and configuration from the base session
    thread_session.cookies.update(base_session.cookies)
    thread_session.headers.update(base_session.headers)
    thread_session.auth = base_session.auth
    thread_session.proxies = base_session.proxies.copy()
    thread_session.verify = base_session.verify
    thread_session.cert = base_session.cert
    thread_session.trust_env = base_session.trust_env
    thread_session.max_redirects = base_session.max_redirects

    # Copy adapters for connection pooling configuration
    for prefix, adapter in base_session.adapters.items():
        # Create new adapter instance to avoid sharing connection pools
        new_adapter = requests.adapters.HTTPAdapter(
            pool_connections=getattr(adapter, "config", {}).get("pool_connections", 10),
            pool_maxsize=getattr(adapter, "config", {}).get("pool_maxsize", 10),
        )
        thread_session.mount(prefix, new_adapter)

    return thread_session


def _test_single_id_with_rate_limiting(
    session: requests.Session,
    url: str,
    test_id: Union[str, int],
    method: str,
    request_data: Optional[dict],
    success_indicators: list[str],
    failure_indicators: list[str],
    request_timeout: int,
    config: AccessDetectorConfig,
    rate_limiter: AdaptiveRateLimiter,
) -> AccessTestResult:
    """
    Execute single ID test with adaptive rate limiting.

    This wrapper adds rate limiting around the core testing logic
    to prevent overwhelming target servers and adapt to response patterns.
    """
    # Apply rate limiting delay if needed
    rate_limiter.wait_if_needed()

    # Record start time for response time measurement
    start_time = time.time()

    try:
        # Execute the actual test
        result = _test_single_id_with_baselines(
            session,
            url,
            test_id,
            method,
            request_data,
            success_indicators,
            failure_indicators,
            request_timeout,
            config,
        )

        # Calculate response time
        response_time = time.time() - start_time

        # Record request metrics for rate limiter adaptation
        rate_limiter.record_request(
            response_time=response_time,
            status_code=result.status_code,
            exception=(
                None
                if result.error_message is None
                else Exception(result.error_message)
            ),
        )

        return result

    except Exception as e:
        # Record failed request for rate limiting adaptation
        response_time = time.time() - start_time
        rate_limiter.record_request(
            response_time=response_time, status_code=0, exception=e
        )
        raise


@monitor_performance("idor_detection_batch")
def detect_idor_flaws(
    session: requests.Session,
    endpoint_template: str,
    test_ids: list[Union[str, int]],
    success_indicators: list[str],
    failure_indicators: list[str],
    config: Optional[AccessDetectorConfig] = None,
) -> list[AccessTestResult]:
    """
    Run IDOR/access control tests for a list of IDs, supporting custom HTTP methods, per-ID data, and multiple baselines.

    THREAD SAFETY: Creates isolated session copies for each worker thread to prevent race conditions.
    ADAPTIVE RATE LIMITING: Automatically adjusts request delays based on server response patterns.
    """
    config = config or AccessDetectorConfig()
    _validate_inputs(
        endpoint_template, test_ids, success_indicators, failure_indicators
    )
    results: list[AccessTestResult] = []

    # Initialize adaptive rate limiter
    rate_limit_config = RateLimitConfig(
        base_delay=config.rate_limit or 0.1,
        max_delay=30.0,
        min_delay=0.01,
        backoff_multiplier=2.0,
        recovery_factor=0.8,
    )
    rate_limiter = rate_limiter_registry.get_limiter(
        f"idor_detection_{endpoint_template.replace('/', '_')}", rate_limit_config
    )

    with ThreadPoolExecutor(max_workers=config.max_concurrent_requests) as executor:
        futures = []
        for test_id in test_ids:
            sanitized_id = _sanitize_test_id(test_id)
            url = endpoint_template.format(id=sanitized_id)
            req_cfg = _get_request_config_for_id(config, test_id)

            # Create thread-safe session copy for each worker
            thread_safe_session = _create_thread_safe_session(session)

            # Use rate-limited testing function
            futures.append(
                executor.submit(
                    _test_single_id_with_rate_limiting,
                    thread_safe_session,  # Use thread-safe session copy
                    url,
                    sanitized_id,
                    req_cfg["method"],
                    req_cfg["data"],
                    success_indicators,
                    failure_indicators,
                    config.request_timeout,
                    config,
                    rate_limiter,  # Pass rate limiter instance
                )
            )

        for future in as_completed(futures):
            result = future.result()
            results.append(
                result
            )  # Record security events for detected vulnerabilities
            if result.is_vulnerable:
                record_security_event(
                    SecurityEventType.IDOR_VULNERABILITY,
                    SecuritySeverity.HIGH,
                    f"IDOR vulnerability detected: {result.id_tested} - {getattr(result, 'vulnerability_evidence', 'N/A')[:200]}...",
                    metadata={
                        "test_id": result.id_tested,
                        "url": result.endpoint_url,
                        "status_code": result.status_code,
                        "evidence": getattr(result, "vulnerability_evidence", "N/A")[
                            :500
                        ],  # Limit evidence size
                        "detection_method": "batch_detection",
                    },
                    source_module="idor_detector",
                )
            elif result.error_message:
                record_security_event(
                    SecurityEventType.SUSPICIOUS_REQUEST,
                    SecuritySeverity.MEDIUM,
                    f"IDOR test error for {result.id_tested}: {result.error_message[:100]}",
                    metadata={
                        "test_id": result.id_tested,
                        "url": result.endpoint_url,
                        "error": result.error_message,
                    },
                    source_module="idor_detector",
                )

    # Check for potential memory leaks with large result sets
    if len(results) > 1000:
        record_security_event(
            SecurityEventType.MEMORY_LEAK_WARNING,
            SecuritySeverity.MEDIUM,
            f"Large IDOR result set detected: {len(results)} results may consume significant memory",
            metadata={
                "result_count": len(results),
                "endpoint_template": endpoint_template,
                "test_id_count": len(test_ids),
            },
            source_module="idor_detector",
        )

    # Log rate limiter metrics after completion
    from logicpwn.core.logging import log_info

    rl_metrics = rate_limiter.get_metrics()
    log_info(f"IDOR detection rate limiting metrics", rl_metrics)

    return results


async def detect_idor_flaws_async(
    endpoint_template: str,
    test_ids: list[Union[str, int]],
    success_indicators: list[str],
    failure_indicators: list[str],
    config: Optional[AccessDetectorConfig] = None,
) -> list[AccessTestResult]:
    """
    Async version of IDOR/access control tests, supporting custom HTTP methods, per-ID data, and multiple baselines.
    """
    config = config or AccessDetectorConfig()
    _validate_inputs(
        endpoint_template, test_ids, success_indicators, failure_indicators
    )
    results: list[AccessTestResult] = []
    async with AsyncRequestRunner(
        max_concurrent=config.max_concurrent_requests, timeout=config.request_timeout
    ) as runner:
        tasks = []
        for test_id in test_ids:
            sanitized_id = _sanitize_test_id(test_id)
            url = endpoint_template.format(id=sanitized_id)
            req_cfg = _get_request_config_for_id(config, test_id)
            tasks.append(
                _test_single_id_with_baselines_async(
                    runner,
                    url,
                    sanitized_id,
                    req_cfg["method"],
                    req_cfg["data"],
                    success_indicators,
                    failure_indicators,
                    config.request_timeout,
                    config,
                )
            )
        results = await asyncio.gather(*tasks)
    return results


async def run_enhanced_access_detection(
    session: requests.Session,
    base_url: str,
    endpoint_template: str,
    example_ids: list[str],
    success_indicators: list[str],
    failure_indicators: list[str],
    current_tenant_id: Optional[str] = None,
    current_role_name: Optional[str] = None,
    config: Optional[EnhancedAccessTestConfig] = None,
) -> EnhancedAccessTestResults:
    """
    High-level function to run enhanced access detection with all capabilities.

    This is the main entry point for comprehensive access control testing.

    Args:
        session: Authenticated requests session
        base_url: Base URL of the application
        endpoint_template: Template for IDOR testing (e.g., "/api/users/{id}")
        example_ids: Known valid IDs to base generation on
        success_indicators: Response indicators for successful access
        failure_indicators: Response indicators for denied access
        current_tenant_id: Current tenant context (for tenant isolation testing)
        current_role_name: Current role context (for privilege escalation testing)
        config: Optional custom configuration

    Returns:
        Comprehensive test results including all vulnerability types
    """
    from .logging import log_error, log_info

    # Create default config if not provided
    if not config:
        config = create_enhanced_access_config(
            enable_all_features=True,
            current_tenant_id=current_tenant_id,
            current_role_name=current_role_name,
            detailed_testing=True,
        )

    start_time = time.time()
    log_info("Starting comprehensive enhanced access control testing")

    results = EnhancedAccessTestResults(test_config=config)

    try:
        # Phase 1: Smart ID Generation
        if config.enable_smart_id_generation:
            generated_ids = await _generate_smart_test_ids(example_ids, config)
            results.generated_ids = generated_ids
            log_info(f"Generated {len(generated_ids)} intelligent test IDs")
        else:
            generated_ids = example_ids

        # Phase 2: Basic IDOR Testing with Enhanced IDs
        idor_results = await _run_enhanced_idor_testing(
            session,
            endpoint_template,
            generated_ids,
            success_indicators,
            failure_indicators,
            config,
        )
        results.idor_results = idor_results
        log_info(f"Completed IDOR testing: {len(idor_results)} tests executed")

        # Phase 3: Tenant Isolation Testing
        if config.enable_tenant_isolation and config.current_tenant_id:
            tenant_results = await _run_tenant_isolation_testing(
                session, base_url, config
            )
            results.tenant_isolation_results = tenant_results
            log_info(
                f"Completed tenant isolation testing: {len(tenant_results)} tests executed"
            )

        # Phase 4: Privilege Escalation Testing
        if config.enable_privilege_escalation and config.current_role_name:
            privilege_results = await _run_privilege_escalation_testing(
                session, base_url, config
            )
            results.privilege_escalation_results = privilege_results
            log_info(
                f"Completed privilege escalation testing: {len(privilege_results)} tests executed"
            )

        # Phase 5: Generate Summary Statistics
        _calculate_summary_statistics(results)

        results.test_duration = time.time() - start_time

        log_info(
            f"Enhanced access testing completed in {results.test_duration:.2f} seconds"
        )
        log_info(f"Total vulnerabilities found: {results.vulnerabilities_found}")
        log_info(f"Critical vulnerabilities: {results.critical_vulnerabilities}")

        return results

    except Exception as e:
        log_error(f"Error in comprehensive access testing: {str(e)}")
        results.test_duration = time.time() - start_time
        return results


async def _generate_smart_test_ids(
    example_ids: list[str], config: EnhancedAccessTestConfig
) -> list[str]:
    """Generate intelligent test IDs using the enhanced ID generator."""
    from .id_generation import generate_smart_id_list

    return generate_smart_id_list(
        example_ids=example_ids,
        max_total_ids=config.max_generated_ids,
        include_privilege_escalation=config.include_privilege_escalation_ids,
        include_tenant_testing=config.include_tenant_testing_ids,
    )


async def _run_enhanced_idor_testing(
    session: requests.Session,
    endpoint_template: str,
    test_ids: list[str],
    success_indicators: list[str],
    failure_indicators: list[str],
    config: EnhancedAccessTestConfig,
) -> list[AccessTestResult]:
    """Run enhanced IDOR testing with the generated IDs."""
    # Use the existing IDOR detection with enhanced configuration
    enhanced_config = config.basic_idor_config or AccessDetectorConfig()
    enhanced_config.max_concurrent_requests = min(
        config.max_concurrent_tests, enhanced_config.max_concurrent_requests
    )
    enhanced_config.request_timeout = config.request_timeout

    # Use async version for better performance
    return await detect_idor_flaws_async(
        endpoint_template=endpoint_template,
        test_ids=test_ids,
        success_indicators=success_indicators,
        failure_indicators=failure_indicators,
        config=enhanced_config,
    )


async def _run_tenant_isolation_testing(
    session: requests.Session, base_url: str, config: EnhancedAccessTestConfig
) -> list:
    """Run comprehensive tenant isolation testing."""
    from .tenant_isolation import run_comprehensive_tenant_isolation_test

    tenant_config = config.tenant_test_config
    if tenant_config:
        tenant_config.max_concurrent_tests = min(
            config.max_concurrent_tests, tenant_config.max_concurrent_tests
        )

    return await run_comprehensive_tenant_isolation_test(
        base_url=base_url,
        session=session,
        current_tenant_id=config.current_tenant_id,
        config=tenant_config,
    )


async def _run_privilege_escalation_testing(
    session: requests.Session, base_url: str, config: EnhancedAccessTestConfig
) -> list:
    """Run comprehensive privilege escalation testing."""
    from .privilege_escalation import run_comprehensive_privilege_escalation_test

    role_config = config.role_test_config
    if role_config:
        role_config.max_concurrent_tests = min(
            config.max_concurrent_tests, role_config.max_concurrent_tests
        )

    return await run_comprehensive_privilege_escalation_test(
        base_url=base_url,
        session=session,
        current_role_name=config.current_role_name,
        config=role_config,
    )


def _calculate_summary_statistics(results: EnhancedAccessTestResults) -> None:
    """Calculate summary statistics for the test results."""
    total_tests = 0
    vulnerabilities = 0
    critical_vulns = 0
    high_risk_vulns = 0

    # Count IDOR results
    total_tests += len(results.idor_results)
    for result in results.idor_results:
        if getattr(result, "vulnerability_detected", False):
            vulnerabilities += 1
            # Assume IDOR vulnerabilities are high risk
            high_risk_vulns += 1

    # Count tenant isolation results
    total_tests += len(results.tenant_isolation_results)
    for result in results.tenant_isolation_results:
        if getattr(result, "isolation_breach", False):
            vulnerabilities += 1
            risk_level = getattr(result, "risk_level", "MEDIUM")
            if risk_level == "CRITICAL":
                critical_vulns += 1
            elif risk_level == "HIGH":
                high_risk_vulns += 1

    # Count privilege escalation results
    total_tests += len(results.privilege_escalation_results)
    for result in results.privilege_escalation_results:
        if getattr(result, "privilege_escalation", False):
            vulnerabilities += 1
            risk_level = getattr(result, "risk_level", "MEDIUM")
            if risk_level == "CRITICAL":
                critical_vulns += 1
            elif risk_level == "HIGH":
                high_risk_vulns += 1

    # Extract discovered data
    results.discovered_tenants = list(
        {
            getattr(result.target_tenant, "tenant_id", None)
            for result in results.tenant_isolation_results
            if hasattr(result, "target_tenant") and result.target_tenant
        }
    )

    results.discovered_roles = list(
        {
            getattr(result.target_role, "role_name", None)
            for result in results.privilege_escalation_results
            if hasattr(result, "target_role") and result.target_role
        }
    )

    results.discovered_admin_functions = list(
        {
            getattr(result, "function_name", "")
            for result in results.privilege_escalation_results
            if hasattr(result, "function_name")
            and "admin" in getattr(result, "function_name", "").lower()
        }
    )

    # Update summary
    results.total_tests_executed = total_tests
    results.vulnerabilities_found = vulnerabilities
    results.critical_vulnerabilities = critical_vulns
    results.high_risk_vulnerabilities = high_risk_vulns


def create_enhanced_access_config(
    enable_all_features: bool = True,
    current_tenant_id: Optional[str] = None,
    current_role_name: Optional[str] = None,
    max_concurrent: int = 20,
    detailed_testing: bool = True,
) -> EnhancedAccessTestConfig:
    """Create a comprehensive enhanced access test configuration."""

    # Create sub-configurations
    idor_config = AccessDetectorConfig(
        max_concurrent_requests=max_concurrent,
        request_timeout=30,
        compare_unauthenticated=True,
    )

    tenant_config = None
    role_config = None

    if enable_all_features:
        try:
            from .tenant_isolation import TenantTestConfig

            tenant_config = TenantTestConfig(max_concurrent_tests=max_concurrent)
        except ImportError:
            pass

        try:
            from .privilege_escalation import RoleTestConfig

            role_config = RoleTestConfig(max_concurrent_tests=max_concurrent)
        except ImportError:
            pass

    return EnhancedAccessTestConfig(
        basic_idor_config=idor_config,
        enable_smart_id_generation=enable_all_features,
        enable_tenant_isolation=enable_all_features and current_tenant_id is not None,
        enable_privilege_escalation=enable_all_features
        and current_role_name is not None,
        enable_admin_discovery=enable_all_features,
        tenant_test_config=tenant_config,
        role_test_config=role_config,
        current_tenant_id=current_tenant_id,
        current_role_name=current_role_name,
        max_concurrent_tests=max_concurrent,
        detailed_reporting=detailed_testing,
    )


def run_enhanced_access_detection_sync(
    session: requests.Session,
    base_url: str,
    endpoint_template: str,
    example_ids: list[str],
    success_indicators: list[str],
    failure_indicators: list[str],
    current_tenant_id: Optional[str] = None,
    current_role_name: Optional[str] = None,
    config: Optional[EnhancedAccessTestConfig] = None,
) -> EnhancedAccessTestResults:
    """
    Synchronous wrapper for enhanced access detection.

    This function provides a synchronous interface to the async testing capabilities.
    """
    return asyncio.run(
        run_enhanced_access_detection(
            session=session,
            base_url=base_url,
            endpoint_template=endpoint_template,
            example_ids=example_ids,
            success_indicators=success_indicators,
            failure_indicators=failure_indicators,
            current_tenant_id=current_tenant_id,
            current_role_name=current_role_name,
            config=config,
        )
    )


# Convenience functions for specific testing scenarios
def quick_idor_with_smart_ids(
    session: requests.Session,
    endpoint_template: str,
    example_ids: list[str],
    success_indicators: list[str],
    failure_indicators: list[str],
    max_generated_ids: int = 500,
) -> list[AccessTestResult]:
    """Quick IDOR testing with intelligent ID generation."""
    config = EnhancedAccessTestConfig(
        enable_smart_id_generation=True,
        max_generated_ids=max_generated_ids,
        enable_tenant_isolation=False,
        enable_privilege_escalation=False,
        enable_admin_discovery=False,
    )

    results = run_enhanced_access_detection_sync(
        session=session,
        base_url="",  # Not needed for basic IDOR
        endpoint_template=endpoint_template,
        example_ids=example_ids,
        success_indicators=success_indicators,
        failure_indicators=failure_indicators,
        config=config,
    )

    return results.idor_results


def tenant_isolation_test_only(
    session: requests.Session, base_url: str, current_tenant_id: str
) -> list:
    """Run only tenant isolation testing."""
    config = EnhancedAccessTestConfig(
        enable_smart_id_generation=False,
        enable_tenant_isolation=True,
        enable_privilege_escalation=False,
        enable_admin_discovery=False,
        current_tenant_id=current_tenant_id,
    )

    results = run_enhanced_access_detection_sync(
        session=session,
        base_url=base_url,
        endpoint_template="/api/dummy/{id}",  # Not used
        example_ids=["dummy"],
        success_indicators=["success"],
        failure_indicators=["error"],
        current_tenant_id=current_tenant_id,
        config=config,
    )

    return results.tenant_isolation_results


def privilege_escalation_test_only(
    session: requests.Session, base_url: str, current_role_name: str
) -> list:
    """Run only privilege escalation testing."""
    config = EnhancedAccessTestConfig(
        enable_smart_id_generation=False,
        enable_tenant_isolation=False,
        enable_privilege_escalation=True,
        enable_admin_discovery=True,
        current_role_name=current_role_name,
    )

    results = run_enhanced_access_detection_sync(
        session=session,
        base_url=base_url,
        endpoint_template="/api/dummy/{id}",  # Not used
        example_ids=["dummy"],
        success_indicators=["success"],
        failure_indicators=["error"],
        current_role_name=current_role_name,
        config=config,
    )

    return results.privilege_escalation_results


class EnhancedAccessTester:
    """
    Enhanced access tester that orchestrates comprehensive access control testing.

    This class integrates all the advanced access testing capabilities into a
    unified interface for complete access control vulnerability assessment.
    """

    def __init__(self, config: Optional[EnhancedAccessTestConfig] = None):
        self.config = config or EnhancedAccessTestConfig()
        from .id_generation import EnhancedIDGenerator, create_id_generation_config

        self.id_generator = EnhancedIDGenerator(
            create_id_generation_config(
                max_ids=self.config.max_generated_ids, enable_edge_cases=True
            )
        )

    async def run_comprehensive_access_test(
        self,
        session: requests.Session,
        base_url: str,
        endpoint_template: str,
        example_ids: list[str],
        success_indicators: list[str],
        failure_indicators: list[str],
    ) -> EnhancedAccessTestResults:
        """
        Run comprehensive access control testing with all enhanced capabilities.

        This is the main entry point for the enhanced access testing system.
        """
        return await run_enhanced_access_detection(
            session=session,
            base_url=base_url,
            endpoint_template=endpoint_template,
            example_ids=example_ids,
            success_indicators=success_indicators,
            failure_indicators=failure_indicators,
            current_tenant_id=self.config.current_tenant_id,
            current_role_name=self.config.current_role_name,
            config=self.config,
        )

    def generate_detailed_report(
        self, results: EnhancedAccessTestResults
    ) -> dict[str, Any]:
        """Generate a detailed report of the test results."""
        report = {
            "summary": {
                "total_tests": results.total_tests_executed,
                "vulnerabilities_found": results.vulnerabilities_found,
                "critical_vulnerabilities": results.critical_vulnerabilities,
                "high_risk_vulnerabilities": results.high_risk_vulnerabilities,
                "test_duration": results.test_duration,
            },
            "id_generation": {
                "total_generated": len(results.generated_ids),
                "example_ids": (
                    results.generated_ids[:10] if results.generated_ids else []
                ),
            },
            "idor_testing": {
                "total_tests": len(results.idor_results),
                "vulnerabilities": [
                    {
                        "id_tested": result.id_tested,
                        "endpoint": result.endpoint_url,
                        "vulnerable": getattr(result, "vulnerability_detected", False),
                        "status_code": result.status_code,
                    }
                    for result in results.idor_results
                    if getattr(result, "vulnerability_detected", False)
                ],
            },
            "tenant_isolation": {
                "total_tests": len(results.tenant_isolation_results),
                "discovered_tenants": results.discovered_tenants,
                "isolation_breaches": [
                    {
                        "test_type": getattr(result, "test_type", "unknown"),
                        "source_tenant": getattr(result, "source_tenant", {}).get(
                            "tenant_id", "unknown"
                        ),
                        "target_tenant": (
                            getattr(result, "target_tenant", {}).get(
                                "tenant_id", "unknown"
                            )
                            if hasattr(result, "target_tenant") and result.target_tenant
                            else None
                        ),
                        "endpoint": getattr(result, "endpoint", "unknown"),
                        "risk_level": getattr(result, "risk_level", "MEDIUM"),
                        "evidence": getattr(result, "evidence", "No evidence"),
                    }
                    for result in results.tenant_isolation_results
                    if getattr(result, "isolation_breach", False)
                ],
            },
            "privilege_escalation": {
                "total_tests": len(results.privilege_escalation_results),
                "discovered_roles": results.discovered_roles,
                "discovered_admin_functions": results.discovered_admin_functions,
                "escalations": [
                    {
                        "test_type": getattr(result, "test_type", "unknown"),
                        "source_role": getattr(result, "source_role", {}).get(
                            "role_name", "unknown"
                        ),
                        "target_role": (
                            getattr(result, "target_role", {}).get(
                                "role_name", "unknown"
                            )
                            if hasattr(result, "target_role") and result.target_role
                            else None
                        ),
                        "endpoint": getattr(result, "endpoint", "unknown"),
                        "function": getattr(result, "function_name", "unknown"),
                        "risk_level": getattr(result, "risk_level", "MEDIUM"),
                        "evidence": getattr(result, "evidence", "No evidence"),
                    }
                    for result in results.privilege_escalation_results
                    if getattr(result, "privilege_escalation", False)
                ],
            },
        }

        return report
