"""
Legacy access detector utilities. All helpers are now split into validation.py,
baseline.py, and core_logic.py. This module re-exports them for backward
compatibility.
"""

# Import functions for backward compatibility
from .validation import _sanitize_test_id, _validate_inputs
from .core_logic import _test_single_id_with_baselines, _test_single_id_with_baselines_async
