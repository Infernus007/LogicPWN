#!/usr/bin/env python3
"""
LogicPWN Indian Law Enforcement Example

This example demonstrates how to use LogicPWN's enhanced reporting
capabilities for Indian law enforcement agencies to conduct cybersecurity
investigations and generate compliance reports.

Usage:
    python indian_law_enforcement_example.py --target https://example.com --case CC_2025_001
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# LogicPWN Core Imports
from logicpwn.core.auth import AuthConfig

# Indian Law Enforcement Reporter Imports
from logicpwn.core.reporter import (
    IndianComplianceFramework,
    IndianLawEnforcementConfig,
    create_indian_law_enforcement_assessment,
)
from logicpwn.core.runner import send_request


def setup_investigation_config(args) -> IndianLawEnforcementConfig:
    """Setup investigation configuration from command line arguments"""
    return IndianLawEnforcementConfig(
        investigating_agency=args.agency,
        fir_number=args.fir,
        case_reference=args.case,
        investigating_officer=args.officer,
        jurisdiction=args.jurisdiction,
        incident_classification=args.classification,
        priority_level=args.priority,
        legal_authorization=f"Investigation authorized under IT Act 2000 - Case {args.case}",
        digital_forensics_team=args.forensics_team,
        compliance_frameworks=[
            IndianComplianceFramework.IT_ACT_2000,
            IndianComplianceFramework.CERT_IN,
            IndianComplianceFramework.DIGITAL_INDIA,
            IndianComplianceFramework.NCIIPC,
        ],
        include_chain_of_custody=True,
        include_legal_analysis=True,
        include_remediation_timeline=True,
        redaction_level="standard",
    )


def create_auth_config(args) -> AuthConfig:
    """Create authentication configuration if credentials provided"""
    if args.username and args.password:
        return AuthConfig(
            url=f"{args.target}/login",
            credentials={"username": args.username, "password": args.password},
            success_indicators=["dashboard", "welcome", "home", "profile"],
            failure_indicators=["error", "invalid", "failed", "unauthorized"],
        )
    return None


def generate_test_endpoints(target_url: str) -> list:
    """Generate common test endpoints for IDOR testing"""
    base_endpoints = [
        "/api/users/{id}",
        "/api/profiles/{id}",
        "/api/accounts/{id}",
        "/api/data/{id}",
        "/admin/users/{id}",
        "/user/{id}/profile",
        "/documents/{id}",
        "/files/{id}",
        "/reports/{id}",
        "/dashboard/user/{id}",
    ]

    return [f"{target_url.rstrip('/')}{endpoint}" for endpoint in base_endpoints]


def generate_test_ids() -> list:
    """Generate test IDs for IDOR detection"""
    return [
        "1",
        "2",
        "3",
        "4",
        "5",
        "10",
        "100",
        "1000",
        "admin",
        "administrator",
        "root",
        "test",
        "demo",
        "guest",
        "user1",
        "user2",
        "user3",
        "a1b2c3",
        "123abc",
        "abc123",
        "00001",
        "99999",
    ]


def run_basic_reconnaissance(target_url: str) -> dict:
    """Run basic reconnaissance to gather target information"""
    print(f"[+] Running basic reconnaissance on {target_url}")

    recon_results = {
        "target_accessible": False,
        "server_info": {},
        "security_headers": {},
        "endpoints_discovered": [],
    }

    try:
        # Test basic connectivity
        response = send_request(None, {"url": target_url, "method": "GET"})
        recon_results["target_accessible"] = True
        recon_results["server_info"] = {
            "status_code": response.status_code,
            "server": response.headers.get("Server", "Unknown"),
            "powered_by": response.headers.get("X-Powered-By", "Unknown"),
        }

        # Check security headers
        security_headers = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
        ]

        for header in security_headers:
            recon_results["security_headers"][header] = response.headers.get(
                header, "Missing"
            )

        print(f"[+] Target is accessible (Status: {response.status_code})")

        # Test common endpoints
        common_paths = ["/api", "/admin", "/login", "/dashboard", "/user", "/profile"]
        for path in common_paths:
            test_url = f"{target_url.rstrip('/')}{path}"
            try:
                test_response = send_request(None, {"url": test_url, "method": "GET"})
                if test_response.status_code != 404:
                    recon_results["endpoints_discovered"].append(
                        {"path": path, "status": test_response.status_code}
                    )
            except Exception:
                continue

    except Exception as e:
        print(f"[-] Reconnaissance failed: {str(e)}")
        recon_results["error"] = str(e)

    return recon_results


def run_indian_law_enforcement_investigation(args):
    """Run comprehensive cybersecurity investigation for Indian law enforcement"""

    print("=" * 80)
    print("LogicPWN - Indian Law Enforcement Cybersecurity Investigation")
    print("=" * 80)
    print(f"Target: {args.target}")
    print(f"Case Reference: {args.case}")
    print(f"Investigating Agency: {args.agency}")
    print(f"Investigating Officer: {args.officer}")
    print(f"Investigation Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Step 1: Basic reconnaissance
    print("\n[PHASE 1] Basic Reconnaissance")
    recon_results = run_basic_reconnaissance(args.target)

    if not recon_results["target_accessible"]:
        print(
            f"[-] Target {args.target} is not accessible. Investigation cannot proceed."
        )
        return False

    print(
        f"[+] Reconnaissance completed. Found {len(recon_results['endpoints_discovered'])} endpoints"
    )

    # Step 2: Setup investigation configuration
    print("\n[PHASE 2] Investigation Setup")
    le_config = setup_investigation_config(args)
    auth_config = create_auth_config(args)

    print("[+] Investigation configuration created")
    print(
        f"[+] Compliance frameworks: {[fw.value for fw in le_config.compliance_frameworks]}"
    )

    # Step 3: Run comprehensive security assessment
    print("\n[PHASE 3] Security Assessment")
    test_endpoints = generate_test_endpoints(args.target)
    test_ids = generate_test_ids()

    print(
        f"[+] Testing {len(test_endpoints)} endpoints with {len(test_ids)} ID variations"
    )

    try:
        # Use the convenience function for assessment
        assessment_results = create_indian_law_enforcement_assessment(
            target_url=args.target,
            investigating_agency=args.agency,
            case_reference=args.case,
            investigating_officer=args.officer,
            auth_config=auth_config,
            test_endpoints=test_endpoints,
            test_ids=test_ids,
            output_dir=args.output_dir,
        )

        print("[+] Security assessment completed")
        print(
            f"[+] Total vulnerabilities found: {assessment_results['assessment_results']['total_vulnerabilities']}"
        )
        print(
            f"[+] Critical vulnerabilities: {assessment_results['assessment_results']['critical_vulnerabilities']}"
        )
        print(
            f"[+] High severity vulnerabilities: {assessment_results['assessment_results']['high_vulnerabilities']}"
        )

    except Exception as e:
        print(f"[-] Security assessment failed: {str(e)}")
        return False

    # Step 4: Generate comprehensive report
    print("\n[PHASE 4] Report Generation")
    try:
        report_files = assessment_results["report_files"]
        print("[+] Investigation reports generated:")
        for format_type, file_path in report_files.items():
            print(f"    - {format_type.upper()}: {file_path}")

        # Generate compliance summary
        compliance_analysis = assessment_results["assessment_results"][
            "compliance_analysis"
        ]
        print("\n[+] Compliance Analysis:")
        print(
            f"    - Frameworks assessed: {len(compliance_analysis['frameworks_assessed'])}"
        )
        print(
            f"    - Compliance gaps identified: {len(compliance_analysis['compliance_gaps'])}"
        )

        # Legal implications summary
        legal_analysis = assessment_results["assessment_results"]["legal_implications"]
        print("\n[+] Legal Analysis:")
        print(f"    - Applicable laws: {', '.join(legal_analysis['applicable_laws'])}")
        print(
            f"    - Potential violations: {len(legal_analysis['potential_violations'])}"
        )
        print(f"    - Prosecution prospects: {legal_analysis['prosecution_prospects']}")

    except Exception as e:
        print(f"[-] Report generation failed: {str(e)}")
        return False

    # Step 5: Investigation summary
    print("\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)
    print(f"Case Reference: {args.case}")
    print("Investigation Status: COMPLETED")
    print(f"Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(
        f"Total Vulnerabilities: {assessment_results['assessment_results']['total_vulnerabilities']}"
    )
    print(
        f"Critical Issues: {assessment_results['assessment_results']['critical_vulnerabilities']}"
    )
    print(f"Reports Generated: {len(report_files)} files")
    print(f"Output Directory: {args.output_dir}")

    # Next steps recommendations
    print("\nNEXT STEPS RECOMMENDED:")
    print(f"1. Review generated reports in {args.output_dir}")
    print("2. Report incident to CERT-In within 6 hours (if required)")
    print("3. Preserve digital evidence as per IT Act Section 65B")
    print("4. Coordinate with legal team for potential prosecution")
    print("5. Follow up on remediation requirements")

    print("\n[+] Investigation completed successfully!")
    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="LogicPWN Indian Law Enforcement Cybersecurity Investigation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic investigation
  python indian_law_enforcement_example.py --target https://example.com --case CC_2025_001

  # Investigation with authentication
  python indian_law_enforcement_example.py --target https://example.com --case CC_2025_001 \\
    --username testuser --password testpass

  # Full investigation with all parameters
  python indian_law_enforcement_example.py --target https://example.com --case CC_2025_001 \\
    --agency "Cyber Crime Cell, Delhi" --officer "Inspector Rajesh Kumar" \\
    --fir FIR_2025_001 --jurisdiction "Delhi" --priority critical
        """,
    )

    # Required arguments
    parser.add_argument(
        "--target",
        required=True,
        help="Target URL to investigate (e.g., https://example.com)",
    )
    parser.add_argument(
        "--case", required=True, help="Case reference number (e.g., CC_2025_001)"
    )

    # Investigation details
    parser.add_argument(
        "--agency",
        default="Cyber Crime Investigation Cell",
        help="Investigating agency name",
    )
    parser.add_argument(
        "--officer",
        default="Investigating Officer",
        help="Name of investigating officer",
    )
    parser.add_argument("--fir", help="FIR number (if applicable)")
    parser.add_argument(
        "--jurisdiction", default="India", help="Investigation jurisdiction"
    )
    parser.add_argument(
        "--classification",
        default="cyber_crime",
        choices=["cyber_crime", "data_breach", "cyber_terrorism", "financial_fraud"],
        help="Incident classification",
    )
    parser.add_argument(
        "--priority",
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help="Investigation priority level",
    )
    parser.add_argument(
        "--forensics-team", dest="forensics_team", help="Digital forensics team name"
    )

    # Authentication (optional)
    parser.add_argument("--username", help="Username for authenticated testing")
    parser.add_argument("--password", help="Password for authenticated testing")

    # Output configuration
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="./investigation_reports",
        help="Output directory for reports (default: ./investigation_reports)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate arguments
    if not args.target.startswith(("http://", "https://")):
        print("[-] Error: Target URL must start with http:// or https://")
        sys.exit(1)

    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Run investigation
    try:
        success = run_indian_law_enforcement_investigation(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[-] Investigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Investigation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
