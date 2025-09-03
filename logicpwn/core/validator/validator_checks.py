"""
Validation check helpers for LogicPwn response validation.
"""

import re
from functools import lru_cache
from typing import Any, Optional

import requests

from .regex_security import safe_regex_findall, validate_regex_pattern
from .response_handler import process_response_safely


# Cache for compiled regex patterns to improve performance
@lru_cache(maxsize=256)
def _compile_regex(pattern: str) -> re.Pattern:
    """Compile and cache regex patterns for performance."""
    try:
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    except re.error:
        # Return a pattern that matches nothing for invalid regex
        return re.compile(r"(?!.*)", re.IGNORECASE | re.MULTILINE)


def _check_response_size_safely(
    response: requests.Response,
    patterns: Optional[list[str]] = None,
    max_size: Optional[int] = None,
) -> dict[str, Any]:
    """Safely check response size and extract evidence if needed."""
    return process_response_safely(response, patterns, max_size)


def _check_regex_patterns(
    response_text: str,
    patterns: list[str],
    timeout: float = 2.0,
    enable_security: bool = True,
) -> tuple[bool, list[str], dict[str, Any]]:
    """Check if response matches regex patterns with security protection.
    This function performs regex pattern matching against response content
    and extracts matching groups for data extraction.

    Args:
        response_text: Response text to check
        patterns: List of regex patterns to match
        timeout: Timeout for regex operations
        enable_security: Enable regex security validation
    Returns:
        Tuple of (has_matches, matched_patterns, extracted_data)
    """
    if not patterns:
        return False, [], {}

    matched_patterns = []
    extracted_data = {}
    group_counter = 1
    security_warnings = []

    for pattern in patterns:
        # Validate pattern security if enabled
        if enable_security:
            is_safe, warning = validate_regex_pattern(pattern)
            if not is_safe:
                security_warnings.append(f"Unsafe pattern '{pattern}': {warning}")
                continue

        try:
            if enable_security:
                matches = safe_regex_findall(pattern, response_text, timeout=timeout)
            else:
                compiled_pattern = _compile_regex(pattern)
                matches = list(compiled_pattern.findall(response_text))

            if matches:
                matched_patterns.append(pattern)
                # For findall, we get strings, so we need to re-search to get groups
                compiled_pattern = _compile_regex(pattern)
                match = compiled_pattern.search(response_text)

                if match:
                    # Extract named groups if present
                    if match.groupdict():
                        extracted_data.update(match.groupdict())
                    else:
                        # Extract all groups
                        for i, group in enumerate(match.groups(), 1):
                            if group is not None:  # Only add non-None groups
                                extracted_data[f"group_{group_counter}"] = group
                                group_counter += 1
        except Exception as e:
            security_warnings.append(f"Pattern '{pattern}' failed: {str(e)}")

    # Add security warnings to extracted data
    if security_warnings:
        extracted_data["_security_warnings"] = security_warnings

    return bool(matched_patterns), matched_patterns, extracted_data


def _check_status_codes(response: requests.Response, status_codes: list[int]) -> bool:
    """Check if response status code is in the list of acceptable codes."""
    if not status_codes:
        return True
    return response.status_code in status_codes


def _check_headers_criteria(
    response: requests.Response, headers_criteria: dict[str, str]
) -> tuple[bool, list[str]]:
    """Check if all response headers match required criteria.
    Returns (True, list of matched header keys) if all criteria are matched.
    Returns (False, []) if any are missing or do not match.
    """
    if not headers_criteria:
        return True, []
    matched = []
    for key, value in headers_criteria.items():
        if key in response.headers and value.lower() in response.headers[key].lower():
            matched.append(key)
        else:
            return False, []  # As soon as one does not match, fail
    return True, matched


def _calculate_confidence_score(
    success_matches: list[str],
    failure_matches: list[str],
    regex_matches: list[str],
    status_match: bool,
    headers_match: bool,
    security_warnings: Optional[list[str]] = None,
) -> float:
    """Calculate confidence score for validation result.

    Returns a score between 0.0 and 1.0 based on validation criteria matches.
    Uses integer arithmetic to avoid floating point precision issues.
    """
    # Use integer scoring to avoid floating point precision issues
    score_int = 0

    if success_matches:
        score_int += 30  # 0.3 * 100
    if regex_matches:
        score_int += 30  # 0.3 * 100
    if status_match:
        score_int += 20  # 0.2 * 100
    if headers_match:
        score_int += 10  # 0.1 * 100
    if failure_matches:
        score_int -= 50  # 0.5 * 100

    # Reduce confidence if there were security warnings
    if security_warnings:
        score_int -= len(security_warnings) * 10  # Reduce by 10% per warning

    # Convert back to float and ensure bounds
    score = score_int / 100.0
    return max(0.0, min(1.0, score))
