#!/usr/bin/env python3
"""
LogicPWN DVWA Complete Example
This example demonstrates complete DVWA testing workflow:
1. Check DVWA availability 
2. Setup database if needed
3. Login with admin/admin
4. Access vulnerability pages

Prerequisites: DVWA running on localhost:8080
Run: docker run -d -p 8080:80 vulnerables/web-dvwa:latest
"""

import asyncio
import re
from logicpwn.core.runner import AsyncRequestRunner

async def check_dvwa_status():
    """Check if DVWA is accessible"""
    print("🔍 Checking DVWA status...")
    
    async with AsyncRequestRunner() as runner:
        try:
            response = await runner.send_request("http://localhost:8080")
            if response.status_code == 200 and "dvwa" in response.body.lower():
                print("✅ DVWA is accessible")
                return True
            else:
                print("❌ DVWA not found")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to DVWA: {e}")
            print("💡 Run: docker run -d -p 8080:80 vulnerables/web-dvwa:latest")
            return False

async def setup_dvwa_database():
    """Setup DVWA database if needed"""
    print("\n🔧 Checking DVWA database setup...")
    
    async with AsyncRequestRunner() as runner:
        try:
            response = await runner.send_request("http://localhost:8080/setup.php")
            
            if "create database" in response.body.lower():
                print("📋 Database needs setup")
                print("🔗 Visit http://localhost:8080/setup.php and click 'Create / Reset Database'")
                return False
            else:
                print("✅ Database appears to be configured")
                return True
                
        except Exception as e:
            print(f"❌ Setup check failed: {e}")
            return False

async def login_to_dvwa():
    """Login to DVWA with admin/admin credentials"""
    print("\n🔐 Logging into DVWA...")
    
    async with AsyncRequestRunner() as runner:
        try:
            # Step 1: Get login page and extract any tokens
            login_response = await runner.send_request("http://localhost:8080/login.php")
            
            if login_response.status_code != 200:
                print("❌ Cannot access login page")
                return None
                
            # Extract CSRF token if present
            csrf_token = None
            token_match = re.search(r'user_token["\']?\s*value=["\']([^"\']+)', login_response.body)
            if token_match:
                csrf_token = token_match.group(1)
                print(f"🛡️  Found CSRF token: {csrf_token[:20]}...")
            
            # Step 2: Prepare login data
            login_data = {
                "username": "admin",
                "password": "admin",
                "Login": "Login"
            }
            
            if csrf_token:
                login_data["user_token"] = csrf_token
            
            # Step 3: Perform login
            print("🔑 Attempting login...")
            login_result = await runner.send_request(
                "http://localhost:8080/login.php",
                method="POST",
                data=login_data
            )
            
            # Step 4: Check if login was successful
            if login_result.status_code == 302 or "index.php" in str(login_result.headers.get("Location", "")):
                print("✅ Login successful!")
                
                # Extract session cookie
                session_cookie = None
                set_cookie = login_result.headers.get("Set-Cookie", "")
                cookie_match = re.search(r'PHPSESSID=([^;]+)', set_cookie)
                if cookie_match:
                    session_cookie = cookie_match.group(1)
                    print(f"🍪 Session cookie: {session_cookie}")
                    
                return session_cookie
            else:
                print("❌ Login failed - check credentials or database setup")
                return None
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None

async def explore_dvwa_vulnerabilities(session_cookie):
    """Explore DVWA vulnerability pages"""
    print("\n🎯 Exploring DVWA vulnerabilities...")
    
    if not session_cookie:
        print("❌ No valid session - cannot explore vulnerabilities")
        return
    
    headers = {"Cookie": f"PHPSESSID={session_cookie}"}
    
    # List of DVWA vulnerability pages
    vulnerability_pages = [
        ("SQL Injection", "/vulnerabilities/sqli/"),
        ("XSS Reflected", "/vulnerabilities/xss_r/"),
        ("XSS Stored", "/vulnerabilities/xss_s/"),
        ("CSRF", "/vulnerabilities/csrf/"),
        ("File Inclusion", "/vulnerabilities/fi/"),
        ("File Upload", "/vulnerabilities/upload/"),
        ("Command Injection", "/vulnerabilities/exec/"),
        ("Brute Force", "/vulnerabilities/brute/")
    ]
    
    async with AsyncRequestRunner() as runner:
        for vuln_name, vuln_path in vulnerability_pages:
            try:
                url = f"http://localhost:8080{vuln_path}"
                response = await runner.send_request(url, headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ {vuln_name}: Accessible")
                    
                    # Check for interesting elements
                    if "form" in response.body.lower():
                        form_count = response.body.lower().count("<form")
                        print(f"   📝 Found {form_count} form(s)")
                        
                    if response.security_analysis:
                        if response.security_analysis.has_csrf_tokens:
                            print(f"   🛡️  CSRF protection detected")
                        if response.security_analysis.has_sensitive_data:
                            print(f"   ⚠️  Sensitive data patterns found")
                else:
                    print(f"❌ {vuln_name}: Not accessible ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ {vuln_name}: Error - {e}")

async def main():
    """Run complete DVWA testing workflow"""
    print("🎯 LogicPWN DVWA Complete Testing Example")
    print("=" * 60)
    print("Complete workflow: Check → Setup → Login → Explore")
    print()
    
    # Step 1: Check DVWA availability
    if not await check_dvwa_status():
        return
    
    # Step 2: Setup database if needed
    if not await setup_dvwa_database():
        print("\n⚠️  Please setup the database manually:")
        print("1. Visit: http://localhost:8080/setup.php")
        print("2. Click 'Create / Reset Database'")
        print("3. Run this script again")
        return
    
    # Step 3: Login to DVWA
    session_cookie = await login_to_dvwa()
    
    # Step 4: Explore vulnerabilities
    if session_cookie:
        await explore_dvwa_vulnerabilities(session_cookie)
    
    print("\n🎉 DVWA testing workflow completed!")
    print("\nNext steps:")
    print("- Modify security level in DVWA")
    print("- Test specific vulnerabilities")
    print("- Build exploit chains")

if __name__ == "__main__":
    asyncio.run(main())
