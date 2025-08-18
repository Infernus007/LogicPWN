#!/usr/bin/env python3
"""
DVWA Proper Setup and Login Workflow
This example demonstrates the correct DVWA workflow:
1. Setup database (if needed)
2. Login with admin/admin 
3. Navigate to index page
4. Access vulnerability pages
5. Test XSS vulnerabilities

Run with: poetry run python examples/08_dvwa_working_flow.py
"""

import asyncio
import re
from urllib.parse import urlencode
from logicpwn.core.runner import AsyncRequestRunner

async def setup_dvwa_database():
    """Setup DVWA database if needed"""
    print("🔧 Setting up DVWA database...")
    
    async with AsyncRequestRunner() as runner:
        try:
            # Get setup page and token
            setup_response = await runner.send_request("http://localhost:8080/setup.php")
            
            if setup_response.status_code != 200:
                print("❌ Cannot access setup page")
                return False
            
            # Extract CSRF token for database creation
            token_match = re.search(r'user_token["\']?\s*value=["\']([^"\']+)', setup_response.body)
            if not token_match:
                print("❌ Cannot find CSRF token for setup")
                return False
            
            setup_token = token_match.group(1)
            print(f"   🛡️  Found setup token: {setup_token[:20]}...")
            
            # Check if database needs setup
            if "create / reset database" in setup_response.body.lower():
                print("   📋 Database needs creation - setting up...")
                
                # Create database
                setup_data = {
                    "create_db": "Create / Reset Database",
                    "user_token": setup_token
                }
                
                create_response = await runner.send_request(
                    "http://localhost:8080/setup.php",
                    method="POST",
                    data=setup_data
                )
                
                if "database has been created" in create_response.body.lower() or \
                   "setup successful" in create_response.body.lower():
                    print("   ✅ Database created successfully!")
                    return True
                else:
                    print("   ⚠️  Database creation response received")
                    return True  # Assume success if no error
            else:
                print("   ✅ Database already exists")
                return True
                
        except Exception as e:
            print(f"   ❌ Database setup error: {e}")
            return False

async def login_to_dvwa():
    """Login to DVWA with admin/admin credentials"""
    print("\n🔐 Logging into DVWA...")
    
    async with AsyncRequestRunner() as runner:
        try:
            # Get login page
            login_response = await runner.send_request("http://localhost:8080/login.php")
            
            if login_response.status_code != 200:
                print("   ❌ Cannot access login page")
                return None
            
            print(f"   📄 Login page status: {login_response.status_code}")
            
            # Extract CSRF token
            csrf_token = None
            token_match = re.search(r'user_token["\']?\s*value=["\']([^"\']+)', login_response.body)
            if token_match:
                csrf_token = token_match.group(1)
                print(f"   🛡️  Found CSRF token: {csrf_token[:20]}...")
            
            # Prepare login data  
            login_data = {
                "username": "admin",
                "password": "password",  # Default DVWA credentials after DB setup
                "Login": "Login"
            }
            
            if csrf_token:
                login_data["user_token"] = csrf_token
            
            print("   🔑 Submitting login credentials (admin/password)...")
            
            # Perform login
            login_result = await runner.send_request(
                "http://localhost:8080/login.php",
                method="POST",
                data=login_data
            )
            
            print(f"   📄 Login response status: {login_result.status_code}")
            
            # Check for successful login (should redirect or show index)
            if login_result.status_code == 302:
                # Handle redirect
                location = login_result.headers.get("Location", "")
                print(f"   ↗️  Redirect to: {location}")
                
                if "index.php" in location:
                    print("   ✅ Login successful - redirected to index!")
                elif "setup.php" in location:
                    print("   ⚠️  Redirected to setup - database may need setup")
                    return None
            elif "welcome to damn vulnerable web application" in login_result.body.lower():
                print("   ✅ Login successful - welcome page detected!")
            elif "login failed" in login_result.body.lower():
                print("   ❌ Login failed - incorrect credentials")
                return None
            else:
                print("   ℹ️  Login response received - checking content...")
            
            # Extract session cookie
            session_cookie = None
            all_cookies = login_result.headers.get("Set-Cookie", "")
            cookie_match = re.search(r'PHPSESSID=([^;]+)', all_cookies)
            if cookie_match:
                session_cookie = cookie_match.group(1)
                print(f"   🍪 Session cookie: {session_cookie}")
            else:
                # Try to get cookie from login page response
                cookie_match = re.search(r'PHPSESSID=([^;]+)', login_response.headers.get("Set-Cookie", ""))
                if cookie_match:
                    session_cookie = cookie_match.group(1)
                    print(f"   🍪 Using login page cookie: {session_cookie}")
            
            return session_cookie
            
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return None

async def access_index_page(session_cookie):
    """Access DVWA index page to verify login"""
    print("\n🏠 Accessing DVWA index page...")
    
    if not session_cookie:
        print("   ❌ No session cookie available")
        return False
    
    async with AsyncRequestRunner() as runner:
        try:
            headers = {"Cookie": f"PHPSESSID={session_cookie}"}
            
            # Try to access index page
            index_response = await runner.send_request(
                "http://localhost:8080/index.php", 
                headers=headers
            )
            
            print(f"   📄 Index page status: {index_response.status_code}")
            
            if index_response.status_code == 200:
                if "logout" in index_response.body.lower():
                    print("   ✅ Successfully authenticated - logout link found!")
                    return True
                elif "vulnerabilities" in index_response.body.lower():
                    print("   ✅ Successfully authenticated - vulnerabilities menu found!")
                    return True
                else:
                    print("   ⚠️  Index page loaded but authentication unclear")
                    return True
            else:
                print(f"   ❌ Cannot access index page: {index_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Index page error: {e}")
            return False

async def test_reflected_xss(session_cookie):
    """Test reflected XSS vulnerability"""
    print("\n🎯 Testing Reflected XSS...")
    
    if not session_cookie:
        print("   ❌ No session available")
        return
    
    async with AsyncRequestRunner() as runner:
        try:
            headers = {"Cookie": f"PHPSESSID={session_cookie}"}
            
            # Access reflected XSS page
            xss_url = "http://localhost:8080/vulnerabilities/xss_r/"
            response = await runner.send_request(xss_url, headers=headers)
            
            print(f"   📄 XSS page status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ XSS page accessible")
                
                # Test XSS payload
                xss_payload = "<script>alert('Reflected XSS')</script>"
                test_url = f"{xss_url}?name={xss_payload}"
                
                print(f"   🔍 Testing payload: {xss_payload}")
                print(f"   🔗 Generated URL: {test_url}")
                
                # Send XSS payload
                xss_response = await runner.send_request(test_url, headers=headers)
                
                if xss_response.status_code == 200:
                    # Check if payload is reflected
                    if xss_payload in xss_response.body:
                        print("   🚨 XSS VULNERABILITY FOUND - Payload reflected!")
                        print("   💀 This URL can be used to exploit victims:")
                        print(f"       {test_url}")
                    elif "&lt;script&gt;" in xss_response.body:
                        print("   🛡️  Payload encoded - XSS appears to be mitigated")
                    else:
                        print("   ℹ️  Payload not found in response")
                else:
                    print(f"   ❌ XSS test failed: {xss_response.status_code}")
            else:
                print(f"   ❌ Cannot access XSS page: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ XSS test error: {e}")

async def main():
    """Run complete DVWA workflow"""
    print("🎯 DVWA Complete Working Workflow")
    print("=" * 60)
    print("Proper sequence: setup → login → index → vulnerabilities")
    print()
    
    # Step 1: Check DVWA availability
    async with AsyncRequestRunner() as runner:
        try:
            response = await runner.send_request("http://localhost:8080")
            if response.status_code != 200:
                print("❌ DVWA not accessible on localhost:8080")
                print("💡 Run: docker run -d -p 8080:80 vulnerables/web-dvwa:latest")
                return
            print("✅ DVWA is accessible")
        except Exception as e:
            print(f"❌ Cannot connect to DVWA: {e}")
            return
    
    # Step 2: Setup database if needed
    db_setup = await setup_dvwa_database()
    if not db_setup:
        print("❌ Database setup failed")
        return
    
    # Step 3: Login to DVWA  
    session_cookie = await login_to_dvwa()
    if not session_cookie:
        print("❌ Login failed - cannot proceed")
        return
    
    # Step 4: Access index page
    index_success = await access_index_page(session_cookie)
    if not index_success:
        print("❌ Cannot access index page")
        return
    
    # Step 5: Test vulnerabilities
    await test_reflected_xss(session_cookie)
    
    print("\n🎉 Complete DVWA workflow test finished!")
    print("\n💡 Next steps:")
    print("• Test other vulnerabilities (stored XSS, SQL injection)")  
    print("• Change security level and retest")
    print("• Build exploit chains")

if __name__ == "__main__":
    asyncio.run(main())
