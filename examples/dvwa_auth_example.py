#!/usr/bin/env python3
"""
DVWA Authentication Example - Working with Real DVWA
This example demonstrates actual login to DVWA using LogicPWN.
Make sure DVWA is running on localhost:8080 and database is setup.
"""

import asyncio

from logicpwn.core.auth import AuthConfig, authenticate_session
from logicpwn.core.runner import AsyncRequestRunner


async def dvwa_login_example():
    """Demonstrate real DVWA login"""
    print("🎯 LogicPWN DVWA Authentication Example")
    print("=" * 50)

    # DVWA default credentials
    credentials = {"username": "admin", "password": "admin"}

    # Create auth config for DVWA
    auth_config = AuthConfig(
        login_url="http://localhost:8080/login.php",
        username_field="username",
        password_field="password",
        login_success_indicator="index.php",
        login_failure_indicator="Login failed",
        csrf_token_field="user_token",
        method="POST",
    )

    async with AsyncRequestRunner() as runner:
        try:
            print("🔐 Testing DVWA Login...")

            # First get the login page to check for CSRF tokens
            print("1. Getting login page...")
            login_page = await runner.send_request("http://localhost:8080/login.php")
            print(f"   Status: {login_page.status_code}")

            if (
                login_page.security_analysis
                and login_page.security_analysis.has_csrf_tokens
            ):
                print("   🛡️  CSRF tokens detected")

            # Attempt authentication
            print("2. Attempting authentication...")
            result = await authenticate_session(auth_config, credentials)

            if result.success:
                print("✅ Login successful!")
                print(f"   Session ID: {result.session_id}")
                print(f"   Response URL: {result.response_url}")

                # Test authenticated request
                print("3. Testing authenticated request...")
                # Use the authenticated session to access a protected page
                auth_response = await runner.send_request(
                    "http://localhost:8080/",
                    headers={"Cookie": f"PHPSESSID={result.session_id}"},
                )

                if "logout" in auth_response.body.lower():
                    print("✅ Successfully authenticated - logout link found!")
                else:
                    print("⚠️  Authentication status unclear")

            else:
                print("❌ Login failed!")
                print(f"   Error: {result.error_message}")
                print("💡 Try setting up DVWA database first:")
                print("   Visit: http://localhost:8080/setup.php")

        except Exception as e:
            print(f"❌ Authentication error: {e}")
            print("💡 Make sure DVWA is running on localhost:8080")


async def dvwa_setup_database():
    """Help setup DVWA database"""
    print("\n🔧 DVWA Database Setup Helper")
    print("=" * 50)

    async with AsyncRequestRunner() as runner:
        try:
            # Check setup page
            setup_page = await runner.send_request("http://localhost:8080/setup.php")

            if "create database" in setup_page.body.lower():
                print("📋 Database needs to be created")
                print("🔗 Visit: http://localhost:8080/setup.php")
                print("🖱️  Click 'Create / Reset Database' button")

                # Try to auto-create database (if button click is possible)
                # This would require form parsing and submission
                print("💡 You may need to manually click the setup button")

            else:
                print("✅ Database appears to be setup")

        except Exception as e:
            print(f"❌ Setup check failed: {e}")


async def main():
    """Run DVWA authentication examples"""
    print("🎯 LogicPWN DVWA Real Authentication Testing")
    print("=" * 60)
    print("Testing against real DVWA instance on localhost:8080")
    print()

    # Check if DVWA is accessible
    async with AsyncRequestRunner() as runner:
        try:
            response = await runner.send_request("http://localhost:8080")
            if response.status_code != 200:
                print(
                    "❌ DVWA not accessible. Make sure it's running on localhost:8080"
                )
                return
        except Exception as e:
            print(f"❌ Cannot connect to DVWA: {e}")
            print("💡 Run: docker run -d -p 8080:80 vulnerables/web-dvwa:latest")
            return

    # Setup database if needed
    await dvwa_setup_database()

    # Attempt login
    await dvwa_login_example()

    print("\n🎉 DVWA authentication testing completed!")
    print("\nNext steps:")
    print("- Try other DVWA vulnerabilities")
    print("- Test with different security levels")
    print("- Explore exploit chaining examples")


if __name__ == "__main__":
    asyncio.run(main())
