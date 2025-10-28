"""
Example 6: Result Export and Reporting
========================================

Export security test results in multiple formats.
Perfect for compliance reporting, documentation, and CI/CD integration.

What this demonstrates:
- Exporting to JSON
- Exporting to Markdown
- Exporting to CSV
- Generating detailed reports
"""

from datetime import datetime

from logicpwn import SecurityTester
from logicpwn.results import SecurityTestResult

print("=" * 60)
print("Security Testing with Report Generation")
print("=" * 60)

# Run security tests
tester = SecurityTester("https://api.example.com")
tester.authenticate("testuser", "password123")

# Perform tests
results = tester.test_idor(
    endpoint_pattern="/api/users/{id}",
    test_ids=[1, 2, 3, "admin", "guest", 100, 999],
    success_indicators=["email", "user_data"],
)

print(f"Completed {results['total_tested']} tests")
print(f"Found {results['vulnerable_count']} vulnerabilities\n")

# Create rich result object
security_result = SecurityTestResult(
    test_type="IDOR Vulnerability Scan",
    target_url="https://api.example.com",
    total_tests=results["total_tested"],
    vulnerabilities=results["vulnerabilities"],
    safe_endpoints=results["safe_endpoints"],
    test_duration=2.5,  # Example duration
    metadata={
        "tester": "testuser",
        "environment": "production",
        "scan_id": f"SCAN-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    },
)

# Example 1: Print summaries
print("=" * 60)
print("Summary Reports")
print("=" * 60)

print("\n--- Basic Summary ---")
print(security_result.summary())

print("\n--- Detailed Summary ---")
print(security_result.detailed_summary())

# Example 2: Export to different formats
print("\n" + "=" * 60)
print("Exporting Reports")
print("=" * 60)

# Export to JSON (machine-readable)
security_result.export_json("security_report.json")
print("✅ Exported to security_report.json (JSON format)")

# Export to Markdown (human-readable documentation)
security_result.export_markdown("security_report.md")
print("✅ Exported to security_report.md (Markdown format)")

# Export to CSV (Excel-compatible)
security_result.export_csv("security_report.csv")
print("✅ Exported to security_report.csv (CSV format)")

# Example 3: Analyze specific vulnerability types
print("\n" + "=" * 60)
print("Vulnerability Analysis")
print("=" * 60)

critical_vulns = security_result.get_critical_vulnerabilities()
high_vulns = security_result.get_high_vulnerabilities()

print(f"Critical vulnerabilities: {len(critical_vulns)}")
print(f"High vulnerabilities: {len(high_vulns)}")
print(f"Pass rate: {security_result.pass_rate:.1f}%")

# Example 4: Generate custom report
print("\n" + "=" * 60)
print("Custom Report Generation")
print("=" * 60)

report_data = security_result.to_dict()

print(f"Report ID: {report_data['metadata'].get('scan_id', 'N/A')}")
print(f"Test Type: {report_data['test_type']}")
print(f"Target: {report_data['target_url']}")
print(f"Timestamp: {report_data['timestamp']}")
print(f"Status: {'🚨 VULNERABLE' if report_data['is_vulnerable'] else '✅ SECURE'}")

# Example 5: Integration with CI/CD
print("\n" + "=" * 60)
print("CI/CD Integration Example")
print("=" * 60)

# Exit with error code if vulnerabilities found (for CI/CD)
exit_code = 1 if security_result.is_vulnerable else 0

print(f"Exit code for CI/CD: {exit_code}")
if exit_code == 1:
    print("⚠️  Pipeline should FAIL (vulnerabilities found)")
else:
    print("✅ Pipeline should PASS (no vulnerabilities)")

# Clean up
tester.close()

print("\n" + "=" * 60)
print("Reports generated successfully!")
print("=" * 60)
print("\nGenerated files:")
print("  - security_report.json  (for automated processing)")
print("  - security_report.md    (for documentation)")
print("  - security_report.csv   (for spreadsheet analysis)")
