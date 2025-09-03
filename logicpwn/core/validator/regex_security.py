"""
Regex security and performance optimization for LogicPWN validator.
Implements timeout limits, pattern complexity analysis, and ReDoS protection.
"""

import re
import time
from typing import Optional, Union

# Use the regex library for better timeout support
try:
    import regex

    REGEX_AVAILABLE = True
except ImportError:
    import re as regex

    REGEX_AVAILABLE = False

from logicpwn.exceptions import ValidationError


class RegexTimeoutError(ValidationError):
    """Raised when regex execution exceeds timeout limit."""

    def __init__(self, pattern: str, timeout: float):
        super().__init__(
            message=f"Regex pattern '{pattern}' exceeded timeout of {timeout}s",
            field="regex_pattern",
            value=pattern,
        )


class RegexComplexityError(ValidationError):
    """Raised when regex pattern is too complex and may cause ReDoS."""

    def __init__(self, pattern: str, complexity_score: float):
        super().__init__(
            message=f"Regex pattern '{pattern}' has high complexity score: {complexity_score:.2f}",
            field="regex_pattern",
            value=pattern,
        )


class RegexSecurityValidator:
    """Validates regex patterns for security and performance issues."""

    # Dangerous regex patterns that can cause ReDoS
    REDOS_PATTERNS = [
        r"\(.*\+.*\)\*",  # (x+)*
        r"\(.*\*.*\)\+",  # (x*)+
        r"\(.*\+.*\)\+",  # (x+)+
        r"\(.*\{.*,.*\}.*\)\*",  # (x{n,})*
        r"\(.*\{.*,.*\}.*\)\+",  # (x{n,})+
        r".*\.\*.*\.\*",  # .*.*
        r".*\.\+.*\.\+",  # .+.+
    ]

    # Additional dangerous patterns for catastrophic backtracking
    EXTENDED_REDOS_PATTERNS = [
        r"\([^)]*[*+?]\?*\)[*+?]\?*",  # (x*?)*? or (x+?)+?
        r"\([^)]*\{[^}]*,\}[^}]*\)[*+?]",  # (x{n,})* or (x{n,})+
        r"[^.]*\.\*[^.]*\.\*",  # .*.* (any character followed by .*)
        r"[^.]*\.\+[^.]*\.\+",  # .+.* (any character followed by .+)
    ]

    # Critical patterns that should never be allowed
    CRITICAL_REDOS_PATTERNS = [
        r"\([^)]*\)\*[^)]*\([^)]*\)\*",  # (x*)(y*) - multiple nested groups
        r"\([^)]*\+[^)]*\)\*[^)]*\([^)]*\+[^)]*\)\*",  # (x+)(y+)* - multiple nested groups with +
        r"[^.]*\.\*[^.]*\.\*[^.]*\.\*",  # .*.*.* - triple .* pattern
    ]

    def __init__(self, max_complexity: float = 5.0):  # Lower default for safety
        self.max_complexity = max_complexity

    def analyze_pattern_complexity(self, pattern: str) -> float:
        """
        Analyze regex pattern complexity to detect potential ReDoS.

        Args:
            pattern: Regex pattern to analyze

        Returns:
            Complexity score (higher = more complex/dangerous)
        """
        complexity = 0.0

        # Count nested quantifiers (most dangerous)
        nested_quantifiers = len(re.findall(r"\([^)]*[*+?{][^)]*\)[*+?{]", pattern))
        complexity += nested_quantifiers * 5.0  # Increased weight

        # Count alternations in groups
        alternations = len(re.findall(r"\([^)]*\|[^)]*\)", pattern))
        complexity += alternations * 2.0

        # Count unbounded quantifiers
        unbounded = len(re.findall(r"[*+]\??", pattern))
        complexity += unbounded * 1.5

        # Count large repetitions
        large_reps = len(re.findall(r"\{[0-9]*,[0-9]*\}", pattern))
        complexity += large_reps * 1.0

        # Check for catastrophic backtracking patterns
        for redos_pattern in self.REDOS_PATTERNS + self.EXTENDED_REDOS_PATTERNS:
            if re.search(redos_pattern, pattern):
                complexity += 8.0  # Increased weight

        # Check for critical patterns
        for critical_pattern in self.CRITICAL_REDOS_PATTERNS:
            if re.search(critical_pattern, pattern):
                complexity += 15.0  # Very high weight

        # Additional checks for specific dangerous combinations
        if re.search(r"\([^)]*\)\*.*\([^)]*\)\*", pattern):
            complexity += 12.0  # Multiple nested groups with *

        if re.search(r"[.*+?{}()[\]|]", pattern):
            complexity += 0.5  # Each special character adds complexity

        # Pattern length penalty
        if len(pattern) > 200:
            complexity += (len(pattern) - 200) / 100.0

        return complexity

    def validate_pattern_safety(self, pattern: str) -> tuple[bool, Optional[str]]:
        """
        Validate if a regex pattern is safe to use.

        Args:
            pattern: Regex pattern to validate

        Returns:
            Tuple of (is_safe, warning_message)
        """
        try:
            # Check if pattern compiles
            re.compile(pattern)
        except re.error:
            return False, "Invalid regex syntax"

        # Check for critical patterns first (immediate rejection)
        for critical_pattern in self.CRITICAL_REDOS_PATTERNS:
            if re.search(critical_pattern, pattern):
                return (
                    False,
                    "Pattern contains critical ReDoS vulnerability - multiple nested quantifiers",
                )

        # Check complexity
        complexity = self.analyze_pattern_complexity(pattern)
        if complexity > self.max_complexity:
            return (
                False,
                f"Pattern complexity ({complexity:.2f}) exceeds limit ({self.max_complexity}) - potential ReDoS",
            )

        # Check for specific dangerous patterns
        for redos_pattern in self.REDOS_PATTERNS + self.EXTENDED_REDOS_PATTERNS:
            if re.search(redos_pattern, pattern):
                return (
                    False,
                    "Pattern contains dangerous nested quantifiers that may cause ReDoS",
                )

        # Additional safety checks
        if len(pattern) > 300:
            return (
                False,
                "Pattern too long (>300 characters) - potential performance issues",
            )

        return True, None


class SafeRegexMatcher:
    """Thread-safe regex matcher with timeout and complexity protection."""

    def __init__(
        self,
        timeout: float = 1.0,  # Lower default timeout
        max_complexity: float = 5.0,  # Lower default complexity
        cache_size: int = 256,
    ):
        self.timeout = timeout
        self.validator = RegexSecurityValidator(max_complexity)
        self.cache_size = cache_size

    def _compile_pattern_safe(self, pattern: str):
        """Compile regex pattern with safety validation."""
        # Validate pattern safety first
        is_safe, warning = self.validator.validate_pattern_safety(pattern)
        if not is_safe:
            raise RegexComplexityError(
                pattern, self.validator.analyze_pattern_complexity(pattern)
            )

        try:
            if REGEX_AVAILABLE:
                # Use regex library with timeout support
                return regex.compile(pattern, regex.IGNORECASE | regex.MULTILINE)
            else:
                # Fallback to standard re
                return re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            raise ValidationError(
                message=f"Failed to compile regex pattern: {e}",
                field="regex_pattern",
                value=pattern,
            )

    def search_with_timeout(
        self, pattern: str, text: str, timeout: Optional[float] = None
    ) -> Optional[Union[re.Match, regex.Match]]:
        """
        Search text with regex pattern using timeout protection.

        Args:
            pattern: Regex pattern to search for
            text: Text to search in
            timeout: Timeout in seconds (uses instance default if None)

        Returns:
            Match object or None if no match found

        Raises:
            RegexTimeoutError: If regex execution exceeds timeout
            RegexComplexityError: If pattern is too complex
        """
        timeout = timeout or self.timeout

        # Compile pattern with safety validation
        compiled_pattern = self._compile_pattern_safe(pattern)

        if REGEX_AVAILABLE:
            # Use regex library with built-in timeout
            try:
                start_time = time.time()
                result = compiled_pattern.search(text, timeout=timeout)
                elapsed = time.time() - start_time

                # Double-check timeout (in case regex library timeout doesn't work)
                if elapsed > timeout:
                    raise RegexTimeoutError(pattern, timeout)

                return result
            except regex.error as e:
                if "timeout" in str(e).lower():
                    raise RegexTimeoutError(pattern, timeout)
                raise
        else:
            # Fallback to standard re with manual timeout check
            start_time = time.time()
            result = compiled_pattern.search(text)
            elapsed = time.time() - start_time

            if elapsed > timeout:
                raise RegexTimeoutError(pattern, timeout)

            return result

    def findall_with_timeout(
        self,
        pattern: str,
        text: str,
        timeout: Optional[float] = None,
        max_matches: int = 1000,
    ) -> list[str]:
        """
        Find all matches with timeout and result limit protection.

        Args:
            pattern: Regex pattern to search for
            text: Text to search in
            timeout: Timeout in seconds
            max_matches: Maximum number of matches to return

        Returns:
            List of matched strings (limited by max_matches)
        """
        timeout = timeout or self.timeout

        # Compile pattern with safety validation
        compiled_pattern = self._compile_pattern_safe(pattern)

        if REGEX_AVAILABLE:
            # Use regex library with built-in timeout
            try:
                start_time = time.time()
                matches = compiled_pattern.findall(text, timeout=timeout)
                elapsed = time.time() - start_time

                # Double-check timeout
                if elapsed > timeout:
                    raise RegexTimeoutError(pattern, timeout)

                return matches[:max_matches]
            except regex.error as e:
                if "timeout" in str(e).lower():
                    raise RegexTimeoutError(pattern, timeout)
                raise
        else:
            # Fallback to standard re with manual timeout check
            start_time = time.time()
            matches = compiled_pattern.findall(text)
            elapsed = time.time() - start_time

            if elapsed > timeout:
                raise RegexTimeoutError(pattern, timeout)

            return matches[:max_matches]

    def finditer_with_timeout(
        self,
        pattern: str,
        text: str,
        timeout: Optional[float] = None,
        max_matches: int = 1000,
    ) -> list[Union[re.Match, regex.Match]]:
        """
        Find all match objects with timeout protection.

        Args:
            pattern: Regex pattern to search for
            text: Text to search in
            timeout: Timeout in seconds
            max_matches: Maximum number of matches to return

        Returns:
            List of match objects (limited by max_matches)
        """
        timeout = timeout or self.timeout

        # Compile pattern with safety validation
        compiled_pattern = self._compile_pattern_safe(pattern)

        if REGEX_AVAILABLE:
            # Use regex library with built-in timeout
            try:
                start_time = time.time()
                matches = list(compiled_pattern.finditer(text, timeout=timeout))
                elapsed = time.time() - start_time

                # Double-check timeout
                if elapsed > timeout:
                    raise RegexTimeoutError(pattern, timeout)

                return matches[:max_matches]
            except regex.error as e:
                if "timeout" in str(e).lower():
                    raise RegexTimeoutError(pattern, timeout)
                raise
        else:
            # Fallback to standard re with manual timeout check
            start_time = time.time()
            matches = list(compiled_pattern.finditer(text))
            elapsed = time.time() - start_time

            if elapsed > timeout:
                raise RegexTimeoutError(pattern, timeout)

            return matches[:max_matches]


# Convenience functions for easy use
def safe_regex_search(
    pattern: str, text: str, timeout: float = 1.0
) -> Optional[Union[re.Match, regex.Match]]:
    """Safe regex search with timeout protection."""
    matcher = SafeRegexMatcher(timeout=timeout)
    return matcher.search_with_timeout(pattern, text, timeout)


def safe_regex_findall(
    pattern: str, text: str, timeout: float = 1.0, max_matches: int = 1000
) -> list[str]:
    """Safe regex findall with timeout protection."""
    matcher = SafeRegexMatcher(timeout=timeout)
    return matcher.findall_with_timeout(pattern, text, timeout, max_matches)


def validate_regex_pattern(
    pattern: str, max_complexity: float = 5.0
) -> tuple[bool, Optional[str]]:
    """Validate regex pattern for safety."""
    validator = RegexSecurityValidator(max_complexity)
    return validator.validate_pattern_safety(pattern)
