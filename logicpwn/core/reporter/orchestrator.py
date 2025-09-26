"""
LogicPwn Reporting Orchestrator
- Professional, extensible, and performant report generation
- Integrates with all core modules (auth, detector, exploit_engine)
- Uses centralized redaction, cache, and performance utilities
- Enhanced with NIST-compliant CVSS, input validation, and authentication
"""

import logging
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from logicpwn.core.performance import monitor_performance
from logicpwn.core.reporter.auth_manager import (
    AuthenticationError,
    AuthorizationError,
    Permission,
    ReportAuthManager,
    User,
)
from logicpwn.core.reporter.cvss import (
    AttackComplexity,
    AttackVector,
    CVSSCalculator,
    CVSSVector,
    ImpactMetric,
    PrivilegesRequired,
    Scope,
    UserInteraction,
)
from logicpwn.core.reporter.input_validator import InputValidator, ValidationError
from logicpwn.core.reporter.models import RedactionRule
from logicpwn.core.reporter.redactor import AdvancedRedactor

logger = logging.getLogger(__name__)


# --- Data Models ---
class VulnerabilityFinding(BaseModel):
    """
    Represents a single vulnerability finding for reporting.
    """

    id: str
    title: str
    severity: str  # "Critical", "High", "Medium", "Low", "Info"
    cvss_score: Optional[float] = None
    description: str
    affected_endpoints: list[str]
    proof_of_concept: str
    impact: str
    remediation: str
    references: list[str] = []
    discovered_at: datetime
    exploit_chain: Optional[list[Any]] = None  # ExploitStepResult
    request_response_pairs: list[Any] = []  # RequestResponsePair


class ReportMetadata(BaseModel):
    """
    Metadata for a vulnerability report, including scan details and summary stats.
    """

    report_id: str
    title: str
    target_url: str
    scan_start_time: datetime
    scan_end_time: datetime
    logicpwn_version: str
    authenticated_user: Optional[str] = None
    total_requests: int
    findings_count: dict[str, int]


class ReportConfig(BaseModel):
    """
    Configuration for report generation, including output style, redaction, and branding.
    """

    target_url: str
    report_title: str
    report_type: str = "vapt"
    format_style: str = "professional"
    include_executive_summary: bool = True
    include_request_response: bool = True
    include_steps_to_reproduce: bool = True
    include_remediation: bool = True
    redaction_enabled: bool = True
    cvss_scoring_enabled: bool = True
    custom_branding: Optional[dict[str, str]] = None
    redaction_rules: list[RedactionRule] = []


# --- Security Enhanced Models ---
class SecureVulnerabilityFinding(BaseModel):
    """
    Security-enhanced vulnerability finding with input validation.
    """

    @classmethod
    def from_dict(cls, data: dict) -> "SecureVulnerabilityFinding":
        """Create from dictionary with input validation."""
        try:
            validated_input = InputValidator.validate_vulnerability_finding(data)
            return cls(
                id=validated_input.id,
                title=validated_input.title,
                severity=validated_input.severity,
                description=validated_input.description,
                affected_endpoints=validated_input.affected_endpoints,
                proof_of_concept=validated_input.proof_of_concept,
                impact=validated_input.impact,
                remediation=validated_input.remediation,
                references=validated_input.references,
                discovered_at=data.get("discovered_at", datetime.now()),
                cvss_score=data.get("cvss_score"),
                exploit_chain=data.get("exploit_chain"),
                request_response_pairs=data.get("request_response_pairs", []),
            )
        except ValidationError as e:
            logger.error(f"Validation failed for vulnerability finding: {e}")
            raise


class SecureReportConfig(BaseModel):
    """
    Security-enhanced report configuration with input validation.
    """

    @classmethod
    def from_dict(cls, data: dict) -> "SecureReportConfig":
        """Create from dictionary with input validation."""
        try:
            validated_input = InputValidator.validate_report_config(data)
            return cls(
                target_url=validated_input.target_url,
                report_title=validated_input.report_title,
                report_type=validated_input.report_type,
                format_style=validated_input.format_style,
                authenticated_user=validated_input.authenticated_user,
                include_executive_summary=data.get("include_executive_summary", True),
                include_request_response=data.get("include_request_response", True),
                include_steps_to_reproduce=data.get("include_steps_to_reproduce", True),
                include_remediation=data.get("include_remediation", True),
                redaction_enabled=data.get("redaction_enabled", True),
                cvss_scoring_enabled=data.get("cvss_scoring_enabled", True),
                custom_branding=data.get("custom_branding"),
                redaction_rules=data.get("redaction_rules", []),
            )
        except ValidationError as e:
            logger.error(f"Validation failed for report config: {e}")
            raise


# --- Main Orchestrator ---
class SecureReportGenerator:
    """
    Security-enhanced report generator with authentication, input validation, and audit logging.
    Provides comprehensive security controls for vulnerability report generation.
    """

    def __init__(
        self, config: ReportConfig, auth_manager: Optional[ReportAuthManager] = None
    ):
        """
        Initialize the secure report generator.

        Args:
            config: Report configuration (will be validated)
            auth_manager: Authentication manager for access control
        """
        # Validate configuration
        self.config = config
        self.findings: list[VulnerabilityFinding] = []
        self.metadata: Optional[ReportMetadata] = None

        # Initialize security components
        self.auth_manager = auth_manager
        self.redactor = None
        if config.redaction_enabled:
            custom_rules = getattr(config, "redaction_rules", [])
            self.redactor = AdvancedRedactor(custom_rules)

        # Initialize audit logging
        self.audit_log = []

        # Initialize metadata
        self._initialize_metadata()

        logger.info("Secure report generator initialized")

    def _initialize_metadata(self):
        """Initialize report metadata with default values."""
        from datetime import datetime

        self.metadata = ReportMetadata(
            report_id=f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            title="Security Assessment Report",
            target_url=self.config.target_url or "Unknown",
            scan_start_time=datetime.utcnow(),
            scan_end_time=datetime.utcnow(),
            logicpwn_version="1.0.0",
            authenticated_user=None,
            total_requests=0,
            findings_count={"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0},
        )

    def authenticate_user(
        self, auth_token: str = None, api_key: str = None, session_id: str = None
    ) -> User:
        """
        Authenticate user for report access.

        Args:
            auth_token: JWT authentication token
            api_key: API key for authentication
            session_id: Session ID for authentication

        Returns:
            Authenticated user

        Raises:
            AuthenticationError: If authentication fails
        """
        if not self.auth_manager:
            # If no auth manager, create default one
            self.auth_manager = ReportAuthManager()

        user = None
        auth_method = None

        try:
            if auth_token:
                user = self.auth_manager.authenticate_jwt(auth_token)
                auth_method = "jwt"
            elif api_key:
                user = self.auth_manager.authenticate_api_key(api_key)
                auth_method = "api_key"
            elif session_id:
                user = self.auth_manager.validate_session(session_id)
                auth_method = "session"
                if not user:
                    raise AuthenticationError("Invalid or expired session")
            else:
                raise AuthenticationError("No authentication credentials provided")

            self._log_audit_event(
                "authentication_success",
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "auth_method": auth_method,
                },
            )

            return user

        except Exception as e:
            self._log_audit_event(
                "authentication_failure", {"auth_method": auth_method, "error": str(e)}
            )
            raise

    def add_finding(self, finding_data: dict, user: User = None) -> None:
        """
        Add a vulnerability finding with security validation.

        Args:
            finding_data: Raw finding data (will be validated)
            user: Authenticated user (if None, will use default)
        """
        try:
            # Validate user permissions
            if user and self.auth_manager:
                self.auth_manager.require_permission(user, Permission.WRITE_REPORTS)

            # Validate input data
            validated_finding = InputValidator.validate_vulnerability_finding(
                finding_data
            )

            # Create VulnerabilityFinding from validated data
            finding = VulnerabilityFinding(
                id=validated_finding.id,
                title=validated_finding.title,
                severity=validated_finding.severity,
                description=validated_finding.description,
                affected_endpoints=validated_finding.affected_endpoints,
                proof_of_concept=validated_finding.proof_of_concept,
                impact=validated_finding.impact,
                remediation=validated_finding.remediation,
                references=validated_finding.references,
                discovered_at=finding_data.get("discovered_at", datetime.now()),
                cvss_score=None,  # Will be calculated
                exploit_chain=finding_data.get("exploit_chain"),
                request_response_pairs=finding_data.get("request_response_pairs", []),
            )

            # Calculate NIST-compliant CVSS score if enabled
            if self.config.cvss_scoring_enabled and finding.cvss_score is None:
                finding.cvss_score = self._calculate_cvss_score(finding)

            self.findings.append(finding)

            self._log_audit_event(
                "finding_added",
                {
                    "finding_id": finding.id,
                    "severity": finding.severity,
                    "user_id": user.user_id if user else "system",
                },
            )

            logger.info(f"Finding added: {finding.id} ({finding.severity})")

        except ValidationError as e:
            logger.error(f"Finding validation failed: {e}")
            self._log_audit_event(
                "finding_validation_failed",
                {"error": str(e), "user_id": user.user_id if user else "system"},
            )
            raise
        except AuthorizationError as e:
            logger.error(f"Finding authorization failed: {e}")
            self._log_audit_event(
                "finding_authorization_failed",
                {"error": str(e), "user_id": user.user_id if user else "system"},
            )
            raise

    def _calculate_cvss_score(self, finding: VulnerabilityFinding) -> float:
        """Calculate NIST-compliant CVSS score for finding."""
        try:
            # Map severity to CVSS metrics (simplified mapping)
            severity_map = {
                "Critical": {
                    "confidentiality": "High",
                    "integrity": "High",
                    "availability": "High",
                },
                "High": {
                    "confidentiality": "High",
                    "integrity": "Low",
                    "availability": "Low",
                },
                "Medium": {
                    "confidentiality": "Low",
                    "integrity": "Low",
                    "availability": "None",
                },
                "Low": {
                    "confidentiality": "Low",
                    "integrity": "None",
                    "availability": "None",
                },
                "Info": {
                    "confidentiality": "None",
                    "integrity": "None",
                    "availability": "None",
                },
            }

            metrics = severity_map.get(finding.severity, severity_map["Medium"])

            # Create CVSS vector
            vector = CVSSVector(
                attack_vector=AttackVector.NETWORK,
                attack_complexity=AttackComplexity.LOW,
                privileges_required=PrivilegesRequired.NONE,
                user_interaction=UserInteraction.NONE,
                scope=Scope.UNCHANGED,
                confidentiality=ImpactMetric(metrics["confidentiality"]),
                integrity=ImpactMetric(metrics["integrity"]),
                availability=ImpactMetric(metrics["availability"]),
            )

            # Calculate full score
            score_result = CVSSCalculator.calculate_full_score(vector)

            logger.debug(
                f"CVSS calculated for {finding.id}: {score_result.base_score} ({score_result.severity})"
            )
            return score_result.base_score

        except Exception as e:
            logger.error(f"CVSS calculation failed for {finding.id}: {e}")
            return 0.0

    @monitor_performance("secure_report_generation")
    def generate_report(
        self,
        format: str = "markdown",
        user: User = None,
        template_dir: Optional[str] = None,
    ) -> str:
        """
        Generate report with security controls and audit logging.

        Args:
            format: Output format (markdown, html, json, etc.)
            user: Authenticated user
            template_dir: Optional template directory

        Returns:
            Generated report content

        Raises:
            AuthorizationError: If user lacks permissions
            ValidationError: If inputs are invalid
        """
        try:
            # Validate user permissions
            if user and self.auth_manager:
                self.auth_manager.require_permission(user, Permission.READ_REPORTS)

            # Validate format
            validated_format = InputValidator.validate_report_format(format)

            # Validate template directory if provided
            if template_dir:
                template_dir = InputValidator.validate_file_path(template_dir)

            # Generate report using existing logic
            from logicpwn.exporters import get_exporter

            exporter = get_exporter(validated_format)
            if hasattr(exporter, "set_template_dir") and template_dir:
                exporter.set_template_dir(template_dir)

            content = exporter.export(self.findings, self.metadata)

            # Apply redaction if enabled
            if self.redactor:
                content = self.redactor.redact_string_body(content)

            # Add security headers to content if HTML format
            if validated_format == "html":
                content = self._add_security_headers(content)

            self._log_audit_event(
                "report_generated",
                {
                    "format": validated_format,
                    "findings_count": len(self.findings),
                    "user_id": user.user_id if user else "system",
                },
            )

            logger.info(
                f"Report generated: {validated_format} format, {len(self.findings)} findings"
            )
            return content

        except Exception as e:
            self._log_audit_event(
                "report_generation_failed",
                {
                    "format": format,
                    "error": str(e),
                    "user_id": user.user_id if user else "system",
                },
            )
            logger.error(f"Report generation failed: {e}")
            raise

    def _add_security_headers(self, html_content: str) -> str:
        """Add security headers to HTML content."""
        if not html_content.strip():
            return html_content

        # Add CSP and other security headers via meta tags
        security_meta_tags = """
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
"""

        # Insert security headers after <head> tag
        if "<head>" in html_content:
            html_content = html_content.replace("<head>", f"<head>{security_meta_tags}")

        return html_content

    def export_to_file(
        self,
        filepath: str,
        format: str,
        user: User = None,
        template_dir: Optional[str] = None,
    ) -> None:
        """
        Export report to file with security validation.

        Args:
            filepath: Output file path (will be validated)
            format: Report format
            user: Authenticated user
            template_dir: Optional template directory
        """
        try:
            # Validate file path
            safe_filepath = InputValidator.validate_file_path(filepath)

            # Generate report
            report = self.generate_report(format, user, template_dir)

            # Write to file
            with open(safe_filepath, "w", encoding="utf-8") as f:
                f.write(report)

            self._log_audit_event(
                "report_exported",
                {
                    "filepath": safe_filepath,
                    "format": format,
                    "user_id": user.user_id if user else "system",
                },
            )

            logger.info(f"Report exported to: {safe_filepath}")

        except Exception as e:
            self._log_audit_event(
                "report_export_failed",
                {
                    "filepath": filepath,
                    "error": str(e),
                    "user_id": user.user_id if user else "system",
                },
            )
            raise

    def _log_audit_event(self, event_type: str, details: dict):
        """Log audit event for compliance."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
        }

        self.audit_log.append(audit_entry)

        # Also log to main logger for external audit systems
        logger.info(f"AUDIT: {event_type}", extra={"audit_details": details})

    def get_audit_log(self, user: User = None) -> list:
        """
        Get audit log entries.

        Args:
            user: Authenticated user

        Returns:
            List of audit log entries

        Raises:
            AuthorizationError: If user lacks audit permissions
        """
        if user and self.auth_manager:
            self.auth_manager.require_permission(user, Permission.AUDIT_LOGS)

        return self.audit_log.copy()

    def encrypt_sensitive_findings(self, user: User = None) -> None:
        """
        Encrypt sensitive data in findings.

        Args:
            user: Authenticated user
        """
        if not self.auth_manager:
            logger.warning("No auth manager available for encryption")
            return

        if user:
            self.auth_manager.require_permission(user, Permission.ADMIN_REPORTS)

        for finding in self.findings:
            # Encrypt sensitive fields
            if hasattr(finding, "proof_of_concept") and finding.proof_of_concept:
                finding.proof_of_concept = self.auth_manager.encrypt_sensitive_data(
                    finding.proof_of_concept
                )

            if hasattr(finding, "description") and finding.description:
                finding.description = self.auth_manager.encrypt_sensitive_data(
                    finding.description
                )

        self._log_audit_event(
            "findings_encrypted",
            {
                "findings_count": len(self.findings),
                "user_id": user.user_id if user else "system",
            },
        )

        logger.info(f"Encrypted sensitive data in {len(self.findings)} findings")


# --- Legacy Compatibility ---
class ReportGenerator:
    """
    Legacy ReportGenerator class for backward compatibility.
    Wraps SecureReportGenerator with default security settings.
    """

    def __init__(self, config: ReportConfig):
        """Initialize with legacy interface but enhanced security."""
        # Enable security by default for new instances
        self.secure_generator = SecureReportGenerator(config)
        self.findings = self.secure_generator.findings
        self.metadata = self.secure_generator.metadata
        self.config = config

        # Initialize redactor for backward compatibility
        self.redactor = self.secure_generator.redactor

        logger.info("Legacy ReportGenerator initialized with security enhancements")

    def add_finding(self, finding_data: dict) -> None:
        """Add finding with legacy interface."""
        try:
            # Convert dict to VulnerabilityFinding if needed
            if isinstance(finding_data, dict):
                self.secure_generator.add_finding(finding_data)
            else:
                # Assume it's already a VulnerabilityFinding object
                self.findings.append(finding_data)
        except Exception as e:
            logger.error(f"Legacy add_finding failed: {e}")
            # Fallback to basic validation for legacy compatibility
            if isinstance(finding_data, dict):
                finding = VulnerabilityFinding(**finding_data)
                self.findings.append(finding)
            else:
                self.findings.append(finding_data)

    def set_metadata(self, metadata: ReportMetadata) -> None:
        """Set report metadata."""
        self.metadata = metadata
        self.secure_generator.metadata = metadata

    @monitor_performance("legacy_report_generation")
    def generate_report(
        self, format: str = "markdown", template_dir: Optional[str] = None
    ) -> str:
        """Generate report with legacy interface but enhanced security."""
        try:
            # Use secure generator but without authentication requirement
            return self.secure_generator.generate_report(
                format, user=None, template_dir=template_dir
            )
        except Exception as e:
            logger.error(f"Legacy report generation failed: {e}")
            # Fallback to basic generation for legacy compatibility
            from logicpwn.exporters import get_exporter

            exporter = get_exporter(format)
            if hasattr(exporter, "set_template_dir") and template_dir:
                exporter.set_template_dir(template_dir)

            # Ensure metadata is not None
            metadata = self.metadata or ReportMetadata(
                report_id="legacy-report",
                title="Legacy Report",
                target_url="unknown",
                scan_start_time=datetime.now(),
                scan_end_time=datetime.now(),
                logicpwn_version="unknown",
                total_requests=0,
                findings_count={},
            )

            content = exporter.export(self.findings, metadata)

            # Apply redaction if available
            if self.redactor:
                content = self.redactor.redact_string_body(content)

            return content

    def export_to_file(
        self, filepath: str, format: str, template_dir: Optional[str] = None
    ) -> None:
        """Export report to file with legacy interface."""
        try:
            self.secure_generator.export_to_file(
                filepath, format, user=None, template_dir=template_dir
            )
        except Exception as e:
            logger.error(f"Legacy export failed: {e}")
            # Fallback for legacy compatibility
            report = self.generate_report(format, template_dir)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)

    # Backward compatibility methods
    def add_redaction_rule(self, rule: RedactionRule) -> None:
        """Add redaction rule (legacy compatibility)."""
        if self.redactor and hasattr(self.redactor, "custom_rules"):
            self.redactor.custom_rules.append(rule)

    def get_findings_summary(self) -> dict:
        """Get summary of findings by severity."""
        summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        for finding in self.findings:
            if finding.severity in summary:
                summary[finding.severity] += 1
        return summary

    def calculate_risk_score(self) -> float:
        """Calculate overall risk score based on findings."""
        total_score = 0.0
        for finding in self.findings:
            if finding.cvss_score:
                total_score += finding.cvss_score

        return min(total_score / len(self.findings) if self.findings else 0.0, 10.0)

    # New security methods (optional for legacy users)
    def enable_security_features(
        self, auth_manager: ReportAuthManager = None
    ) -> SecureReportGenerator:
        """
        Enable enhanced security features.

        Returns:
            SecureReportGenerator instance for advanced security features
        """
        if auth_manager:
            self.secure_generator.auth_manager = auth_manager

        logger.info("Security features enabled for legacy ReportGenerator")
        return self.secure_generator

    def get_audit_log(self) -> list:
        """Get audit log if available."""
        return self.secure_generator.audit_log
