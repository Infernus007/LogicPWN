"""
LogicPWN Reporter Module - Enhanced for Indian Law Enforcement

This module provides comprehensive reporting capabilities for LogicPWN
penetration testing results, with specialized support for Indian law
enforcement agencies and cybersecurity compliance frameworks.
"""

from .cvss import CVSSCalculator
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
from .models import RedactionRule

# Core reporting functionality
from .orchestrator import (
    ReportConfig,
    ReportGenerator,
    ReportMetadata,
    VulnerabilityFinding,
)
from .redactor import AdvancedRedactor
from .template_renderer import TemplateRenderer

__all__ = [
    # Core reporting
    "VulnerabilityFinding",
    "ReportMetadata",
    "ReportConfig",
    "ReportGenerator",
    "RedactionRule",
    "CVSSCalculator",
    "TemplateRenderer",
    "AdvancedRedactor",
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
