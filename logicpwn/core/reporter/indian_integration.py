"""
LogicPWN Indian Law Enforcement Integration

This module integrates Indian law enforcement reporting capabilities
with the core LogicPWN penetration testing framework.
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

from logicpwn.core.access import EnhancedAccessTester
from logicpwn.core.access.detector import detect_idor_flaws
from logicpwn.core.auth import AuthConfig, authenticate_session
from logicpwn.core.reporter.framework_mapper import IndianFrameworkMapper
from logicpwn.core.reporter.indian_compliance import IndianComplianceFramework
from logicpwn.core.reporter.indian_law_enforcement import (
    IndianLawEnforcementConfig,
    IndianLawEnforcementReportGenerator,
)
from logicpwn.core.reporter.orchestrator import (
    ReportConfig,
    ReportMetadata,
    VulnerabilityFinding,
)
from logicpwn.core.stress import StressTestConfig, StressTester


class LogicPWNIndianLawEnforcementIntegrator:
    """
    Main integration class that connects LogicPWN testing capabilities
    with Indian law enforcement reporting requirements.
    """

    def __init__(self, law_enforcement_config: IndianLawEnforcementConfig):
        self.le_config = law_enforcement_config
        self.framework_mapper = IndianFrameworkMapper()
        self.findings: list[VulnerabilityFinding] = []
        self.test_results = {
            "idor_results": [],
            "enhanced_access_results": [],
            "exploit_chain_results": [],
            "stress_test_results": [],
            "auth_test_results": [],
        }

    def create_report_config(
        self, target_url: str, report_title: str = None
    ) -> ReportConfig:
        """Create a report configuration for Indian law enforcement"""
        if not report_title:
            report_title = (
                f"Cybersecurity Investigation Report - {self.le_config.case_reference}"
            )

        return ReportConfig(
            target_url=target_url,
            report_title=report_title,
            report_type="indian_law_enforcement",
            format_style="professional",
            include_executive_summary=True,
            include_request_response=True,
            include_steps_to_reproduce=True,
            include_remediation=True,
            redaction_enabled=True,
            cvss_scoring_enabled=True,
            custom_branding={
                "agency": self.le_config.investigating_agency,
                "case_ref": self.le_config.case_reference,
                "officer": self.le_config.investigating_officer,
            },
        )

    def run_comprehensive_security_assessment(
        self,
        target_url: str,
        auth_config: Optional[AuthConfig] = None,
        test_endpoints: Optional[list[str]] = None,
        test_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Run comprehensive security assessment using LogicPWN capabilities
        and generate findings for law enforcement reporting.
        """
        session = None
        if auth_config:
            session = authenticate_session(auth_config)
            self.test_results["auth_test_results"].append(
                {
                    "success": True,
                    "timestamp": datetime.now(),
                    "auth_type": "form_based",
                }
            )

        # Run IDOR detection tests
        if test_endpoints and test_ids:
            idor_findings = self._run_idor_assessment(session, test_endpoints, test_ids)
            self.findings.extend(idor_findings)

        # Run enhanced access control tests
        if session and test_endpoints:
            enhanced_findings = self._run_enhanced_access_assessment(
                session, target_url, test_endpoints
            )
            self.findings.extend(enhanced_findings)

        # Compile comprehensive results
        assessment_results = {
            "total_vulnerabilities": len(self.findings),
            "critical_vulnerabilities": len(
                [f for f in self.findings if f.severity.lower() == "critical"]
            ),
            "high_vulnerabilities": len(
                [f for f in self.findings if f.severity.lower() == "high"]
            ),
            "findings": self.findings,
            "test_summary": self.test_results,
            "compliance_analysis": self._analyze_compliance(),
            "legal_implications": self._analyze_legal_implications(),
        }

        return assessment_results

    def _run_idor_assessment(
        self, session, test_endpoints: list[str], test_ids: list[str]
    ) -> list[VulnerabilityFinding]:
        """Run IDOR assessment and convert results to vulnerability findings"""
        findings = []

        for endpoint in test_endpoints:
            try:
                idor_results = detect_idor_flaws(
                    session=session,
                    endpoint_template=endpoint,
                    test_ids=test_ids,
                    success_indicators=["user", "profile", "data", "account"],
                    failure_indicators=["unauthorized", "access denied", "403", "401"],
                )

                self.test_results["idor_results"].extend(idor_results)

                # Convert IDOR results to vulnerability findings
                for result in idor_results:
                    if result.vulnerability_detected:
                        finding = VulnerabilityFinding(
                            id=f"IDOR_{result.id_tested}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            title=f"Insecure Direct Object Reference - {endpoint}",
                            severity="High",
                            description=f"IDOR vulnerability allows unauthorized access to resources belonging to user ID {result.id_tested}",
                            affected_endpoints=[result.endpoint_url],
                            proof_of_concept=f"Accessing {result.endpoint_url} with ID {result.id_tested} returns data unauthorized",
                            impact="Unauthorized access to sensitive user data, potential privacy violations",
                            remediation="Implement proper access controls and object-level authorization checks",
                            references=[
                                "OWASP Top 10 - Broken Access Control",
                                "CWE-639: Authorization Bypass",
                            ],
                            discovered_at=datetime.now(),
                        )
                        findings.append(finding)

            except Exception as e:
                print(f"Error in IDOR assessment for {endpoint}: {str(e)}")

        return findings

    def _run_enhanced_access_assessment(
        self, session, base_url: str, test_endpoints: list[str]
    ) -> list[VulnerabilityFinding]:
        """Run enhanced access control assessment"""
        findings = []

        try:
            enhanced_tester = EnhancedAccessTester()

            for endpoint in test_endpoints:
                results = asyncio.run(
                    enhanced_tester.run_comprehensive_access_test(
                        session=session,
                        base_url=base_url,
                        endpoint_template=endpoint,
                        example_ids=["1", "2", "3", "admin", "test"],
                        success_indicators=["user", "profile", "data"],
                        failure_indicators=["unauthorized", "403", "401"],
                    )
                )

                self.test_results["enhanced_access_results"].append(results)

                # Convert enhanced results to findings
                if results.vulnerabilities_found > 0:
                    finding = VulnerabilityFinding(
                        id=f"ENHANCED_ACCESS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        title=f"Enhanced Access Control Vulnerabilities - {endpoint}",
                        severity=(
                            "High" if results.critical_vulnerabilities > 0 else "Medium"
                        ),
                        description=f"Enhanced access testing found {results.vulnerabilities_found} vulnerabilities",
                        affected_endpoints=[endpoint],
                        proof_of_concept=f"Enhanced testing revealed access control weaknesses in {endpoint}",
                        impact="Multiple access control vulnerabilities allowing unauthorized data access",
                        remediation="Implement comprehensive access control review and remediation",
                        references=["OWASP ASVS - Access Control Requirements"],
                        discovered_at=datetime.now(),
                    )
                    findings.append(finding)

        except Exception as e:
            print(f"Error in enhanced access assessment: {str(e)}")

        return findings

    def _analyze_compliance(self) -> dict[str, Any]:
        """Analyze findings against Indian compliance frameworks"""
        compliance_analysis = {
            "frameworks_assessed": [
                framework.value for framework in IndianComplianceFramework
            ],
            "compliance_gaps": [],
            "legal_violations": [],
            "remediation_requirements": [],
        }

        for finding in self.findings:
            # Map findings to compliance frameworks
            vuln_type = self._determine_vulnerability_type(finding)
            framework_mappings = self.framework_mapper.map_vulnerability_to_frameworks(
                vuln_type, finding.severity
            )

            for mapping in framework_mappings:
                if mapping.compliance_status.value == "non_compliant":
                    compliance_analysis["compliance_gaps"].append(
                        {
                            "framework": mapping.framework.value,
                            "requirement": mapping.requirement.value,
                            "description": mapping.description,
                            "legal_implications": mapping.legal_implications,
                        }
                    )

        return compliance_analysis

    def _analyze_legal_implications(self) -> dict[str, Any]:
        """Analyze legal implications of findings"""
        legal_analysis = {
            "applicable_laws": [
                "Information Technology Act 2000",
                "Indian Penal Code 1860",
            ],
            "potential_violations": [],
            "recommended_actions": [],
            "prosecution_prospects": "To be assessed based on evidence quality",
        }

        critical_count = len(
            [f for f in self.findings if f.severity.lower() == "critical"]
        )
        high_count = len([f for f in self.findings if f.severity.lower() == "high"])

        if critical_count > 0:
            legal_analysis["potential_violations"].append(
                "Critical security vulnerabilities may constitute violations under IT Act 2000"
            )
            legal_analysis["recommended_actions"].append(
                "Immediate incident reporting to CERT-In"
            )
            legal_analysis["prosecution_prospects"] = (
                "Strong evidence for potential prosecution"
            )

        if high_count > 2:
            legal_analysis["potential_violations"].append(
                "Multiple high-severity vulnerabilities indicate systemic security failures"
            )
            legal_analysis["recommended_actions"].append(
                "Comprehensive security audit and remediation required"
            )

        return legal_analysis

    def _determine_vulnerability_type(self, finding: VulnerabilityFinding) -> str:
        """Determine vulnerability type from finding"""
        title_lower = finding.title.lower()

        if "idor" in title_lower or "direct object" in title_lower:
            return "idor"
        elif "privilege" in title_lower or "escalation" in title_lower:
            return "privilege_escalation"
        elif "access control" in title_lower:
            return "unauthorized_access"
        elif "sql injection" in title_lower:
            return "sql_injection"
        elif "xss" in title_lower or "cross-site scripting" in title_lower:
            return "xss"
        elif "csrf" in title_lower or "cross-site request" in title_lower:
            return "csrf"
        else:
            return "system_damage"

    def generate_law_enforcement_report(
        self, target_url: str, output_dir: str = "./reports"
    ) -> dict[str, str]:
        """Generate comprehensive law enforcement report"""
        # Create report configuration
        report_config = self.create_report_config(target_url)

        # Create report metadata
        metadata = ReportMetadata(
            report_id=f"LE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=report_config.report_title,
            target_url=target_url,
            scan_start_time=datetime.now(),
            scan_end_time=datetime.now(),
            logicpwn_version="1.0.0",
            authenticated_user=self.le_config.investigating_officer,
            total_requests=sum(
                [len(results) for results in self.test_results.values()]
            ),
            findings_count={
                "critical": len(
                    [f for f in self.findings if f.severity.lower() == "critical"]
                ),
                "high": len([f for f in self.findings if f.severity.lower() == "high"]),
                "medium": len(
                    [f for f in self.findings if f.severity.lower() == "medium"]
                ),
                "low": len([f for f in self.findings if f.severity.lower() == "low"]),
            },
        )

        # Create Indian law enforcement report generator
        le_report_generator = IndianLawEnforcementReportGenerator(
            report_config, self.le_config
        )

        # Add findings with compliance classification
        for finding in self.findings:
            le_report_generator.add_finding_with_compliance(finding)

        # Generate and export comprehensive report package
        files_created = le_report_generator.export_law_enforcement_package(output_dir)

        return files_created

    def run_stress_test_for_evidence(
        self, target_urls: list[str], duration: int = 30, max_concurrent: int = 10
    ) -> dict[str, Any]:
        """Run stress test to gather performance evidence"""
        try:
            stress_config = StressTestConfig(
                max_concurrent=max_concurrent, duration=duration, memory_monitoring=True
            )

            stress_results = asyncio.run(
                self._run_async_stress_test(stress_config, target_urls)
            )
            self.test_results["stress_test_results"].append(stress_results)

            return {
                "stress_test_completed": True,
                "performance_metrics": stress_results,
                "evidence_collected": True,
            }

        except Exception as e:
            return {
                "stress_test_completed": False,
                "error": str(e),
                "evidence_collected": False,
            }

    async def _run_async_stress_test(
        self, config: StressTestConfig, target_urls: list[str]
    ) -> dict[str, Any]:
        """Run asynchronous stress test"""
        async with StressTester(config) as tester:
            target_configs = [{"url": url, "method": "GET"} for url in target_urls]
            metrics = await tester.run_stress_test(target_configs)

            return {
                "requests_per_second": metrics.requests_per_second,
                "error_rate": metrics.error_rate,
                "avg_response_time": metrics.avg_response_time,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
            }


def create_indian_law_enforcement_assessment(
    target_url: str,
    investigating_agency: str,
    case_reference: str,
    investigating_officer: str,
    auth_config: Optional[AuthConfig] = None,
    test_endpoints: Optional[list[str]] = None,
    test_ids: Optional[list[str]] = None,
    output_dir: str = "./reports",
) -> dict[str, Any]:
    """
    Convenience function to create a complete Indian law enforcement assessment
    """
    # Create law enforcement configuration
    le_config = IndianLawEnforcementConfig(
        investigating_agency=investigating_agency,
        case_reference=case_reference,
        investigating_officer=investigating_officer,
        jurisdiction="India",
        incident_classification="cyber_crime",
        priority_level="high",
        compliance_frameworks=[
            IndianComplianceFramework.IT_ACT_2000,
            IndianComplianceFramework.CERT_IN,
            IndianComplianceFramework.DIGITAL_INDIA,
        ],
        include_chain_of_custody=True,
        include_legal_analysis=True,
        include_remediation_timeline=True,
    )

    # Create integrator
    integrator = LogicPWNIndianLawEnforcementIntegrator(le_config)

    # Run comprehensive assessment
    assessment_results = integrator.run_comprehensive_security_assessment(
        target_url=target_url,
        auth_config=auth_config,
        test_endpoints=test_endpoints
        or [f"{target_url}/api/users/{{id}}", f"{target_url}/api/data/{{id}}"],
        test_ids=test_ids or ["1", "2", "3", "admin", "test"],
    )

    # Generate law enforcement report
    report_files = integrator.generate_law_enforcement_report(target_url, output_dir)

    return {
        "assessment_results": assessment_results,
        "report_files": report_files,
        "integrator": integrator,
        "law_enforcement_config": le_config,
    }


# Example usage function for law enforcement
def example_indian_law_enforcement_usage():
    """Example usage of Indian law enforcement integration"""

    # Authentication configuration (if target requires authentication)
    auth_config = AuthConfig(
        url="https://target.com/login",
        credentials={"username": "testuser", "password": "testpass"},
        success_indicators=["dashboard", "welcome"],
    )

    # Run comprehensive assessment
    results = create_indian_law_enforcement_assessment(
        target_url="https://target.com",
        investigating_agency="Cyber Crime Investigation Cell, Delhi",
        case_reference="CC_2025_08_001",
        investigating_officer="Inspector Rajesh Kumar",
        auth_config=auth_config,
        test_endpoints=[
            "https://target.com/api/users/{id}",
            "https://target.com/api/profiles/{id}",
            "https://target.com/admin/users/{id}",
        ],
        test_ids=["1", "2", "3", "admin", "test", "100", "999"],
        output_dir="./investigation_reports",
    )

    print("Assessment completed:")
    print(
        f"Total vulnerabilities found: {results['assessment_results']['total_vulnerabilities']}"
    )
    print(
        f"Critical vulnerabilities: {results['assessment_results']['critical_vulnerabilities']}"
    )
    print(f"Report files generated: {list(results['report_files'].keys())}")

    return results
