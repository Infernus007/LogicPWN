#!/usr/bin/env python3
"""
LogicPWN Basic Example - Simple HTTP Requests
This example demonstrates basic LogicPWN functionality with simple HTTP requests.
"""

import asyncio
from logicpwn.core.runner import AsyncRequestRunner

async def basic_request_example():
    """Demonstrate basic HTTP requests with LogicPWN"""
    print("🎯 LogicPWN Basic Request Example")
    print("=" * 40)
    
    async with AsyncRequestRunner() as runner:
        try:
            # Example 1: Simple GET request
            print("1. Simple GET request...")
            response = await runner.send_request("http://httpbin.org/get")
            print(f"   Status: {response.status_code}")
            print(f"   Headers count: {len(response.headers)}")
            
            # Example 2: POST request with data
            print("\n2. POST request with form data...")
            post_data = {"key": "value", "test": "data"}
            response = await runner.send_request(
                "http://httpbin.org/post",
                method="POST",
                data=post_data
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response size: {len(response.body)}")
            
            # Example 3: Request with custom headers
            print("\n3. Request with custom headers...")
            custom_headers = {
                "User-Agent": "LogicPWN-Example/1.0",
                "X-Custom-Header": "test-value"
            }
            response = await runner.send_request(
                "http://httpbin.org/headers",
                headers=custom_headers
            )
            print(f"   Status: {response.status_code}")
            print(f"   Security analysis available: {response.security_analysis is not None}")
            
            print("\n✅ Basic request examples completed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def security_analysis_example():
    """Demonstrate security analysis features"""
    print("\n🔍 LogicPWN Security Analysis Example")
    print("=" * 40)
    
    async with AsyncRequestRunner() as runner:
        try:
            # Test against a site with various response types
            response = await runner.send_request("http://httpbin.org/json")
            
            if response.security_analysis:
                analysis = response.security_analysis
                print(f"📊 Security Analysis Results:")
                print(f"   Has sensitive data: {analysis.has_sensitive_data}")
                print(f"   Has error messages: {analysis.has_error_messages}")
                print(f"   Has debug info: {analysis.has_debug_info}")
                print(f"   Has CSRF tokens: {analysis.has_csrf_tokens}")
            else:
                print("ℹ️  No security analysis available")
                
        except Exception as e:
            print(f"❌ Security analysis error: {e}")

async def main():
    """Run all basic examples"""
    print("🚀 LogicPWN Basic Examples")
    print("=" * 50)
    print("This demonstrates core LogicPWN functionality")
    print()
    
    await basic_request_example()
    await security_analysis_example()
    
    print("\n🎉 All examples completed!")
    print("\nNext steps:")
    print("- Try dvwa_real_test.py for DVWA testing")
    print("- Try dvwa_auth_example.py for authentication")

if __name__ == "__main__":
    asyncio.run(main())
