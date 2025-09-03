"""
Configurable response size handling for LogicPWN validator.
Prevents truncation of vulnerability evidence while maintaining security.
"""

import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass
class ResponseSizeConfig:
    """Configuration for response size handling."""

    # Size limits (in bytes)
    max_response_size: int = 10 * 1024 * 1024  # 10MB default
    warning_size: int = 1 * 1024 * 1024  # 1MB warning threshold
    truncation_size: int = 500 * 1024  # 500KB truncation threshold

    # Evidence preservation
    preserve_evidence: bool = True
    evidence_window_size: int = 1024  # Bytes around matches to preserve
    max_evidence_chunks: int = 50  # Maximum evidence chunks to store

    # Security settings
    sanitize_sensitive_data: bool = True
    log_size_warnings: bool = True
    compress_large_responses: bool = True

    # Content type handling
    text_content_types: list[str] = None
    binary_content_types: list[str] = None

    def __post_init__(self):
        if self.text_content_types is None:
            self.text_content_types = [
                "text/",
                "application/json",
                "application/xml",
                "application/javascript",
                "application/x-www-form-urlencoded",
            ]

        if self.binary_content_types is None:
            self.binary_content_types = [
                "image/",
                "video/",
                "audio/",
                "application/octet-stream",
                "application/pdf",
                "application/zip",
            ]


class ResponseProcessor:
    """Processes HTTP responses with configurable size handling."""

    def __init__(self, config: Optional[ResponseSizeConfig] = None):
        self.config = config or ResponseSizeConfig()
        self.logger = logging.getLogger(__name__)

    def process_response(
        self, response: requests.Response, patterns: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Process response with size-aware handling.

        Args:
            response: HTTP response object
            patterns: Regex patterns for evidence extraction

        Returns:
            Dictionary containing processed response data
        """
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content_type": response.headers.get("content-type", ""),
            "size_info": self._analyze_response_size(response),
            "content": None,
            "evidence_chunks": [],
            "truncated": False,
            "processing_warnings": [],
        }

        # Determine content type
        content_type = result["content_type"].lower()
        is_text_content = any(
            ct in content_type for ct in self.config.text_content_types
        )
        is_binary_content = any(
            ct in content_type for ct in self.config.binary_content_types
        )

        if is_binary_content:
            result["content"] = self._process_binary_response(response)
            result["processing_warnings"].append(
                "Binary content detected - limited processing"
            )
        elif is_text_content:
            result["content"] = self._process_text_response(response, patterns)
        else:
            # Unknown content type - try to process as text
            try:
                result["content"] = self._process_text_response(response, patterns)
            except UnicodeDecodeError:
                result["content"] = self._process_binary_response(response)
                result["processing_warnings"].append(
                    "Content decoded as binary due to encoding issues"
                )

        return result

    def _analyze_response_size(self, response: requests.Response) -> dict[str, Any]:
        """Analyze response size and provide recommendations."""
        try:
            content_length = len(response.content)
        except Exception:
            content_length = 0

        size_info = {
            "content_length": content_length,
            "exceeds_warning": content_length > self.config.warning_size,
            "exceeds_max": content_length > self.config.max_response_size,
            "should_truncate": content_length > self.config.truncation_size,
            "size_category": self._categorize_size(content_length),
        }

        # Log warnings if enabled
        if self.config.log_size_warnings and size_info["exceeds_warning"]:
            self.logger.warning(
                f"Large response detected: {content_length} bytes "
                f"(warning threshold: {self.config.warning_size})"
            )

        return size_info

    def _categorize_size(self, size: int) -> str:
        """Categorize response size for analysis."""
        if size < 1024:
            return "small"
        elif size < 10 * 1024:
            return "medium"
        elif size < 100 * 1024:
            return "large"
        elif size < 1024 * 1024:
            return "very_large"
        else:
            return "huge"

    def _process_text_response(
        self, response: requests.Response, patterns: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Process text response with evidence preservation."""
        try:
            text_content = response.text
        except Exception as e:
            return {
                "raw_content": "",
                "error": f"Failed to decode response text: {e}",
                "evidence_chunks": [],
            }

        content_length = len(text_content)
        result = {
            "raw_content": text_content,
            "evidence_chunks": [],
            "truncated": False,
            "hash": hashlib.sha256(text_content.encode()).hexdigest(),
        }

        # Extract evidence chunks if patterns provided
        if patterns and self.config.preserve_evidence:
            result["evidence_chunks"] = self._extract_evidence_chunks(
                text_content, patterns
            )

        # Handle large responses
        if content_length > self.config.truncation_size:
            if self.config.preserve_evidence and result["evidence_chunks"]:
                # Keep evidence chunks and truncate the rest
                result["raw_content"] = self._smart_truncate_with_evidence(
                    text_content, result["evidence_chunks"]
                )
                result["truncated"] = True
            else:
                # Simple truncation
                result["raw_content"] = (
                    text_content[: self.config.truncation_size] + "...[TRUNCATED]"
                )
                result["truncated"] = True

        # Sanitize sensitive data if enabled
        if self.config.sanitize_sensitive_data:
            result["raw_content"] = self._sanitize_sensitive_content(
                result["raw_content"]
            )

        return result

    def _process_binary_response(self, response: requests.Response) -> dict[str, Any]:
        """Process binary response with size limits."""
        try:
            content = response.content
        except Exception as e:
            return {
                "content_summary": "Failed to read binary content",
                "error": str(e),
                "size": 0,
            }

        content_length = len(content)

        result = {
            "content_summary": f"Binary content ({content_length} bytes)",
            "size": content_length,
            "hash": hashlib.sha256(content).hexdigest(),
            "mime_type": response.headers.get("content-type", "unknown"),
        }

        # For small binary content, include base64 representation
        if content_length < 1024:
            import base64

            result["base64_content"] = base64.b64encode(content).decode("ascii")

        return result

    def _extract_evidence_chunks(
        self, text: str, patterns: list[str]
    ) -> list[dict[str, Any]]:
        """Extract evidence chunks around pattern matches."""
        from .regex_security import safe_regex_findall

        evidence_chunks = []
        window_size = self.config.evidence_window_size

        for pattern in patterns:
            try:
                # Use findall to get match strings, then find their positions
                match_strings = safe_regex_findall(
                    pattern, text, max_matches=self.config.max_evidence_chunks
                )

                for match_string in match_strings:
                    # Find the position of this match in the text
                    start_pos = text.find(match_string)
                    if start_pos == -1:
                        continue

                    end_pos = start_pos + len(match_string)
                    context_start = max(0, start_pos - window_size // 2)
                    context_end = min(len(text), end_pos + window_size // 2)

                    chunk = {
                        "pattern": pattern,
                        "match_text": match_string,
                        "context": text[context_start:context_end],
                        "position": {
                            "start": start_pos,
                            "end": end_pos,
                            "context_start": context_start,
                            "context_end": context_end,
                        },
                        "groups": [],  # findall doesn't provide groups, so we use empty list
                    }

                    evidence_chunks.append(chunk)

                    # Limit number of evidence chunks
                    if len(evidence_chunks) >= self.config.max_evidence_chunks:
                        break

            except Exception as e:
                self.logger.warning(
                    f"Failed to extract evidence for pattern '{pattern}': {e}"
                )

        return evidence_chunks

    def _smart_truncate_with_evidence(
        self, text: str, evidence_chunks: list[dict[str, Any]]
    ) -> str:
        """Intelligently truncate text while preserving evidence."""
        if not evidence_chunks:
            return text[: self.config.truncation_size] + "...[TRUNCATED]"

        # Calculate total evidence size
        evidence_size = sum(len(chunk["context"]) for chunk in evidence_chunks)

        # If evidence is small enough, include it all plus some context
        if evidence_size < self.config.truncation_size // 2:
            # Include beginning of response + all evidence
            prefix_size = (self.config.truncation_size - evidence_size) // 2
            prefix = text[:prefix_size]

            evidence_text = "\n...[EVIDENCE CHUNKS]...\n"
            for chunk in evidence_chunks:
                evidence_text += f"\n--- Pattern: {chunk['pattern']} ---\n"
                evidence_text += chunk["context"] + "\n"

            return prefix + evidence_text + "\n...[TRUNCATED]"
        else:
            # Just include evidence chunks
            result = "...[RESPONSE TRUNCATED - EVIDENCE PRESERVED]...\n"
            for chunk in evidence_chunks[:10]:  # Limit to first 10 chunks
                result += f"\n--- Pattern: {chunk['pattern']} ---\n"
                result += chunk["context"] + "\n"

            if len(evidence_chunks) > 10:
                result += f"\n...[{len(evidence_chunks) - 10} more evidence chunks omitted]..."

            return result

    def _sanitize_sensitive_content(self, content: str) -> str:
        """Sanitize sensitive data from content."""
        import re

        sensitive_patterns = [
            (r'password["\']?\s*[:=]\s*["\']?([^"\s\n]+)', r'password": "[REDACTED]"'),
            (r'token["\']?\s*[:=]\s*["\']?([^"\s\n]+)', r'token": "[REDACTED]"'),
            (r'key["\']?\s*[:=]\s*["\']?([^"\s\n]+)', r'key": "[REDACTED]"'),
            (r'secret["\']?\s*[:=]\s*["\']?([^"\s\n]+)', r'secret": "[REDACTED]"'),
            (
                r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\s\n]+)',
                r'api_key": "[REDACTED]"',
            ),
            (
                r'authorization["\']?\s*[:=]\s*["\']?([^"\s\n]+)',
                r'authorization": "[REDACTED]"',
            ),
            (r"bearer\s+([a-zA-Z0-9\-._~+/]+=*)", r"bearer [REDACTED]"),
            (r"basic\s+([a-zA-Z0-9+/]+=*)", r"basic [REDACTED]"),
        ]

        for pattern, replacement in sensitive_patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        return content


def create_response_processor(
    max_size: Optional[int] = None,
    preserve_evidence: bool = True,
    sanitize_data: bool = True,
) -> ResponseProcessor:
    """
    Create a response processor with custom configuration.

    Args:
        max_size: Maximum response size to process (bytes)
        preserve_evidence: Whether to preserve evidence chunks
        sanitize_data: Whether to sanitize sensitive data

    Returns:
        Configured ResponseProcessor instance
    """
    config = ResponseSizeConfig()

    if max_size is not None:
        config.max_response_size = max_size
        config.truncation_size = min(config.truncation_size, max_size // 2)

    config.preserve_evidence = preserve_evidence
    config.sanitize_sensitive_data = sanitize_data

    return ResponseProcessor(config)


def process_response_safely(
    response: requests.Response,
    patterns: Optional[list[str]] = None,
    max_size: Optional[int] = None,
) -> dict[str, Any]:
    """
    Safely process HTTP response with size limits and evidence preservation.

    Args:
        response: HTTP response object
        patterns: Regex patterns for evidence extraction
        max_size: Maximum response size to process

    Returns:
        Processed response data
    """
    processor = create_response_processor(max_size=max_size)
    return processor.process_response(response, patterns)
