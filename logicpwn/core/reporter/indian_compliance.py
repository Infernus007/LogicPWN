"""
Indian Cybersecurity Compliance Frameworks for Law Enforcement Reports

This module provides compliance frameworks and reporting standards specifically
designed for Indian law enforcement agencies, including:
- CERT-In guidelines
- Indian Cyber Security Framework
- Information Technology Act 2000 compliance
- Digital India compliance requirements
- Indian government security standards
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from logicpwn.core.reporter.orchestrator import ReportMetadata, VulnerabilityFinding


class IndianComplianceFramework(Enum):
    """Indian cybersecurity compliance frameworks"""

    CERT_IN = "cert_in"
    IT_ACT_2000 = "it_act_2000"
    DIGITAL_INDIA = "digital_india"
    NCIIPC = "nciipc"  # National Critical Information Infrastructure Protection Centre
    CDAC = "cdac"  # Centre for Development of Advanced Computing
    MEITY = "meity"  # Ministry of Electronics & Information Technology
    RBI_CYBER = "rbi_cyber"  # Reserve Bank of India Cyber Security Framework
    INDIAN_COMPUTER_EMERGENCY_RESPONSE_TEAM = "icert"


class ThreatClassification(Enum):
    """Threat classification as per Indian security standards"""

    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    FINANCIAL_SYSTEMS = "financial_systems"
    GOVERNMENT_SYSTEMS = "government_systems"
    PERSONAL_DATA = "personal_data"
    NATIONAL_SECURITY = "national_security"
    CYBER_TERRORISM = "cyber_terrorism"
    CYBER_CRIME = "cyber_crime"
    DATA_BREACH = "data_breach"


class LegalSeverity(Enum):
    """Legal severity classification for Indian law enforcement"""

    SECTION_43_ITA = "section_43_ita"  # Penalty for damage to computer, computer system
    SECTION_43A_ITA = "section_43a_ita"  # Compensation for failure to protect data
    SECTION_66_ITA = "section_66_ita"  # Computer related offenses
    SECTION_66A_ITA = "section_66a_ita"  # Punishment for sending offensive messages
    SECTION_66B_ITA = "section_66b_ita"  # Punishment for dishonestly receiving stolen computer resource
    SECTION_66C_ITA = "section_66c_ita"  # Punishment for identity theft
    SECTION_66D_ITA = "section_66d_ita"  # Punishment for cheating by personation by using computer resource
    SECTION_66E_ITA = "section_66e_ita"  # Punishment for violation of privacy
    SECTION_66F_ITA = "section_66f_ita"  # Punishment for cyber terrorism
    SECTION_67_ITA = (
        "section_67_ita"  # Punishment for publishing or transmitting obscene material
    )
    SECTION_70_ITA = "section_70_ita"  # Protected systems
    SECTION_72_ITA = "section_72_ita"  # Breach of confidentiality and privacy
    SECTION_72A_ITA = "section_72a_ita"  # Punishment for disclosure of information in breach of lawful contract


@dataclass
class IndianComplianceMapping:
    """Maps vulnerabilities to Indian legal and compliance frameworks"""

    framework: IndianComplianceFramework
    threat_classification: ThreatClassification
    legal_sections: list[LegalSeverity]
    compliance_requirements: list[str]
    remediation_standards: list[str]
    reporting_requirements: dict[str, Any]


class IndianVulnerabilityFinding(VulnerabilityFinding):
    """Extended vulnerability finding with Indian compliance data"""

    legal_classification: Optional[list[LegalSeverity]] = []
    threat_classification: Optional[ThreatClassification] = None
    indian_compliance_mapping: Optional[list[IndianComplianceMapping]] = []
    cert_in_advisory_reference: Optional[str] = None
    digital_evidence_hash: Optional[str] = None
    forensic_chain_of_custody: Optional[dict[str, Any]] = None
    potential_legal_implications: Optional[str] = None
    recommended_law_enforcement_actions: Optional[list[str]] = []


class IndianReportMetadata(ReportMetadata):
    """Extended report metadata for Indian law enforcement"""

    investigating_agency: Optional[str] = None
    fir_number: Optional[str] = None
    case_reference: Optional[str] = None
    jurisdiction: Optional[str] = None
    investigating_officer: Optional[str] = None
    cert_in_incident_id: Optional[str] = None
    digital_forensics_team: Optional[str] = None
    evidence_collection_timestamp: Optional[datetime] = None
    chain_of_custody_maintained: bool = True
    legal_authorization: Optional[str] = None
    compliance_frameworks_assessed: list[IndianComplianceFramework] = field(
        default_factory=list
    )


class IndianComplianceChecker:
    """Checks vulnerabilities against Indian compliance frameworks"""

    def __init__(self):
        self.compliance_mappings = self._initialize_compliance_mappings()
        self.legal_mappings = self._initialize_legal_mappings()
        self.evidence_requirements = self._initialize_evidence_requirements()
        self.investigation_protocols = self._initialize_investigation_protocols()

    def _initialize_compliance_mappings(
        self,
    ) -> dict[IndianComplianceFramework, dict[str, Any]]:
        """Initialize compliance framework mappings"""
        return {
            IndianComplianceFramework.CERT_IN: {
                "requirements": [
                    "Incident reporting within 6 hours",
                    "Vulnerability assessment documentation",
                    "Security control implementation",
                    "Digital forensics evidence preservation",
                ],
                "threat_categories": [
                    "Malware attacks",
                    "Phishing attempts",
                    "Website defacements",
                    "DDoS attacks",
                    "Data breaches",
                    "Ransomware",
                ],
            },
            IndianComplianceFramework.IT_ACT_2000: {
                "applicable_sections": [
                    "Section 43 - Penalty for damage to computer system",
                    "Section 43A - Compensation for failure to protect data",
                    "Section 66 - Computer related offenses",
                    "Section 66C - Identity theft",
                    "Section 66E - Violation of privacy",
                    "Section 70 - Protected systems",
                    "Section 72 - Breach of confidentiality",
                ],
                "penalties": {
                    "data_breach": "Up to Rs. 5 crore compensation",
                    "computer_damage": "Up to Rs. 1 crore penalty",
                    "identity_theft": "Imprisonment up to 3 years",
                },
            },
            IndianComplianceFramework.DIGITAL_INDIA: {
                "security_requirements": [
                    "Multi-factor authentication",
                    "Encryption of sensitive data",
                    "Regular security audits",
                    "Incident response procedures",
                    "Data localization compliance",
                ]
            },
            IndianComplianceFramework.RBI_CYBER: {
                "applicable_to": ["Banks", "NBFCs", "Payment systems"],
                "requirements": [
                    "Board-approved cyber security policy",
                    "Baseline cyber security controls",
                    "Advanced monitoring and controls",
                    "Incident reporting to RBI within 2-6 hours",
                    "Third-party risk management",
                ],
            },
        }

    def _initialize_legal_mappings(self) -> dict[str, list[LegalSeverity]]:
        """Map vulnerability types to legal sections"""
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
            "identity_theft": [LegalSeverity.SECTION_66C_ITA],
            "privacy_violation": [
                LegalSeverity.SECTION_66E_ITA,
                LegalSeverity.SECTION_72_ITA,
            ],
            "unauthorized_access": [
                LegalSeverity.SECTION_43_ITA,
                LegalSeverity.SECTION_66_ITA,
            ],
            "cyber_fraud": [LegalSeverity.SECTION_66D_ITA],
            "system_damage": [
                LegalSeverity.SECTION_43_ITA,
                LegalSeverity.SECTION_66_ITA,
            ],
            "information_disclosure": [
                LegalSeverity.SECTION_72_ITA,
                LegalSeverity.SECTION_72A_ITA,
            ],
        }

    def _initialize_evidence_requirements(self) -> dict[str, list[str]]:
        """Initialize digital evidence requirements for different vulnerability types"""
        return {
            "idor": [
                "HTTP request/response logs showing unauthorized access",
                "Screenshot/video proof of accessing other user's data",
                "Database query logs if available",
                "Session/authentication tokens used",
                "Timestamp records of the unauthorized access",
            ],
            "privilege_escalation": [
                "HTTP request/response logs showing privilege escalation",
                "Before/after screenshots of user privileges",
                "Application logs showing role changes",
                "Authentication and authorization logs",
                "System access logs",
            ],
            "data_breach": [
                "Complete data extraction logs",
                "Database dump evidence (redacted for sensitive data)",
                "Network traffic captures",
                "System and application logs",
                "Affected user/record count documentation",
            ],
            "authentication_bypass": [
                "Login attempt logs",
                "Session management evidence",
                "Authentication token analysis",
                "HTTP request/response for bypass attempts",
                "User account access evidence",
            ],
        }

    def _initialize_investigation_protocols(self) -> dict[str, dict[str, Any]]:
        """Initialize investigation protocols for law enforcement"""
        return {
            "immediate_response": {
                "timeline": "0-6 hours",
                "actions": [
                    "Secure and preserve digital evidence",
                    "Document the vulnerability discovery",
                    "Notify CERT-In and relevant authorities",
                    "Initiate chain of custody procedures",
                    "Begin preliminary impact assessment",
                ],
                "stakeholders": [
                    "Investigating Officer",
                    "Digital Forensics Team",
                    "CERT-In",
                ],
            },
            "detailed_investigation": {
                "timeline": "6-72 hours",
                "actions": [
                    "Conduct comprehensive forensic analysis",
                    "Interview relevant personnel",
                    "Analyze system logs and evidence",
                    "Determine scope and impact",
                    "Prepare detailed technical report",
                ],
                "stakeholders": ["Cyber Crime Cell", "Technical Experts", "Legal Team"],
            },
            "legal_proceedings": {
                "timeline": "72+ hours",
                "actions": [
                    "File FIR if criminal activity suspected",
                    "Prepare legal documentation",
                    "Coordinate with public prosecutor",
                    "Submit evidence to court",
                    "Follow up on remediation",
                ],
                "stakeholders": ["Legal Team", "Public Prosecutor", "Court System"],
            },
        }

    def classify_vulnerability(
        self, finding: VulnerabilityFinding
    ) -> IndianVulnerabilityFinding:
        """Classify vulnerability according to Indian legal and compliance frameworks"""
        # Convert to Indian compliance finding
        indian_finding = IndianVulnerabilityFinding(**finding.dict())

        # Determine vulnerability type and map to legal sections
        vuln_type = self._determine_vulnerability_type(finding)
        indian_finding.legal_classification = self.legal_mappings.get(vuln_type, [])

        # Classify threat
        indian_finding.threat_classification = self._classify_threat(finding)

        # Add compliance mappings
        indian_finding.indian_compliance_mapping = self._generate_compliance_mappings(
            finding, vuln_type
        )

        # Add legal implications
        indian_finding.potential_legal_implications = self._generate_legal_implications(
            vuln_type
        )

        # Add law enforcement recommendations
        indian_finding.recommended_law_enforcement_actions = (
            self._generate_law_enforcement_actions(finding, vuln_type)
        )

        return indian_finding

    def _determine_vulnerability_type(self, finding: VulnerabilityFinding) -> str:
        """Determine vulnerability type from finding data"""
        title_lower = finding.title.lower()
        description_lower = finding.description.lower()

        if any(
            keyword in title_lower or keyword in description_lower
            for keyword in ["idor", "insecure direct object", "object reference"]
        ):
            return "idor"
        elif any(
            keyword in title_lower or keyword in description_lower
            for keyword in ["privilege escalation", "elevation", "admin access"]
        ):
            return "privilege_escalation"
        elif any(
            keyword in title_lower or keyword in description_lower
            for keyword in ["data breach", "data exposure", "information disclosure"]
        ):
            return "data_breach"
        elif any(
            keyword in title_lower or keyword in description_lower
            for keyword in ["identity", "impersonation"]
        ):
            return "identity_theft"
        elif any(
            keyword in title_lower or keyword in description_lower
            for keyword in ["privacy", "personal data"]
        ):
            return "privacy_violation"
        elif any(
            keyword in title_lower or keyword in description_lower
            for keyword in ["unauthorized access", "authentication bypass"]
        ):
            return "unauthorized_access"
        elif any(
            keyword in title_lower or keyword in description_lower
            for keyword in ["fraud", "financial"]
        ):
            return "cyber_fraud"
        else:
            return "system_damage"

    def _classify_threat(self, finding: VulnerabilityFinding) -> ThreatClassification:
        """Classify threat according to Indian security standards"""
        severity = finding.severity.lower()
        description = finding.description.lower()

        if any(
            keyword in description for keyword in ["financial", "banking", "payment"]
        ):
            return ThreatClassification.FINANCIAL_SYSTEMS
        elif any(
            keyword in description for keyword in ["government", "public", "citizen"]
        ):
            return ThreatClassification.GOVERNMENT_SYSTEMS
        elif any(
            keyword in description for keyword in ["personal data", "pii", "privacy"]
        ):
            return ThreatClassification.PERSONAL_DATA
        elif severity in ["critical", "high"]:
            return ThreatClassification.CRITICAL_INFRASTRUCTURE
        else:
            return ThreatClassification.CYBER_CRIME

    def _generate_compliance_mappings(
        self, finding: VulnerabilityFinding, vuln_type: str
    ) -> list[IndianComplianceMapping]:
        """Generate compliance mappings for the vulnerability"""
        mappings = []

        # CERT-In mapping
        cert_in_mapping = IndianComplianceMapping(
            framework=IndianComplianceFramework.CERT_IN,
            threat_classification=self._classify_threat(finding),
            legal_sections=self.legal_mappings.get(vuln_type, []),
            compliance_requirements=[
                "Immediate incident reporting to CERT-In",
                "Detailed vulnerability assessment report",
                "Evidence preservation and digital forensics",
                "Remediation timeline and progress tracking",
            ],
            remediation_standards=[
                "Follow CERT-In vulnerability handling guidelines",
                "Implement security controls as per Indian Cyber Security Framework",
                "Ensure data protection as per IT Act 2000",
            ],
            reporting_requirements={
                "timeline": "Within 6 hours of discovery",
                "format": "CERT-In incident reporting format",
                "authorities": ["CERT-In", "Local cyber crime cell"],
                "evidence_requirements": [
                    "Digital forensics report",
                    "System logs",
                    "Network traces",
                ],
            },
        )
        mappings.append(cert_in_mapping)

        # IT Act 2000 mapping
        it_act_mapping = IndianComplianceMapping(
            framework=IndianComplianceFramework.IT_ACT_2000,
            threat_classification=self._classify_threat(finding),
            legal_sections=self.legal_mappings.get(vuln_type, []),
            compliance_requirements=[
                "Legal compliance with Information Technology Act 2000",
                "Data protection and privacy measures",
                "Penalty avoidance through proper security controls",
            ],
            remediation_standards=[
                "Implement reasonable security practices",
                "Maintain data protection standards",
                "Ensure confidentiality and privacy protection",
            ],
            reporting_requirements={
                "legal_authority": "Cyber crime investigation cell",
                "jurisdiction": "As per Indian Penal Code and IT Act",
                "evidence_chain": "Maintain legal chain of custody",
            },
        )
        mappings.append(it_act_mapping)

        return mappings

    def _generate_legal_implications(self, vuln_type: str) -> str:
        """Generate legal implications text"""
        legal_implications = {
            "idor": "This vulnerability may constitute unauthorized access to computer systems under Section 43 of IT Act 2000, potentially leading to penalties up to Rs. 1 crore. If personal data is accessed, Section 72 regarding breach of confidentiality may apply.",
            "privilege_escalation": "Unauthorized elevation of privileges may violate Section 66 (computer-related offenses) and Section 70 (protected systems) of IT Act 2000, potentially resulting in imprisonment up to 3 years.",
            "data_breach": "Data breach incidents fall under Section 43A of IT Act 2000, requiring organizations to implement reasonable security practices. Failure may result in compensation liability up to Rs. 5 crore.",
            "identity_theft": "Identity theft through computer systems is punishable under Section 66C of IT Act 2000 with imprisonment up to 3 years and fine up to Rs. 1 lakh.",
            "privacy_violation": "Violation of privacy through unauthorized access is covered under Section 66E of IT Act 2000, punishable with imprisonment up to 3 years.",
            "unauthorized_access": "Unauthorized access to computer systems violates Section 43 and 66 of IT Act 2000, potentially resulting in significant penalties and imprisonment.",
            "cyber_fraud": "Cyber fraud and cheating using computer resources is punishable under Section 66D of IT Act 2000 with imprisonment up to 3 years.",
            "system_damage": "Damage to computer systems is covered under Section 43 of IT Act 2000, with penalties proportional to the damage caused.",
        }
        return legal_implications.get(
            vuln_type,
            "This vulnerability may have legal implications under the Information Technology Act 2000 and relevant sections of Indian Penal Code.",
        )

    def _generate_law_enforcement_actions(
        self, finding: VulnerabilityFinding, vuln_type: str
    ) -> list[str]:
        """Generate recommended law enforcement actions"""
        severity = finding.severity.lower()

        base_actions = [
            "Document the vulnerability with complete technical details",
            "Preserve digital evidence maintaining chain of custody",
            "Report to CERT-In within stipulated timeframe",
            "Coordinate with local cyber crime investigation cell",
        ]

        if severity in ["critical", "high"]:
            base_actions.extend(
                [
                    "Immediate incident escalation to senior authorities",
                    "Consider invoking Computer Emergency Response procedures",
                    "Notify affected stakeholders and data subjects if applicable",
                    "Coordinate with National Critical Information Infrastructure Protection Centre (NCIIPC) if critical infrastructure is affected",
                ]
            )

        if vuln_type in ["data_breach", "privacy_violation"]:
            base_actions.extend(
                [
                    "Assess scope of personal data affected",
                    "Prepare data breach notification as per applicable laws",
                    "Consider notification to Data Protection Authority when established",
                ]
            )

        return base_actions

    def generate_chain_of_custody_document(
        self, finding: IndianVulnerabilityFinding, investigating_officer: str
    ) -> dict[str, Any]:
        """Generate chain of custody documentation for digital evidence"""
        return {
            "document_id": f"COC_{finding.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "case_reference": finding.forensic_chain_of_custody.get(
                "case_reference", ""
            ),
            "evidence_items": [
                {
                    "item_id": f"EVD_{finding.id}_{i+1:03d}",
                    "description": evidence,
                    "collection_timestamp": datetime.now(),
                    "collection_method": "Digital forensics extraction",
                    "integrity_hash": f"SHA256_{i+1:03d}",
                    "collected_by": investigating_officer,
                    "storage_location": "Secure digital evidence locker",
                }
                for i, evidence in enumerate(
                    self.evidence_requirements.get(
                        self._determine_vulnerability_type(finding), []
                    )
                )
            ],
            "chain_entries": [
                {
                    "timestamp": datetime.now(),
                    "action": "Evidence collected and secured",
                    "person": investigating_officer,
                    "purpose": "Initial digital forensics collection",
                }
            ],
            "compliance_certification": "This chain of custody follows CERT-In and IT Act 2000 evidence handling requirements",
        }

    def generate_legal_impact_assessment(
        self, finding: IndianVulnerabilityFinding
    ) -> dict[str, Any]:
        """Generate comprehensive legal impact assessment"""
        vuln_type = self._determine_vulnerability_type(finding)

        return {
            "vulnerability_summary": {
                "type": vuln_type,
                "severity": finding.severity,
                "legal_classification": [
                    section.value for section in finding.legal_classification
                ],
                "threat_category": (
                    finding.threat_classification.value
                    if finding.threat_classification
                    else None
                ),
            },
            "applicable_laws": {
                "primary": "Information Technology Act 2000",
                "sections": [section.value for section in finding.legal_classification],
                "secondary": ["Indian Penal Code 1860", "Indian Evidence Act 1872"],
            },
            "potential_penalties": self._get_penalty_matrix(
                finding.legal_classification
            ),
            "investigation_requirements": {
                "mandatory_reporting": "CERT-In within 6 hours",
                "evidence_preservation": "As per IT Act Section 65B requirements",
                "jurisdictional_authority": "Local cyber crime investigation cell",
            },
            "victim_impact": self._assess_victim_impact(finding),
            "remediation_obligations": self._get_remediation_obligations(vuln_type),
            "compliance_status": self._assess_compliance_status(finding),
        }

    def _get_penalty_matrix(
        self, legal_sections: list[LegalSeverity]
    ) -> dict[str, str]:
        """Get penalty matrix for legal sections"""
        penalty_map = {
            LegalSeverity.SECTION_43_ITA: "Penalty up to Rs. 1 crore for damage to computer system",
            LegalSeverity.SECTION_43A_ITA: "Compensation up to Rs. 5 crore for data protection failure",
            LegalSeverity.SECTION_66_ITA: "Imprisonment up to 3 years or fine up to Rs. 5 lakh",
            LegalSeverity.SECTION_66C_ITA: "Imprisonment up to 3 years and fine up to Rs. 1 lakh",
            LegalSeverity.SECTION_66E_ITA: "Imprisonment up to 3 years and fine up to Rs. 2 lakh",
            LegalSeverity.SECTION_66F_ITA: "Imprisonment for life (cyber terrorism)",
            LegalSeverity.SECTION_70_ITA: "Imprisonment up to 10 years for protected systems",
            LegalSeverity.SECTION_72_ITA: "Imprisonment up to 2 years and fine up to Rs. 1 lakh",
        }

        return {
            section.value: penalty_map.get(section, "Penalties as per IT Act 2000")
            for section in legal_sections
        }

    def _assess_victim_impact(
        self, finding: IndianVulnerabilityFinding
    ) -> dict[str, Any]:
        """Assess victim impact for legal proceedings"""
        severity = finding.severity.lower()
        self._determine_vulnerability_type(finding)

        impact_levels = {
            "critical": {
                "financial_loss": "High potential for significant financial loss",
                "privacy_violation": "Severe privacy breach with personal data exposure",
                "reputation_damage": "Major reputation and trust damage",
                "systemic_risk": "Risk to critical infrastructure or multiple victims",
            },
            "high": {
                "financial_loss": "Moderate to high financial impact",
                "privacy_violation": "Substantial privacy concerns",
                "reputation_damage": "Significant reputation impact",
                "systemic_risk": "Limited systemic risk",
            },
            "medium": {
                "financial_loss": "Limited financial impact",
                "privacy_violation": "Moderate privacy concerns",
                "reputation_damage": "Manageable reputation impact",
                "systemic_risk": "Minimal systemic risk",
            },
        }

        return impact_levels.get(severity, impact_levels["medium"])

    def _get_remediation_obligations(self, vuln_type: str) -> list[str]:
        """Get remediation obligations for vulnerability type"""
        remediation_map = {
            "idor": [
                "Implement proper access controls and authorization checks",
                "Conduct comprehensive access control audit",
                "Implement user-specific data isolation",
                "Add logging and monitoring for data access attempts",
            ],
            "privilege_escalation": [
                "Review and fix role-based access control implementation",
                "Implement principle of least privilege",
                "Add audit trails for privilege changes",
                "Conduct security testing of authorization mechanisms",
            ],
            "data_breach": [
                "Immediate containment of data exposure",
                "Notification to affected individuals as per law",
                "Implementation of data protection measures",
                "Regular security audits and monitoring",
            ],
        }

        return remediation_map.get(
            vuln_type,
            [
                "Implement appropriate security controls",
                "Conduct regular security assessments",
                "Maintain incident response procedures",
            ],
        )

    def _assess_compliance_status(
        self, finding: IndianVulnerabilityFinding
    ) -> dict[str, str]:
        """Assess compliance status across different frameworks"""
        return {
            "IT_Act_2000": "Non-compliant - Vulnerability violates reasonable security practices",
            "CERT_In_Guidelines": "Requires immediate reporting and remediation",
            "Digital_India_Framework": "Security controls need enhancement",
            "Data_Protection_Requirements": "Personal data protection measures insufficient",
        }
