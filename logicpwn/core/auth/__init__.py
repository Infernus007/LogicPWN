from .auth_constants import (
    DEFAULT_SESSION_TIMEOUT,
    HTTP_METHODS,
    MAX_RESPONSE_TEXT_LENGTH,
)
from .auth_models import AuthConfig, CSRFConfig, SessionState
from .auth_session import (
    authenticate_session,
    authenticate_session_advanced,
    create_csrf_config,
    logout_session,
    validate_session,
)
from .auth_utils import _sanitize_credentials
from .enhanced_auth import (
    AuthFlow,
    EnhancedAuthConfig,
    EnhancedAuthenticator,
    RedirectInfo,
    create_enhanced_config,
    create_mfa_enhanced_config,
    create_oauth_enhanced_config,
    create_saml_enhanced_config,
)
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
from .mfa_handler import (
    BackupCodeHandler,
    EmailHandler,
    MFAChallenge,
    MFAConfig,
    MFAManager,
    SMSHandler,
    TOTPHandler,
    TOTPSecret,
    create_totp_qr_code,
    validate_totp_code,
)

# Enhanced authentication modules
from .oauth_handler import (
    OAuthConfig,
    OAuthHandler,
    OAuthToken,
    PKCEChallenge,
    create_github_oauth_config,
    create_google_oauth_config,
    create_microsoft_oauth_config,
    create_oauth_config_from_well_known,
)
from .saml_handler import (
    IdPMetadata,
    SAMLAssertion,
    SAMLConfig,
    SAMLHandler,
    create_azure_saml_config,
    create_okta_saml_config,
    create_saml_config_from_metadata,
    load_idp_metadata_from_url,
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
    # OAuth 2.0 Support
    "OAuthHandler",
    "OAuthConfig",
    "OAuthToken",
    "PKCEChallenge",
    "create_oauth_config_from_well_known",
    "create_google_oauth_config",
    "create_microsoft_oauth_config",
    "create_github_oauth_config",
    # SAML SSO Support
    "SAMLHandler",
    "SAMLConfig",
    "SAMLAssertion",
    "IdPMetadata",
    "load_idp_metadata_from_url",
    "create_saml_config_from_metadata",
    "create_okta_saml_config",
    "create_azure_saml_config",
    # JWT Token Management
    "JWTHandler",
    "JWTConfig",
    "JWTClaims",
    "JWTHeader",
    "JWK",
    "create_jwt_config_from_well_known",
    # Multi-Factor Authentication
    "MFAManager",
    "MFAConfig",
    "MFAChallenge",
    "TOTPHandler",
    "SMSHandler",
    "EmailHandler",
    "BackupCodeHandler",
    "TOTPSecret",
    "create_totp_qr_code",
    "validate_totp_code",
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
    # Enhanced Authentication
    "EnhancedAuthenticator",
    "EnhancedAuthConfig",
    "RedirectInfo",
    "AuthFlow",
    "create_enhanced_config",
    "create_oauth_enhanced_config",
    "create_saml_enhanced_config",
    "create_mfa_enhanced_config",
    # Utilities and constants
    "_sanitize_credentials",
    "HTTP_METHODS",
    "DEFAULT_SESSION_TIMEOUT",
    "MAX_RESPONSE_TEXT_LENGTH",
]
