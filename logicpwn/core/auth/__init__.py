from .auth_constants import (
    DEFAULT_SESSION_TIMEOUT,
    HTTP_METHODS,
    MAX_RESPONSE_TEXT_LENGTH,
)
from .auth_models import (
    AdvancedAuthConfig,
    AuthConfig,
    AuthFlow,
    CSRFConfig,
    RedirectInfo,
    SessionState,
)
from .auth_session import (
    Authenticator,
    authenticate_session,
    authenticate_session_advanced,
    create_advanced_config,
    create_csrf_config,
    logout_session,
    validate_session,
)
from .auth_utils import _sanitize_credentials
from .http_client import LogicPwnHTTPClient, create_authenticated_client
from .idp_integration import (
    AttributeMapping,
    AuthenticationSession,
    IdPConfig,
    IdPManager,
    OIDCProvider,
    SAMLIdPProvider,
    UserProfile,
    create_google_idp_config,
    create_microsoft_idp_config,
    create_okta_idp_config,
)
from .jwt_handler import (
    JWK,
    JWTClaims,
    JWTConfig,
    JWTHandler,
    JWTHeader,
    create_jwt_config_from_well_known,
)

__all__ = [
    # Core authentication functions
    "authenticate_session",
    "validate_session",
    "logout_session",
    # Advanced authentication with HTTP client
    "authenticate_session_advanced",
    "create_authenticated_client",
    "create_csrf_config",
    # Models and configurations
    "AuthConfig",
    "SessionState",
    "CSRFConfig",
    "LogicPwnHTTPClient",
    # JWT Token Management
    "JWTHandler",
    "JWTConfig",
    "JWTClaims",
    "JWTHeader",
    "JWK",
    "create_jwt_config_from_well_known",
    # Identity Provider Integration
    "IdPManager",
    "IdPConfig",
    "AuthenticationSession",
    "UserProfile",
    "AttributeMapping",
    "OIDCProvider",
    "SAMLIdPProvider",
    "create_google_idp_config",
    "create_microsoft_idp_config",
    "create_okta_idp_config",
    # Advanced Authentication
    "Authenticator",
    "AdvancedAuthConfig",
    "RedirectInfo",
    "AuthFlow",
    "create_advanced_config",
    # Utilities and constants
    "_sanitize_credentials",
    "HTTP_METHODS",
    "DEFAULT_SESSION_TIMEOUT",
    "MAX_RESPONSE_TEXT_LENGTH",
]
