"""
Example 2: Authenticated Security Testing
===========================================

Test for IDOR vulnerabilities with authentication.
Shows how to authenticate and then perform security tests.

What this tests:
- Authentication flow
- Authorized access testing
- Multiple endpoint testing
"""

from logicpwn import SecurityTester

# Initialize tester with your target URL
tester = SecurityTester("https://api.example.com")

# Authenticate (returns True if successful)
if tester.authenticate(
    username="testuser",
    password="password123",
    login_endpoint="/api/auth/login",
    success_indicators=["token", "success", "authenticated"],
):
    print("✅ Authentication successful!\n")

    # Test 1: Check user endpoints for IDOR
    print("Testing user endpoints...")
    user_results = tester.test_idor(
        endpoint_pattern="/api/users/{id}",
        test_ids=[1, 2, 3, 100, 999],
        success_indicators=["email", "user_data", "profile"],
    )
    print(user_results["summary"])

    # Test 2: Check document endpoints
    print("\nTesting document endpoints...")
    doc_results = tester.test_idor(
        endpoint_pattern="/api/documents/{id}",
        test_ids=["doc1", "doc2", "doc3", "admin_doc"],
        success_indicators=["content", "document"],
    )
    print(doc_results["summary"])

    # Test 3: Check if admin endpoints are exposed
    print("\nTesting unauthorized access to admin endpoints...")
    admin_results = tester.test_unauthorized_access(
        [
            "/api/admin/users",
            "/api/admin/settings",
            "/api/admin/logs",
            "/api/admin/config",
        ]
    )
    print(admin_results["summary"])

    if admin_results["vulnerable"]:
        print("\n⚠️  WARNING: Admin endpoints are accessible!")
        for endpoint in admin_results["accessible"]:
            print(f"   - {endpoint['endpoint']} (Status: {endpoint['status']})")

    # Clean up
    tester.close()
else:
    print("❌ Authentication failed!")
    print("Check your credentials and success indicators")
