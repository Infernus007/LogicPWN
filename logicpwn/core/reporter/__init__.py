"""
LogicPWN Reporter Module - Enhanced for Indian Law Enforcement

This module provides comprehensive reporting capabilities for LogicPWN
penetration testing results, with specialized support for Indian law
enforcement agencies and cybersecurity compliance frameworks.
"""

# Core reporting functionality
from .orchestrator import (
    VulnerabilityFinding,
    ReportMetadata, 
    ReportConfig,
    ReportGenerator
)

from .models import RedactionRule

from .cvss import CVSSCalculator

from .template_renderer import TemplateRenderer

from .redactor import AdvancedRedactor

# Indian compliance and law enforcement
from .indian_compliance import (
    IndianComplianceFramework,
    ThreatClassification,
    LegalSeverity,
    IndianComplianceMapping,
    IndianVulnerabilityFinding,
    IndianReportMetadata,
    IndianComplianceChecker
)

from .indian_law_enforcement import (
    IndianLawEnforcementConfig,
    IndianLawEnforcementReportGenerator
)

from .framework_mapper import (
    ComplianceStatus,
    FrameworkRequirement,
    ComplianceMapping,
    IndianFrameworkMapper
)

from .indian_integration import (
    LogicPWNIndianLawEnforcementIntegrator,
    create_indian_law_enforcement_assessment,
    example_indian_law_enforcement_usage
)

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
    "example_indian_law_enforcement_usage"
]
