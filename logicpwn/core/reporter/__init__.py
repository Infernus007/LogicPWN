"""
LogicPWN Reporter - Enhanced for Indian Law Enforcement

This module provides comprehensive reporting capabilities for LogicPWN
penetration testing results, with specialized support for Indian law
enforcement agencies and cybersecurity compliance frameworks.
"""

from .auth_manager import (
    AuthenticationError,
    AuthorizationError,
    Permission,
    ReportAuthManager,
    Role,
    User,
)
from .cvss import (
    AttackComplexity,
    AttackVector,
    CVSSCalculator,
    CVSSVector,
    ImpactMetric,
    PrivilegesRequired,
    Scope,
    UserInteraction,
)
from .framework_mapper import (
    ComplianceMapping,
    ComplianceStatus,
    FrameworkRequirement,
    IndianFrameworkMapper,
)

# Indian compliance and law enforcement
from .indian_compliance import (
    IndianComplianceChecker,
    IndianComplianceFramework,
    IndianComplianceMapping,
    IndianReportMetadata,
    IndianVulnerabilityFinding,
    LegalSeverity,
    ThreatClassification,
)
from .indian_integration import (
    LogicPWNIndianLawEnforcementIntegrator,
    create_indian_law_enforcement_assessment,
    example_indian_law_enforcement_usage,
)
from .indian_law_enforcement import (
    IndianLawEnforcementConfig,
    IndianLawEnforcementReportGenerator,
)

# Security components
from .input_validator import (
    InputValidator,
    ReportConfigInput,
    ValidationError,
    VulnerabilityInput,
)
from .models import RedactionRule

# Core reporting functionality
from .orchestrator import (
    ReportConfig,
    ReportGenerator,
    ReportMetadata,
    SecureReportConfig,
    SecureReportGenerator,
    SecureVulnerabilityFinding,
    VulnerabilityFinding,
)
from .redactor import AdvancedRedactor
from .security_middleware import (
    AuditLogger,
    ReportSecurityMiddleware,
    SecurityPolicy,
    require_authentication,
    validate_input,
)
from .template_renderer import TemplateRenderer

__all__ = [
    # Core reporting
    "VulnerabilityFinding",
    "ReportMetadata",
    "ReportConfig",
    "ReportGenerator",
    "RedactionRule",
    "CVSSCalculator",
    "CVSSVector",
    "AttackVector",
    "AttackComplexity",
    "PrivilegesRequired",
    "UserInteraction",
    "Scope",
    "ImpactMetric",
    "TemplateRenderer",
    "AdvancedRedactor",
    # Security components
    "SecureReportGenerator",
    "SecureVulnerabilityFinding",
    "SecureReportConfig",
    "InputValidator",
    "ValidationError",
    "VulnerabilityInput",
    "ReportConfigInput",
    "ReportAuthManager",
    "User",
    "Permission",
    "Role",
    "AuthenticationError",
    "AuthorizationError",
    "ReportSecurityMiddleware",
    "SecurityPolicy",
    "AuditLogger",
    "require_authentication",
    "validate_input",
    # Indian compliance
    "IndianComplianceFramework",
    "ThreatClassification",
    "LegalSeverity",
    "IndianComplianceMapping",
    "IndianVulnerabilityFinding",
    "IndianReportMetadata",
    "IndianComplianceChecker",
    # Indian law enforcement
    "IndianLawEnforcementConfig",
    "IndianLawEnforcementReportGenerator",
    # Framework mapping
    "ComplianceStatus",
    "FrameworkRequirement",
    "ComplianceMapping",
    "IndianFrameworkMapper",
    # Integration
    "LogicPWNIndianLawEnforcementIntegrator",
    "create_indian_law_enforcement_assessment",
    "example_indian_law_enforcement_usage",
]
