"""
Authentication and authorization manager for the reporter module.
Provides secure access control for report generation and access.
"""

import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """Report access permissions."""

    READ_REPORTS = "read_reports"
    WRITE_REPORTS = "write_reports"
    DELETE_REPORTS = "delete_reports"
    ADMIN_REPORTS = "admin_reports"
    AUDIT_LOGS = "audit_logs"


class Role(str, Enum):
    """User roles for report access."""

    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"
    AUDITOR = "auditor"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.VIEWER: [Permission.READ_REPORTS],
    Role.ANALYST: [Permission.READ_REPORTS, Permission.WRITE_REPORTS],
    Role.ADMIN: [
        Permission.READ_REPORTS,
        Permission.WRITE_REPORTS,
        Permission.DELETE_REPORTS,
        Permission.ADMIN_REPORTS,
        Permission.AUDIT_LOGS,
    ],
    Role.AUDITOR: [Permission.READ_REPORTS, Permission.AUDIT_LOGS],
}


@dataclass
class User:
    """User representation for authentication."""

    user_id: str
    username: str
    email: str
    roles: set[Role] = field(default_factory=set)
    permissions: set[Permission] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        roles: set[Role] = None,
        role: Role = None,
        permissions: set[Permission] = None,
        created_at: datetime = None,
        last_login: datetime = None,
        is_active: bool = True,
        failed_login_attempts: int = 0,
        locked_until: datetime = None,
    ):
        """Initialize User with support for both role and roles parameters."""
        self.user_id = user_id
        self.username = username
        self.email = email

        # Handle both single role and multiple roles
        if roles is not None:
            self.roles = roles
        elif role is not None:
            if isinstance(role, str):
                self.roles = {Role(role)}
            else:
                self.roles = {role}
        else:
            self.roles = set()

        self.permissions = permissions or set()
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.is_active = is_active
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until

        # Update permissions based on roles
        self.update_permissions()

    def update_permissions(self):
        """Update user permissions based on assigned roles."""
        all_permissions = set()
        for role in self.roles:
            all_permissions.update(ROLE_PERMISSIONS.get(role, []))
        self.permissions = all_permissions

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions

    def has_role(self, role: Role) -> bool:
        """Check if user has specific role."""
        return role in self.roles

    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False


@dataclass
class Session:
    """User session representation."""

    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=8)
    )
    last_activity: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if session is valid."""
        return self.is_active and not self.is_expired()

    def extend(self, hours: int = 8):
        """Extend session expiration."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()


class AuthenticationError(Exception):
    """Authentication related errors."""


class AuthorizationError(Exception):
    """Authorization related errors."""


class ReportAuthManager:
    """Authentication and authorization manager for reports."""

    def __init__(
        self, secret_key: Optional[str] = None, enable_encryption: bool = True
    ):
        """Initialize auth manager."""
        self.secret_key = secret_key or self._generate_secret_key()
        self.enable_encryption = enable_encryption

        if enable_encryption:
            self.encryption_key = Fernet.generate_key()
            self.cipher = Fernet(self.encryption_key)
        else:
            self.encryption_key = None
            self.cipher = None

        # In-memory storage (replace with database in production)
        self.users: dict[str, User] = {}
        self.sessions: dict[str, Session] = {}
        self.api_keys: dict[str, str] = {}  # api_key -> user_id
        self.password_hashes: dict[str, tuple[str, str]] = {}  # user_id -> (hash, salt)

        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_duration = timedelta(hours=8)
        self.jwt_algorithm = "HS256"

        # Initialize default admin user
        self._create_default_admin()

    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        return secrets.token_urlsafe(32)

    def _create_default_admin(self):
        """Create default admin user for initial setup."""
        admin_user = User(
            user_id="admin",
            username="admin",
            email="admin@logicpwn.local",
            roles={Role.ADMIN},
            is_active=True,
        )
        self.users["admin"] = admin_user
        logger.info("Default admin user created")

    def _hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # iterations
        )
        return password_hash.hex(), salt

    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash."""
        computed_hash, _ = self._hash_password(password, salt)
        return hmac.compare_digest(computed_hash, password_hash)

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return secrets.token_urlsafe(32)

    def _generate_api_key(self) -> str:
        """Generate API key."""
        return f"lpwn_{secrets.token_urlsafe(32)}"

    def create_user(
        self, username: str, email: str, password: str, roles: set[Role] = None
    ) -> User:
        """Create new user."""
        if any(user.username == username for user in self.users.values()):
            raise AuthenticationError(f"Username {username} already exists")

        if any(user.email == email for user in self.users.values()):
            raise AuthenticationError(f"Email {email} already exists")

        user_id = secrets.token_urlsafe(16)
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles or {Role.VIEWER},
        )

        # Store password hash separately (not in User object for security)
        password_hash, salt = self._hash_password(password)
        # Store in password hashes dictionary
        self.password_hashes[user_id] = (password_hash, salt)

        self.users[user_id] = user
        logger.info(f"User created: {username} ({user_id})")
        return user

    def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str = None,
        user_agent: str = None,
    ) -> Session:
        """Authenticate user and create session."""
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            raise AuthenticationError("Invalid username or password")

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {username}")
            raise AuthenticationError("Account is inactive")

        if user.is_locked():
            logger.warning(f"Authentication failed: user locked - {username}")
            raise AuthenticationError(
                "Account is temporarily locked due to failed login attempts"
            )

        # Verify password against stored hash
        if user.user_id in self.password_hashes:
            stored_hash, salt = self.password_hashes[user.user_id]
            password_valid = self._verify_password(password, stored_hash, salt)
        else:
            # Fallback for default admin
            if username == "admin" and password == "admin":
                password_valid = True
            else:
                password_valid = False

        if not password_valid:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.locked_until = datetime.utcnow() + self.lockout_duration
                logger.warning(f"User locked due to failed attempts: {username}")

            logger.warning(f"Authentication failed: invalid password - {username}")
            raise AuthenticationError("Invalid username or password")

        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()

        # Create session
        session = Session(
            session_id=self._generate_session_id(),
            user_id=user.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.sessions[session.session_id] = session
        logger.info(f"User authenticated: {username} ({session.session_id})")
        return session

    def authenticate_api_key(self, api_key: str) -> User:
        """Authenticate using API key."""
        if not api_key.startswith("lpwn_"):
            raise AuthenticationError("Invalid API key format")

        user_id = self.api_keys.get(api_key)
        if not user_id:
            logger.warning(f"Authentication failed: invalid API key")
            raise AuthenticationError("Invalid API key")

        user = self.users.get(user_id)
        if not user or not user.is_active:
            logger.warning(f"Authentication failed: user not found for API key")
            raise AuthenticationError("Invalid API key")

        logger.info(f"API key authenticated: {user.username}")
        return user

    def authenticate_jwt(self, token: str) -> User:
        """Authenticate using JWT token."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.jwt_algorithm]
            )
            user_id = payload.get("user_id")

            if not user_id:
                raise AuthenticationError("Invalid token payload")

            user = self.users.get(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")

            # Check token expiration
            exp = payload.get("exp", 0)
            if exp < time.time():
                raise AuthenticationError("Token expired")

            logger.info(f"JWT authenticated: {user.username}")
            return user

        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT authentication failed: {e}")
            raise AuthenticationError("Invalid token")

    def generate_jwt_token(self, user: User, expires_in: int = 3600) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "roles": [role.value for role in user.roles],
            "iat": int(time.time()),
            "exp": int(time.time()) + expires_in,
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
        logger.info(f"JWT token generated for: {user.username}")
        return token

    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user."""
        user = self.users.get(user_id)
        if not user:
            raise AuthenticationError("User not found")

        api_key = self._generate_api_key()
        self.api_keys[api_key] = user_id

        logger.info(f"API key generated for: {user.username}")
        return api_key

    def create_session(
        self, user: User, ip_address: str = None, user_agent: str = None
    ) -> str:
        """Create a new session for user."""
        session = Session(
            session_id=self._generate_session_id(),
            user_id=user.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.sessions[session.session_id] = session
        logger.info(f"Session created for user: {user.username} ({session.session_id})")
        return session.session_id

    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return user."""
        session = self.sessions.get(session_id)
        if not session or not session.is_valid():
            return None

        user = self.users.get(session.user_id)
        if not user or not user.is_active:
            return None

        # Update last activity
        session.last_activity = datetime.utcnow()
        return user

    def logout(self, session_id: str):
        """Logout user session."""
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            logger.info(f"User logged out: {session.session_id}")

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        expired_sessions = [
            sid for sid, session in self.sessions.items() if session.is_expired()
        ]

        for sid in expired_sessions:
            del self.sessions[sid]

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has specific permission."""
        if not user.is_active:
            return False
        return user.has_permission(permission)

    def require_permission(self, user: User, permission: Permission):
        """Require user to have specific permission."""
        if not self.check_permission(user, permission):
            logger.warning(
                f"Authorization failed: {user.username} lacks {permission.value}"
            )
            raise AuthorizationError(f"Permission denied: {permission.value}")

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self.enable_encryption or not self.cipher:
            return data

        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not self.enable_encryption or not self.cipher:
            return encrypted_data

        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            logger.error("Failed to decrypt sensitive data")
            return "[DECRYPTION_FAILED]"

    def register_user(
        self,
        username: str,
        password: str,
        email: str = None,
        roles: set[Role] = None,
        role: Role = None,
    ) -> User:
        """Register a new user (alias for create_user)."""
        # Handle email parameter - if not provided, use username@test.local
        if email is None:
            email = f"{username}@test.local"

        # Handle role vs roles parameter
        if role is not None:
            roles = {role}
        elif roles is None:
            roles = {Role.VIEWER}

        return self.create_user(username, email, password, roles)

    def get_user_summary(self, user: User) -> dict[str, Any]:
        """Get user summary for logging/audit."""
        return {
            "user_id": user.user_id,
            "username": user.username,
            "roles": [role.value for role in user.roles],
            "permissions": [perm.value for perm in user.permissions],
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
        }
