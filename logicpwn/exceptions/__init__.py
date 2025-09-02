"""
Custom exceptions for LogicPwn Business Logic Exploitation Framework.

This package contains all custom exceptions used throughout the framework
for authentication, request execution, and other modules.
"""

from .auth_exceptions import (
    AuthenticationError,
    LoginFailedException,
)
from .auth_exceptions import NetworkError as AuthNetworkError
from .auth_exceptions import (
    SessionError,
)
from .auth_exceptions import TimeoutError as AuthTimeoutError
from .auth_exceptions import ValidationError as AuthValidationError
from .request_exceptions import (
    NetworkError,
    RequestExecutionError,
    ResponseError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    # Authentication exceptions
    "AuthenticationError",
    "LoginFailedException",
    "AuthNetworkError",
    "AuthValidationError",
    "SessionError",
    "AuthTimeoutError",
    # Request execution exceptions
    "RequestExecutionError",
    "NetworkError",
    "ValidationError",
    "TimeoutError",
    "ResponseError",
]
