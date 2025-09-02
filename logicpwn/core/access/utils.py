"""
Legacy access detector utilities. All helpers are now split into validation.py,
baseline.py, and core_logic.py. This module re-exports them for backward
compatibility.
"""

from .core_logic import _determine_vulnerability, _should_have_access

# Import functions for backward compatibility
from .validation import _sanitize_test_id, _validate_inputs

# This module provides utility functions for access detection
# It re-exports core functions for backward compatibility

__all__ = [
    "_validate_inputs",
    "_sanitize_test_id",
    "_determine_vulnerability",
    "_should_have_access",
]
