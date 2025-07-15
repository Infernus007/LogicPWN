"""
Validation presets for common security testing scenarios.
This module provides pre-configured validation rules for typical exploit detection,
making it easier for users to validate responses without manual configuration.
"""
from typing import Dict, List, Any
from .validator_models import ValidationConfig
from .validator_patterns import VulnerabilityPatterns


class ValidationPresets:
    """Pre-configured validation profiles for common security testing scenarios."""
    
    @staticmethod
    def sql_injection_detection() -> ValidationConfig:
        """Validation preset for SQL injection vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "mysql_fetch_array",
                "mysql_num_rows",
                "ORA-",
                "Microsoft JET Database",
                "ODBC SQL Server",
                "SQLite/JDBCDriver",
                "PostgreSQL query failed"
            ],
            regex_patterns=VulnerabilityPatterns.SQL_INJECTION,
            status_codes=[500],  # Internal server errors often indicate SQL errors
            confidence_threshold=0.4
        )
    
    @staticmethod
    def xss_detection() -> ValidationConfig:
        """Validation preset for Cross-Site Scripting (XSS) vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "<script>",
                "javascript:",
                "onerror=",
                "onload=",
                "onclick="
            ],
            regex_patterns=VulnerabilityPatterns.XSS_INDICATORS,
            confidence_threshold=0.3
        )
    
    @staticmethod
    def directory_traversal_detection() -> ValidationConfig:
        """Validation preset for directory traversal vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "root:x:0:0:",
                "[boot loader]",
                "../",
                "..\\",
                "/etc/passwd",
                "C:\\Windows\\"
            ],
            regex_patterns=VulnerabilityPatterns.DIRECTORY_TRAVERSAL,
            confidence_threshold=0.5
        )
    
    @staticmethod
    def authentication_bypass() -> ValidationConfig:
        """Validation preset for authentication bypass detection."""
        return ValidationConfig(
            success_criteria=[
                "admin panel",
                "administrator",
                "privileged access",
                "dashboard",
                "control panel"
            ],
            failure_criteria=[
                "access denied",
                "unauthorized",
                "login required",
                "authentication failed"
            ],
            status_codes=[200, 302],
            confidence_threshold=0.6
        )
    
    @staticmethod
    def information_disclosure() -> ValidationConfig:
        """Validation preset for information disclosure detection."""
        return ValidationConfig(
            failure_criteria=[
                "stack trace",
                "debug information",
                "internal error",
                "version",
                "build number",
                "database error",
                "exception",
                "traceback"
            ],
            regex_patterns=VulnerabilityPatterns.INFO_DISCLOSURE,
            confidence_threshold=0.3
        )
    
    @staticmethod
    def api_success_validation() -> ValidationConfig:
        """Validation preset for successful API responses."""
        return ValidationConfig(
            success_criteria=[
                "success",
                "ok",
                "completed",
                "accepted"
            ],
            status_codes=[200, 201, 202, 204],
            headers_criteria={"content-type": "application/json"},
            confidence_threshold=0.4
        )
    
    @staticmethod
    def login_success_validation() -> ValidationConfig:
        """Validation preset for successful login attempts."""
        return ValidationConfig(
            success_criteria=[
                "welcome",
                "dashboard",
                "logged in",
                "authentication successful",
                "login successful"
            ],
            status_codes=[200, 302],
            headers_criteria={"set-cookie": "session"},
            confidence_threshold=0.5
        )
    
    @staticmethod
    def error_page_detection() -> ValidationConfig:
        """Validation preset for error page detection."""
        return ValidationConfig(
            failure_criteria=[
                "404",
                "not found",
                "page not found",
                "error",
                "exception",
                "internal server error"
            ],
            status_codes=[404, 500, 503],
            confidence_threshold=0.3
        )
    
    @staticmethod
    def custom_preset(
        success_patterns: List[str] = None,
        failure_patterns: List[str] = None,
        status_codes: List[int] = None,
        confidence_threshold: float = 0.3
    ) -> ValidationConfig:
        """Create a custom validation preset with specified parameters."""
        return ValidationConfig(
            success_criteria=success_patterns or [],
            failure_criteria=failure_patterns or [],
            status_codes=status_codes or [],
            confidence_threshold=confidence_threshold
        )


# Convenience dictionary for easy access to presets
VALIDATION_PRESETS = {
    'sql_injection': ValidationPresets.sql_injection_detection,
    'xss': ValidationPresets.xss_detection,
    'directory_traversal': ValidationPresets.directory_traversal_detection,
    'auth_bypass': ValidationPresets.authentication_bypass,
    'info_disclosure': ValidationPresets.information_disclosure,
    'api_success': ValidationPresets.api_success_validation,
    'login_success': ValidationPresets.login_success_validation,
    'error_page': ValidationPresets.error_page_detection
}


def get_preset(preset_name: str) -> ValidationConfig:
    """
    Get a validation preset by name.
    
    Args:
        preset_name: Name of the preset to retrieve
        
    Returns:
        ValidationConfig object for the specified preset
        
    Raises:
        ValueError: If preset name is not found
    """
    if preset_name not in VALIDATION_PRESETS:
        available = ', '.join(VALIDATION_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available presets: {available}")
    
    return VALIDATION_PRESETS[preset_name]()
