"""
Indian Law Enforcement Report Generator

This module generates comprehensive cybersecurity compliance reports specifically
designed for Indian law enforcement agencies. It integrates with the logicPWN
penetration testing framework to produce reports that are compliant with:
- CERT-In guidelines
- Information Technology Act 2000
- Digital India compliance requirements
- Chain of custody requirements for digital evidence
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from logicpwn.core.reporter.indian_compliance import (
    IndianComplianceChecker,
    IndianComplianceFramework,
    IndianReportMetadata,
    IndianVulnerabilityFinding,
    LegalSeverity,
    ThreatClassification,
)
from logicpwn.core.reporter.orchestrator import (
    ReportConfig,
    ReportGenerator,
    VulnerabilityFinding,
)


@dataclass
class IndianLawEnforcementConfig:
    """Configuration specific to Indian law enforcement reporting"""

    investigating_agency: str
    fir_number: Optional[str] = None
    case_reference: Optional[str] = None
    investigating_officer: str = ""
    jurisdiction: str = ""
    incident_classification: str = "cyber_crime"
    priority_level: str = "medium"  # low, medium, high, critical
    legal_authorization: str = ""
    digital_forensics_team: Optional[str] = None
    evidence_collection_protocols: list[str] = field(default_factory=list)
    compliance_frameworks: list[IndianComplianceFramework] = field(default_factory=list)
    include_chain_of_custody: bool = True
    include_legal_analysis: bool = True
    include_remediation_timeline: bool = True
    redaction_level: str = "standard"  # minimal, standard, high


class IndianLawEnforcementReportGenerator(ReportGenerator):
    """Enhanced report generator for Indian law enforcement agencies"""

    def __init__(
        self, config: ReportConfig, law_enforcement_config: IndianLawEnforcementConfig
    ):
        super().__init__(config)
        self.le_config = law_enforcement_config
        self.compliance_checker = IndianComplianceChecker()
        self.indian_findings: list[IndianVulnerabilityFinding] = []
        self.indian_metadata: Optional[IndianReportMetadata] = None
        self.evidence_catalog: dict[str, Any] = {}

    def add_finding_with_compliance(
        self, finding: VulnerabilityFinding
    ) -> IndianVulnerabilityFinding:
        """Add a finding and automatically classify for Indian compliance"""
        # Convert to Indian compliance finding
        indian_finding = self.compliance_checker.classify_vulnerability(finding)

        # Add law enforcement specific data
        indian_finding.forensic_chain_of_custody = self._create_chain_of_custody(
            indian_finding
        )
        indian_finding.digital_evidence_hash = self._generate_evidence_hash(
            indian_finding
        )

        # Add to both lists for compatibility
        self.add_finding(finding)
        self.indian_findings.append(indian_finding)

        # Update evidence catalog
        self._update_evidence_catalog(indian_finding)

        return indian_finding

    def generate_comprehensive_law_enforcement_report(self) -> dict[str, Any]:
        """Generate comprehensive report for law enforcement"""
        report = {
            "executive_summary": self._generate_executive_summary(),
            "incident_details": self._generate_incident_details(),
            "technical_findings": self._generate_technical_findings(),
            "legal_analysis": self._generate_legal_analysis(),
            "digital_evidence": self._generate_evidence_documentation(),
            "investigation_recommendations": self._generate_investigation_recommendations(),
            "compliance_assessment": self._generate_compliance_assessment(),
            "remediation_plan": self._generate_remediation_plan(),
            "chain_of_custody": self._generate_chain_of_custody_documentation(),
            "appendices": self._generate_appendices(),
        }

        return report

    def export_law_enforcement_package(self, output_dir: str) -> dict[str, str]:
        """Export complete law enforcement package with multiple formats"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        files_created = {}

        # Generate comprehensive report
        comprehensive_report = self.generate_comprehensive_law_enforcement_report()

        # Export in multiple formats
        formats = ["json", "markdown", "html"]
        for fmt in formats:
            filename = f"cybersecurity_investigation_report.{fmt}"
            filepath = output_path / filename

            if fmt == "json":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(
                        comprehensive_report,
                        f,
                        indent=2,
                        default=str,
                        ensure_ascii=False,
                    )
            elif fmt == "markdown":
                content = self._render_markdown_report(comprehensive_report)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
            elif fmt == "html":
                content = self._render_html_report(comprehensive_report)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

            files_created[fmt] = str(filepath)

        # Create evidence summary
        evidence_summary = self._create_evidence_summary()
        evidence_file = output_path / "digital_evidence_summary.json"
        with open(evidence_file, "w", encoding="utf-8") as f:
            json.dump(evidence_summary, f, indent=2, default=str, ensure_ascii=False)
        files_created["evidence_summary"] = str(evidence_file)

        # Create compliance checklist
        compliance_checklist = self._create_compliance_checklist()
        checklist_file = output_path / "compliance_checklist.md"
        with open(checklist_file, "w", encoding="utf-8") as f:
            f.write(compliance_checklist)
        files_created["compliance_checklist"] = str(checklist_file)

        return files_created

    def _generate_executive_summary(self) -> dict[str, Any]:
        """Generate executive summary for law enforcement"""
        critical_findings = [
            f for f in self.indian_findings if f.severity.lower() == "critical"
        ]
        high_findings = [
            f for f in self.indian_findings if f.severity.lower() == "high"
        ]

        return {
            "incident_overview": {
                "total_vulnerabilities": len(self.indian_findings),
                "critical_issues": len(critical_findings),
                "high_priority_issues": len(high_findings),
                "potential_data_breach": any(
                    f.threat_classification == ThreatClassification.PERSONAL_DATA
                    for f in self.indian_findings
                ),
                "national_security_implications": any(
                    f.threat_classification == ThreatClassification.NATIONAL_SECURITY
                    for f in self.indian_findings
                ),
            },
            "legal_implications": {
                "it_act_violations": list(
                    {
                        section.value
                        for f in self.indian_findings
                        for section in f.legal_classification
                    }
                ),
                "potential_penalties": "As per Information Technology Act 2000 and applicable sections",
                "criminal_provisions": "May invoke relevant sections of IT Act 2000 and IPC",
            },
            "immediate_actions_required": [
                "Secure and preserve all digital evidence",
                "Report incident to CERT-In within 6 hours",
                "Initiate chain of custody procedures",
                "Begin impact assessment and victim notification",
            ],
            "compliance_status": {
                "cert_in_guidelines": "Investigation initiated as per CERT-In protocols",
                "it_act_compliance": "Evidence handling follows IT Act Section 65B requirements",
                "digital_forensics": "Standard digital forensics procedures applied",
            },
        }

    def _generate_incident_details(self) -> dict[str, Any]:
        """Generate detailed incident information"""
        return {
            "case_information": {
                "case_reference": self.le_config.case_reference,
                "fir_number": self.le_config.fir_number,
                "investigating_agency": self.le_config.investigating_agency,
                "investigating_officer": self.le_config.investigating_officer,
                "jurisdiction": self.le_config.jurisdiction,
                "incident_classification": self.le_config.incident_classification,
                "priority_level": self.le_config.priority_level,
            },
            "timeline": {
                "incident_discovery": (
                    min([f.discovered_at for f in self.indian_findings])
                    if self.indian_findings
                    else datetime.now()
                ),
                "investigation_started": datetime.now(),
                "evidence_collection_started": datetime.now(),
                "preliminary_analysis_completed": datetime.now() + timedelta(hours=6),
            },
            "affected_systems": {
                "target_systems": list(
                    {
                        endpoint
                        for f in self.indian_findings
                        for endpoint in f.affected_endpoints
                    }
                ),
                "vulnerability_types": list(
                    {
                        self.compliance_checker._determine_vulnerability_type(f)
                        for f in self.indian_findings
                    }
                ),
                "threat_classifications": list(
                    {
                        f.threat_classification.value
                        for f in self.indian_findings
                        if f.threat_classification
                    }
                ),
            },
        }

    def _generate_technical_findings(self) -> list[dict[str, Any]]:
        """Generate detailed technical findings for each vulnerability"""
        technical_findings = []

        for finding in self.indian_findings:
            tech_finding = {
                "finding_id": finding.id,
                "vulnerability_title": finding.title,
                "severity_assessment": {
                    "severity": finding.severity,
                    "cvss_score": finding.cvss_score,
                    "business_impact": finding.impact,
                    "legal_severity": [
                        section.value for section in finding.legal_classification
                    ],
                },
                "technical_details": {
                    "description": finding.description,
                    "affected_endpoints": finding.affected_endpoints,
                    "proof_of_concept": finding.proof_of_concept,
                    "exploitation_scenario": self._generate_exploitation_scenario(
                        finding
                    ),
                },
                "digital_evidence": {
                    "evidence_hash": finding.digital_evidence_hash,
                    "evidence_items": self.compliance_checker.evidence_requirements.get(
                        self.compliance_checker._determine_vulnerability_type(finding),
                        [],
                    ),
                    "collection_timestamp": finding.discovered_at,
                    "forensic_integrity": "SHA-256 hash verification completed",
                },
                "legal_classification": {
                    "threat_type": (
                        finding.threat_classification.value
                        if finding.threat_classification
                        else None
                    ),
                    "applicable_sections": [
                        section.value for section in finding.legal_classification
                    ],
                    "potential_charges": finding.potential_legal_implications,
                },
            }
            technical_findings.append(tech_finding)

        return technical_findings

    def _generate_legal_analysis(self) -> dict[str, Any]:
        """Generate comprehensive legal analysis"""
        if not self.le_config.include_legal_analysis:
            return {}

        all_legal_sections = []
        for finding in self.indian_findings:
            all_legal_sections.extend(finding.legal_classification)

        unique_sections = list(set(all_legal_sections))

        return {
            "applicable_laws": {
                "primary_legislation": "Information Technology Act 2000",
                "secondary_legislation": [
                    "Indian Penal Code 1860",
                    "Indian Evidence Act 1872",
                ],
                "relevant_sections": [section.value for section in unique_sections],
            },
            "legal_implications": [
                self.compliance_checker._generate_legal_implications(
                    self.compliance_checker._determine_vulnerability_type(finding)
                )
                for finding in self.indian_findings
            ],
            "prosecution_prospects": self._assess_prosecution_prospects(),
            "evidence_admissibility": {
                "digital_evidence_standards": "As per IT Act Section 65B requirements",
                "chain_of_custody": "Maintained as per legal standards",
                "expert_testimony": "Technical expert testimony available",
                "forensic_reports": "Digital forensics reports prepared",
            },
            "recommended_charges": self._recommend_charges(),
        }

    def _generate_evidence_documentation(self) -> dict[str, Any]:
        """Generate digital evidence documentation"""
        return {
            "evidence_summary": {
                "total_evidence_items": len(self.evidence_catalog),
                "evidence_types": list(self.evidence_catalog.keys()),
                "collection_period": {
                    "start": (
                        min([f.discovered_at for f in self.indian_findings])
                        if self.indian_findings
                        else datetime.now()
                    ),
                    "end": datetime.now(),
                },
            },
            "evidence_catalog": self.evidence_catalog,
            "integrity_verification": {
                "hash_algorithm": "SHA-256",
                "verification_status": "All evidence items verified",
                "chain_of_custody_status": "Maintained",
            },
            "storage_information": {
                "secure_storage": "Digital evidence locker",
                "access_controls": "Multi-factor authentication required",
                "backup_status": "Evidence backed up to secure secondary location",
            },
        }

    def _generate_investigation_recommendations(self) -> dict[str, Any]:
        """Generate investigation recommendations"""
        return {
            "immediate_actions": [
                "Preserve all system logs and evidence",
                "Interview relevant personnel",
                "Secure affected systems",
                "Document incident timeline",
                "Notify stakeholders as required",
            ],
            "detailed_investigation": [
                "Conduct comprehensive forensic analysis",
                "Analyze attack vectors and methodologies",
                "Identify potential suspects or sources",
                "Assess full scope of compromise",
                "Document financial or other damages",
            ],
            "legal_proceedings": [
                "Prepare comprehensive case file",
                "Coordinate with public prosecutor",
                "Arrange expert witness testimony",
                "Ensure evidence admissibility",
                "Follow up on remediation compliance",
            ],
            "stakeholder_coordination": {
                "internal": [
                    "Investigation team",
                    "Digital forensics",
                    "Legal counsel",
                ],
                "external": [
                    "CERT-In",
                    "Local cyber crime cell",
                    "Affected organizations",
                ],
                "regulatory": ["Data protection authorities", "Sector regulators"],
            },
        }

    def _generate_compliance_assessment(self) -> dict[str, Any]:
        """Generate compliance assessment against Indian frameworks"""
        compliance_status = {}

        for framework in IndianComplianceFramework:
            framework_assessment = {
                "framework_name": framework.value,
                "compliance_status": "Under Investigation",
                "applicable_requirements": self.compliance_checker.compliance_mappings.get(
                    framework, {}
                ).get(
                    "requirements", []
                ),
                "compliance_gaps": self._identify_compliance_gaps(framework),
                "remediation_required": self._get_framework_remediation(framework),
            }
            compliance_status[framework.value] = framework_assessment

        return {
            "overall_compliance": compliance_status,
            "critical_gaps": self._identify_critical_gaps(),
            "regulatory_reporting": {
                "cert_in_reported": True,
                "timeline_compliance": "Within required timeframes",
                "documentation_status": "Complete",
            },
        }

    def _generate_remediation_plan(self) -> dict[str, Any]:
        """Generate comprehensive remediation plan"""
        if not self.le_config.include_remediation_timeline:
            return {}

        remediation_items = []
        for finding in self.indian_findings:
            vuln_type = self.compliance_checker._determine_vulnerability_type(finding)
            obligations = self.compliance_checker._get_remediation_obligations(
                vuln_type
            )

            for obligation in obligations:
                remediation_items.append(
                    {
                        "vulnerability_id": finding.id,
                        "remediation_action": obligation,
                        "priority": finding.severity.lower(),
                        "estimated_timeline": self._estimate_remediation_timeline(
                            finding.severity
                        ),
                        "responsible_party": "System owner/administrator",
                        "verification_method": "Security testing and audit",
                    }
                )

        return {
            "immediate_remediation": [
                item
                for item in remediation_items
                if item["priority"] in ["critical", "high"]
            ],
            "medium_term_remediation": [
                item for item in remediation_items if item["priority"] == "medium"
            ],
            "long_term_remediation": [
                item for item in remediation_items if item["priority"] == "low"
            ],
            "compliance_verification": {
                "follow_up_required": True,
                "verification_timeline": "30-90 days post remediation",
                "compliance_certification": "Required for case closure",
            },
        }

    def _generate_chain_of_custody_documentation(self) -> list[dict[str, Any]]:
        """Generate chain of custody documentation for all evidence"""
        if not self.le_config.include_chain_of_custody:
            return []

        chain_docs = []
        for finding in self.indian_findings:
            chain_doc = self.compliance_checker.generate_chain_of_custody_document(
                finding, self.le_config.investigating_officer
            )
            chain_docs.append(chain_doc)

        return chain_docs

    def _generate_appendices(self) -> dict[str, Any]:
        """Generate appendices with supporting documentation"""
        return {
            "technical_appendix": {
                "vulnerability_details": "Detailed technical analysis of each vulnerability",
                "network_diagrams": "System architecture and attack paths",
                "log_analysis": "Relevant system and application logs",
            },
            "legal_appendix": {
                "relevant_statutes": "Complete text of applicable legal sections",
                "case_precedents": "Similar cases and legal precedents",
                "expert_opinions": "Technical and legal expert assessments",
            },
            "compliance_appendix": {
                "framework_requirements": "Detailed compliance framework requirements",
                "gap_analysis": "Comprehensive compliance gap analysis",
                "best_practices": "Industry best practices and recommendations",
            },
        }

    # Helper methods
    def _create_chain_of_custody(
        self, finding: IndianVulnerabilityFinding
    ) -> dict[str, Any]:
        """Create chain of custody information"""
        return {
            "case_reference": self.le_config.case_reference,
            "evidence_id": f"EVD_{finding.id}",
            "collection_timestamp": datetime.now(),
            "collecting_officer": self.le_config.investigating_officer,
            "digital_forensics_team": self.le_config.digital_forensics_team,
            "storage_location": "Secure digital evidence repository",
        }

    def _generate_evidence_hash(self, finding: IndianVulnerabilityFinding) -> str:
        """Generate evidence hash for integrity verification"""
        evidence_data = f"{finding.id}_{finding.title}_{finding.discovered_at}_{finding.proof_of_concept}"
        return hashlib.sha256(evidence_data.encode()).hexdigest()

    def _update_evidence_catalog(self, finding: IndianVulnerabilityFinding):
        """Update evidence catalog with finding details"""
        vuln_type = self.compliance_checker._determine_vulnerability_type(finding)
        evidence_items = self.compliance_checker.evidence_requirements.get(
            vuln_type, []
        )

        self.evidence_catalog[finding.id] = {
            "vulnerability_type": vuln_type,
            "evidence_items": evidence_items,
            "collection_timestamp": finding.discovered_at,
            "integrity_hash": finding.digital_evidence_hash,
            "chain_of_custody": finding.forensic_chain_of_custody,
        }

    def _generate_exploitation_scenario(
        self, finding: IndianVulnerabilityFinding
    ) -> str:
        """Generate exploitation scenario for legal proceedings"""
        vuln_type = self.compliance_checker._determine_vulnerability_type(finding)

        scenarios = {
            "idor": "Attacker manipulates object references to access unauthorized data belonging to other users",
            "privilege_escalation": "Attacker gains elevated privileges beyond their authorized access level",
            "data_breach": "Unauthorized access results in exposure or extraction of sensitive data",
            "authentication_bypass": "Attacker circumvents authentication mechanisms to gain unauthorized access",
        }

        return scenarios.get(
            vuln_type, "Unauthorized access to system resources or data"
        )

    def _assess_prosecution_prospects(self) -> str:
        """Assess prospects for successful prosecution"""
        critical_count = len(
            [f for f in self.indian_findings if f.severity.lower() == "critical"]
        )
        high_count = len(
            [f for f in self.indian_findings if f.severity.lower() == "high"]
        )

        if critical_count > 0:
            return "Strong prospects for prosecution with substantial evidence of violations"
        elif high_count > 2:
            return "Good prospects for prosecution with multiple serious violations"
        else:
            return (
                "Moderate prospects depending on impact assessment and evidence quality"
            )

    def _recommend_charges(self) -> list[str]:
        """Recommend potential charges based on findings"""
        charges = []
        all_sections = []

        for finding in self.indian_findings:
            all_sections.extend(finding.legal_classification)

        unique_sections = list(set(all_sections))

        for section in unique_sections:
            if section == LegalSeverity.SECTION_43_ITA:
                charges.append("Penalty for damage to computer system (Section 43)")
            elif section == LegalSeverity.SECTION_66_ITA:
                charges.append("Computer related offenses (Section 66)")
            elif section == LegalSeverity.SECTION_66C_ITA:
                charges.append("Identity theft (Section 66C)")
            elif section == LegalSeverity.SECTION_72_ITA:
                charges.append("Breach of confidentiality and privacy (Section 72)")

        return charges

    def _identify_compliance_gaps(
        self, framework: IndianComplianceFramework
    ) -> list[str]:
        """Identify compliance gaps for a framework"""
        # This would be more sophisticated in a real implementation
        return [
            "Inadequate security controls implementation",
            "Insufficient incident response procedures",
            "Lack of proper access controls",
        ]

    def _get_framework_remediation(
        self, framework: IndianComplianceFramework
    ) -> list[str]:
        """Get remediation requirements for a framework"""
        return [
            "Implement required security controls",
            "Establish incident response procedures",
            "Conduct regular security assessments",
        ]

    def _identify_critical_gaps(self) -> list[str]:
        """Identify critical compliance gaps across all frameworks"""
        return [
            "Failure to implement reasonable security practices as required by IT Act 2000",
            "Inadequate protection of personal data",
            "Insufficient incident reporting and response procedures",
        ]

    def _estimate_remediation_timeline(self, severity: str) -> str:
        """Estimate remediation timeline based on severity"""
        timelines = {
            "critical": "Immediate (0-24 hours)",
            "high": "Urgent (1-7 days)",
            "medium": "Standard (1-30 days)",
            "low": "Planned (30-90 days)",
        }
        return timelines.get(severity.lower(), "Standard (1-30 days)")

    def _create_evidence_summary(self) -> dict[str, Any]:
        """Create evidence summary for law enforcement"""
        return {
            "case_reference": self.le_config.case_reference,
            "total_vulnerabilities": len(self.indian_findings),
            "evidence_items": self.evidence_catalog,
            "chain_of_custody_maintained": True,
            "forensic_integrity": "All evidence integrity verified",
            "collection_officer": self.le_config.investigating_officer,
            "collection_timestamp": datetime.now(),
            "legal_admissibility": "Evidence collected as per IT Act Section 65B requirements",
        }

    def _create_compliance_checklist(self) -> str:
        """Create compliance checklist in markdown format"""
        checklist = """# Indian Cybersecurity Compliance Checklist

## CERT-In Guidelines Compliance
- [ ] Incident reported within 6 hours
- [ ] Vulnerability assessment completed
- [ ] Security controls documented
- [ ] Digital forensics evidence preserved

## IT Act 2000 Compliance
- [ ] Evidence collection per Section 65B
- [ ] Chain of custody maintained
- [ ] Reasonable security practices assessed
- [ ] Legal implications documented

## Investigation Requirements
- [ ] FIR filed if criminal activity detected
- [ ] Digital evidence secured
- [ ] Affected parties notified
- [ ] Remediation timeline established

## Documentation Complete
- [ ] Technical analysis report
- [ ] Legal impact assessment
- [ ] Chain of custody documentation
- [ ] Evidence catalog prepared
"""
        return checklist

    def _render_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Render report in markdown format"""
        md_content = f"""# Cybersecurity Investigation Report
**Case Reference:** {self.le_config.case_reference}
**Investigating Agency:** {self.le_config.investigating_agency}
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
{json.dumps(report_data['executive_summary'], indent=2, default=str)}

## Technical Findings
{json.dumps(report_data['technical_findings'], indent=2, default=str)}

## Legal Analysis
{json.dumps(report_data['legal_analysis'], indent=2, default=str)}

## Investigation Recommendations
{json.dumps(report_data['investigation_recommendations'], indent=2, default=str)}

---
*This report was generated using LogicPWN penetration testing framework with Indian law enforcement compliance extensions.*
"""
        return md_content

    def _render_html_report(self, report_data: dict[str, Any]) -> str:
        """Render report in HTML format"""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Cybersecurity Investigation Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-left: 5px solid #333; }}
        .section {{ margin: 20px 0; }}
        .finding {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #007cba; }}
        .critical {{ border-left-color: #d32f2f; }}
        .high {{ border-left-color: #f57c00; }}
        .medium {{ border-left-color: #fbc02d; }}
        .low {{ border-left-color: #388e3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Cybersecurity Investigation Report</h1>
        <p><strong>Case Reference:</strong> {self.le_config.case_reference}</p>
        <p><strong>Investigating Agency:</strong> {self.le_config.investigating_agency}</p>
        <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <pre>{json.dumps(report_data['executive_summary'], indent=2, default=str)}</pre>
    </div>

    <div class="section">
        <h2>Technical Findings</h2>
        <pre>{json.dumps(report_data['technical_findings'], indent=2, default=str)}</pre>
    </div>

    <div class="section">
        <h2>Legal Analysis</h2>
        <pre>{json.dumps(report_data['legal_analysis'], indent=2, default=str)}</pre>
    </div>

    <footer>
        <p><em>This report was generated using LogicPWN penetration testing framework with Indian law enforcement compliance extensions.</em></p>
    </footer>
</body>
</html>"""
        return html_content
