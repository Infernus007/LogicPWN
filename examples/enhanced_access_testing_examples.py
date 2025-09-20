"""
Enhanced Access Testing Examples

This file demonstrates the new functionality added to the access module:
- GraphQL protocol support
- WebSocket testing capabilities
- Authentication integration
- Result streaming and memory management
- SSL verification enforcement
"""

import asyncio

import requests

from logicpwn.core.access import (  # Enhanced protocol support; Authentication integration; Result streaming; Core functionality
    AccessDetectorConfig,
    AuthenticatedAccessTester,
    GraphQLQuery,
    GraphQLTester,
    PaginatedResultManager,
    ProtocolType,
    StreamingMode,
    WebSocketConfig,
    WebSocketTester,
    create_authenticated_access_tester,
    create_buffered_streamer,
    create_memory_efficient_streamer,
    create_ssl_context,
    detect_protocol_type,
    run_authenticated_access_test_suite,
)


def example_graphql_testing():
    """Example: Testing GraphQL endpoints for access control vulnerabilities."""
    print("=== GraphQL Access Testing Example ===")

    # Initialize GraphQL tester
    graphql_tester = GraphQLTester(
        endpoint="https://api.example.com/graphql",
        headers={"Authorization": "Bearer token123"},
    )

    # Test GraphQL introspection (security risk if enabled)
    session = requests.Session()
    introspection_result = graphql_tester.test_introspection(session)

    if introspection_result.vulnerability_detected:
        print("⚠️  GraphQL introspection is enabled - potential security risk")

    # Test specific GraphQL queries with ID substitution
    user_query = GraphQLQuery(
        query="""
        query GetUser($userId: ID!) {
            user(id: $userId) {
                id
                email
                profile {
                    firstName
                    lastName
                }
            }
        }
        """,
        variables={"userId": "{ID}"},
        operation_name="GetUser",
    )

    # Test access for different user IDs
    test_ids = ["1", "2", "3", "admin", "999"]
    for user_id in test_ids:
        result = graphql_tester.test_query_access(session, user_query, user_id)
        if result.vulnerability_detected:
            print(f"🚨 Unauthorized access to user {user_id}")


async def example_websocket_testing():
    """Example: Testing WebSocket connections for access control."""
    print("=== WebSocket Access Testing Example ===")

    # Configure WebSocket connection
    ws_config = WebSocketConfig(
        url="wss://api.example.com/ws/user/{ID}",
        headers={"Authorization": "Bearer token123"},
        timeout=30,
        ssl_context=create_ssl_context(verify_ssl=True),
    )

    # Initialize WebSocket tester
    ws_tester = WebSocketTester(ws_config)

    # Test connection access for different user IDs
    test_ids = ["1", "2", "admin", "guest"]
    for user_id in test_ids:
        result = await ws_tester.test_connection_access(user_id)
        if result.access_granted:
            print(f"✅ WebSocket connection established for user {user_id}")
        else:
            print(f"❌ WebSocket connection denied for user {user_id}")

    # Test specific WebSocket messages
    test_messages = [
        {"type": "subscribe", "channel": "user_updates"},
        {"type": "get_data", "resource": "sensitive_info"},
        {"type": "admin_action", "command": "list_users"},
    ]

    message_results = await ws_tester.test_message_access("1", test_messages)
    for result in message_results:
        if result.vulnerability_detected:
            print(f"🚨 Unauthorized message access: {result.request_data}")


def example_authenticated_testing():
    """Example: Integrated authentication with access testing."""
    print("=== Authenticated Access Testing Example ===")

    # Create authenticated access tester
    access_config = AccessDetectorConfig(
        current_user_id="user123", unauthorized_ids=["admin", "root", "system"]
    )

    auth_tester = create_authenticated_access_tester(
        auth_url="https://app.example.com/login",
        auth_method="POST",
        credentials={"username": "testuser", "password": "testpass"},
        access_config=access_config,
        success_indicators=["Welcome", "Dashboard"],
        failure_indicators=["Invalid", "Error"],
    )

    # Test multiple endpoints with automatic session management
    test_results = auth_tester.test_multiple_ids_authenticated(
        endpoint_template="https://app.example.com/api/users/{ID}/profile",
        id_values=["1", "2", "admin", "999"],
        success_indicators=["profile", "user_data"],
        failure_indicators=["unauthorized", "forbidden"],
    )

    # Process results
    for result in test_results:
        if result.vulnerability_detected:
            print(f"🚨 IDOR vulnerability found for ID {result.id_tested}")
        elif result.error_message:
            print(f"❌ Error testing ID {result.id_tested}: {result.error_message}")
        else:
            print(f"✅ Access properly controlled for ID {result.id_tested}")

    # Clean up
    auth_tester.close()


def example_memory_efficient_testing():
    """Example: Memory-efficient testing for large datasets."""
    print("=== Memory-Efficient Testing Example ===")

    # Create memory-efficient streamer
    streamer = create_memory_efficient_streamer(
        memory_threshold_mb=100,  # Low threshold for demo
        buffer_size=50,
        export_format="json",
    )

    # Simulate large-scale testing
    print("Simulating tests for 10,000 IDs...")

    for i in range(10000):
        # Simulate test result
        from logicpwn.core.access.models import AccessTestResult

        result = AccessTestResult(
            id_tested=str(i),
            endpoint_url=f"https://api.example.com/resource/{i}",
            status_code=200 if i % 10 != 0 else 403,
            access_granted=i % 10 != 0,
            vulnerability_detected=i % 100 == 0,  # 1% vulnerability rate
            response_indicators=["success"] if i % 10 != 0 else ["forbidden"],
        )

        # Add to streamer (automatically manages memory)
        streamer.add_result(result)

        # Show progress every 1000 results
        if i % 1000 == 0:
            stats = streamer.get_statistics()
            print(
                f"Processed: {stats['total_processed']}, "
                f"Vulnerabilities: {stats['vulnerabilities_found']}, "
                f"Memory warnings: {stats['memory_warnings']}"
            )

    # Export results
    streamer.export_stream("large_test_results.json")
    print("Results exported to large_test_results.json")


def example_paginated_results():
    """Example: Paginated result management."""
    print("=== Paginated Results Example ===")

    # Create paginated result manager
    paginator = PaginatedResultManager(page_size=25)

    # Add sample results
    from logicpwn.core.access.models import AccessTestResult

    sample_results = []
    for i in range(150):  # 6 pages of results
        result = AccessTestResult(
            id_tested=str(i),
            endpoint_url=f"https://api.example.com/item/{i}",
            status_code=200,
            access_granted=True,
            vulnerability_detected=i % 20 == 0,
            response_indicators=["success"],
        )
        sample_results.append(result)

    paginator.add_results(sample_results)

    # Navigate through pages
    page_info = paginator.get_page_info()
    print(f"Total pages: {page_info['total_pages']}")
    print(f"Total results: {page_info['total_results']}")

    # Show first page
    current_page = paginator.get_current_page()
    print(f"Page 1: {len(current_page)} results")

    # Navigate to next pages
    while paginator.has_next_page():
        next_page = paginator.next_page()
        page_info = paginator.get_page_info()
        vulnerabilities = sum(1 for r in next_page if r.vulnerability_detected)
        print(
            f"Page {page_info['current_page'] + 1}: {len(next_page)} results, "
            f"{vulnerabilities} vulnerabilities"
        )


async def example_comprehensive_test_suite():
    """Example: Comprehensive test suite with all protocols."""
    print("=== Comprehensive Test Suite Example ===")

    # Create authenticated tester
    access_config = AccessDetectorConfig(
        current_user_id="user123", unauthorized_ids=["admin", "system"]
    )

    auth_tester = create_authenticated_access_tester(
        auth_url="https://app.example.com/login",
        auth_method="POST",
        credentials={"username": "testuser", "password": "testpass"},
        access_config=access_config,
        success_indicators=["Welcome"],
        failure_indicators=["Invalid"],
    )

    # Define comprehensive test suite
    test_suite = {
        "http_tests": {
            "endpoint_template": "https://app.example.com/api/users/{ID}",
            "id_values": ["1", "2", "admin", "999"],
            "success_indicators": ["user_data", "profile"],
            "failure_indicators": ["unauthorized", "forbidden"],
            "timeout": 30,
        },
        "graphql_tests": {
            "endpoint": "https://app.example.com/graphql",
            "query": "query GetUser($id: ID!) { user(id: $id) { email profile } }",
            "variables": {"id": "{ID}"},
            "id_values": ["1", "2", "admin"],
            "headers": {"Content-Type": "application/json"},
        },
        "websocket_tests": {
            "url": "wss://app.example.com/ws/user/{ID}",
            "id_values": ["1", "2", "admin"],
            "timeout": 30,
        },
    }

    # Run comprehensive test suite
    all_results = await run_authenticated_access_test_suite(auth_tester, test_suite)

    # Process results by protocol
    for protocol, results in all_results.items():
        print(f"\n{protocol.upper()} Results:")
        vulnerabilities = sum(1 for r in results if r.vulnerability_detected)
        errors = sum(1 for r in results if r.error_message)
        print(f"  Total tests: {len(results)}")
        print(f"  Vulnerabilities: {vulnerabilities}")
        print(f"  Errors: {errors}")

    auth_tester.close()


def example_ssl_verification():
    """Example: Enhanced SSL verification."""
    print("=== SSL Verification Example ===")

    # Create SSL context with enhanced security
    secure_context = create_ssl_context(
        verify_ssl=True,
        cert_file=None,  # Optional client certificate
        key_file=None,  # Optional client key
    )

    print("✅ Secure SSL context created with:")
    print("  - TLS 1.2+ minimum version")
    print("  - Strong cipher suites only")
    print("  - Certificate verification enabled")

    # Use with WebSocket testing
    ws_config = WebSocketConfig(
        url="wss://secure-api.example.com/ws", ssl_context=secure_context, timeout=30
    )

    print("🔒 WebSocket configured with enhanced SSL security")


if __name__ == "__main__":
    print("LogicPWN Enhanced Access Testing Examples\n")

    # Run examples
    example_graphql_testing()
    print()

    asyncio.run(example_websocket_testing())
    print()

    example_authenticated_testing()
    print()

    example_memory_efficient_testing()
    print()

    example_paginated_results()
    print()

    asyncio.run(example_comprehensive_test_suite())
    print()

    example_ssl_verification()

    print("\n✅ All examples completed!")
    print("\nKey improvements implemented:")
    print("• GraphQL protocol support with introspection testing")
    print("• WebSocket connection and message testing")
    print("• Integrated authentication with automatic session management")
    print("• Memory-efficient result streaming and pagination")
    print("• Enhanced SSL verification with strong security settings")
    print("• Comprehensive test suites supporting multiple protocols")
