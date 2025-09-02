"""
Indian Cybersecurity Framework Mapper

This module maps vulnerabilities discovered by LogicPWN to specific Indian
cybersecurity frameworks and generates detailed compliance reports.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from logicpwn.core.reporter.indian_compliance import (
    IndianComplianceFramework,
    LegalSeverity,
)


class ComplianceStatus(Enum):
    """Compliance status levels"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNDER_REVIEW = "under_review"


class FrameworkRequirement(Enum):
    """Standard framework requirements"""

    ACCESS_CONTROL = "access_control"
    AUTHENTICATION = "authentication"
    ENCRYPTION = "encryption"
    INCIDENT_RESPONSE = "incident_response"
    VULNERABILITY_MANAGEMENT = "vulnerability_management"
    SECURITY_MONITORING = "security_monitoring"
    DATA_PROTECTION = "data_protection"
    AUDIT_LOGGING = "audit_logging"
    NETWORK_SECURITY = "network_security"
    BUSINESS_CONTINUITY = "business_continuity"


@dataclass
class ComplianceMapping:
    """Maps vulnerabilities to compliance requirements"""

    framework: IndianComplianceFramework
    requirement: FrameworkRequirement
    requirement_id: str
    description: str
    compliance_status: ComplianceStatus
    evidence_required: list[str]
    remediation_actions: list[str]
    legal_implications: Optional[str] = None
    priority_level: str = "medium"


class IndianFrameworkMapper:
    """Maps vulnerabilities to Indian cybersecurity frameworks"""

    def __init__(self):
        self.framework_mappings = self._initialize_framework_mappings()
        self.requirement_mappings = self._initialize_requirement_mappings()
        self.legal_mappings = self._initialize_legal_mappings()

    def _initialize_framework_mappings(
        self,
    ) -> dict[IndianComplianceFramework, dict[str, Any]]:
        """Initialize detailed framework mappings"""
        return {
            IndianComplianceFramework.CERT_IN: {
                "name": "Computer Emergency Response Team - India",
                "authority": "Ministry of Electronics & Information Technology",
                "scope": "National cybersecurity coordination and incident response",
                "mandatory_reporting": True,
                "reporting_timeline": "6 hours",
                "key_requirements": [
                    "Incident reporting and coordination",
                    "Vulnerability disclosure and management",
                    "Security advisories compliance",
                    "Digital forensics cooperation",
                ],
                "penalties": "As per IT Act 2000 and subordinate legislation",
            },
            IndianComplianceFramework.IT_ACT_2000: {
                "name": "Information Technology Act 2000",
                "authority": "Parliament of India",
                "scope": "Legal framework for electronic transactions and cybersecurity",
                "mandatory_reporting": True,
                "reporting_timeline": "Immediate",
                "key_requirements": [
                    "Reasonable security practices (Section 43A)",
                    "Data protection and privacy (Section 72)",
                    "Computer system protection (Section 70)",
                    "Digital evidence standards (Section 65B)",
                ],
                "penalties": "Fines up to Rs. 5 crore, imprisonment up to 10 years",
            },
            IndianComplianceFramework.DIGITAL_INDIA: {
                "name": "Digital India Framework",
                "authority": "Ministry of Electronics & Information Technology",
                "scope": "Digital governance and cybersecurity for government systems",
                "mandatory_reporting": False,
                "reporting_timeline": "As required",
                "key_requirements": [
                    "Multi-factor authentication",
                    "Data encryption and protection",
                    "Regular security audits",
                    "Secure software development",
                ],
                "penalties": "Administrative actions and compliance orders",
            },
            IndianComplianceFramework.NCIIPC: {
                "name": "National Critical Information Infrastructure Protection Centre",
                "authority": "National Security Council Secretariat",
                "scope": "Protection of critical information infrastructure",
                "mandatory_reporting": True,
                "reporting_timeline": "Immediate",
                "key_requirements": [
                    "Critical infrastructure identification",
                    "Threat intelligence sharing",
                    "Incident response coordination",
                    "Security control implementation",
                ],
                "penalties": "As per IT Act Section 70 (protected systems)",
            },
            IndianComplianceFramework.RBI_CYBER: {
                "name": "RBI Cybersecurity Framework",
                "authority": "Reserve Bank of India",
                "scope": "Banking and financial services cybersecurity",
                "mandatory_reporting": True,
                "reporting_timeline": "2-6 hours",
                "key_requirements": [
                    "Board-approved cybersecurity policy",
                    "Baseline security controls",
                    "Advanced threat monitoring",
                    "Third-party risk management",
                ],
                "penalties": "Monetary penalties, regulatory actions",
            },
        }

    def _initialize_requirement_mappings(
        self,
    ) -> dict[FrameworkRequirement, list[ComplianceMapping]]:
        """Initialize requirement to framework mappings"""
        mappings = {
            FrameworkRequirement.ACCESS_CONTROL: [
                ComplianceMapping(
                    framework=IndianComplianceFramework.IT_ACT_2000,
                    requirement=FrameworkRequirement.ACCESS_CONTROL,
                    requirement_id="ITA_43A_ACCESS",
                    description="Implement reasonable security practices for access control",
                    compliance_status=ComplianceStatus.NON_COMPLIANT,
                    evidence_required=[
                        "Access control policy documentation",
                        "User access logs and audit trails",
                        "Role-based access control implementation",
                    ],
                    remediation_actions=[
                        "Implement proper authentication mechanisms",
                        "Establish role-based access controls",
                        "Regular access review and certification",
                    ],
                    legal_implications="Violation may result in compensation liability under Section 43A",
                    priority_level="high",
                ),
                ComplianceMapping(
                    framework=IndianComplianceFramework.DIGITAL_INDIA,
                    requirement=FrameworkRequirement.ACCESS_CONTROL,
                    requirement_id="DI_ACCESS_001",
                    description="Multi-factor authentication and access controls",
                    compliance_status=ComplianceStatus.NON_COMPLIANT,
                    evidence_required=[
                        "MFA implementation evidence",
                        "Access control testing results",
                    ],
                    remediation_actions=[
                        "Deploy multi-factor authentication",
                        "Implement strong access controls",
                    ],
                    priority_level="high",
                ),
            ],
            FrameworkRequirement.DATA_PROTECTION: [
                ComplianceMapping(
                    framework=IndianComplianceFramework.IT_ACT_2000,
                    requirement=FrameworkRequirement.DATA_PROTECTION,
                    requirement_id="ITA_72_DATA",
                    description="Protect confidentiality and privacy of data",
                    compliance_status=ComplianceStatus.NON_COMPLIANT,
                    evidence_required=[
                        "Data classification policy",
                        "Encryption implementation",
                        "Data access controls",
                    ],
                    remediation_actions=[
                        "Implement data encryption",
                        "Establish data classification",
                        "Deploy data loss prevention",
                    ],
                    legal_implications="Breach may result in penalties under Section 72",
                    priority_level="critical",
                )
            ],
            FrameworkRequirement.INCIDENT_RESPONSE: [
                ComplianceMapping(
                    framework=IndianComplianceFramework.CERT_IN,
                    requirement=FrameworkRequirement.INCIDENT_RESPONSE,
                    requirement_id="CERT_IN_IR_001",
                    description="Incident reporting and response procedures",
                    compliance_status=ComplianceStatus.PARTIALLY_COMPLIANT,
                    evidence_required=[
                        "Incident response plan",
                        "CERT-In reporting evidence",
                        "Incident handling logs",
                    ],
                    remediation_actions=[
                        "Establish formal incident response procedures",
                        "Train incident response team",
                        "Regular incident response drills",
                    ],
                    priority_level="high",
                )
            ],
        }

        return mappings

    def _initialize_legal_mappings(self) -> dict[str, list[LegalSeverity]]:
        """Initialize legal section mappings for vulnerabilities"""
        return {
            "idor": [LegalSeverity.SECTION_43_ITA, LegalSeverity.SECTION_72_ITA],
            "privilege_escalation": [
                LegalSeverity.SECTION_66_ITA,
                LegalSeverity.SECTION_70_ITA,
            ],
            "data_breach": [
                LegalSeverity.SECTION_43A_ITA,
                LegalSeverity.SECTION_72_ITA,
            ],
            "authentication_bypass": [
                LegalSeverity.SECTION_43_ITA,
                LegalSeverity.SECTION_66_ITA,
            ],
            "sql_injection": [
                LegalSeverity.SECTION_43_ITA,
                LegalSeverity.SECTION_66_ITA,
            ],
            "xss": [LegalSeverity.SECTION_66_ITA, LegalSeverity.SECTION_66D_ITA],
            "csrf": [LegalSeverity.SECTION_43_ITA, LegalSeverity.SECTION_66_ITA],
            "file_upload": [LegalSeverity.SECTION_43_ITA, LegalSeverity.SECTION_66_ITA],
            "information_disclosure": [
                LegalSeverity.SECTION_72_ITA,
                LegalSeverity.SECTION_72A_ITA,
            ],
        }

    def map_vulnerability_to_frameworks(
        self, vulnerability_type: str, severity: str
    ) -> list[ComplianceMapping]:
        """Map a vulnerability to relevant framework requirements"""
        mappings = []

        # Determine relevant frameworks based on vulnerability type
        relevant_frameworks = self._get_relevant_frameworks(
            vulnerability_type, severity
        )

        for framework in relevant_frameworks:
            framework_mappings = self._get_framework_mappings_for_vulnerability(
                framework, vulnerability_type, severity
            )
            mappings.extend(framework_mappings)

        return mappings

    def _get_relevant_frameworks(
        self, vulnerability_type: str, severity: str
    ) -> list[IndianComplianceFramework]:
        """Get relevant frameworks for a vulnerability"""
        frameworks = []

        # All vulnerabilities are relevant to IT Act 2000
        frameworks.append(IndianComplianceFramework.IT_ACT_2000)

        # High/Critical vulnerabilities require CERT-In reporting
        if severity.lower() in ["high", "critical"]:
            frameworks.append(IndianComplianceFramework.CERT_IN)

        # Government systems need Digital India compliance
        frameworks.append(IndianComplianceFramework.DIGITAL_INDIA)

        # Critical infrastructure vulnerabilities
        if severity.lower() == "critical":
            frameworks.append(IndianComplianceFramework.NCIIPC)

        return frameworks

    def _get_framework_mappings_for_vulnerability(
        self,
        framework: IndianComplianceFramework,
        vulnerability_type: str,
        severity: str,
    ) -> list[ComplianceMapping]:
        """Get specific mappings for a framework and vulnerability"""
        mappings = []

        if framework == IndianComplianceFramework.IT_ACT_2000:
            mappings.extend(self._get_it_act_mappings(vulnerability_type, severity))
        elif framework == IndianComplianceFramework.CERT_IN:
            mappings.extend(self._get_cert_in_mappings(vulnerability_type, severity))
        elif framework == IndianComplianceFramework.DIGITAL_INDIA:
            mappings.extend(
                self._get_digital_india_mappings(vulnerability_type, severity)
            )
        elif framework == IndianComplianceFramework.NCIIPC:
            mappings.extend(self._get_nciipc_mappings(vulnerability_type, severity))

        return mappings

    def _get_it_act_mappings(
        self, vulnerability_type: str, severity: str
    ) -> list[ComplianceMapping]:
        """Get IT Act 2000 specific mappings"""
        mappings = []

        # Section 43A - Data protection
        if vulnerability_type in ["data_breach", "idor", "information_disclosure"]:
            mappings.append(
                ComplianceMapping(
                    framework=IndianComplianceFramework.IT_ACT_2000,
                    requirement=FrameworkRequirement.DATA_PROTECTION,
                    requirement_id="ITA_43A_DATA",
                    description="Reasonable security practices for data protection",
                    compliance_status=ComplianceStatus.NON_COMPLIANT,
                    evidence_required=[
                        "Data protection policy",
                        "Security control implementation",
                        "Incident documentation",
                    ],
                    remediation_actions=[
                        "Implement reasonable security practices",
                        "Establish data protection controls",
                        "Regular security assessments",
                    ],
                    legal_implications="Compensation liability up to Rs. 5 crore under Section 43A",
                    priority_level=(
                        "critical" if severity.lower() == "critical" else "high"
                    ),
                )
            )

        # Section 43 - Computer damage
        if vulnerability_type in ["privilege_escalation", "authentication_bypass"]:
            mappings.append(
                ComplianceMapping(
                    framework=IndianComplianceFramework.IT_ACT_2000,
                    requirement=FrameworkRequirement.ACCESS_CONTROL,
                    requirement_id="ITA_43_ACCESS",
                    description="Protection against computer system damage",
                    compliance_status=ComplianceStatus.NON_COMPLIANT,
                    evidence_required=[
                        "Access control documentation",
                        "System integrity evidence",
                        "Unauthorized access logs",
                    ],
                    remediation_actions=[
                        "Strengthen access controls",
                        "Implement system monitoring",
                        "Regular security updates",
                    ],
                    legal_implications="Penalty up to Rs. 1 crore under Section 43",
                    priority_level="high",
                )
            )

        return mappings

    def _get_cert_in_mappings(
        self, vulnerability_type: str, severity: str
    ) -> list[ComplianceMapping]:
        """Get CERT-In specific mappings"""
        return [
            ComplianceMapping(
                framework=IndianComplianceFramework.CERT_IN,
                requirement=FrameworkRequirement.INCIDENT_RESPONSE,
                requirement_id="CERT_IN_REPORT",
                description="Incident reporting to CERT-In within 6 hours",
                compliance_status=ComplianceStatus.UNDER_REVIEW,
                evidence_required=[
                    "CERT-In incident report",
                    "Vulnerability assessment report",
                    "Digital evidence package",
                ],
                remediation_actions=[
                    "Report incident to CERT-In",
                    "Provide detailed technical analysis",
                    "Cooperate with investigation",
                ],
                priority_level="critical",
            )
        ]

    def _get_digital_india_mappings(
        self, vulnerability_type: str, severity: str
    ) -> list[ComplianceMapping]:
        """Get Digital India framework mappings"""
        mappings = []

        if vulnerability_type in ["authentication_bypass", "idor"]:
            mappings.append(
                ComplianceMapping(
                    framework=IndianComplianceFramework.DIGITAL_INDIA,
                    requirement=FrameworkRequirement.AUTHENTICATION,
                    requirement_id="DI_AUTH_001",
                    description="Multi-factor authentication implementation",
                    compliance_status=ComplianceStatus.NON_COMPLIANT,
                    evidence_required=[
                        "Authentication system audit",
                        "MFA implementation status",
                        "Security assessment report",
                    ],
                    remediation_actions=[
                        "Deploy multi-factor authentication",
                        "Strengthen authentication controls",
                        "Regular authentication testing",
                    ],
                    priority_level="high",
                )
            )

        return mappings

    def _get_nciipc_mappings(
        self, vulnerability_type: str, severity: str
    ) -> list[ComplianceMapping]:
        """Get NCIIPC specific mappings"""
        return [
            ComplianceMapping(
                framework=IndianComplianceFramework.NCIIPC,
                requirement=FrameworkRequirement.SECURITY_MONITORING,
                requirement_id="NCIIPC_MONITOR",
                description="Critical infrastructure security monitoring",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evidence_required=[
                    "Security monitoring logs",
                    "Threat detection capabilities",
                    "Incident response procedures",
                ],
                remediation_actions=[
                    "Enhance security monitoring",
                    "Implement threat detection",
                    "Coordinate with NCIIPC",
                ],
                priority_level="critical",
            )
        ]

    def generate_compliance_matrix(
        self, vulnerabilities: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate comprehensive compliance matrix"""
        matrix = {
            "overall_status": {},
            "framework_analysis": {},
            "gap_analysis": {},
            "remediation_priorities": {},
        }

        # Analyze each vulnerability against frameworks
        all_mappings = []
        for vuln in vulnerabilities:
            vuln_mappings = self.map_vulnerability_to_frameworks(
                vuln.get("type", "unknown"), vuln.get("severity", "medium")
            )
            all_mappings.extend(vuln_mappings)

        # Calculate overall compliance status
        for framework in IndianComplianceFramework:
            framework_mappings = [m for m in all_mappings if m.framework == framework]
            matrix["framework_analysis"][framework.value] = {
                "total_requirements": len(framework_mappings),
                "compliant": len(
                    [
                        m
                        for m in framework_mappings
                        if m.compliance_status == ComplianceStatus.COMPLIANT
                    ]
                ),
                "non_compliant": len(
                    [
                        m
                        for m in framework_mappings
                        if m.compliance_status == ComplianceStatus.NON_COMPLIANT
                    ]
                ),
                "partially_compliant": len(
                    [
                        m
                        for m in framework_mappings
                        if m.compliance_status == ComplianceStatus.PARTIALLY_COMPLIANT
                    ]
                ),
                "compliance_percentage": self._calculate_compliance_percentage(
                    framework_mappings
                ),
            }

        # Identify gaps and priorities
        matrix["gap_analysis"] = self._analyze_gaps(all_mappings)
        matrix["remediation_priorities"] = self._prioritize_remediation(all_mappings)

        return matrix

    def _calculate_compliance_percentage(
        self, mappings: list[ComplianceMapping]
    ) -> float:
        """Calculate compliance percentage for a set of mappings"""
        if not mappings:
            return 0.0

        compliant_count = len(
            [m for m in mappings if m.compliance_status == ComplianceStatus.COMPLIANT]
        )
        partially_compliant_count = len(
            [
                m
                for m in mappings
                if m.compliance_status == ComplianceStatus.PARTIALLY_COMPLIANT
            ]
        )

        # Partially compliant counts as 0.5
        total_compliance_score = compliant_count + (partially_compliant_count * 0.5)

        return (total_compliance_score / len(mappings)) * 100

    def _analyze_gaps(self, mappings: list[ComplianceMapping]) -> dict[str, Any]:
        """Analyze compliance gaps"""
        gaps = {
            "critical_gaps": [],
            "high_priority_gaps": [],
            "medium_priority_gaps": [],
            "framework_specific_gaps": {},
        }

        for mapping in mappings:
            if mapping.compliance_status == ComplianceStatus.NON_COMPLIANT:
                gap_info = {
                    "framework": mapping.framework.value,
                    "requirement": mapping.requirement.value,
                    "description": mapping.description,
                    "legal_implications": mapping.legal_implications,
                    "remediation_actions": mapping.remediation_actions,
                }

                if mapping.priority_level == "critical":
                    gaps["critical_gaps"].append(gap_info)
                elif mapping.priority_level == "high":
                    gaps["high_priority_gaps"].append(gap_info)
                else:
                    gaps["medium_priority_gaps"].append(gap_info)

                # Framework-specific gaps
                framework_key = mapping.framework.value
                if framework_key not in gaps["framework_specific_gaps"]:
                    gaps["framework_specific_gaps"][framework_key] = []
                gaps["framework_specific_gaps"][framework_key].append(gap_info)

        return gaps

    def _prioritize_remediation(
        self, mappings: list[ComplianceMapping]
    ) -> list[dict[str, Any]]:
        """Prioritize remediation actions"""
        remediation_items = []

        for mapping in mappings:
            if mapping.compliance_status != ComplianceStatus.COMPLIANT:
                for action in mapping.remediation_actions:
                    remediation_items.append(
                        {
                            "action": action,
                            "framework": mapping.framework.value,
                            "requirement": mapping.requirement.value,
                            "priority": mapping.priority_level,
                            "legal_implications": mapping.legal_implications,
                            "evidence_required": mapping.evidence_required,
                        }
                    )

        # Sort by priority (critical, high, medium, low)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        remediation_items.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return remediation_items
