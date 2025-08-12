#!/usr/bin/env python3
"""
LogicPwn Integration Enhancement and Validation Report
=====================================================

This module provides comprehensive enhancement utilities and validation for the
integrated LogicPwn authentication, validation, and performance monitoring system.
"""

from typing import Dict, List, Any, Optional, Tuple
import time
import json
from dataclasses import dataclass, asdict
from loguru import logger

from logicpwn.core.integration_utils import (
    AuthenticatedValidator, 
    create_dvwa_validator, 
    quick_auth_test
)
from logicpwn.core.auth import AuthConfig, CSRFConfig, create_csrf_config
from logicpwn.core.validator import (
    ValidationResult, 
   ValidationConfig,
    list_available_presets,
    validate_response
)
from logicpwn.core.performance import (
    PerformanceMetrics,
    PerformanceMonitor,
    monitor_performance
)


@dataclass
class IntegrationTestResult:
    """Result of an integration test."""
    test_name: str
    success: bool
    duration: float
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class IntegrationReport:
    """Comprehensive integration test report."""
    test_results: List[IntegrationTestResult]
    total_tests: int
    successful_tests: int
    failed_tests: int
    total_duration: float
    system_info: Dict[str, Any]
    
    def get_success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.successful_tests / self.total_tests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class IntegrationEnhancer:
    """Enhanced integration testing and validation utilities."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.test_results: List[IntegrationTestResult] = []
        
    @monitor_performance("auth_config_validation")
    def validate_auth_config(self, auth_config: AuthConfig) -> IntegrationTestResult:
        """Validate an authentication configuration."""
        start_time = time.time()
        
        try:
            # Test configuration validity
            validator = AuthenticatedValidator(auth_config, "http://localhost")
            
            details = {
                "url": auth_config.url,
                "method": auth_config.method,
                "has_credentials": bool(auth_config.credentials),
                "has_success_indicators": bool(auth_config.success_indicators),
                "has_csrf_config": auth_config.csrf_config is not None,
                "timeout": auth_config.timeout,
                "ssl_verification": auth_config.verify_ssl
            }
            
            duration = time.time() - start_time
            return IntegrationTestResult(
                test_name="auth_config_validation",
                success=True,
                duration=duration,
                details=details
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return IntegrationTestResult(
                test_name="auth_config_validation",
                success=False,
                duration=duration,
                details={},
                error_message=str(e)
            )
    
    @monitor_performance("csrf_configuration_test")
    def test_csrf_configurations(self) -> List[IntegrationTestResult]:
        """Test various CSRF configurations."""
        results = []
        
        csrf_configs = [
            ("basic_csrf", create_csrf_config(enabled=True)),
            ("auto_include_csrf", create_csrf_config(enabled=True, auto_include=True)),
            ("refresh_on_failure", create_csrf_config(enabled=True, refresh_on_failure=True)),
            ("full_csrf", create_csrf_config(enabled=True, auto_include=True, refresh_on_failure=True)),
            ("disabled_csrf", create_csrf_config(enabled=False))
        ]
        
        for config_name, csrf_config in csrf_configs:
            start_time = time.time()
            
            try:
                auth_config = AuthConfig(
                    url="http://localhost:8080/login",
                    credentials={"username": "test", "password": "test"},
                    success_indicators=["welcome"],
                    csrf_config=csrf_config
                )
                
                validator = AuthenticatedValidator(auth_config, "http://localhost:8080")
                
                details = {
                    "config_name": config_name,
                    "enabled": csrf_config.enabled,
                    "auto_include": csrf_config.auto_include,
                    "refresh_on_failure": csrf_config.refresh_on_failure,
                    "pattern_count": len(csrf_config.token_patterns)
                }
                
                duration = time.time() - start_time
                results.append(IntegrationTestResult(
                    test_name=f"csrf_config_{config_name}",
                    success=True,
                    duration=duration,
                    details=details
                ))
                
            except Exception as e:
                duration = time.time() - start_time
                results.append(IntegrationTestResult(
                    test_name=f"csrf_config_{config_name}",
                    success=False,
                    duration=duration,
                    details={"config_name": config_name},
                    error_message=str(e)
                ))
        
        return results
    
    @monitor_performance("validation_preset_test")
    def test_validation_presets(self) -> List[IntegrationTestResult]:
        """Test all available validation presets."""
        results = []
        
        try:
            presets = list_available_presets()
            
            # Create a sample response for testing
            import requests
            from unittest.mock import Mock
            
            mock_response = Mock()
            mock_response.text = """
            <html>
                <body>
                    <script>alert('xss')</script>
                    <div>Welcome to the application</div>
                    <input type="hidden" name="csrf_token" value="abc123">
                    <form action="/login" method="post">
                        <input name="username" type="text">
                        <input name="password" type="password">
                    </form>
                </body>
            </html>
            """
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "text/html"}
            
            for preset in presets:
                start_time = time.time()
                
                try:
                    # Test preset validation
                    from logicpwn.core.validator import validate_with_preset
                    result = validate_with_preset(mock_response, preset)
                    
                    details = {
                        "preset": preset,
                        "is_valid": result.is_valid,
                        "confidence_score": result.confidence_score,
                        "matched_patterns": len(result.matched_patterns),
                        "has_extracted_data": bool(result.extracted_data)
                    }
                    
                    duration = time.time() - start_time
                    results.append(IntegrationTestResult(
                        test_name=f"validation_preset_{preset}",
                        success=True,
                        duration=duration,
                        details=details
                    ))
                    
                except Exception as e:
                    duration = time.time() - start_time
                    results.append(IntegrationTestResult(
                        test_name=f"validation_preset_{preset}",
                        success=False,
                        duration=duration,
                        details={"preset": preset},
                        error_message=str(e)
                    ))
                    
        except Exception as e:
            results.append(IntegrationTestResult(
                test_name="validation_presets_discovery",
                success=False,
                duration=0.0,
                details={},
                error_message=str(e)
            ))
        
        return results
    
    @monitor_performance("performance_monitoring_test")
    def test_performance_monitoring(self) -> IntegrationTestResult:
        """Test performance monitoring functionality."""
        start_time = time.time()
        
        try:
            # Test decorator
            @monitor_performance("test_slow_function")
            def slow_function(delay: float = 0.01):
                time.sleep(delay)
                return "completed"
            
            # Test monitor directly
            monitor = PerformanceMonitor()
            
            # Run tests
            result1 = slow_function(0.01)
            result2 = slow_function(0.02)
            
            details = {
                "decorator_working": result1 == "completed",
                "monitor_instance_created": monitor is not None,
                "multiple_calls_handled": result2 == "completed"
            }
            
            duration = time.time() - start_time
            return IntegrationTestResult(
                test_name="performance_monitoring",
                success=True,
                duration=duration,
                details=details
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return IntegrationTestResult(
                test_name="performance_monitoring",
                success=False,
                duration=duration,
                details={},
                error_message=str(e)
            )
    
    @monitor_performance("dvwa_validator_test")
    def test_dvwa_validator_creation(self) -> IntegrationTestResult:
        """Test DVWA validator creation and configuration."""
        start_time = time.time()
        
        try:
            # Test DVWA validator creation
            dvwa_validator = create_dvwa_validator("http://localhost:8080/DVWA")
            
            details = {
                "auth_url": dvwa_validator.auth_config.url,
                "has_csrf": dvwa_validator.auth_config.csrf_config is not None,
                "ssl_verification": dvwa_validator.auth_config.verify_ssl,
                "has_session_validation": dvwa_validator.auth_config.session_validation_url is not None,
                "timeout": dvwa_validator.auth_config.timeout,
                "credential_count": len(dvwa_validator.auth_config.credentials)
            }
            
            duration = time.time() - start_time
            return IntegrationTestResult(
                test_name="dvwa_validator_creation",
                success=True,
                duration=duration,
                details=details
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return IntegrationTestResult(
                test_name="dvwa_validator_creation",
                success=False,
                duration=duration,
                details={},
                error_message=str(e)
            )
    
    def run_comprehensive_tests(self) -> IntegrationReport:
        """Run comprehensive integration tests."""
        logger.info("Starting comprehensive integration tests")
        
        all_results = []
        total_start_time = time.time()
        
        # Test 1: Auth config validation
        logger.info("Testing authentication configuration validation")
        try:
            auth_config = AuthConfig(
                url="http://localhost:8080/login",
                credentials={"username": "test", "password": "test"},
                success_indicators=["welcome", "dashboard"]
            )
            result = self.validate_auth_config(auth_config)
            all_results.append(result)
        except Exception as e:
            logger.error(f"Auth config test failed: {e}")
        
        # Test 2: CSRF configurations
        logger.info("Testing CSRF configurations")
        try:
            csrf_results = self.test_csrf_configurations()
            all_results.extend(csrf_results)
        except Exception as e:
            logger.error(f"CSRF tests failed: {e}")
        
        # Test 3: Validation presets
        logger.info("Testing validation presets")
        try:
            preset_results = self.test_validation_presets()
            all_results.extend(preset_results)
        except Exception as e:
            logger.error(f"Validation preset tests failed: {e}")
        
        # Test 4: Performance monitoring
        logger.info("Testing performance monitoring")
        try:
            perf_result = self.test_performance_monitoring()
            all_results.append(perf_result)
        except Exception as e:
            logger.error(f"Performance monitoring test failed: {e}")
        
        # Test 5: DVWA validator
        logger.info("Testing DVWA validator creation")
        try:
            dvwa_result = self.test_dvwa_validator_creation()
            all_results.append(dvwa_result)
        except Exception as e:
            logger.error(f"DVWA validator test failed: {e}")
        
        total_duration = time.time() - total_start_time
        
        # Compile report
        successful_tests = sum(1 for r in all_results if r.success)
        failed_tests = len(all_results) - successful_tests
        
        system_info = {
            "total_presets": len(list_available_presets()),
            "test_timestamp": time.time(),
            "python_version": "3.12+",
            "logicpwn_integration_version": "1.0.0"
        }
        
        report = IntegrationReport(
            test_results=all_results,
            total_tests=len(all_results),
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            total_duration=total_duration,
            system_info=system_info
        )
        
        logger.info(f"Integration tests completed: {successful_tests}/{len(all_results)} passed")
        return report
    
    def generate_integration_summary(self, report: IntegrationReport) -> str:
        """Generate a human-readable integration summary."""
        summary = []
        summary.append("=" * 60)
        summary.append("LogicPwn Integration Test Summary")
        summary.append("=" * 60)
        summary.append(f"Total Tests: {report.total_tests}")
        summary.append(f"Successful: {report.successful_tests}")
        summary.append(f"Failed: {report.failed_tests}")
        summary.append(f"Success Rate: {report.get_success_rate():.1f}%")
        summary.append(f"Total Duration: {report.total_duration:.3f}s")
        summary.append("")
        
        summary.append("Test Results:")
        summary.append("-" * 40)
        for result in report.test_results:
            status = "✓" if result.success else "✗"
            summary.append(f"{status} {result.test_name} ({result.duration:.3f}s)")
            if result.error_message:
                summary.append(f"    Error: {result.error_message}")
        
        summary.append("")
        summary.append("System Information:")
        summary.append("-" * 40)
        for key, value in report.system_info.items():
            summary.append(f"{key}: {value}")
        
        summary.append("")
        summary.append("Integration Status: " + ("✅ HEALTHY" if report.get_success_rate() > 80 else "⚠️  NEEDS ATTENTION"))
        summary.append("=" * 60)
        
        return "\n".join(summary)


def main():
    """Main function to run integration enhancement tests."""
    enhancer = IntegrationEnhancer()
    
    print("Starting LogicPwn Integration Enhancement and Validation...")
    
    # Run comprehensive tests
    report = enhancer.run_comprehensive_tests()
    
    # Generate and display summary
    summary = enhancer.generate_integration_summary(report)
    print(summary)
    
    # Save detailed report
    with open("integration_test_report.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: integration_test_report.json")
    
    return report.get_success_rate() > 80


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
