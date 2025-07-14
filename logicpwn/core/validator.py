"""
Response validation module for LogicPwn Business Logic Exploitation Framework.

This module provides HTTP response validation functionality based on logical patterns,
content indicators, and known vulnerability triggers. Designed for exploit chaining,
logic flaw detection, and automation of business logic exploitation workflows.

Key Features:
- Multi-criteria response validation (keywords, regex, status codes, headers)
- Vulnerability pattern detection (SQL injection, XSS, directory traversal)
- Data extraction from responses using regex patterns
- Structured validation results with confidence scoring
- Integration with existing RequestResult and middleware systems
- Comprehensive error handling and secure logging
- Performance optimization with caching capabilities

Usage::

    # Basic response validation for exploit chaining
    result = validate_response(response, success_criteria=["welcome", "authenticated"])
    
    # Advanced validation with multiple criteria
    result = validate_response(
                    response=response,
                    success_criteria=["admin", "privileged"],
                    failure_criteria=["denied", "unauthorized"],
                    regex_patterns=[r"token:\s*([a-zA-Z0-9]+)"],
                    status_codes=[200, 201],
                    return_structured=True
    )
    
    # Extract data from responses
    extracted = extract_from_response(response, r"user_id:\s*(\d+)")
    
    # Vulnerability detection
    vuln_result = validate_response(
                    response=response,
                    regex_patterns=VulnerabilityPatterns.SQL_INJECTION
    )

"""

import re
import json
from typing import Dict, Optional, List, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

import requests
from pydantic import BaseModel, Field, field_validator

from ..models.request_result import RequestResult
from ..exceptions import ValidationError, ResponseError
from .config import get_max_log_body_size, get_redaction_string
from .utils import check_indicators, validate_config
from .performance import monitor_performance, performance_context
from .validator_patterns import VulnerabilityPatterns
from .validator_utils import _sanitize_response_text


# Module constants for maintainability and configuration
MAX_RESPONSE_TEXT_LENGTH = 500
DEFAULT_CONFIDENCE_THRESHOLD = 0.3  # Lowered from 0.5 to be more permissive
CACHE_SIZE = 1000
CACHE_TTL = 300  # 5 minutes


class ValidationType(Enum):
    """Types of validation criteria."""
    SUCCESS_CRITERIA = "success_criteria"
    FAILURE_CRITERIA = "failure_criteria"
    REGEX_PATTERN = "regex_pattern"
    STATUS_CODE = "status_code"
    HEADER_CRITERIA = "header_criteria"
    JSON_PATH = "json_path"


@dataclass
class ValidationResult:
    """Structured result from response validation.
    
    This dataclass provides a comprehensive validation result including
    the validation outcome, matched patterns, extracted data, and
    confidence scoring for exploit chaining workflows.
    """
    is_valid: bool = False
    matched_patterns: List[str] = field(default_factory=list)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_type: Optional[ValidationType] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
                                            """Convert validation result to dictionary."""
                                            return {
                                                "is_valid": self.is_valid,
                                                "matched_patterns": self.matched_patterns,
                                                "extracted_data": self.extracted_data,
                                                "confidence_score": self.confidence_score,
                                                "metadata": self.metadata,
                                                "validation_type": self.validation_type.value if self.validation_type else None,
                                                "error_message": self.error_message
                                            }

    def __str__(self) -> str:
                                            return f"ValidationResult(valid={self.is_valid}, confidence={self.confidence_score:.2f})"


class ValidationConfig(BaseModel):
    """Configuration model for response validation.
    
    This model validates and stores validation configuration parameters
    including success/failure criteria, regex patterns, and other
    validation settings for exploit chaining workflows.
    """
    
    success_criteria: List[str] = Field(default_factory=list, description="Text indicators of successful validation")
    failure_criteria: List[str] = Field(default_factory=list, description="Text indicators of failed validation")
    regex_patterns: List[str] = Field(default_factory=list, description="Regex patterns to match against response content")
    status_codes: List[int] = Field(default_factory=list, description="Acceptable HTTP status codes")
    headers_criteria: Dict[str, str] = Field(default_factory=dict, description="Required headers and their values")
    json_paths: List[str] = Field(default_factory=list, description="JSON path expressions for JSON responses")
    return_structured: bool = Field(default=False, description="Return ValidationResult object instead of boolean")
    confidence_threshold: float = Field(default=DEFAULT_CONFIDENCE_THRESHOLD, ge=0.0, le=1.0, description="Minimum confidence score for validation")
    
    @field_validator('regex_patterns')
    @classmethod
    def validate_regex_patterns(cls, v: List[str]) -> List[str]:
                                            """Validate regex patterns are compilable."""
                                            for pattern in v:
                                                try:
                                                    re.compile(pattern)
                                                except re.error as e:
                                                    raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
                                            return v
    
    @field_validator('status_codes')
    @classmethod
    def validate_status_codes(cls, v: List[int]) -> List[int]:
                                            """Validate HTTP status codes are in valid range."""
                                            for code in v:
                                                if not (100 <= code <= 599):
                                                    raise ValueError(f"Invalid HTTP status code: {code}")
                                            return v


def validate_validation_config(config: Union[dict, ValidationConfig]) -> ValidationConfig:
    """
    Validate and convert a configuration dict or ValidationConfig instance to a ValidationConfig instance.
    This is a wrapper around the generic validate_config function specifically for ValidationConfig.
    
    Args:
                                            config: dict or ValidationConfig instance
    Returns:
                                            Validated ValidationConfig instance
    Raises:
                                            LogicPwnValidationError: if config is not valid
    """
    try:
                                            return validate_config(config, ValidationConfig)
    except (ValueError, Exception) as e:
                                                # Try to catch pydantic ValidationError as well
                                            from pydantic import ValidationError as PydanticValidationError
                                            if isinstance(e, PydanticValidationError):
                                                raise ValidationError(str(e))
                                            raise ValidationError(str(e))


def _check_regex_patterns(response_text: str, patterns: List[str]) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Check if response matches regex patterns.
    
    This function performs regex pattern matching against response content
    and extracts matching groups for data extraction.
    
    Args:
                                            response_text: Response text to check
                                            patterns: List of regex patterns to match
                                            
    Returns:
                                            Tuple of (has_matches, matched_patterns, extracted_data)
    """
    if not patterns:
                                            return False, [], {}
    
    matched_patterns = []
    extracted_data = {}
    group_counter = 1
    
    for pattern in patterns:
                                            try:
                                                matches = list(re.finditer(pattern, response_text, re.IGNORECASE | re.MULTILINE))
                                                if matches:
                                                    matched_patterns.append(pattern)
                                                    
                                                    # Only process the first match of each pattern
                                                    match = matches[0]
                                                    
                                                    # Extract named groups if present
                                                    if match.groupdict():
                                                        for name, value in match.groupdict().items():
                                                            if value:
                                                                extracted_data[name] = value
                                                    
                                                    # Extract numbered groups (only for the first match of each pattern)
                                                    for i, group in enumerate(match.groups(), 1):
                                                        if group:
                                                            extracted_data[f"group_{group_counter}"] = group
                                                            group_counter += 1
                                                    
                                                    logger.debug(f"Regex pattern matched: {pattern}")
                                                    
                                            except re.error as e:
                                                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                                                continue
    
    return len(matched_patterns) > 0, matched_patterns, extracted_data


def _check_status_codes(response: requests.Response, status_codes: List[int]) -> bool:
    """Check if response status code is in acceptable range.
    
    Args:
                                            response: HTTP response object
                                            status_codes: List of acceptable status codes
                                            
    Returns:
                                            True if status code is acceptable, False otherwise
    """
    if not status_codes:
                                            return True  # No criteria specified means all codes are acceptable
    
    return response.status_code in status_codes


def _check_headers_criteria(response: requests.Response, headers_criteria: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Check if response headers meet specified criteria.
    
    Args:
                                            response: HTTP response object
                                            headers_criteria: Dictionary of header names and expected values
                                            
    Returns:
                                            Tuple of (criteria_met, matched_headers)
    """
    if not headers_criteria:
                                            return True, []
    
    matched_headers = []
    response_headers = {k.lower(): v for k, v in response.headers.items()}
    
    for header_name, expected_value in headers_criteria.items():
                                            header_lower = header_name.lower()
                                            if header_lower in response_headers:
                                                actual_value = response_headers[header_lower]
                                                if expected_value.lower() in actual_value.lower():
                                                    matched_headers.append(f"{header_name}: {actual_value}")
                                                    logger.debug(f"Header criteria matched: {header_name}")
    
    return len(matched_headers) == len(headers_criteria), matched_headers


def _calculate_confidence_score(
    success_matches: List[str],
    failure_matches: List[str],
    regex_matches: List[str],
    status_match: bool,
    headers_match: bool
) -> float:
    """Calculate confidence score for validation result.
    
    This function computes a confidence score based on the number and
    type of criteria that were matched during validation.
    
    Args:
                                            success_matches: List of matched success criteria
                                            failure_matches: List of matched failure criteria
                                            regex_matches: List of matched regex patterns
                                            status_match: Whether status code criteria were met
                                            headers_match: Whether header criteria were met
                                            
    Returns:
                                            Confidence score between 0.0 and 1.0
    """
    # Base score from different criteria types
    score = 0.0
    
    # Success criteria contribute positively
    if success_matches:
                                            score += min(len(success_matches) * 0.2, 0.4)
    
    # Failure criteria contribute negatively
    if failure_matches:
                                            score -= min(len(failure_matches) * 0.3, 0.6)
    
    # Regex matches contribute significantly
    if regex_matches:
                                            score += min(len(regex_matches) * 0.25, 0.5)
    
    # Status code match contributes moderately
    if status_match:
                                            score += 0.2
    
    # Header match contributes moderately
    if headers_match:
                                            score += 0.2
    
    # Ensure score is within bounds
    return max(0.0, min(1.0, score))


@monitor_performance("response_validation")
def validate_response(
    response: requests.Response,
    success_criteria: Optional[List[str]] = None,
    failure_criteria: Optional[List[str]] = None,
    regex_patterns: Optional[List[str]] = None,
    status_codes: Optional[List[int]] = None,
    headers_criteria: Optional[Dict[str, str]] = None,
    json_paths: Optional[List[str]] = None,
    return_structured: bool = False,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
) -> Union[bool, ValidationResult]:
    """
    Validates a response based on multiple criteria types.
    
    This function performs comprehensive response validation using various
    criteria including text matching, regex patterns, status codes, and
    headers. It's designed for exploit chaining and security testing workflows.
    
    Args:
                                            response: The response object to analyze
                                            success_criteria: Substrings that suggest successful validation
                                            failure_criteria: Substrings that suggest failed validation
                                            regex_patterns: Regex patterns to match against response content
                                            status_codes: Acceptable HTTP status codes
                                            headers_criteria: Required headers and their values
                                            json_paths: JSON path expressions for JSON responses (future feature)
                                            return_structured: Return ValidationResult object instead of boolean
                                            confidence_threshold: Minimum confidence score for validation
                                            
    Returns:
                                            Union[bool, ValidationResult]: Validation result
                                            
    Raises:
                                            ValidationError: If validation configuration is invalid
                                            ResponseError: If response cannot be processed
                                            
    Examples:::
                        # Basic validation
                    is_valid = validate_response(response, success_criteria=["welcome"])
                    
                        # Advanced validation with structured result
                    result = validate_response(
                        response=response,
                        success_criteria=["admin", "privileged"],
                        regex_patterns=[r"user_id:(\d+)"],
                        status_codes=[200, 201],
                        return_structured=True
                    )
                    
                    if result.is_valid and result.confidence_score > 0.8:
                        user_id = result.extracted_data.get("group_1")
    """
    try:
                                                # Validate configuration
                                            config_dict = {
                                                "success_criteria": success_criteria or [],
                                                "failure_criteria": failure_criteria or [],
                                                "regex_patterns": regex_patterns or [],
                                                "status_codes": status_codes or [],
                                                "headers_criteria": headers_criteria or {},
                                                "json_paths": json_paths or [],
                                                "return_structured": return_structured,
                                                "confidence_threshold": confidence_threshold
                                            }
                                            
                                            config = validate_validation_config(config_dict)
                                            
                                                # Get response text safely
                                            try:
                                                response_text = response.text
                                            except Exception as e:
                                                logger.error(f"Failed to read response text: {e}")
                                                response_text = ""
                                            
                                                # Sanitize for logging
                                            safe_text = _sanitize_response_text(response_text)
                                            logger.debug(f"Validating response: status={response.status_code}, size={len(response_text)}")
                                            
                                                # Perform validation checks
                                            success_match, success_matches = check_indicators(response_text, config.success_criteria, "success")
                                            failure_match, failure_matches = check_indicators(response_text, config.failure_criteria, "failure")
                                            regex_match, regex_matches, extracted_data = _check_regex_patterns(response_text, config.regex_patterns)
                                            status_match = _check_status_codes(response, config.status_codes)
                                            headers_match, header_matches = _check_headers_criteria(response, config.headers_criteria)
                                            
                                                # Determine overall validation result
                                            is_valid = (
                                                (not config.success_criteria or success_match) and
                                                (not config.failure_criteria or not failure_match) and
                                                (not config.status_codes or status_match) and
                                                (not config.headers_criteria or headers_match)
                                            )
                                            
                                                # Calculate confidence score
                                            confidence_score = _calculate_confidence_score(
                                                success_matches, failure_matches, regex_matches, status_match, headers_match
                                            )
                                            
                                                # Apply confidence threshold
                                            if confidence_score < config.confidence_threshold:
                                                is_valid = False
                                                logger.debug(f"Validation failed due to low confidence: {confidence_score:.2f} < {config.confidence_threshold}")
                                            
                                                # Prepare metadata
                                            metadata = {
                                                "response_status": response.status_code,
                                                "response_size": len(response_text),
                                                "headers_count": len(response.headers),
                                                "validation_criteria_count": (
                                                    len(config.success_criteria) + len(config.failure_criteria) + 
                                                    len(config.regex_patterns) + len(config.status_codes) + 
                                                    len(config.headers_criteria)
                                                )
                                            }
                                            
                                                # Create result
                                            result = ValidationResult(
                                                is_valid=is_valid,
                                                matched_patterns=success_matches + failure_matches + regex_matches + header_matches,
                                                extracted_data=extracted_data,
                                                confidence_score=confidence_score,
                                                metadata=metadata
                                            )
                                            
                                            if return_structured:
                                                return result
                                            else:
                                                return is_valid
                                                
    except Exception as e:
                                            logger.error(f"Validation error: {e}")
                                            if return_structured:
                                                return ValidationResult(
                                                    is_valid=False,
                                                    error_message=str(e),
                                                    confidence_score=0.0
                                                )
                                            else:
                                                return False


def extract_from_response(
    response: requests.Response,
    regex: str,
    group_names: Optional[List[str]] = None,
    extract_all: bool = False
) -> Union[List[str], Dict[str, str]]:
    """
    Extract matching data from response using regex patterns.

    This function extracts data from HTTP responses using regex patterns
    with optional named groups for structured data extraction.

    Args:
                                            response: Response to extract from
                                            regex: Regex pattern with optional named groups
                                            group_names: Names of regex groups to extract
                                            extract_all: Extract all matches vs first match only

    Returns:
                                            Union[List[str], Dict[str, str]]: Extracted data

    Raises:
                                            ValidationError: If regex pattern is invalid
                                            ResponseError: If response cannot be processed

    Examples:
                    Extract user ID::

                        user_ids = extract_from_response(response, r"user_id:(\d+)")

                    Extract with named groups::

                        data = extract_from_response(
                            response,
                            r"user_id:(?P<id>\d+).*name:(?P<name>\w+)",
                            group_names=["id", "name"]
                        )
    """
    # Validate regex pattern first
    try:
                                            compiled_regex = re.compile(regex, re.IGNORECASE | re.MULTILINE)
    except re.error as e:
                                            raise ValidationError(
                                                message=f"Invalid regex pattern: {e}",
                                                field="regex",
                                                value=regex
                                            )
    
    # Get response text safely
    try:
                                            response_text = response.text
                                                # Handle Mock objects that might not have proper text attribute
                                            if hasattr(response_text, '__call__'):
                                                response_text = response_text()
                                            if not isinstance(response_text, str):
                                                response_text = str(response_text) if response_text else ""
    except Exception as e:
                                            logger.error(f"Failed to read response text: {e}")
                                            return [] if not group_names else {}
    
    # Find matches
    matches = list(compiled_regex.finditer(response_text))
    
    if not matches:
                                            logger.debug(f"No matches found for regex pattern: {regex}")
                                            return [] if not group_names else {}
    
    # Extract data based on configuration
    if group_names:
                                                # Return dictionary with named groups
                                            result = {}
                                            for match in matches:
                                                for group_name in group_names:
                                                    if group_name in match.groupdict():
                                                        value = match.group(group_name)
                                                        if value:
                                                            if group_name not in result:
                                                                result[group_name] = []
                                                            result[group_name].append(value)
                                            
                                                # Convert single values to strings if extract_all is False
                                            if not extract_all:
                                                result = {k: v[0] if v else "" for k, v in result.items()}
                                            
                                            return result
    else:
                                                # Return list of matched strings
                                            if extract_all:
                                                return [match.group(0) for match in matches]
                                            else:
                                                return [matches[0].group(0)] if matches else []


def validate_json_response(
    response: requests.Response,
    json_schema: Optional[Dict] = None,
    required_keys: Optional[List[str]] = None,
    forbidden_keys: Optional[List[str]] = None
) -> ValidationResult:
    """
    Validate JSON response structure and content.
    
    This function validates JSON responses against schemas, required keys,
    and forbidden keys for security testing and data validation.
    
    Args:
                                            response: HTTP response object
                                            json_schema: JSON schema for validation (future feature)
                                            required_keys: Keys that must be present in JSON response
                                            forbidden_keys: Keys that must not be present in JSON response
                                            
    Returns:
                                            ValidationResult: Validation result with extracted data
    """
    try:
                                                # Check if response is JSON
                                            content_type = response.headers.get("content-type", "").lower()
                                            if "json" not in content_type:
                                                return ValidationResult(
                                                    is_valid=False,
                                                    error_message="Response is not JSON",
                                                    confidence_score=0.0
                                                )
                                            
                                                # Parse JSON
                                            try:
                                                json_data = response.json()
                                            except json.JSONDecodeError as e:
                                                return ValidationResult(
                                                    is_valid=False,
                                                    error_message=f"Invalid JSON: {e}",
                                                    confidence_score=0.0
                                                )
                                            
                                                # Validate required keys
                                            missing_keys = []
                                            if required_keys:
                                                for key in required_keys:
                                                    if key not in json_data:
                                                        missing_keys.append(key)
                                            
                                                # Check forbidden keys
                                            found_forbidden_keys = []
                                            if forbidden_keys:
                                                for key in forbidden_keys:
                                                    if key in json_data:
                                                        found_forbidden_keys.append(key)
                                            
                                                # Determine validation result
                                            is_valid = len(missing_keys) == 0 and len(found_forbidden_keys) == 0
                                            confidence_score = 1.0 if is_valid else 0.0
                                            
                                                # Prepare metadata
                                            metadata = {
                                                "json_keys_count": len(json_data) if isinstance(json_data, dict) else 0,
                                                "missing_keys": missing_keys,
                                                "forbidden_keys_found": found_forbidden_keys
                                            }
                                            
                                            return ValidationResult(
                                                is_valid=is_valid,
                                                extracted_data={"json_data": json_data},
                                                confidence_score=confidence_score,
                                                metadata=metadata,
                                                validation_type=ValidationType.JSON_PATH
                                            )
                                            
    except Exception as e:
                                            logger.error(f"JSON validation error: {e}")
                                            return ValidationResult(
                                                is_valid=False,
                                                error_message=str(e),
                                                confidence_score=0.0
                                            )


def validate_html_response(
    response: requests.Response,
    css_selectors: Optional[List[str]] = None,
    xpath_expressions: Optional[List[str]] = None,
    title_patterns: Optional[List[str]] = None
) -> ValidationResult:
    """
    Validate HTML response using CSS selectors and XPath.
    
    This function validates HTML responses using various selectors
    and patterns for content analysis and security testing.
    
    Args:
                                            response: HTTP response object
                                            css_selectors: CSS selectors to validate
                                            xpath_expressions: XPath expressions to validate
                                            title_patterns: Title patterns to validate
                                            
    Returns:
                                            ValidationResult: Validation result with extracted data
    """
    try:
                                                # Check if response is HTML
                                            content_type = response.headers.get("content-type", "").lower()
                                            if "html" not in content_type:
                                                return ValidationResult(
                                                    is_valid=False,
                                                    error_message="Response is not HTML",
                                                    confidence_score=0.0
                                                )
                                            
                                                # Get response text
                                            try:
                                                html_text = response.text
                                            except Exception as e:
                                                logger.error(f"Failed to read HTML response: {e}")
                                                return ValidationResult(
                                                    is_valid=False,
                                                    error_message=f"Failed to read response: {e}",
                                                    confidence_score=0.0
                                                )
                                            
                                                # Basic HTML validation (without external dependencies)
                                            validation_results = []
                                            extracted_data = {}
                                            
                                                # Check title patterns
                                            if title_patterns:
                                                title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
                                                if title_match:
                                                    title_text = title_match.group(1).strip()
                                                    for pattern in title_patterns:
                                                        if pattern.lower() in title_text.lower():
                                                            validation_results.append(f"title_pattern: {pattern}")
                                                            extracted_data["title"] = title_text
                                                            break
                                            
                                                # Check for basic HTML structure
                                            if "<html" in html_text.lower():
                                                validation_results.append("html_structure")
                                            
                                                # Calculate confidence
                                            confidence_score = min(len(validation_results) * 0.3, 1.0)
                                            is_valid = len(validation_results) > 0
                                            
                                            return ValidationResult(
                                                is_valid=is_valid,
                                                matched_patterns=validation_results,
                                                extracted_data=extracted_data,
                                                confidence_score=confidence_score,
                                                metadata={"html_size": len(html_text)},
                                                validation_type=ValidationType.REGEX_PATTERN
                                            )
                                            
    except Exception as e:
                                            logger.error(f"HTML validation error: {e}")
                                            return ValidationResult(
                                                is_valid=False,
                                                error_message=str(e),
                                                confidence_score=0.0
                                            )


def chain_validations(
    response: requests.Response,
    validation_chain: List[Dict[str, Any]]
) -> List[ValidationResult]:
    """
    Execute a chain of validations with conditional logic.

    This function executes multiple validation steps in sequence,
    allowing for complex validation workflows and exploit chaining.

    Args:
                                            response: Response to validate
                                            validation_chain: List of validation configurations

    Returns:
                                            List[ValidationResult]: Results for each validation step

    Examples::

                                            chain = [
                                                {"success_criteria": ["welcome"], "return_structured": True},
                                                {"regex_patterns": [r"user_id:\s*(\d+)"], "return_structured": True},
                                                {"status_codes": [200, 201], "return_structured": True}
                                            ]

                                            results = chain_validations(response, chain)
                                            for i, result in enumerate(results):
                                                print(f"Step {i+1}: {result.is_valid}")
    """
    results = []
    
    for i, validation_config in enumerate(validation_chain):
                                            try:
                                                logger.debug(f"Executing validation step {i+1}/{len(validation_chain)}")
                                                
                                                # Ensure structured result for chaining
                                                validation_config["return_structured"] = True
                                                
                                                result = validate_response(response, **validation_config)
                                                results.append(result)
                                                
                                                # Log step result
                                                if result.is_valid:
                                                    logger.debug(f"Validation step {i+1} passed")
                                                else:
                                                    logger.debug(f"Validation step {i+1} failed")
                                                    
                                            except Exception as e:
                                                logger.error(f"Validation step {i+1} error: {e}")
                                                results.append(ValidationResult(
                                                    is_valid=False,
                                                    error_message=str(e),
                                                    confidence_score=0.0
                                                ))
    
    return results 