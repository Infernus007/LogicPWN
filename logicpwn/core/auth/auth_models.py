"""
Authentication models for LogicPwn.

Enhanced authentication capabilities including:
- Advanced redirect handling
- Multi-step authentication flows
- JWT token management
- Session management with enhanced security
"""

import re
import time
from dataclasses import dataclass, field
from re import Pattern
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

HTTP_METHODS = {"GET", "POST"}


@dataclass
class SessionState:
    """Represents the state of an HTTP session"""

    cookies: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    csrf_tokens: dict[str, str] = field(
        default_factory=dict
    )  # token_name -> token_value
    auth_data: dict[str, Any] = field(default_factory=dict)
    last_auth_time: float = 0.0
    is_authenticated: bool = False
    base_url: str = ""


@dataclass
class CSRFConfig:
    """Configuration for CSRF token handling"""

    enabled: bool = True
    token_patterns: list[Pattern] = field(
        default_factory=lambda: [
            re.compile(
                r'name=["\']([^"\']*token[^"\']*)["\'].*?value=["\']([^"\']+)["\']',
                re.IGNORECASE,
            ),
            re.compile(
                r'name=["\'](_token)["\'].*?value=["\']([^"\']+)["\']', re.IGNORECASE
            ),
            re.compile(
                r'name=["\']([^"\']*csrf[^"\']*)["\'].*?value=["\']([^"\']+)["\']',
                re.IGNORECASE,
            ),
            re.compile(
                r'<meta[^>]+name=["\']([^"\']*token[^"\']*)["\'][^>]+content=["\']([^"\']+)["\']',
                re.IGNORECASE,
            ),
        ]
    )
    auto_include: bool = True  # Automatically include tokens in subsequent requests
    refresh_on_failure: bool = True  # Re-fetch tokens if auth fails


class AuthConfig(BaseModel):
    """Enhanced authentication configuration with advanced HTTP client features"""

    url: str = Field(..., description="Login endpoint URL")
    method: str = Field(default="POST", description="HTTP method for login")
    credentials: dict[str, Any] = Field(
        default_factory=dict, description="Login credentials"
    )
    success_indicators: list[str] = Field(
        default_factory=list, description="Text indicators of successful login"
    )
    failure_indicators: list[str] = Field(
        default_factory=list, description="Text indicators of failed login"
    )
    headers: Optional[dict[str, str]] = Field(
        default=None, description="Additional HTTP headers"
    )
    timeout: int = Field(
        default=30, ge=1, le=300, description="Request timeout in seconds"
    )
    verify_ssl: bool = Field(
        default=True, description="Whether to verify SSL certificates"
    )

    # Advanced HTTP client features
    csrf_config: Optional[CSRFConfig] = Field(
        default=None, description="CSRF token handling configuration"
    )
    session_validation_url: Optional[str] = Field(
        default=None, description="URL to validate session persistence"
    )
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum authentication retry attempts"
    )
    pre_auth_callback: Optional[Callable] = Field(
        default=None, description="Custom pre-authentication logic"
    )
    post_auth_callback: Optional[Callable] = Field(
        default=None, description="Custom post-authentication validation"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow Callable types

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format - must include scheme and netloc")
        return v

    @field_validator("credentials")
    @classmethod
    def validate_credentials(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not v:
            raise ValueError("Credentials cannot be empty")
        return v

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        v_up = v.upper()
        if v_up not in HTTP_METHODS:
            raise ValueError(f"method must be one of {HTTP_METHODS}")
        return v_up


@dataclass
class RedirectInfo:
    """Information about authentication redirects."""

    url: str
    method: str = "GET"
    parameters: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    is_form_post: bool = False

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.headers is None:
            self.headers = {}


@dataclass
class AuthFlow:
    """Authentication flow state for multi-step authentication."""

    flow_id: str
    flow_type: str  # form, jwt, multi_step
    current_step: int
    total_steps: int
    state_data: dict[str, Any]
    started_at: float
    expires_at: float

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    @property
    def is_complete(self) -> bool:
        return self.current_step >= self.total_steps


class AdvancedAuthConfig(BaseModel):
    """Advanced authentication configuration with comprehensive features."""

    # Basic auth config
    base_config: AuthConfig = Field(
        ..., description="Base authentication configuration"
    )

    # JWT configuration
    jwt_secret_key: Optional[str] = Field(
        default=None, description="JWT secret key for token validation"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiry_seconds: int = Field(
        default=3600, description="JWT token expiry in seconds"
    )

    # Flow settings
    enable_redirect_detection: bool = Field(
        default=True, description="Enable intelligent redirect detection"
    )
    max_redirects: int = Field(default=10, description="Maximum redirects to follow")
    flow_timeout: int = Field(
        default=1800, description="Authentication flow timeout in seconds"
    )

    # Security settings
    require_https: bool = Field(
        default=True, description="Require HTTPS for auth endpoints"
    )
    validate_state: bool = Field(default=True, description="Validate state parameters")
    csrf_protection: bool = Field(default=True, description="Enable CSRF protection")
