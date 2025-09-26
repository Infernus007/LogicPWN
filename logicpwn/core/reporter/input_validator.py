"""
Comprehensive input validation for the reporter module.
Provides security-focused validation for all user inputs to prevent injection attacks.
"""

import logging
import re
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error for input validation failures."""


class SeverityLevel(str, Enum):
    """Valid severity levels for vulnerability findings."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


class ReportFormat(str, Enum):
    """Valid report output formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PDF = "pdf"
    XML = "xml"


class InputSanitizer:
    """Sanitizes and validates user inputs for security."""

    # Dangerous patterns that should be rejected
    DANGEROUS_PATTERNS = {
        "sql_injection": [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\balter\b.*\btable\b)",
            r"(--|\#|\/\*)",
            r"(\bor\b.*=.*\bor\b)",
            r"(\band\b.*=.*\band\b)",
        ],
        "xss": [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"vbscript:",
            r"data:text/html",
        ],
        "command_injection": [
            r"(\||&|;|\$\(|\`)",
            r"(rm\s|del\s|format\s)",
            r"(nc\s|netcat\s|telnet\s)",
            r"(wget\s|curl\s|fetch\s)",
            r"(python\s|perl\s|ruby\s|php\s)",
            r"(bash\s|sh\s|cmd\s|powershell\s)",
        ],
        "path_traversal": [
            r"\.\.\/+",
            r"\.\.\\+",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"/etc/passwd",
            r"/etc/shadow",
            r"/proc/self/",
            r"C:\\Windows\\",
        ],
        "template_injection": [
            r"\{\{.*\}\}",
            r"\{%.*%\}",
            r"\$\{.*\}",
            r"<%.*%>",
            r"#\{.*\}",
        ],
    }

    # Maximum lengths for different input types
    MAX_LENGTHS = {
        "title": 500,
        "description": 10000,
        "url": 2048,
        "filename": 255,
        "username": 100,
        "email": 320,
        "generic_text": 5000,
        "id": 100,
        "name": 255,
    }

    # Allowed characters for different input types
    ALLOWED_PATTERNS = {
        "alphanumeric": r"^[a-zA-Z0-9_-]+$",
        "alphanumeric_space": r"^[a-zA-Z0-9\s_.-]+$",
        "filename": r"^[a-zA-Z0-9\s._-]+$",
        "id": r"^[a-zA-Z0-9_-]+$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "url": r"^https?://[a-zA-Z0-9.-]+(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?$",
        "version": r"^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9]+)?$",
    }

    @staticmethod
    def is_safe_string(value: str, check_patterns: Optional[list[str]] = None) -> bool:
        """Check if a string is safe from injection attacks."""
        if not isinstance(value, str):
            return False

        # Check against dangerous patterns
        patterns_to_check = check_patterns or [
            "sql_injection",
            "xss",
            "command_injection",
            "template_injection",
        ]

        for pattern_type in patterns_to_check:
            if pattern_type in InputSanitizer.DANGEROUS_PATTERNS:
                for pattern in InputSanitizer.DANGEROUS_PATTERNS[pattern_type]:
                    if re.search(pattern, value, re.IGNORECASE):
                        logger.warning(
                            f"Dangerous pattern detected: {pattern_type} in input: {value[:100]}..."
                        )
                        return False

        return True

    @staticmethod
    def sanitize_string(
        value: str,
        max_length: Optional[int] = None,
        allowed_pattern: Optional[str] = None,
    ) -> str:
        """Sanitize a string input by removing/escaping dangerous content."""
        if not isinstance(value, str):
            raise ValidationError(f"Expected string, got {type(value)}")

        # Check length
        if max_length and len(value) > max_length:
            raise ValidationError(f"Input too long: {len(value)} > {max_length}")

        # Check safety
        if not InputSanitizer.is_safe_string(value):
            raise ValidationError("Input contains potentially dangerous patterns")

        # Check allowed pattern
        if allowed_pattern and allowed_pattern in InputSanitizer.ALLOWED_PATTERNS:
            pattern = InputSanitizer.ALLOWED_PATTERNS[allowed_pattern]
            if not re.match(pattern, value):
                raise ValidationError(
                    f"Input does not match required pattern: {allowed_pattern}"
                )

        # Basic sanitization
        sanitized = value.strip()

        # Remove null bytes and control characters
        sanitized = "".join(
            char for char in sanitized if ord(char) >= 32 or char in "\t\n\r"
        )

        return sanitized

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate and sanitize URL input."""
        if not isinstance(url, str):
            raise ValidationError(f"URL must be string, got {type(url)}")

        if len(url) > InputSanitizer.MAX_LENGTHS["url"]:
            raise ValidationError(f"URL too long: {len(url)}")

        # Parse URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError("Invalid URL format")

            # Only allow http/https
            if parsed.scheme not in ["http", "https"]:
                raise ValidationError(f"Invalid URL scheme: {parsed.scheme}")

            # Check for dangerous patterns in URL
            if not InputSanitizer.is_safe_string(url, ["xss", "command_injection"]):
                raise ValidationError("URL contains dangerous patterns")

        except Exception as e:
            raise ValidationError(f"URL validation failed: {str(e)}")

        return url.strip()

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address."""
        if not isinstance(email, str):
            raise ValidationError(f"Email must be string, got {type(email)}")

        email = email.strip().lower()

        if len(email) > InputSanitizer.MAX_LENGTHS["email"]:
            raise ValidationError(f"Email too long: {len(email)}")

        pattern = InputSanitizer.ALLOWED_PATTERNS["email"]
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")

        return email

    @staticmethod
    def validate_severity(severity: str) -> str:
        """Validate severity level."""
        if not isinstance(severity, str):
            raise ValidationError(f"Severity must be string, got {type(severity)}")

        try:
            validated = SeverityLevel(severity.title())
            return validated.value
        except ValueError:
            valid_levels = [level.value for level in SeverityLevel]
            raise ValidationError(
                f"Invalid severity level: {severity}. Must be one of: {valid_levels}"
            )


class ValidatedInput(BaseModel):
    """Base model for validated inputs with security constraints."""

    model_config = ConfigDict(
        validate_assignment=True, str_strip_whitespace=True, str_max_length=10000
    )


class VulnerabilityInput(ValidatedInput):
    """Validated input for vulnerability findings."""

    id: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    title: str = Field(..., min_length=1, max_length=500)
    severity: str = Field(...)
    description: str = Field(..., min_length=1, max_length=10000)
    affected_endpoints: list[str] = Field(default_factory=list, max_length=100)
    proof_of_concept: str = Field(default="", max_length=10000)
    impact: str = Field(default="", max_length=5000)
    remediation: str = Field(default="", max_length=5000)
    references: list[str] = Field(default_factory=list)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        return InputSanitizer.validate_severity(v)

    @field_validator(
        "title", "description", "impact", "remediation", "proof_of_concept"
    )
    @classmethod
    def validate_text_fields(cls, v):
        if not InputSanitizer.is_safe_string(v):
            raise ValueError("Text contains potentially dangerous patterns")
        return v

    @field_validator("affected_endpoints")
    @classmethod
    def validate_endpoints(cls, v):
        validated_endpoints = []
        for endpoint in v:
            try:
                validated_url = InputSanitizer.validate_url(endpoint)
                validated_endpoints.append(validated_url)
            except ValidationError:
                logger.warning(f"Skipping invalid endpoint: {endpoint}")
        return validated_endpoints

    @field_validator("references")
    @classmethod
    def validate_references(cls, v):
        validated_refs = []
        for ref in v:
            if isinstance(ref, str) and InputSanitizer.is_safe_string(ref):
                if len(ref) <= 2048:  # Max URL length
                    validated_refs.append(ref.strip())
        return validated_refs


class ReportConfigInput(ValidatedInput):
    """Validated input for report configuration."""

    target_url: str = Field(...)
    report_title: str = Field(..., min_length=1, max_length=500)
    report_type: str = Field(default="vapt", pattern=r"^[a-zA-Z0-9_-]+$")
    format_style: str = Field(default="professional", pattern=r"^[a-zA-Z0-9_-]+$")
    authenticated_user: Optional[str] = Field(None, max_length=100)

    @field_validator("target_url")
    @classmethod
    def validate_target_url(cls, v):
        return InputSanitizer.validate_url(v)

    @field_validator("report_title")
    @classmethod
    def validate_title(cls, v):
        if not InputSanitizer.is_safe_string(v):
            raise ValueError("Title contains potentially dangerous patterns")
        return v

    @field_validator("authenticated_user")
    @classmethod
    def validate_user(cls, v):
        if v is None:
            return v
        if not InputSanitizer.is_safe_string(v, ["xss", "command_injection"]):
            raise ValueError("Username contains potentially dangerous patterns")
        return v


class InputValidator:
    """Main input validator for the reporter module."""

    @staticmethod
    def validate_vulnerability_finding(data: dict[str, Any]) -> VulnerabilityInput:
        """Validate vulnerability finding input data."""
        try:
            return VulnerabilityInput(**data)
        except Exception as e:
            logger.error(f"Vulnerability finding validation failed: {e}")
            raise ValidationError(f"Invalid vulnerability finding data: {str(e)}")

    @staticmethod
    def validate_report_config(data: dict[str, Any]) -> ReportConfigInput:
        """Validate report configuration input data."""
        try:
            return ReportConfigInput(**data)
        except Exception as e:
            logger.error(f"Report configuration validation failed: {e}")
            raise ValidationError(f"Invalid report configuration data: {str(e)}")

    @staticmethod
    def validate_file_path(file_path: str) -> str:
        """Validate file path for security."""
        if not isinstance(file_path, str):
            raise ValidationError(f"File path must be string, got {type(file_path)}")

        # Check for path traversal
        if not InputSanitizer.is_safe_string(file_path, ["path_traversal"]):
            raise ValidationError("File path contains dangerous patterns")

        # Normalize and validate
        normalized = file_path.strip()

        # Check length
        if (
            len(normalized) > InputSanitizer.MAX_LENGTHS["filename"] * 3
        ):  # Allow for paths
            raise ValidationError("File path too long")

        # Basic filename validation
        import os

        basename = os.path.basename(normalized)
        if not re.match(InputSanitizer.ALLOWED_PATTERNS["filename"], basename):
            raise ValidationError("Invalid filename characters")

        return normalized

    @staticmethod
    def validate_template_content(content: str) -> str:
        """Validate template content for security."""
        if not isinstance(content, str):
            raise ValidationError(
                f"Template content must be string, got {type(content)}"
            )

        # Check for template injection patterns
        if not InputSanitizer.is_safe_string(content, ["template_injection", "xss"]):
            raise ValidationError("Template content contains dangerous patterns")

        # Check length
        if len(content) > 100000:  # 100KB limit
            raise ValidationError("Template content too large")

        return content

    @staticmethod
    def sanitize_dict_values(
        data: dict[str, Any], max_depth: int = 3
    ) -> dict[str, Any]:
        """Recursively sanitize dictionary values."""
        if max_depth <= 0:
            return {}

        sanitized = {}
        for key, value in data.items():
            try:
                # Validate key
                safe_key = InputSanitizer.sanitize_string(
                    str(key), max_length=100, allowed_pattern="alphanumeric"
                )

                # Sanitize value based on type
                if isinstance(value, str):
                    if InputSanitizer.is_safe_string(value):
                        sanitized[safe_key] = InputSanitizer.sanitize_string(
                            value, max_length=5000
                        )
                elif isinstance(value, (int, float, bool)):
                    sanitized[safe_key] = value
                elif isinstance(value, dict):
                    sanitized[safe_key] = InputValidator.sanitize_dict_values(
                        value, max_depth - 1
                    )
                elif isinstance(value, list):
                    sanitized_list = []
                    for item in value[:50]:  # Limit list size
                        if isinstance(item, str) and InputSanitizer.is_safe_string(
                            item
                        ):
                            sanitized_list.append(
                                InputSanitizer.sanitize_string(item, max_length=1000)
                            )
                        elif isinstance(item, (int, float, bool)):
                            sanitized_list.append(item)
                    sanitized[safe_key] = sanitized_list
                else:
                    logger.warning(f"Skipping unsupported value type: {type(value)}")

            except ValidationError as e:
                logger.warning(
                    f"Skipping invalid key-value pair: {key} = {value} ({e})"
                )
                continue

        return sanitized

    @staticmethod
    def validate_report_format(format_type: str) -> str:
        """Validate report format."""
        if not isinstance(format_type, str):
            raise ValidationError(f"Format must be string, got {type(format_type)}")

        try:
            validated = ReportFormat(format_type.lower())
            return validated.value
        except ValueError:
            valid_formats = [fmt.value for fmt in ReportFormat]
            raise ValidationError(
                f"Invalid format: {format_type}. Must be one of: {valid_formats}"
            )
