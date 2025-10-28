"""
Enhanced exception hierarchy with helpful error messages and recovery suggestions.

All exceptions inherit from LogicPwnError and include:
- Clear error messages
- Actionable suggestions
- Context information for debugging
"""

from typing import Any, Optional


class LogicPwnError(Exception):
    """
    Base exception for LogicPWN framework.

    Provides enhanced error messages with suggestions and context.
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize enhanced exception.

        Args:
            message: Clear description of what went wrong
            suggestion: Actionable suggestion for fixing the issue
            context: Additional context information for debugging
        """
        self.message = message
        self.suggestion = suggestion
        self.context = context or {}
        super().__init__(self.formatted_message())

    def formatted_message(self) -> str:
        """Format error message with suggestion and context."""
        msg = f"❌ {self.message}"

        if self.suggestion:
            msg += f"\n\n💡 Suggestion: {self.suggestion}"

        if self.context:
            msg += f"\n\n📋 Context:"
            for key, value in self.context.items():
                msg += f"\n   - {key}: {value}"

        return msg


class AuthenticationError(LogicPwnError):
    """
    Raised when authentication fails.

    Examples:
        - Invalid credentials
        - Connection to auth endpoint failed
        - Success indicators not found in response
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        """
        Initialize authentication error.

        Args:
            message: Description of authentication failure
            url: Login URL that was attempted
            status_code: HTTP status code received
            response_text: Response text (truncated for security)
        """
        suggestion = (
            "Verify your credentials are correct. "
            "Check that success_indicators match text in the actual response. "
            "Enable debug logging to see the full response."
        )

        context = {}
        if url:
            context["login_url"] = url
        if status_code:
            context["status_code"] = status_code
        if response_text:
            # Truncate response for security
            context["response_preview"] = (
                response_text[:200] + "..."
                if len(response_text) > 200
                else response_text
            )

        super().__init__(message, suggestion, context)


class IDORTestError(LogicPwnError):
    """
    Raised when IDOR test execution fails.

    Examples:
        - Invalid endpoint pattern (missing {id} placeholder)
        - Network errors during testing
        - Configuration errors
    """

    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        test_id: Optional[str] = None,
        error_details: Optional[str] = None,
    ):
        """
        Initialize IDOR test error.

        Args:
            message: Description of what went wrong
            endpoint: Endpoint template that failed
            test_id: Specific ID that caused failure
            error_details: Additional error details
        """
        suggestion = (
            "Ensure endpoint_pattern contains {id} placeholder. "
            "Verify success/failure indicators match actual response text. "
            "Check network connectivity and target availability."
        )

        context = {}
        if endpoint:
            context["endpoint_template"] = endpoint
        if test_id:
            context["test_id"] = test_id
        if error_details:
            context["details"] = error_details

        super().__init__(message, suggestion, context)


class ExploitChainError(LogicPwnError):
    """
    Raised when exploit chain execution fails.

    Examples:
        - YAML syntax errors
        - Missing required fields
        - Step execution failures
    """

    def __init__(
        self,
        message: str,
        chain_name: Optional[str] = None,
        step_name: Optional[str] = None,
        step_number: Optional[int] = None,
        yaml_file: Optional[str] = None,
    ):
        """
        Initialize exploit chain error.

        Args:
            message: Description of the failure
            chain_name: Name of the exploit chain
            step_name: Name of the failing step
            step_number: Step number (0-indexed)
            yaml_file: Path to YAML file
        """
        suggestion = (
            "Validate YAML syntax. "
            "Ensure all required fields are present (name, request_config, etc.). "
            "Check that URLs are valid and success_indicators are correct."
        )

        context = {}
        if chain_name:
            context["chain_name"] = chain_name
        if step_name:
            context["failed_step"] = step_name
        if step_number is not None:
            context["step_number"] = step_number + 1  # Make 1-indexed for users
        if yaml_file:
            context["yaml_file"] = yaml_file

        super().__init__(message, suggestion, context)


class ConfigurationError(LogicPwnError):
    """
    Raised when configuration is invalid.

    Examples:
        - Missing required configuration fields
        - Invalid configuration values
        - Type mismatches
    """

    def __init__(
        self,
        message: str,
        config_field: Optional[str] = None,
        provided_value: Any = None,
        expected_type: Optional[str] = None,
    ):
        """
        Initialize configuration error.

        Args:
            message: Description of configuration issue
            config_field: Name of the problematic field
            provided_value: The value that was provided
            expected_type: Expected type/format for the field
        """
        suggestion = "Review the documentation for correct configuration format and required fields."

        context = {}
        if config_field:
            context["field"] = config_field
        if provided_value is not None:
            context["provided_value"] = str(provided_value)
        if expected_type:
            context["expected_type"] = expected_type

        super().__init__(message, suggestion, context)


class SessionError(LogicPwnError):
    """
    Raised when session-related operations fail.

    Examples:
        - Session expired
        - Session not initialized
        - Session validation failed
    """

    def __init__(
        self,
        message: str,
        session_state: Optional[str] = None,
        action: Optional[str] = None,
    ):
        """
        Initialize session error.

        Args:
            message: Description of session issue
            session_state: Current state of the session
            action: Action that was being attempted
        """
        suggestion = (
            "Ensure you authenticate before running tests. "
            "Check if session has expired and re-authenticate if needed."
        )

        context = {}
        if session_state:
            context["session_state"] = session_state
        if action:
            context["attempted_action"] = action

        super().__init__(message, suggestion, context)


class ValidationError(LogicPwnError):
    """
    Raised when response validation fails unexpectedly.

    Note: This is different from a validation result indicating vulnerability.
    This is raised when the validation process itself fails.
    """

    def __init__(
        self,
        message: str,
        validation_type: Optional[str] = None,
        pattern: Optional[str] = None,
    ):
        """
        Initialize validation error.

        Args:
            message: Description of validation issue
            validation_type: Type of validation that failed
            pattern: Pattern that caused the issue
        """
        suggestion = (
            "Check that validation patterns are properly formatted. "
            "Ensure response data is in expected format."
        )

        context = {}
        if validation_type:
            context["validation_type"] = validation_type
        if pattern:
            context["pattern"] = pattern

        super().__init__(message, suggestion, context)


# Export all exception classes
__all__ = [
    "LogicPwnError",
    "AuthenticationError",
    "IDORTestError",
    "ExploitChainError",
    "ConfigurationError",
    "SessionError",
    "ValidationError",
]
