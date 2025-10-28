"""
Example 5: Context Manager Usage (with automatic cleanup)
===========================================================

Use context managers for automatic resource cleanup.
Best practice for production code and long-running tests.

What this demonstrates:
- Automatic session cleanup
- Exception handling
- Resource management
"""

from logicpwn import SecurityTester

# Example 1: Basic context manager usage
print("=" * 60)
print("Example 1: Basic Context Manager")
print("=" * 60)

with SecurityTester("https://api.example.com") as tester:
    # Authenticate
    if tester.authenticate("admin", "password123"):
        print("✅ Authenticated\n")

        # Run tests
        results = tester.test_idor("/api/users/{id}", [1, 2, 3])
        print(results["summary"])

# Resources automatically cleaned up here!
print("\n✅ Resources automatically cleaned up")

# Example 2: Exception handling with context manager
print("\n" + "=" * 60)
print("Example 2: Exception Handling")
print("=" * 60)

try:
    with SecurityTester("https://api.example.com") as tester:
        tester.authenticate("user", "pass")

        # This might fail
        results = tester.test_idor("/api/nonexistent/{id}", [1, 2, 3])

except Exception as e:
    print(f"❌ Error occurred: {e}")
    # Resources still cleaned up even on error!
    print("✅ Resources still cleaned up properly")

# Example 3: Multiple operations in one context
print("\n" + "=" * 60)
print("Example 3: Multiple Operations")
print("=" * 60)

with SecurityTester("https://api.example.com") as tester:
    if tester.authenticate("admin", "password"):
        # Operation 1: Test IDOR
        idor_results = tester.test_idor("/api/users/{id}", [1, 2, 3])
        print(f"IDOR Test: {idor_results['vulnerable_count']} vulnerabilities")

        # Operation 2: Test unauthorized access
        admin_results = tester.test_unauthorized_access(
            ["/api/admin/users", "/api/admin/settings"]
        )
        print(f"Admin Access: {len(admin_results['accessible'])} exposed endpoints")

        # Operation 3: Run exploit chain
        chain_results = tester.run_exploit_chain("../simple_exploit_corrected.yaml")
        print(f"Exploit Chain: {len(chain_results)} steps executed")

print("\n✅ All operations complete, resources cleaned up")

# Example 4: Nested context managers
print("\n" + "=" * 60)
print("Example 4: Testing Multiple Targets")
print("=" * 60)

targets = [
    ("https://api.example.com", "user1", "pass1"),
    ("https://staging.example.com", "user2", "pass2"),
]

for url, username, password in targets:
    print(f"\nTesting {url}...")

    with SecurityTester(url) as tester:
        if tester.authenticate(username, password):
            results = tester.test_idor("/api/users/{id}", [1, 2])
            print(f"   {results['summary']}")

    # Each tester is cleaned up before the next one starts

print("\n✅ All targets tested, all resources cleaned up")
