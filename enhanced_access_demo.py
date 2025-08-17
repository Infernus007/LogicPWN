"""
Enhanced Access Detection Demonstration Script.

This script demonstrates all the advanced access control testing capabilities
including intelligent ID generation, tenant isolation testing, privilege
escalation detection, and comprehensive vulnerability assessment.
"""

import asyncio
import requests
from typing import List, Dict, Any
import json
from datetime import datetime

# Import enhanced access detection capabilities
from logicpwn.core.access import (
    run_enhanced_access_detection_sync,
    create_enhanced_access_config,
    quick_idor_with_smart_ids,
    tenant_isolation_test_only,
    privilege_escalation_test_only,
    generate_smart_id_list,
    EnhancedIDGenerator,
    create_id_generation_config
)


def print_banner():
    """Print the demo banner."""
    print("🔍" + "=" * 70 + "🔍")
    print("   🚀 LogicPWN Enhanced Access Detection Demonstration 🚀")
    print("      Advanced IDOR, Tenant Isolation & Privilege Escalation")
    print("🔍" + "=" * 70 + "🔍")
    print()


def demo_intelligent_id_generation():
    """Demonstrate intelligent ID generation and fuzzing."""
    print("📋 DEMO 1: Intelligent ID Generation and Fuzzing")
    print("-" * 50)
    
    # Example 1: UUID-based IDs
    print("🔸 Example 1: UUID Pattern Detection and Generation")
    uuid_examples = [
        "550e8400-e29b-41d4-a716-446655440000",
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "123e4567-e89b-12d3-a456-426614174000"
    ]
    
    generated_uuids = generate_smart_id_list(
        example_ids=uuid_examples,
        max_total_ids=20,
        include_privilege_escalation=True
    )
    
    print(f"  📥 Input UUIDs: {len(uuid_examples)} examples")
    print(f"  📤 Generated: {len(generated_uuids)} intelligent test IDs")
    print(f"  🎯 Sample generated IDs:")
    for i, id_val in enumerate(generated_uuids[:5]):
        print(f"    {i+1}. {id_val}")
    print()
    
    # Example 2: Sequential IDs
    print("🔸 Example 2: Sequential Pattern Detection")
    sequential_examples = ["user1", "user2", "user3", "user4"]
    
    generated_sequential = generate_smart_id_list(
        example_ids=sequential_examples,
        max_total_ids=30,
        include_privilege_escalation=True
    )
    
    print(f"  📥 Input sequential IDs: {sequential_examples}")
    print(f"  📤 Generated: {len(generated_sequential)} test IDs")
    print(f"  🎯 Sample generated IDs:")
    for i, id_val in enumerate(generated_sequential[:8]):
        print(f"    {i+1}. {id_val}")
    print()
    
    # Example 3: Advanced ID Generator
    print("🔸 Example 3: Advanced Multi-Pattern Generation")
    config = create_id_generation_config(max_ids=100)
    generator = EnhancedIDGenerator(config)
    
    mixed_examples = [
        "tenant-123",
        "org-456", 
        "admin-001",
        "5d41402abc4b2a76b9719d911017c592",  # MD5 hash
        "user_abc123"
    ]
    
    pattern_results = generator.generate_intelligent_ids(mixed_examples)
    
    print(f"  📥 Mixed pattern examples: {len(mixed_examples)} IDs")
    print(f"  🔍 Detected patterns:")
    for pattern_name, ids in pattern_results.items():
        print(f"    • {pattern_name}: {len(ids)} generated IDs")
        if ids:
            print(f"      Sample: {ids[0]}")
    print()


def demo_privilege_escalation_testing():
    """Demonstrate privilege escalation testing capabilities."""
    print("📋 DEMO 2: Privilege Escalation and Role Testing")
    print("-" * 50)
    
    print("🔸 Example 1: Role Hierarchy Discovery")
    print("  Discovering application roles and privileges...")
    
    # Simulate role discovery
    discovered_roles = [
        "guest", "user", "premium_user", "moderator", 
        "admin", "super_admin", "system"
    ]
    
    print(f"  🎯 Discovered roles: {', '.join(discovered_roles)}")
    print("  🔗 Inferred hierarchy:")
    print("    guest → user → premium_user → moderator → admin → super_admin → system")
    print()
    
    print("🔸 Example 2: Admin Function Discovery")
    admin_functions = [
        "user_management", "system_config", "audit_logs",
        "billing_admin", "security_settings", "backup_restore"
    ]
    
    print("  🔍 Discovered admin functions:")
    for i, func in enumerate(admin_functions, 1):
        print(f"    {i}. {func}")
    print()
    
    print("🔸 Example 3: Privilege Escalation Test Matrix")
    test_matrix = [
        ("user", "admin_panel", "❌ BLOCKED"),
        ("user", "admin/users", "⚠️  ACCESSIBLE - VULNERABILITY!"),
        ("moderator", "admin/logs", "❌ BLOCKED"),
        ("moderator", "admin/content", "✅ ALLOWED"),
        ("guest", "user_profile", "⚠️  ACCESSIBLE - VULNERABILITY!")
    ]
    
    print("  🎯 Test results:")
    for role, endpoint, result in test_matrix:
        status_icon = "🚨" if "VULNERABILITY" in result else "✅" if "ALLOWED" in result else "🛡️"
        print(f"    {status_icon} {role:12} → {endpoint:15} {result}")
    
    vulnerabilities_found = sum(1 for _, _, result in test_matrix if "VULNERABILITY" in result)
    print(f"\n  📊 Summary: {vulnerabilities_found} privilege escalation vulnerabilities detected!")
    print()


def demo_tenant_isolation_testing():
    """Demonstrate tenant isolation testing capabilities."""
    print("📋 DEMO 3: Tenant Isolation Testing")
    print("-" * 50)
    
    print("🔸 Example 1: Tenant Discovery")
    discovered_tenants = [
        "acme-corp", "demo-org", "test-company", 
        "trial-tenant", "admin-tenant", "system-tenant"
    ]
    
    print(f"  🎯 Discovered tenants: {len(discovered_tenants)}")
    for i, tenant in enumerate(discovered_tenants, 1):
        print(f"    {i}. {tenant}")
    print()
    
    print("🔸 Example 2: Cross-Tenant Access Testing")
    current_tenant = "acme-corp"
    
    cross_tenant_tests = [
        ("demo-org", "/api/users", "200", "⚠️  DATA LEAKAGE"),
        ("test-company", "/api/documents", "403", "✅ BLOCKED"),
        ("admin-tenant", "/api/settings", "200", "🚨 CRITICAL - ADMIN ACCESS"),
        ("trial-tenant", "/api/billing", "404", "✅ NOT FOUND"),
        ("system-tenant", "/api/logs", "200", "🚨 CRITICAL - SYSTEM ACCESS")
    ]
    
    print(f"  🎯 Testing from tenant: {current_tenant}")
    print("  📊 Cross-tenant access results:")
    
    isolation_breaches = 0
    for target, endpoint, status, result in cross_tenant_tests:
        if "LEAKAGE" in result or "CRITICAL" in result:
            isolation_breaches += 1
            icon = "🚨"
        elif "BLOCKED" in result or "NOT FOUND" in result:
            icon = "🛡️"
        else:
            icon = "⚠️"
        
        print(f"    {icon} {target:15} {endpoint:15} [{status}] {result}")
    
    print(f"\n  📊 Summary: {isolation_breaches} tenant isolation breaches detected!")
    print()
    
    print("🔸 Example 3: Tenant Context Manipulation")
    manipulation_tests = [
        ("Header manipulation", "X-Tenant-ID: admin-tenant", "SUCCESS", "🚨 BYPASS"),
        ("Parameter injection", "?tenant_id=system-tenant", "SUCCESS", "🚨 BYPASS"),  
        ("Cookie manipulation", "tenant=demo-org", "BLOCKED", "✅ SECURE"),
        ("URL path traversal", "../admin-tenant/", "BLOCKED", "✅ SECURE")
    ]
    
    print("  🔧 Context manipulation test results:")
    bypasses = 0
    for technique, payload, result, status in manipulation_tests:
        if "BYPASS" in status:
            bypasses += 1
            icon = "🚨"
        else:
            icon = "🛡️"
        print(f"    {icon} {technique:20} {payload:25} [{result}] {status}")
    
    print(f"\n  📊 Summary: {bypasses} context manipulation bypasses found!")
    print()


def demo_comprehensive_testing():
    """Demonstrate comprehensive access testing workflow."""
    print("📋 DEMO 4: Comprehensive Access Testing Workflow")
    print("-" * 50)
    
    print("🔸 Simulating Comprehensive Security Assessment")
    print("  🎯 Target: Multi-tenant SaaS Application")
    print("  👤 Current context: User 'alice' in tenant 'acme-corp'")
    print()
    
    # Simulate comprehensive test execution
    test_phases = [
        ("ID Generation", "Generating intelligent test IDs", 847),
        ("IDOR Testing", "Testing 847 endpoints for access control", 23),
        ("Tenant Isolation", "Cross-tenant boundary testing", 7),
        ("Privilege Escalation", "Role and permission testing", 12),
        ("Admin Discovery", "Mapping administrative functions", 5)
    ]
    
    total_vulnerabilities = 0
    
    print("  🚀 Execution phases:")
    for phase, description, vulns in test_phases:
        total_vulnerabilities += vulns
        status = "🚨 CRITICAL" if vulns > 15 else "⚠️  HIGH" if vulns > 5 else "✅ CLEAN"
        print(f"    • {phase:18} - {description}")
        print(f"      └─ Result: {vulns} vulnerabilities {status}")
    
    print()
    print("  📊 COMPREHENSIVE ASSESSMENT RESULTS:")
    print("  " + "=" * 45)
    print(f"    Total vulnerabilities found: {total_vulnerabilities}")
    print(f"    Critical issues: {sum(1 for _, _, v in test_phases if v > 15)}")
    print(f"    High-risk issues: {sum(1 for _, _, v in test_phases if 5 < v <= 15)}")
    print(f"    Risk level: {'🚨 CRITICAL' if total_vulnerabilities > 30 else '⚠️ HIGH'}")
    print()
    
    print("  🎯 Top Vulnerability Categories:")
    vulnerability_types = [
        ("IDOR (Insecure Direct Object References)", 23, "🔴"),
        ("Privilege Escalation", 12, "🟠"),
        ("Tenant Isolation Bypass", 7, "🟡"),
        ("Admin Function Exposure", 5, "🟢")
    ]
    
    for vuln_type, count, severity in vulnerability_types:
        percentage = (count / total_vulnerabilities) * 100
        print(f"    {severity} {vuln_type:35} {count:3} ({percentage:4.1f}%)")
    print()


def demo_real_world_scenarios():
    """Demonstrate real-world testing scenarios."""
    print("📋 DEMO 5: Real-World Security Testing Scenarios")
    print("-" * 50)
    
    scenarios = [
        {
            "name": "E-commerce Platform",
            "description": "Testing customer data access controls",
            "endpoints": ["/api/customers/{id}", "/api/orders/{id}", "/api/payments/{id}"],
            "vulnerabilities": ["Customer data exposure", "Order manipulation", "Payment bypass"],
            "impact": "HIGH - Customer PII exposure"
        },
        {
            "name": "Banking API",
            "description": "Multi-tier account access testing", 
            "endpoints": ["/api/accounts/{id}", "/api/transactions/{id}", "/api/admin/{id}"],
            "vulnerabilities": ["Cross-account access", "Transaction viewing", "Admin escalation"],
            "impact": "CRITICAL - Financial data breach"
        },
        {
            "name": "Healthcare System",
            "description": "Patient record isolation testing",
            "endpoints": ["/api/patients/{id}", "/api/records/{id}", "/api/providers/{id}"],
            "vulnerabilities": ["Patient data leakage", "Medical record access"],
            "impact": "CRITICAL - HIPAA violation"
        },
        {
            "name": "SaaS Multi-tenant",
            "description": "Tenant boundary enforcement",
            "endpoints": ["/api/tenants/{id}", "/api/workspaces/{id}", "/api/billing/{id}"],
            "vulnerabilities": ["Cross-tenant access", "Billing manipulation"],
            "impact": "HIGH - Data isolation breach"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🔸 Scenario {i}: {scenario['name']}")
        print(f"  📝 Description: {scenario['description']}")
        print(f"  🎯 Test endpoints: {len(scenario['endpoints'])} endpoints")
        print(f"  ⚠️  Vulnerabilities found: {len(scenario['vulnerabilities'])}")
        for vuln in scenario['vulnerabilities']:
            print(f"    • {vuln}")
        print(f"  💥 Business impact: {scenario['impact']}")
        print()


def demo_advanced_features():
    """Demonstrate advanced features and capabilities."""
    print("📋 DEMO 6: Advanced Features and Capabilities") 
    print("-" * 50)
    
    print("🔸 Advanced ID Generation Techniques")
    techniques = [
        ("Pattern Recognition", "Automatically detects UUID, hash, sequential patterns"),
        ("Privilege-Aware Generation", "Creates admin/system user variations"),
        ("Tenant-Specific IDs", "Generates cross-tenant test identifiers"),
        ("Edge Case Testing", "Includes boundary values and injection attempts"),
        ("Smart Enumeration", "Intelligent range detection and expansion")
    ]
    
    for technique, description in techniques:
        print(f"  ✨ {technique:25} - {description}")
    print()
    
    print("🔸 Tenant Isolation Testing Techniques")
    isolation_tests = [
        ("Subdomain Enumeration", "Discovers tenant subdomains"),
        ("API Discovery", "Maps tenant-specific endpoints"),
        ("Context Manipulation", "Tests header/parameter injection"),
        ("Data Leakage Detection", "Identifies cross-tenant information"),
        ("Access Control Bypass", "Tests isolation boundaries")
    ]
    
    for test, description in isolation_tests:
        print(f"  🏢 {test:25} - {description}")
    print()
    
    print("🔸 Privilege Escalation Detection")
    escalation_tests = [
        ("Role Discovery", "Maps application role hierarchy"),
        ("Function Enumeration", "Discovers admin/privileged functions"),
        ("Vertical Escalation", "Tests lower to higher privilege access"),
        ("Horizontal Escalation", "Tests same-level user access"),
        ("Permission Bypass", "Tests authorization controls")
    ]
    
    for test, description in escalation_tests:
        print(f"  👑 {test:25} - {description}")
    print()


def generate_demo_report():
    """Generate a comprehensive demo report."""
    print("📋 DEMO 7: Comprehensive Security Assessment Report")
    print("-" * 50)
    
    # Simulate report generation
    report_data = {
        "assessment_info": {
            "target": "https://demo-app.example.com",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": "2.5 hours",
            "tester": "LogicPWN Enhanced Access Detection"
        },
        "summary": {
            "total_tests": 1247,
            "vulnerabilities": 47,
            "critical": 8,
            "high": 15,
            "medium": 24,
            "coverage": "94.2%"
        },
        "findings": [
            {
                "id": "IDOR-001", 
                "title": "Customer Data Access Control Bypass",
                "severity": "CRITICAL",
                "description": "Users can access other customers' personal data",
                "endpoint": "/api/customers/{id}",
                "evidence": "HTTP 200 response with customer data for unauthorized ID"
            },
            {
                "id": "PRIV-002",
                "title": "Administrative Function Access",
                "severity": "CRITICAL", 
                "description": "Regular users can access admin panel",
                "endpoint": "/admin/users",
                "evidence": "User role gained access to user management functions"
            },
            {
                "id": "TENANT-003",
                "title": "Cross-Tenant Data Leakage",
                "severity": "HIGH",
                "description": "Tenant A can view Tenant B's documents",
                "endpoint": "/api/documents/search",
                "evidence": "Search results include documents from other tenants"
            }
        ]
    }
    
    print("🎯 EXECUTIVE SUMMARY")
    print("  " + "=" * 40)
    print(f"  Target Application: {report_data['assessment_info']['target']}")
    print(f"  Assessment Date: {report_data['assessment_info']['date']}")
    print(f"  Duration: {report_data['assessment_info']['duration']}")
    print()
    
    print("📊 VULNERABILITY SUMMARY")
    summary = report_data['summary']
    print(f"  Total Tests Executed: {summary['total_tests']:,}")
    print(f"  Vulnerabilities Found: {summary['vulnerabilities']}")
    print(f"  • Critical: {summary['critical']:2} ({summary['critical']/summary['vulnerabilities']*100:.1f}%)")
    print(f"  • High:     {summary['high']:2} ({summary['high']/summary['vulnerabilities']*100:.1f}%)")
    print(f"  • Medium:   {summary['medium']:2} ({summary['medium']/summary['vulnerabilities']*100:.1f}%)")
    print(f"  Coverage: {summary['coverage']}")
    print()
    
    print("🚨 CRITICAL FINDINGS")
    critical_findings = [f for f in report_data['findings'] if f['severity'] == 'CRITICAL']
    
    for i, finding in enumerate(critical_findings, 1):
        print(f"  {i}. {finding['id']}: {finding['title']}")
        print(f"     Endpoint: {finding['endpoint']}")
        print(f"     Impact: {finding['description']}")
        print(f"     Evidence: {finding['evidence']}")
        print()
    
    print("💡 RECOMMENDATIONS")
    recommendations = [
        "Implement proper access control validation for all endpoints",
        "Add tenant context validation to prevent cross-tenant access",
        "Review and strengthen role-based permission checks",
        "Implement comprehensive audit logging for privilege changes",
        "Regular security testing with automated tools like LogicPWN"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    print()


def main():
    """Run the complete enhanced access detection demonstration."""
    print_banner()
    
    print("🎬 Starting Enhanced Access Detection Demonstration...")
    print("   This demo showcases the advanced capabilities for:")
    print("   • Intelligent ID generation and fuzzing")
    print("   • Tenant isolation testing")
    print("   • Privilege escalation detection")
    print("   • Comprehensive vulnerability assessment")
    print()
    
    # Run all demonstration sections
    demo_intelligent_id_generation()
    print("⏳ Press Enter to continue to privilege escalation demo...")
    input()
    
    demo_privilege_escalation_testing()
    print("⏳ Press Enter to continue to tenant isolation demo...")
    input()
    
    demo_tenant_isolation_testing()
    print("⏳ Press Enter to continue to comprehensive testing demo...")
    input()
    
    demo_comprehensive_testing()
    print("⏳ Press Enter to continue to real-world scenarios...")
    input()
    
    demo_real_world_scenarios()
    print("⏳ Press Enter to continue to advanced features...")
    input()
    
    demo_advanced_features()
    print("⏳ Press Enter to generate final assessment report...")
    input()
    
    generate_demo_report()
    
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 70)
    print("The LogicPWN Enhanced Access Detection system provides:")
    print("✨ Intelligent ID generation with pattern detection")
    print("🏢 Comprehensive tenant isolation testing")
    print("👑 Advanced privilege escalation detection")
    print("🎯 Complete vulnerability assessment workflows")
    print("📊 Detailed security assessment reporting")
    print()
    print("Ready for production security testing!")
    print("=" * 70)


if __name__ == "__main__":
    main()
