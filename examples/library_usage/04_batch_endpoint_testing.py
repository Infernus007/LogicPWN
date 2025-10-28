"""
Example 4: Batch Endpoint Testing
===================================

Test multiple endpoints and resource types in parallel.
Efficient way to scan entire API surfaces for IDOR vulnerabilities.

What this demonstrates:
- Testing multiple resource types
- Batch vulnerability scanning
- Result aggregation and reporting
"""

from logicpwn import SecurityTester
from logicpwn.results import SecurityTestResult

# Initialize tester
tester = SecurityTester("https://api.example.com")

# Authenticate
tester.authenticate("testuser", "password123")

# Define resource types and IDs to test
resources = {
    "users": [1, 2, 3, "admin", "guest", 100, 999],
    "orders": [100, 101, 102, 200, 999],
    "documents": ["doc1", "doc2", "doc3", "confidential_doc"],
    "invoices": ["INV001", "INV002", "INV999"],
    "profiles": [1, 2, 3, 10, 50],
}

print("=" * 60)
print("Batch IDOR Vulnerability Scan")
print("=" * 60)

all_vulnerabilities = []
all_results = {}

# Test each resource type
for resource_type, test_ids in resources.items():
    print(f"\n🔍 Testing {resource_type}...")

    results = tester.test_idor(
        endpoint_pattern=f"/api/{resource_type}/{{id}}",
        test_ids=test_ids,
        success_indicators=["data", "details", "content"],
    )

    all_results[resource_type] = results
    all_vulnerabilities.extend(results["vulnerabilities"])

    # Show summary for this resource
    print(f"   Total: {results['total_tested']}")
    print(f"   Vulnerable: {results['vulnerable_count']}")
    print(f"   Pass Rate: {results['pass_rate']:.1f}%")

# Overall summary
print("\n" + "=" * 60)
print("Overall Results")
print("=" * 60)
print(f"Total Resources Tested: {len(resources)}")
print(f"Total Endpoints Tested: {sum(r['total_tested'] for r in all_results.values())}")
print(f"Total Vulnerabilities: {len(all_vulnerabilities)}")

# Show vulnerable resources
vulnerable_resources = {
    name: results
    for name, results in all_results.items()
    if results["vulnerable_count"] > 0
}

if vulnerable_resources:
    print(f"\n🚨 Vulnerable Resource Types: {len(vulnerable_resources)}")
    for resource, results in vulnerable_resources.items():
        print(f"\n   {resource}:")
        for vuln in results["vulnerabilities"]:
            print(f"      - {vuln.endpoint_url} (Status: {vuln.status_code})")
else:
    print("\n✅ All endpoints are properly secured!")

# Export results
print("\n📁 Exporting results...")
combined_result = SecurityTestResult(
    test_type="Batch IDOR Scan",
    target_url="https://api.example.com",
    total_tests=sum(r["total_tested"] for r in all_results.values()),
    vulnerabilities=all_vulnerabilities,
    safe_endpoints=[
        endpoint
        for results in all_results.values()
        for endpoint in results["safe_endpoints"]
    ],
)

combined_result.export_json("batch_scan_results.json")
combined_result.export_markdown("batch_scan_report.md")
print("   ✅ Results exported to batch_scan_results.json and batch_scan_report.md")

# Clean up
tester.close()
