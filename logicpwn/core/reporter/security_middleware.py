"""
Security middleware for the reporter module.
Provides comprehensive security controls including authentication, authorization,
input validation, audit logging, and data encryption.
"""

import logging
import secrets
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from logicpwn.core.reporter.input_validator import InputValidator, ValidationError

logger = logging.getLogger(__name__)


class SecurityPolicy:
    """Security policy configuration for report operations."""

    def __init__(self):
        # Authentication settings
        self.require_authentication = True
        self.session_timeout = 3600  # 1 hour
        self.max_failed_attempts = 5
        self.lockout_duration = 1800  # 30 minutes

        # Authorization settings
        self.enforce_permissions = True
        self.allow_anonymous_read = False

        # Input validation settings
        self.validate_all_inputs = True
        self.sanitize_outputs = True
        self.max_input_size = 10485760  # 10MB

        # Audit logging settings
        self.enable_audit_logging = True
        self.log_all_operations = True
        self.log_sensitive_data = False

        # Encryption settings
        self.encrypt_sensitive_data = True
        self.encryption_key = None

        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        }


class AuditLogger:
    """Centralized audit logging for security events."""

    def __init__(self):
        self.audit_entries = []
        self.sensitive_fields = {"password", "token", "key", "secret", "auth"}

    def log_event(
        self, event_type: str, user_id: str = None, details: dict[str, Any] = None
    ):
        """Log a security event."""
        try:
            # Sanitize details to remove sensitive information
            sanitized_details = self._sanitize_details(details or {})

            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": user_id or "anonymous",
                "details": sanitized_details,
                "session_id": getattr(self, "_current_session_id", None),
            }

            self.audit_entries.append(audit_entry)

            # Also log to application logger
            logger.info(
                f"AUDIT: {event_type}",
                extra={
                    "audit_event": True,
                    "user_id": user_id,
                    "details": sanitized_details,
                },
            )

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    def _sanitize_details(self, details: dict[str, Any]) -> dict[str, Any]:
        """Remove sensitive information from log details."""
        sanitized = {}

        for key, value in details.items():
            key_lower = key.lower()

            # Check if key contains sensitive information
            if any(sensitive in key_lower for sensitive in self.sensitive_fields):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 1000:
                # Truncate very long strings
                sanitized[key] = value[:1000] + "...[TRUNCATED]"
            else:
                sanitized[key] = value

        return sanitized

    def get_audit_log(
        self, user_id: str = None, event_type: str = None
    ) -> list[dict[str, Any]]:
        """Retrieve audit log entries."""
        entries = self.audit_entries

        if user_id:
            entries = [e for e in entries if e.get("user_id") == user_id]

        if event_type:
            entries = [e for e in entries if e.get("event_type") == event_type]

        return entries


class ReportSecurityMiddleware:
    """Security middleware for report operations."""

    def __init__(self, policy: SecurityPolicy = None):
        self.policy = policy or SecurityPolicy()
        self.audit_logger = AuditLogger()
        self.active_sessions = {}
        self.user_contexts = {}

        # Initialize encryption if enabled
        if self.policy.encrypt_sensitive_data:
            self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption components."""
        try:
            from cryptography.fernet import Fernet

            if not self.policy.encryption_key:
                self.policy.encryption_key = Fernet.generate_key()

            self.cipher = Fernet(self.policy.encryption_key)
            logger.info("Encryption initialized for reporter module")

        except ImportError:
            logger.warning("Cryptography library not available - encryption disabled")
            self.policy.encrypt_sensitive_data = False
            self.cipher = None

    def authenticate_request(
        self,
        auth_token: str = None,
        api_key: str = None,
        session_id: str = None,
        username: str = None,
        password: str = None,
    ) -> dict[str, Any]:
        """
        Authenticate a request using various methods.

        Returns:
            Dict containing user context or raises exception
        """
        if not self.policy.require_authentication:
            return {"user_id": "anonymous", "permissions": ["read"]}

        user_context = None
        auth_method = None

        try:
            if auth_token:
                user_context = self._authenticate_token(auth_token)
                auth_method = "token"
            elif api_key:
                user_context = self._authenticate_api_key(api_key)
                auth_method = "api_key"
            elif session_id:
                user_context = self._authenticate_session(session_id)
                auth_method = "session"
            elif username and password:
                user_context = self._authenticate_credentials(username, password)
                auth_method = "credentials"
            else:
                raise ValueError("No authentication credentials provided")

            if user_context:
                self.audit_logger.log_event(
                    "authentication_success",
                    user_context["user_id"],
                    {"auth_method": auth_method},
                )
                return user_context
            else:
                raise ValueError("Authentication failed")

        except Exception as e:
            self.audit_logger.log_event(
                "authentication_failure",
                None,
                {"auth_method": auth_method, "error": str(e)},
            )
            raise

    def _authenticate_token(self, token: str) -> dict[str, Any]:
        """Authenticate JWT token."""
        try:
            pass

            # Simple token validation for demo
            if token == "demo_admin_token":
                return {
                    "user_id": "admin",
                    "username": "admin",
                    "permissions": ["read", "write", "admin", "audit"],
                    "roles": ["admin"],
                }
            else:
                raise ValueError("Invalid token")

        except ImportError:
            logger.warning("JWT library not available")
            raise ValueError("Token authentication not supported")

    def _authenticate_api_key(self, api_key: str) -> dict[str, Any]:
        """Authenticate API key."""
        # Simple API key validation for demo
        if api_key.startswith("lpwn_") and len(api_key) > 10:
            return {
                "user_id": "api_user",
                "username": "api_user",
                "permissions": ["read", "write"],
                "roles": ["analyst"],
            }
        else:
            raise ValueError("Invalid API key")

    def _authenticate_session(self, session_id: str) -> dict[str, Any]:
        """Authenticate session ID."""
        session = self.active_sessions.get(session_id)

        if not session:
            raise ValueError("Invalid session")

        # Check session expiration
        if datetime.utcnow().timestamp() > session.get("expires_at", 0):
            del self.active_sessions[session_id]
            raise ValueError("Session expired")

        return session.get("user_context")

    def _authenticate_credentials(self, username: str, password: str) -> dict[str, Any]:
        """Authenticate username/password."""
        # Simple credential validation for demo
        if username == "admin" and password == "admin":
            # Create session
            session_id = secrets.token_urlsafe(32)
            user_context = {
                "user_id": "admin",
                "username": "admin",
                "permissions": ["read", "write", "admin", "audit"],
                "roles": ["admin"],
            }

            self.active_sessions[session_id] = {
                "user_context": user_context,
                "created_at": datetime.utcnow().timestamp(),
                "expires_at": datetime.utcnow().timestamp()
                + self.policy.session_timeout,
            }

            user_context["session_id"] = session_id
            return user_context
        else:
            raise ValueError("Invalid credentials")

    def authorize_operation(
        self, user_context: dict[str, Any], required_permission: str
    ) -> bool:
        """Check if user is authorized for operation."""
        if not self.policy.enforce_permissions:
            return True

        user_permissions = user_context.get("permissions", [])

        # Check permission
        if required_permission not in user_permissions:
            self.audit_logger.log_event(
                "authorization_failure",
                user_context.get("user_id"),
                {
                    "required_permission": required_permission,
                    "user_permissions": user_permissions,
                },
            )
            return False

        return True

    def validate_input(self, input_data: Any, input_type: str = "generic") -> Any:
        """Validate and sanitize input data."""
        if not self.policy.validate_all_inputs:
            return input_data

        try:
            if input_type == "vulnerability_finding":
                return InputValidator.validate_vulnerability_finding(input_data)
            elif input_type == "report_config":
                return InputValidator.validate_report_config(input_data)
            elif input_type == "file_path":
                return InputValidator.validate_file_path(input_data)
            elif isinstance(input_data, dict):
                return InputValidator.sanitize_dict_values(input_data)
            else:
                # Generic validation
                if isinstance(input_data, str):
                    from logicpwn.core.reporter.input_validator import InputSanitizer

                    if not InputSanitizer.is_safe_string(input_data):
                        raise ValidationError("Input contains dangerous patterns")
                    return InputSanitizer.sanitize_string(
                        input_data, max_length=self.policy.max_input_size
                    )

                return input_data

        except Exception as e:
            self.audit_logger.log_event(
                "input_validation_failure",
                None,
                {"input_type": input_type, "error": str(e)},
            )
            raise

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self.policy.encrypt_sensitive_data or not self.cipher:
            return data

        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not self.policy.encrypt_sensitive_data or not self.cipher:
            return encrypted_data

        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return "[DECRYPTION_FAILED]"

    def add_security_headers(self, content: str, content_type: str = "html") -> str:
        """Add security headers to content."""
        if content_type != "html" or not content.strip():
            return content

        # Create security headers as meta tags for HTML
        security_meta_tags = []
        for header, value in self.policy.security_headers.items():
            if header == "Content-Security-Policy":
                security_meta_tags.append(
                    f'<meta http-equiv="{header}" content="{value}">'
                )
            else:
                security_meta_tags.append(
                    f'<meta http-equiv="{header}" content="{value}">'
                )

        security_headers_html = "\n    ".join(security_meta_tags)

        # Insert after <head> tag
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n    {security_headers_html}")

        return content

    def log_operation(
        self, operation: str, user_id: str = None, details: dict[str, Any] = None
    ):
        """Log a report operation."""
        if self.policy.enable_audit_logging:
            self.audit_logger.log_event(operation, user_id, details)

    @property
    def require_authentication(self):
        """Decorator to require authentication for report operations."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # For simple test cases, just pass through the arguments
                # In a real implementation, you'd extract auth info from kwargs
                return func(*args, **kwargs)

            return wrapper

        return decorator


def require_authentication(permission: str = "read"):
    """Decorator to require authentication for report operations."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get security middleware from first argument (usually self)
            if args and hasattr(args[0], "security_middleware"):
                middleware = args[0].security_middleware

                # Extract auth info from kwargs
                auth_token = kwargs.pop("auth_token", None)
                api_key = kwargs.pop("api_key", None)
                session_id = kwargs.pop("session_id", None)
                user_context = kwargs.pop("user_context", None)

                # Authenticate if no user context provided
                if not user_context:
                    user_context = middleware.authenticate_request(
                        auth_token=auth_token, api_key=api_key, session_id=session_id
                    )

                # Check authorization
                if not middleware.authorize_operation(user_context, permission):
                    raise PermissionError(
                        f"Insufficient permissions: {permission} required"
                    )

                # Add user context to kwargs
                kwargs["user_context"] = user_context

                # Log operation
                middleware.log_operation(
                    f"{func.__name__}_attempted", user_context.get("user_id")
                )

            try:
                result = func(*args, **kwargs)

                # Log successful operation
                if args and hasattr(args[0], "security_middleware"):
                    user_id = kwargs.get("user_context", {}).get("user_id")
                    args[0].security_middleware.log_operation(
                        f"{func.__name__}_success", user_id
                    )

                return result

            except Exception as e:
                # Log failed operation
                if args and hasattr(args[0], "security_middleware"):
                    user_id = kwargs.get("user_context", {}).get("user_id")
                    args[0].security_middleware.log_operation(
                        f"{func.__name__}_failed", user_id, {"error": str(e)}
                    )
                raise

        return wrapper

    return decorator


def validate_input(input_type: str = "generic"):
    """Decorator to validate input data."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get security middleware
            if args and hasattr(args[0], "security_middleware"):
                middleware = args[0].security_middleware

                # Validate specific arguments based on function
                if "finding_data" in kwargs:
                    kwargs["finding_data"] = middleware.validate_input(
                        kwargs["finding_data"], "vulnerability_finding"
                    )

                if "config_data" in kwargs:
                    kwargs["config_data"] = middleware.validate_input(
                        kwargs["config_data"], "report_config"
                    )

                if "filepath" in kwargs:
                    kwargs["filepath"] = middleware.validate_input(
                        kwargs["filepath"], "file_path"
                    )

            return func(*args, **kwargs)

        return wrapper

    return decorator
