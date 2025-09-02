# Validator module exports - Enhanced with critical vulnerability presets
from .validation_presets import (
    VALIDATION_PRESETS,
    ValidationPresets,
    get_preset,
    list_all_presets,
    list_critical_presets,
)
from .validator_api import (
    chain_validations,
    create_custom_preset,
    extract_from_response,
    list_available_presets,
    list_vulnerability_presets,
    validate_business_logic,
    validate_html_response,
    validate_json_response,
    validate_response,
    validate_timing_attack,
    validate_with_preset,
)
from .validator_checks import (
    _calculate_confidence_score,
    _check_headers_criteria,
    _check_regex_patterns,
    _check_status_codes,
)
from .validator_models import (
    AdaptiveConfidenceWeights,
    BusinessLogicRule,
    BusinessLogicTemplate,
    ConfidenceLevel,
    SeverityLevel,
    ValidationConfig,
    ValidationResult,
    ValidationType,
)
from .validator_patterns import VulnerabilityPatterns
from .validator_utils import _sanitize_response_text

__all__ = [
    # Core validation functions
    "validate_response",
    "extract_from_response",
    "validate_json_response",
    "validate_html_response",
    "chain_validations",
    "validate_with_preset",
    "list_available_presets",
    "list_vulnerability_presets",
    # Enhanced validation functions
    "validate_business_logic",
    "validate_timing_attack",
    "create_custom_preset",
    # Models and enums
    "ValidationResult",
    "ValidationConfig",
    "ValidationType",
    "SeverityLevel",
    "ConfidenceLevel",
    "AdaptiveConfidenceWeights",
    "BusinessLogicRule",
    "BusinessLogicTemplate",
    # Patterns and presets
    "VulnerabilityPatterns",
    "ValidationPresets",
    "get_preset",
    "VALIDATION_PRESETS",
    "list_critical_presets",
    "list_all_presets",
]
