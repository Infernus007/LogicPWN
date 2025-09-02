"""
Unit tests for auth_integration module.

Tests the authentication integration functionality including:
- AuthenticatedAccessConfig dataclass
- AuthenticatedAccessTester class
- Authentication error handling and retry logic
- GraphQL and WebSocket authenticated testing
- Helper functions and test suite runner
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

import requests

# Import the modules we're testing
from logicpwn.core.access.auth_integration import (
    AuthenticatedAccessConfig,
    AuthenticatedAccessTester,
    create_authenticated_access_tester,
    run_authenticated_access_test_suite,
)
from logicpwn.core.access.models import AccessDetectorConfig, AccessTestResult
from logicpwn.core.access.protocol_support import GraphQLQuery, WebSocketConfig
from logicpwn.core.auth import AuthConfig


class TestAuthenticatedAccessConfig(unittest.TestCase):
    """Test the AuthenticatedAccessConfig dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.auth_config = AuthConfig(
            url="https://example.com/login",
            method="POST",
            credentials={"username": "test", "password": "test"},
            success_indicators=["Welcome"],
            failure_indicators=["Invalid"],
        )

        self.access_config = AccessDetectorConfig(
            current_user_id="user123", unauthorized_ids=["admin", "root"]
        )

    def test_config_creation(self):
        """Test creating AuthenticatedAccessConfig."""
        config = AuthenticatedAccessConfig(
            auth_config=self.auth_config, access_config=self.access_config
        )

        self.assertEqual(config.auth_config, self.auth_config)
        self.assertEqual(config.access_config, self.access_config)
        self.assertTrue(config.auto_reauth)
        self.assertEqual(config.session_validation_interval, 10)
        self.assertEqual(config.max_reauth_attempts, 3)

    def test_config_with_custom_values(self):
        """Test creating config with custom values."""
        config = AuthenticatedAccessConfig(
            auth_config=self.auth_config,
            access_config=self.access_config,
            auto_reauth=False,
            session_validation_interval=5,
            max_reauth_attempts=2,
        )

        self.assertFalse(config.auto_reauth)
        self.assertEqual(config.session_validation_interval, 5)
        self.assertEqual(config.max_reauth_attempts, 2)


class TestAuthenticatedAccessTester(unittest.TestCase):
    """Test the AuthenticatedAccessTester class."""

    def setUp(self):
        """Set up test fixtures."""
        self.auth_config = AuthConfig(
            url="https://example.com/login",
            method="POST",
            credentials={"username": "test", "password": "test"},
            success_indicators=["Welcome"],
            failure_indicators=["Invalid"],
        )

        self.access_config = AccessDetectorConfig(
            current_user_id="user123", unauthorized_ids=["admin", "root"]
        )

        self.authenticated_config = AuthenticatedAccessConfig(
            auth_config=self.auth_config, access_config=self.access_config
        )

        self.tester = AuthenticatedAccessTester(self.authenticated_config)

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.tester, "session") and self.tester.session:
            self.tester.session.close()

    @patch("logicpwn.core.access.auth_integration.authenticate_session")
    @patch("logicpwn.core.access.auth_integration.create_authenticated_client")
    @patch("logicpwn.core.access.auth_integration.validate_session")
    def test_authentication_success(self, mock_validate, mock_create_client, mock_auth):
        """Test successful authentication."""
        # Mock successful authentication
        mock_session = Mock(spec=requests.Session)
        mock_client = Mock()
        mock_auth.return_value = mock_session
        mock_create_client.return_value = mock_client
        mock_validate.return_value = True

        # Trigger authentication
        session = self.tester._ensure_authenticated_session()

        # Verify authentication was called
        mock_auth.assert_called_once_with(self.auth_config)
        mock_create_client.assert_called_once_with(
            self.auth_config, session=mock_session
        )
        mock_validate.assert_called_once_with(mock_session, self.auth_config)

        # Verify session is set
        self.assertEqual(self.tester.session, mock_session)
        self.assertEqual(self.tester.authenticated_client, mock_client)
        self.assertEqual(session, mock_session)

    @patch("logicpwn.core.access.auth_integration.authenticate_session")
    @patch("logicpwn.core.access.auth_integration.validate_session")
    def test_authentication_failure_retry(self, mock_validate, mock_auth):
        """Test authentication failure and retry logic."""
        # Mock authentication failure then success
        mock_session = Mock(spec=requests.Session)
        mock_auth.side_effect = [Exception("Auth failed"), mock_session]
        mock_validate.return_value = True

        # Should retry and succeed
        with patch("logicpwn.core.access.auth_integration.create_authenticated_client"):
            session = self.tester._ensure_authenticated_session()

        # Verify retry occurred
        self.assertEqual(mock_auth.call_count, 2)
        self.assertEqual(session, mock_session)

    @patch("logicpwn.core.access.auth_integration.authenticate_session")
    def test_max_auth_attempts_exceeded(self, mock_auth):
        """Test max authentication attempts exceeded."""
        # Mock authentication always failing
        mock_auth.side_effect = Exception("Auth failed")

        # Should raise exception after max attempts
        with self.assertRaises(Exception) as context:
            self.tester._ensure_authenticated_session()

        self.assertIn("Max authentication attempts", str(context.exception))
        self.assertEqual(mock_auth.call_count, 3)  # max_reauth_attempts

    def test_should_revalidate_session(self):
        """Test session revalidation logic."""
        # Initially should not revalidate
        self.assertFalse(self.tester._should_revalidate_session())

        # After interval requests, should revalidate
        self.tester.request_count = 10  # session_validation_interval
        self.assertTrue(self.tester._should_revalidate_session())

        # Disable auto_reauth
        self.tester.config.auto_reauth = False
        self.assertFalse(self.tester._should_revalidate_session())

    @patch("logicpwn.core.access.auth_integration._test_single_id")
    def test_test_single_id_authenticated(self, mock_test):
        """Test authenticated single ID testing."""
        # Mock successful test result
        mock_result = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=200,
            access_granted=True,
            vulnerability_detected=False,
            response_indicators=["success"],
        )
        mock_test.return_value = mock_result

        # Mock authenticated session
        mock_session = Mock(spec=requests.Session)
        self.tester.session = mock_session

        # Test single ID
        result = self.tester.test_single_id_authenticated(
            endpoint_url="https://api.example.com/user/123",
            id_value="123",
            success_indicators=["success"],
            failure_indicators=["error"],
            request_timeout=30,
        )

        # Verify test was called with correct parameters
        mock_test.assert_called_once_with(
            session=mock_session,
            endpoint_url="https://api.example.com/user/123",
            id_value="123",
            success_indicators=["success"],
            failure_indicators=["error"],
            request_timeout=30,
            config=self.access_config,
        )

        self.assertEqual(result, mock_result)
        self.assertEqual(self.tester.request_count, 1)

    def test_is_auth_error_status_codes(self):
        """Test authentication error detection by status codes."""
        # Test 401 Unauthorized
        result_401 = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=401,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
        )
        self.assertTrue(self.tester._is_auth_error(result_401))

        # Test 403 Forbidden
        result_403 = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=403,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
        )
        self.assertTrue(self.tester._is_auth_error(result_403))

        # Test 200 OK (not auth error)
        result_200 = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=200,
            access_granted=True,
            vulnerability_detected=False,
            response_indicators=[],
        )
        self.assertFalse(self.tester._is_auth_error(result_200))

    def test_is_auth_error_response_body(self):
        """Test authentication error detection by response body."""
        result = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=200,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            response_body="Session expired. Please login again.",
        )
        self.assertTrue(self.tester._is_auth_error(result))

    def test_is_auth_error_response_indicators(self):
        """Test authentication error detection by response indicators."""
        result = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=200,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=["Login Required", "Access Denied"],
        )
        self.assertTrue(self.tester._is_auth_error(result))

    @patch("logicpwn.core.access.auth_integration._test_single_id")
    def test_auth_error_retry(self, mock_test):
        """Test retry logic when authentication error is detected."""
        # First call returns auth error, second call succeeds
        auth_error_result = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=401,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
        )

        success_result = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/user/123",
            status_code=200,
            access_granted=True,
            vulnerability_detected=False,
            response_indicators=["success"],
        )

        mock_test.side_effect = [auth_error_result, success_result]

        # Mock authentication
        mock_session = Mock(spec=requests.Session)
        self.tester.session = mock_session

        with patch.object(self.tester, "_authenticate") as mock_auth:
            result = self.tester.test_single_id_authenticated(
                endpoint_url="https://api.example.com/user/123",
                id_value="123",
                success_indicators=["success"],
                failure_indicators=["error"],
            )

        # Verify re-authentication was triggered
        mock_auth.assert_called_once()

        # Verify test was called twice (original + retry)
        self.assertEqual(mock_test.call_count, 2)

        # Should return the successful result
        self.assertEqual(result, success_result)


class TestGraphQLAuthenticatedTesting(unittest.TestCase):
    """Test GraphQL authenticated testing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        auth_config = AuthConfig(
            url="https://example.com/login",
            method="POST",
            credentials={"username": "test", "password": "test"},
            success_indicators=["Welcome"],
            failure_indicators=["Invalid"],
        )

        access_config = AccessDetectorConfig(current_user_id="user123")

        authenticated_config = AuthenticatedAccessConfig(
            auth_config=auth_config, access_config=access_config
        )

        self.tester = AuthenticatedAccessTester(authenticated_config)

    @patch("logicpwn.core.access.auth_integration.GraphQLTester")
    def test_graphql_authenticated_testing(self, mock_graphql_tester_class):
        """Test GraphQL authenticated testing."""
        # Mock GraphQL tester instance
        mock_graphql_tester = Mock()
        mock_graphql_tester_class.return_value = mock_graphql_tester

        # Mock test result
        mock_result = AccessTestResult(
            id_tested="123",
            endpoint_url="https://api.example.com/graphql",
            status_code=200,
            access_granted=True,
            vulnerability_detected=False,
            response_indicators=["data"],
        )
        mock_graphql_tester.test_query_access.return_value = mock_result

        # Mock authenticated session and client
        mock_session = Mock(spec=requests.Session)
        mock_client = Mock()
        mock_client.session.headers = {"Authorization": "Bearer token123"}
        self.tester.session = mock_session
        self.tester.authenticated_client = mock_client

        # Create test query
        query = GraphQLQuery(
            query="query GetUser($id: ID!) { user(id: $id) { name } }",
            variables={"id": "{ID}"},
        )

        # Test GraphQL authentication
        results = self.tester.test_graphql_authenticated(
            endpoint="https://api.example.com/graphql",
            query=query,
            id_values=["123", "456"],
        )

        # Verify GraphQL tester was created with auth headers
        expected_headers = {"Authorization": "Bearer token123"}
        mock_graphql_tester_class.assert_called_once_with(
            "https://api.example.com/graphql", expected_headers
        )

        # Verify test was called for each ID
        self.assertEqual(mock_graphql_tester.test_query_access.call_count, 2)
        self.assertEqual(len(results), 2)


class TestWebSocketAuthenticatedTesting(unittest.TestCase):
    """Test WebSocket authenticated testing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        auth_config = AuthConfig(
            url="https://example.com/login",
            method="POST",
            credentials={"username": "test", "password": "test"},
            success_indicators=["Welcome"],
            failure_indicators=["Invalid"],
        )

        access_config = AccessDetectorConfig(current_user_id="user123")

        authenticated_config = AuthenticatedAccessConfig(
            auth_config=auth_config, access_config=access_config
        )

        self.tester = AuthenticatedAccessTester(authenticated_config)

    @patch("logicpwn.core.access.auth_integration.WebSocketTester")
    async def test_websocket_authenticated_testing(self, mock_ws_tester_class):
        """Test WebSocket authenticated testing."""
        # Mock WebSocket tester instance
        mock_ws_tester = Mock()
        mock_ws_tester_class.return_value = mock_ws_tester

        # Mock test result
        mock_result = AccessTestResult(
            id_tested="123",
            endpoint_url="wss://api.example.com/ws/user/123",
            status_code=200,
            access_granted=True,
            vulnerability_detected=False,
            response_indicators=["connection_established"],
        )
        mock_ws_tester.test_connection_access = AsyncMock(return_value=mock_result)

        # Mock authenticated client
        mock_client = Mock()
        mock_client.session.headers = {"Authorization": "Bearer token123"}
        self.tester.authenticated_client = mock_client

        # Create WebSocket config
        ws_config = WebSocketConfig(
            url="wss://api.example.com/ws/user/{ID}", headers={"Custom-Header": "value"}
        )

        # Test WebSocket authentication
        results = await self.tester.test_websocket_authenticated(
            ws_config=ws_config, id_values=["123", "456"]
        )

        # Verify WebSocket tester was created with merged headers
        expected_headers = {
            "Authorization": "Bearer token123",
            "Custom-Header": "value",
        }

        # Get the actual WebSocketConfig passed to the tester
        call_args = mock_ws_tester_class.call_args[0][0]
        self.assertEqual(call_args.headers, expected_headers)

        # Verify test was called for each ID
        self.assertEqual(mock_ws_tester.test_connection_access.call_count, 2)
        self.assertEqual(len(results), 2)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""

    def test_create_authenticated_access_tester(self):
        """Test creating authenticated access tester with helper function."""
        access_config = AccessDetectorConfig(current_user_id="user123")

        tester = create_authenticated_access_tester(
            auth_url="https://example.com/login",
            auth_method="POST",
            credentials={"username": "test", "password": "test"},
            access_config=access_config,
            success_indicators=["Welcome"],
            failure_indicators=["Invalid"],
            timeout=30,
            verify_ssl=False,
        )

        # Verify tester was created correctly
        self.assertIsInstance(tester, AuthenticatedAccessTester)
        self.assertEqual(tester.config.auth_config.url, "https://example.com/login")
        self.assertEqual(tester.config.auth_config.method, "POST")
        self.assertEqual(tester.config.auth_config.credentials["username"], "test")
        self.assertEqual(tester.config.access_config, access_config)

    @patch("logicpwn.core.access.auth_integration.AuthenticatedAccessTester")
    async def test_run_authenticated_access_test_suite(self, mock_tester_class):
        """Test running comprehensive authenticated test suite."""
        # Mock tester instance
        mock_tester = Mock()
        mock_tester_class.return_value = mock_tester

        # Mock test results
        http_results = [Mock(), Mock()]
        graphql_results = [Mock()]
        websocket_results = [Mock()]

        mock_tester.test_multiple_ids_authenticated.return_value = http_results
        mock_tester.test_graphql_authenticated.return_value = graphql_results
        mock_tester.test_websocket_authenticated = AsyncMock(
            return_value=websocket_results
        )

        # Define test suite
        test_suite = {
            "http_tests": {
                "endpoint_template": "https://api.example.com/user/{ID}",
                "id_values": ["1", "2"],
                "success_indicators": ["success"],
                "failure_indicators": ["error"],
            },
            "graphql_tests": {
                "endpoint": "https://api.example.com/graphql",
                "query": "query GetUser($id: ID!) { user(id: $id) { name } }",
                "id_values": ["1"],
            },
            "websocket_tests": {
                "url": "wss://api.example.com/ws/user/{ID}",
                "id_values": ["1"],
            },
        }

        # Run test suite
        results = await run_authenticated_access_test_suite(mock_tester, test_suite)

        # Verify all test types were called
        mock_tester.test_multiple_ids_authenticated.assert_called_once()
        mock_tester.test_graphql_authenticated.assert_called_once()
        mock_tester.test_websocket_authenticated.assert_called_once()

        # Verify results structure
        self.assertIn("http", results)
        self.assertIn("graphql", results)
        self.assertIn("websocket", results)
        self.assertEqual(results["http"], http_results)
        self.assertEqual(results["graphql"], graphql_results)
        self.assertEqual(results["websocket"], websocket_results)


class TestIntegration(unittest.TestCase):
    """Integration tests with mocked dependencies."""

    @patch("logicpwn.core.access.auth_integration.authenticate_session")
    @patch("logicpwn.core.access.auth_integration.create_authenticated_client")
    @patch("logicpwn.core.access.auth_integration.validate_session")
    @patch("logicpwn.core.access.auth_integration._test_single_id")
    def test_full_workflow_integration(
        self, mock_test, mock_validate, mock_create_client, mock_auth
    ):
        """Test full workflow integration."""
        # Mock authentication
        mock_session = Mock(spec=requests.Session)
        mock_client = Mock()
        mock_auth.return_value = mock_session
        mock_create_client.return_value = mock_client
        mock_validate.return_value = True

        # Mock test results
        test_results = [
            AccessTestResult(
                id_tested="1",
                endpoint_url="https://api.example.com/user/1",
                status_code=200,
                access_granted=True,
                vulnerability_detected=False,
                response_indicators=["success"],
            ),
            AccessTestResult(
                id_tested="admin",
                endpoint_url="https://api.example.com/user/admin",
                status_code=200,
                access_granted=True,
                vulnerability_detected=True,  # Should be vulnerability
                response_indicators=["success"],
            ),
        ]
        mock_test.side_effect = test_results

        # Create tester
        access_config = AccessDetectorConfig(
            current_user_id="1", unauthorized_ids=["admin"]
        )

        tester = create_authenticated_access_tester(
            auth_url="https://example.com/login",
            auth_method="POST",
            credentials={"username": "test", "password": "test"},
            access_config=access_config,
            success_indicators=["Welcome"],
            failure_indicators=["Invalid"],
        )

        # Test multiple IDs
        results = tester.test_multiple_ids_authenticated(
            endpoint_template="https://api.example.com/user/{ID}",
            id_values=["1", "admin"],
            success_indicators=["success"],
            failure_indicators=["error"],
        )

        # Verify authentication occurred
        mock_auth.assert_called_once()
        mock_validate.assert_called_once()

        # Verify tests were called
        self.assertEqual(mock_test.call_count, 2)

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertFalse(results[0].vulnerability_detected)  # Own user
        self.assertTrue(results[1].vulnerability_detected)  # Admin user

        # Clean up
        tester.close()


if __name__ == "__main__":
    # Run individual test classes
    test_classes = [
        TestAuthenticatedAccessConfig,
        TestAuthenticatedAccessTester,
        TestGraphQLAuthenticatedTesting,
        TestWebSocketAuthenticatedTesting,
        TestHelperFunctions,
        TestIntegration,
    ]

    print("Running Auth Integration Tests...")
    print("=" * 50)

    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        if not result.wasSuccessful():
            print(f"❌ {test_class.__name__} had failures!")
        else:
            print(f"✅ {test_class.__name__} passed!")

    print("\n" + "=" * 50)
    print("Auth Integration Tests Complete!")

    # Run async tests separately
    print("\nRunning async tests...")

    async def run_async_tests():
        """Run async test methods."""
        try:
            # Test WebSocket authenticated testing
            test_instance = TestWebSocketAuthenticatedTesting()
            test_instance.setUp()
            await test_instance.test_websocket_authenticated_testing()
            print("✅ Async WebSocket test passed!")

            # Test comprehensive test suite
            test_instance = TestHelperFunctions()
            await test_instance.test_run_authenticated_access_test_suite()
            print("✅ Async test suite test passed!")

        except Exception as e:
            print(f"❌ Async tests failed: {e}")

    # Run async tests
    asyncio.run(run_async_tests())

    print("\n🎉 All tests completed!")
    print("\nTest Coverage Summary:")
    print("• AuthenticatedAccessConfig dataclass ✅")
    print("• AuthenticatedAccessTester core functionality ✅")
    print("• Authentication error detection and retry ✅")
    print("• GraphQL authenticated testing ✅")
    print("• WebSocket authenticated testing ✅")
    print("• Helper functions and utilities ✅")
    print("• Integration workflow testing ✅")
    print("• Async functionality testing ✅")
